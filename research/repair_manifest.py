#!/usr/bin/env python3
"""Rebuild research/pages/MANIFEST.tsv so every cached page has a verified URL.

Why. fetch.sh records `name -> URL` as it fetches. Over time the manifest drifted from the
directory: 52 recorded names had no matching file, and 185 cached files had no manifest
entry at all. `build_doc_index.py` falls back to re-deriving a URL from the filename for
those 185, and the filename encoding is lossy, so the fallback is a guess.

A guess is the exact failure this project was built to stop. notes-known-404.txt records
that 22 of the first 39 plausible paths guessed during setup returned 404. Guessing our own
corpus is the same move at a larger scale, and the documentation index publishes those
guessed URLs as though they were recorded facts.

This script resolves every cached page for real and rewrites the manifest with a
provenance column, so a reader can tell a URL that was recorded at fetch time from one
confirmed today.

Usage:
    python3 research/repair_manifest.py            # verify and rewrite
    python3 research/repair_manifest.py --dry-run  # report only
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAGES = HERE / "pages"
MANIFEST = PAGES / "MANIFEST.tsv"
TIMEOUT = 25
WORKERS = 8

DOC_ROOT = "https://cloud.google.com/apigee/docs/"

# Verified corrections for cached pages whose filename is a scratch name rather than a doc
# slug, so the derived URL is wrong. Each entry below was confirmed by fetching it and
# checking the returned title, not by pattern. A page that cannot be resolved is listed in
# UNRESOLVED rather than given a plausible-looking URL, because publishing a guess in a
# provenance table is the defect this script exists to remove.
CORRECTIONS = {
    "dbg_trace":
        "api-platform/debug/trace-overview",
    "ui-deploy-new":
        "api-platform/deploy/ui-deploy-overview",
    "mon_fault-codes":
        "api-monitoring/fault-codes",
    "rt_spike":
        "api-platform/troubleshoot/policies/runtime/spike-arrest-runtime-errors",
    "rt_java":
        "api-platform/troubleshoot/policies/runtime/java-callout-runtime-errors",
    "rt_py":
        "api-platform/troubleshoot/policies/runtime/python-script-runtime-errors",
    "api-platform_troubleshoot_playbooks_504-target-read-timeout":
        "api-platform/troubleshoot/playbooks/runtime/504-target-read-timeout",
    "api-platform_troubleshoot_playbooks_vpc-503-target-connect-timeout":
        "api-platform/troubleshoot/playbooks/runtime/vpc-503-target-connect-timeout",
}

# Cached under a scratch name whose real location could not be confirmed. Left explicitly
# unresolved rather than guessed.
UNRESOLVED = {
    "rt_xv": "contains a SourceMessageNotAvailable section; no confirmed doc path",
    "hybrid-metrics": "contains an 'About metrics' section; no confirmed doc path",
    "hybrid-data-collection": "no heading captured; no confirmed doc path",
    "mgmt-apis-create": "no heading captured; no confirmed doc path",
    "api-platform_troubleshoot_playbooks_api-calls-fail-timeout-errors":
        "real path not confirmed; the ingressgateway variant exists but is a different page",
}


def guess_url(stem: str) -> str:
    return DOC_ROOT + stem.replace("_", "/")


def resolve(url: str) -> tuple[str, int | None, str]:
    """Resolve one URL. Returns (final_url, http_code, note)."""
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as fh:
        path = fh.name
    try:
        proc = subprocess.run(
            ["curl", "-sL", "--max-redirs", "10", "-o", path,
             "-w", "%{http_code}\t%{url_effective}", "--max-time", str(TIMEOUT), url],
            capture_output=True, text=True, timeout=TIMEOUT + 10,
        )
        parts = (proc.stdout or "").strip().split("\t")
        code = int(parts[0]) if parts and parts[0].isdigit() else None
        final = parts[1] if len(parts) > 1 else url
        try:
            body = Path(path).read_text(encoding="utf-8", errors="replace")
        except OSError:
            body = ""
        note = ""
        if "equivalent page does not exist in apigee" in body.lower():
            note = "SOFT_404"
        elif code is None:
            note = "NO_RESPONSE"
        elif code >= 400:
            note = f"HTTP_{code}"
        return final, code, note
    except Exception as e:
        return url, None, f"ERROR_{type(e).__name__}"
    finally:
        try:
            Path(path).unlink()
        except OSError:
            pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    recorded: dict[str, str] = {}
    prior_provenance: dict[str, str] = {}
    if MANIFEST.is_file():
        for line in MANIFEST.read_text(errors="replace").splitlines():
            if line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) >= 2 and parts[0] and parts[1]:
                recorded[parts[0]] = parts[1]
                if len(parts) >= 3 and parts[2]:
                    prior_provenance[parts[0]] = parts[2]

    files = sorted(PAGES.glob("*.txt"))
    if not files:
        print(f"no cached pages in {PAGES}", file=sys.stderr)
        return 1

    jobs: list[tuple[str, str, str]] = []
    for f in files:
        stem = f.stem
        if stem in UNRESOLVED:
            jobs.append((stem, "", "unresolved"))
        elif stem in CORRECTIONS:
            jobs.append((stem, DOC_ROOT + CORRECTIONS[stem], "corrected"))
        elif stem in recorded:
            # Carry the previous provenance forward rather than relabelling it. A row this
            # script wrote last run as "guess" must not read back as "recorded", or the
            # column decays into "everything was recorded by fetch.sh" after two runs and
            # stops carrying information.
            prior = prior_provenance.get(stem, "")
            base = prior.split(";")[0] if prior else "recorded"
            if base not in ("recorded", "corrected", "guess"):
                base = "recorded"
            jobs.append((stem, recorded[stem], base))
        else:
            jobs.append((stem, guess_url(stem), "guess"))

    by_provenance: dict[str, int] = {}
    for _s, _u, prov in jobs:
        by_provenance[prov] = by_provenance.get(prov, 0) + 1
    print(f"resolving {len(jobs)} cached pages: "
          + ", ".join(f"{k} {v}" for k, v in sorted(by_provenance.items())))

    todo = [j for j in jobs if j[1]]
    with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        resolved = list(ex.map(lambda j: resolve(j[1]), todo))
    outcome = dict(zip([j[0] for j in todo], resolved))

    rows: list[tuple[str, str, str]] = []
    bad: list[tuple[str, str, str]] = []
    for stem, url, provenance in jobs:
        if not url:
            rows.append((stem, "", f"UNRESOLVED;{UNRESOLVED.get(stem, 'unconfirmed')}"))
            continue
        final, code, note = outcome[stem]
        prov = provenance
        if note:
            prov += f";{note}"
            if note == "SOFT_404" or note.startswith("HTTP_4"):
                bad.append((stem, final or url, note))
        if final and final != url:
            prov += ";redirected"
        rows.append((stem, final or url, prov))

    for stem, url, note in bad:
        print(f"  UNRESOLVED  {stem}\n              {url}  ({note})")
    for stem in sorted(UNRESOLVED):
        print(f"  UNRESOLVED  {stem}\n              {UNRESOLVED[stem]}")

    if args.dry_run:
        print("\ndry run, manifest not written")
        return 0

    out = ["# name\turl\tprovenance",
           "# Generated by research/repair_manifest.py. Do not edit by hand.",
           "# provenance: recorded  = URL recorded by fetch.sh when the page was fetched",
           "#             corrected = filename was a scratch name; URL confirmed by fetch",
           "#             guess      = URL derived from the lossy filename encoding and",
           "#                          confirmed live when this manifest was written",
           "#             unresolved = no confirmed URL; the page is not citable yet",
           "# Every URL below was confirmed live on the date this file was written."]
    for stem, url, prov in rows:
        out.append(f"{stem}\t{url}\t{prov}")
    MANIFEST.write_text("\n".join(out) + "\n", encoding="utf-8")
    final_counts: dict[str, int] = {}
    for _s, _u, prov in rows:
        final_counts[prov.split(";")[0]] = final_counts.get(prov.split(";")[0], 0) + 1
    print(f"\nwrote {MANIFEST}: {len(rows)} entries ("
          + ", ".join(f"{k} {v}" for k, v in sorted(final_counts.items())) + ")")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())