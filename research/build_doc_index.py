#!/usr/bin/env python3
"""Build research/official-documentation-index.md from the pages actually fetched.

The project brief asks for a documentation index and, separately, for honesty about how
complete it is. This script produces both: the index, and a measured coverage statement
derived from what is on disk rather than from an optimistic guess.

Every row is a page that exists in research/pages/, which means it returned 200 at fetch
time. Pass --verify to re-check every URL right now, which also catches pages that have
since moved. Pass --check-known to re-check a hand-maintained list of URLs that returned
404 during research, so a dead link that gets revived is noticed.

Usage:
    python3 research/build_doc_index.py
    python3 research/build_doc_index.py --verify
    python3 research/build_doc_index.py --check-known
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import re
import subprocess
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
PAGES = HERE / "pages"
NOTES = HERE / "notes-known-404.txt"
OUT = HERE / "official-documentation-index.md"

DOC_ROOT = "https://cloud.google.com/apigee/docs/"
OPDK_ROOT = "https://docs.apigee.com/private-cloud/"

# Areas used to group the index. Order is the order they appear in the output.
AREAS = [
    ("Fundamentals", ("/api-platform/fundamentals", "/api-platform/get-started")),
    ("Policy reference", ("/api-platform/reference/policies",)),
    ("Other reference", ("/api-platform/reference",)),
    ("Troubleshooting and debugging", ("/api-platform/troubleshoot", "/api-platform/debug", "/api-platform/monitoring")),
    ("Proxy development", ("/api-platform/develop", "/api-platform/proxy-development", "/api-platform/reference/policies")),
    ("Deployment and CI/CD", ("/api-platform/deploy",)),
    ("Security", ("/api-platform/security",)),
    ("Hybrid", ("/hybrid",)),
    ("Edge for Private Cloud", ("/private-cloud", "/edge-private-cloud")),
]

OTHER = "Other"


def area_for(path: str) -> str:
    if not path.startswith("/"):
        path = "/" + path
    for label, prefixes in AREAS:
        if any(p in path for p in prefixes):
            return label
    return OTHER


MANIFEST = PAGES / "MANIFEST.tsv"


def load_manifest() -> dict[str, str]:
    """name -> URL, from the manifest fetch.sh writes.

    Deriving the URL from the filename does not work. fetch.sh replaces slashes and
    colons with underscores, and that mapping is lossy: `https___docs.apigee.com_x`
    cannot be inverted reliably. Earlier revisions of this script guessed, and guessed
    wrong for every absolute URL. Read the manifest instead.
    """
    if not MANIFEST.is_file():
        return {}
    out: dict[str, str] = {}
    for line in MANIFEST.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.split("\t")
        if len(parts) >= 2 and parts[0] and parts[1]:
            out[parts[0]] = parts[1]
    return out


def url_for(stem: str, manifest: dict[str, str]) -> str:
    if stem in manifest:
        return manifest[stem]
    return DOC_ROOT + stem.replace("_", "/")


def title_of(text: str, fallback: str) -> str:
    m = re.search(r"^#\s+(.*)$", text, re.MULTILINE)
    if not m:
        return fallback
    t = m.group(1)
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"\s+", " ", t).replace("*", "").strip()
    return t or fallback


def note_for(url: str) -> str:
    """Why a page matters for support work, inferred from its path.

    Deliberately shallow. A richer per-page purpose belongs in the research notes; this
    is only so the index is not a bare URL dump.
    """
    p = url
    if "/reference/policies/" in p:
        policy = p.rsplit("/", 1)[-1].replace("-policy", "").replace("-", " ")
        return f"Configuration, element and error reference for the {policy} policy."
    if "compare-apigee-products" in p:
        return "Which features and APIs each product supports. Load before any product-specific procedure."
    if "/fundamentals/" in p:
        return "Core runtime behaviour that explains policy faults."
    if "/troubleshoot" in p:
        return "Symptom-led diagnostic procedure."
    if "/deploy" in p:
        return "Revision and deployment lifecycle."
    if "/hybrid" in p:
        return "Hybrid runtime or control-plane behaviour."
    if "private-cloud" in p:
        return "Edge for Private Cloud operational reference."
    if "release-notes" in p:
        return "Version history and behaviour changes."
    return "Supporting reference."


def http_status(url: str) -> str:
    try:
        out = subprocess.run(
            ["curl", "-sL", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", "20", url],
            capture_output=True, text=True, timeout=30,
        )
        return out.stdout.strip() or "000"
    except Exception:
        return "000"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true", help="re-check every indexed URL now")
    ap.add_argument("--check-known", action="store_true", help="re-check the recorded 404 list")
    args = ap.parse_args()

    if args.check_known and NOTES.is_file():
        known = [ln.strip() for ln in NOTES.read_text().splitlines()
                 if ln.strip() and not ln.startswith("#")]
        print(f"re-checking {len(known)} recorded 404 URLs")
        revived = []
        with cf.ThreadPoolExecutor(max_workers=12) as ex:
            for url, code in zip(known, ex.map(http_status, known)):
                if code != "404":
                    revived.append((url, code))
        if revived:
            print("no longer 404:")
            for url, code in revived:
                print(f"  {code}  {url}")
        else:
            print("all still 404")
        return 0

    pages = sorted(PAGES.glob("*.txt"))
    if not pages:
        print(f"no pages in {PAGES}, run research/fetch.sh first")
        return 1

    manifest = load_manifest()
    rows = []
    for p in pages:
        text = p.read_text(encoding="utf-8", errors="replace")
        url = url_for(p.stem, manifest)
        rows.append({
            "title": title_of(text, p.stem),
            "url": url,
            "path": url.replace(DOC_ROOT, "").replace(OPDK_ROOT, ""),
            "bytes": p.stat().st_size,
            "area": area_for(url.replace(DOC_ROOT, "").replace(OPDK_ROOT, "")),
        })

    status_line = "status not re-verified in this run (each page returned 200 when fetched)"
    if args.verify:
        print(f"verifying {len(rows)} URLs")
        with cf.ThreadPoolExecutor(max_workers=12) as ex:
            codes = list(ex.map(http_status, [r["url"] for r in rows]))
        for r, c in zip(rows, codes):
            r["status"] = c
        bad = [r for r in rows if r["status"] != "200"]
        status_line = (f"re-verified this run, {len(rows) - len(bad)} of {len(rows)} returned 200")
        if bad:
            status_line += f", {len(bad)} did not"
            print("not reachable now:")
            for r in bad[:20]:
                print(f"  {r['status']}  {r['url']}")

    grouped = defaultdict(list)
    for r in rows:
        grouped[r["area"]].append(r)

    L = []
    A = L.append
    A("# Official documentation index")
    A("")
    A("Generated by `python3 research/build_doc_index.py`. Every row is a page that was")
    A("actually fetched into `research/pages/`, not a link taken from a search result.")
    A("")
    A(f"**Coverage statement.** This index contains {len(rows)} Apigee documentation pages")
    A("that were fetched and read during this project. That is not every page Google has")
    A("published. The set was built by walking the navigation tree of seed pages, so it")
    A("reflects what a reader starting from those seeds would reach. Areas that are thin")
    A("are thin because the seeds led there, and the count below should be read that way.")
    A("")
    A(f"**Verification.** {status_line}.")
    A("")
    A("## How to re-verify")
    A("")
    A("```bash")
    A("cd research")
    A("./fetch.sh <doc-path>              # fetch one page, prints status")
    A("python3 build_doc_index.py --verify # re-check every URL in this index")
    A("python3 build_doc_index.py --check-known  # re-check the recorded 404 list")
    A("```")
    A("")
    A("## Records")
    A("")
    A("URLs that returned 404 during research are listed in `notes-known-404.txt`.")
    A("Negative results matter: a URL that 404s today may be a page that moved, and")
    A("citing it anyway is how a skill ends up teaching a dead link.")
    A("")

    ordered = [label for label, _ in AREAS] + [OTHER]
    for area in ordered:
        items = sorted(grouped.get(area, []), key=lambda r: r["path"])
        if not items:
            continue
        A(f"## {area} ({len(items)})")
        A("")
        A("| Page | URL | Bytes | Why it is here |")
        A("| --- | --- | --- | --- |")
        for r in items:
            A(f"| {r['title']} | [{r['path']}]({r['url']}) | {r['bytes']} | {note_for(r['url'])} |")
        A("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"wrote {OUT}")
    for area in ordered:
        if grouped.get(area):
            print(f"  {area}: {len(grouped[area])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())