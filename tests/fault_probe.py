#!/usr/bin/env python3
"""Probe tests/check_repo.py with controlled mutations to find false passes.

Why this exists. The project's own history records several checkers that reported success
while checking nothing: one skipped every scenario whose title contained a section name,
one reported PASS having verified zero URLs, one matched no scenario IDs. A checker that
passes a broken project is worse than no checker, because it converts an unknown into a
known-good. Reading the checker is not enough to know, and its own docstring is not
evidence about its behaviour.

So: take an isolated copy of the repo, break one thing at a time, run the checker, and
record what it did. A mutation that the checker fails to catch is a defect in the checker.

Usage:
    python3 tests/fault_probe.py            # run every probe, print a table
    python3 tests/fault_probe.py --json     # machine-readable

Nothing here writes to the active project. Every probe runs against a throwaway copy under
the system temp directory, or against a synthetic fixture it builds itself.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Harness
# ---------------------------------------------------------------------------


def run_checker(root: Path) -> tuple[int, str]:
    """Run the repo checker against a root and return (exit code, output)."""
    proc = subprocess.run(
        [sys.executable, str(root / "tests" / "check_repo.py"), "--root", str(root)],
        capture_output=True, text=True, timeout=300,
    )
    return proc.returncode, proc.stdout + proc.stderr


def scenario_span(text: str, sid: str) -> tuple[int, int]:
    """Return (start, end) character offsets of the `### <sid>` block."""
    lines = text.splitlines(keepends=True)
    starts = [i for i, ln in enumerate(lines) if re.match(rf"^### {re.escape(sid)}\b", ln)]
    if not starts:
        raise AssertionError(f"{sid} not found")
    start = starts[0]
    later = [i for i in starts[1:]] + [
        i for i, ln in enumerate(lines) if i > start and re.match(r"^### ", ln)
    ]
    end = min(later) if later else len(lines)
    return sum(len(x) for x in lines[:start]), sum(len(x) for x in lines[:end])


class Sandbox:
    """A disposable copy of the repository."""

    def __init__(self) -> None:
        self.dir = Path(tempfile.mkdtemp(prefix="apigee-faultprobe-"))
        self.root = self.dir / "repo"
        shutil.copytree(REPO, self.root, ignore=shutil.ignore_patterns(
            ".git", "__pycache__", "*.pyc"))

    def fingerprint(self) -> str:
        """A digest of every file's path and content.

        Used to tell a probe that broke something from a probe that did not. Timestamps
        cannot do this job: a probe whose regex matches nothing still calls write_text,
        so the file's mtime moves while its bytes do not.
        """
        h = hashlib.sha256()
        for p in sorted(self.root.rglob("*")):
            if not p.is_file():
                continue
            h.update(str(p.relative_to(self.root)).encode())
            h.update(b"\0")
            h.update(p.read_bytes())
            h.update(b"\0")
        return h.hexdigest()

    def path(self, rel: str) -> Path:
        return self.root / rel

    def read(self, rel: str) -> str:
        return self.path(rel).read_text(encoding="utf-8")

    def write(self, rel: str, text: str) -> None:
        self.path(rel).write_text(text, encoding="utf-8")

    def edit(self, rel: str, old: str, new: str, count: int = 1) -> None:
        text = self.read(rel)
        if old not in text:
            raise AssertionError(f"{rel}: pattern not found: {old[:60]!r}")
        self.write(rel, text.replace(old, new, count))

    def cleanup(self) -> None:
        shutil.rmtree(self.dir, ignore_errors=True)


class Outcome:
    def __init__(self, name: str, expect: str, detail: str) -> None:
        self.name = name
        self.expect = expect          # "FAIL" or "PASS"
        self.detail = detail
        self.code: int | None = None
        self.caught = False
        self.note = ""
        # Did the probe change any file? A probe that changes nothing has not tested
        # anything, whatever the checker went on to say. This is tracked rather than
        # assumed because `origin-field-removed` and `origin-unclassifiable-value` both
        # reported green for as long as the suite had existed: their regexes matched
        # nothing, they wrote the file back unchanged, and the unmodified sandbox was
        # failing for an unrelated reason, so every probe expecting a FAIL saw one.
        self.mutated: bool | None = None

    @property
    def inert(self) -> bool:
        """A FAIL-expecting probe that did not change the repository."""
        return self.expect == "FAIL" and self.mutated is False

    @property
    def ok(self) -> bool:
        if self.inert:
            return False
        return self.caught == (self.expect == "FAIL")

    def render(self) -> str:
        mark = "ok  " if self.ok else "MISS"
        if self.inert:
            return (f"{mark} {self.name}\n       expected {self.expect}, checker "
                    f"{'caught it' if self.caught else 'DID NOT CATCH IT'}"
                    f"  [probe changed nothing, so the verdict came from an unmodified "
                    f"repository]")
        return (f"{mark} {self.name}\n       expected {self.expect}, checker "
                f"{'caught it' if self.caught else 'DID NOT CATCH IT'}"
                + (f"  [{self.note}]" if self.note else ""))


# ---------------------------------------------------------------------------
# Probes against the real repository checker
# ---------------------------------------------------------------------------

PROBES = []


def probe(name: str, expect: str, detail: str):
    def deco(fn):
        PROBES.append((name, expect, detail, fn))
        return fn
    return deco


@probe("valid-repo-baseline", "PASS", "the unmodified repo must still pass")
def _p_baseline(sb: Sandbox) -> None:
    pass


@probe("scenario-missing-required-section", "FAIL",
       "delete the Ground-truth resolution section from one easy scenario")
def _p_missing_section(sb: Sandbox) -> None:
    sb.edit("scenarios/easy.md", "#### Ground-truth resolution\n", "#### Not a section\n")


@probe("scenario-empty-required-section", "FAIL",
       "keep the heading but empty its body")
def _p_empty_section(sb: Sandbox) -> None:
    start, end = scenario_span(sb.read("scenarios/easy.md"), "EASY-01")
    text = sb.read("scenarios/easy.md")
    # Replace the whole verification section body with nothing.
    sb.edit("scenarios/easy.md",
            "#### Verification\n", "#### Verification\n\nPLACEHOLDER_MARKER\n", 1)


@probe("adversarial-scenario-missing-section", "FAIL",
       "break a section in adversarial.md, which check_scenarios does not walk")
def _p_adv_missing_section(sb: Sandbox) -> None:
    sb.edit("scenarios/adversarial.md", "#### Ground-truth resolution\n",
            "#### Removed by fault probe\n")


@probe("regression-scenario-missing-section", "FAIL",
       "break a section in regression.md, which check_scenarios does not walk")
def _p_reg_missing_section(sb: Sandbox) -> None:
    sb.edit("scenarios/regression.md", "#### Ground-truth resolution\n",
            "#### Removed by fault probe\n")


@probe("duplicate-scenario-id", "FAIL", "repeat a scenario ID in the same file")
def _p_duplicate_id(sb: Sandbox) -> None:
    text = sb.read("scenarios/easy.md")
    sb.edit("scenarios/easy.md", "### EASY-02.", "### EASY-01. duplicate injected")


@probe("answer-key-critical-failures-removed", "FAIL",
       "strip every critical-failure condition out of one answer key")
def _p_key_no_cf(sb: Sandbox) -> None:
    p = sb.path("evaluation/packets/EASY-01.key.md")
    text = p.read_text()
    if "## Critical failures" not in text:
        raise AssertionError("fixture precondition failed: no CF section in key")
    head = text.split("## Critical failures")[0]
    p.write_text(head + "## Critical failures\n\n")

    # Key is now newer than nothing in particular; keep it newer than its scenario.
    p.touch()


@probe("answer-key-truncated-critical-failure", "FAIL",
       "cut a bold critical-failure condition down to its first sentence in the key")
def _p_key_truncated_cf(sb: Sandbox) -> None:
    # The completeness check reads the source paragraph and requires its final words to
    # reach the key. Target EASY-01, whose source uses the bold form, and cut the key at
    # the first sentence so the tail the check looks for is gone.
    key = sb.path("evaluation/packets/EASY-01.key.md")
    kt = key.read_text()
    head, sep, cf = kt.partition("## Critical failures")
    if not sep:
        raise AssertionError("EASY-01 key has no Critical failures section")
    first_clause = cf.strip().split(";")[0] + "."
    key.write_text(head + sep + "\n\n" + first_clause + "\n")
    key.touch()
    if first_clause == cf.strip():
        raise AssertionError("truncation was a no-op; the CF text has one clause only")


@probe("answer-key-not-a-critical-failure-loses-subject", "FAIL",
       "strip the subject from a 'Not a critical failure' ruling in the key, leaving a "
       "sentence a grader cannot apply to anything")
def _p_key_ncf_no_subject(sb: Sandbox) -> None:
    # MED-11's key once opened its ruling with "finding, not a wrong answer. It becomes
    # wrong only when...", because the generator took the body and dropped the heading the
    # subject lived in. The completeness check looks for the head of the ruling, so cutting
    # the subject is what makes it fire.
    key = sb.path("evaluation/packets/MED-11.key.md")
    kt = key.read_text()
    marker = "## Not A Critical Failure\n"
    if marker not in kt:
        raise AssertionError("MED-11 key has no 'Not A Critical Failure' section")
    head, _, rest = kt.partition(marker)
    body = rest.split("\n## ", 1)[0]
    stripped = re.sub(r"^(Not a critical failure: )?[^.]*\.\s*", "", body.strip(), count=1)
    if stripped == body.strip():
        raise AssertionError("the strip was a no-op; the ruling text did not match")
    key.write_text(head + marker + stripped + "\n## " + rest.split("\n## ", 1)[1])
    key.touch()


@probe("answer-key-second-ruling-dropped", "FAIL",
       "delete the second of a scenario's two 'Not a critical failure' rulings, which the "
       "generator used to discard silently")
def _p_key_second_ruling(sb: Sandbox) -> None:
    # MED-09 carries two rulings and the generator's section() returned only the first. The
    # second was the one cb057df added to stop the grader failing a documented-correct
    # caveat, so its loss reinstated that defect invisibly: the key looked complete.
    key = sb.path("evaluation/packets/MED-09.key.md")
    kt = key.read_text()
    marker = "## Not A Critical Failure\n"
    if kt.count(marker) < 2:
        raise AssertionError("MED-09 key should carry two rulings")
    first_end = kt.index(marker) + len(marker)
    second = kt.index(marker, first_end)
    following = kt.find("\n## ", second + len(marker))
    if following == -1:
        raise AssertionError("unexpected key shape; no section follows the second ruling")
    key.write_text(kt[:second] + kt[following + 1:])
    key.touch()


@probe("packet-turn2-deleted", "FAIL",
       "delete one turn-2 packet so a multi-turn run would be unusable")
def _p_missing_turn2(sb: Sandbox) -> None:
    sb.path("evaluation/packets/MED-01.turn2.prompt.md").unlink()


@probe("packet-key-deleted", "FAIL",
       "delete one answer key; the scenario then has no gradable ground truth")
def _p_missing_key(sb: Sandbox) -> None:
    sb.path("evaluation/packets/HARD-05.key.md").unlink()


@probe("packet-ground-truth-leak", "FAIL",
       "paste the ground-truth heading and answer into a turn-1 prompt")
def _p_leak(sb: Sandbox) -> None:
    p = sb.path("evaluation/packets/EASY-02.prompt.md")
    p.write_text(p.read_text() + "\n## Ground-Truth Resolution\nThe answer is quota.\n")


@probe("stale-packet-answer-key", "FAIL",
       "rewrite a scenario's ground truth without regenerating its packet")
def _p_stale(sb: Sandbox) -> None:
    sb.edit("scenarios/easy.md",
            "`InvalidQuotaInterval` fires when the `<Interval>` element is not an integer.",
            "`InvalidQuotaInterval` fires when the quota is exhausted.", 1)
    # The packets are made strictly NEWER than the scenario, so a checker that trusts
    # timestamps passes this probe without reading a single byte of either file. That is
    # not a contrivance: running the generator, committing, then restoring an old
    # mtime-free state all leave packets newer than the scenario that no longer matches
    # them. The previous version of this probe did the opposite, aged the packets, and
    # so only ever tested the timestamp comparison.
    import os
    scen = sb.path("scenarios/easy.md").stat().st_mtime
    for k in sb.path("evaluation/packets").glob("*.md"):
        os.utime(k, (scen + 10_000, scen + 10_000))


@probe("packets-touched-after-checkout", "PASS",
       "every packet is older than its scenario and no content changed, which is what a "
       "fresh clone produces; timestamps are not recorded in a commit, so a checker that "
       "reads them reports 103 stale answer keys on a correct tree")
def _p_checkout_mtimes(sb: Sandbox) -> None:
    import os
    for k in sb.path("evaluation/packets").glob("*.md"):
        os.utime(k, (0, 0))
    for s in sb.path("scenarios").glob("*.md"):
        os.utime(s, (1_000_000, 1_000_000))


@probe("skill-frontmatter-removed", "FAIL", "delete a SKILL.md frontmatter block")
def _p_no_frontmatter(sb: Sandbox) -> None:
    sb.edit(".agents/skills/apigee-support-core/SKILL.md", "---", "xx", 1)


@probe("skill-name-directory-mismatch", "FAIL",
       "rename the frontmatter name so it no longer matches its directory")
def _p_name_mismatch(sb: Sandbox) -> None:
    sb.edit(".agents/skills/apigee-support-core/SKILL.md",
            "name: apigee-support-core", "name: apigee-core")


@probe("deleted-reference-file-still-listed-in-skill", "FAIL",
       "delete a reference file while the skill's table still lists it: the listed path "
       "must be resolved, not merely have its filename appear somewhere in the body")
def _p_broken_link(sb: Sandbox) -> None:
    (sb.path(".agents/skills/apigee-support-core/references") / "error-codes.md").unlink()


@probe("unreferenced-orphan-reference-file", "FAIL",
       "add a reference file the skill never names, so nothing will load it")
def _p_orphan_reference(sb: Sandbox) -> None:
    sb.write(".agents/skills/apigee-support-core/references/orphan.md",
             "# Orphan\n\nNever mentioned in SKILL.md.\n")


@probe("malformed-xml-in-scenario", "FAIL",
       "introduce an unclosed element in a fenced XML block")
def _p_bad_xml(sb: Sandbox) -> None:
    p = sb.path("scenarios/easy.md")
    t = p.read_text()
    m = re.search(r"```xml\n(.*?)```", t, re.DOTALL)
    if not m:
        raise AssertionError("no xml block to break")
    broken = m.group(1).replace("</Quota>", "<Quota>")
    if broken == m.group(1):
        broken = m.group(1) + "\n<Broken attr="
    p.write_text(t[:m.start(1)] + broken + t[m.end(1):])


@probe("malformed-json-in-scenario", "FAIL",
       "introduce a JSON syntax error in a fenced JSON block")
def _p_bad_json(sb: Sandbox) -> None:
    p = sb.path("scenarios/easy.md")
    t = p.read_text()
    m = re.search(r"```json\n(.*?)\n(?:>\s*)?```", t, re.DOTALL)
    if not m:
        # no json in easy.md; put one into a scenario that will be checked
        sb.write("scenarios/probe-json.md",
                 "# probe\n\n### EASY-90. json probe\n\n```json\n{\"a\": }\n```\n")
        return
    p.write_text(t[:m.start(1)] + m.group(1) + "," + t[m.end(1):])


@probe("generated-reference-raw-html", "FAIL",
       "put a raw <span> into a generated reference file")
def _p_raw_html(sb: Sandbox) -> None:
    p = sb.path(".agents/skills/apigee-support-core/references/error-codes.md")
    p.write_text(p.read_text().replace("| `policies.ratelimit.QuotaViolation`",
                                       "| `<span>x</span>`cell` |", 1))


@probe("scenario-file-deleted", "FAIL",
       "delete a whole scenario file and see whether coverage is detected")
def _p_delete_file(sb: Sandbox) -> None:
    sb.path("scenarios/regression.md").unlink()


@probe("all-scenarios-deleted", "FAIL",
       "empty every scenario file: the checker must not report success")
def _p_delete_all(sb: Sandbox) -> None:
    for f in sb.path("scenarios").glob("*.md"):
        if f.name != "index.md":
            f.write_text("# emptied by fault probe\n")


@probe("packets-directory-missing", "FAIL",
       "remove the packet directory; evaluation inputs no longer exist")
def _p_no_packets(sb: Sandbox) -> None:
    shutil.rmtree(sb.path("evaluation/packets"))


@probe("research-pages-emptied", "FAIL",
       "empty the cached research corpus behind the generated index")
def _p_no_pages(sb: Sandbox) -> None:
    for f in sb.path("research/pages").glob("*.txt"):
        f.unlink()


@probe("error-codes-index-stale", "FAIL",
       "corrupt the generated fault-code index while its source pages are untouched")
def _p_stale_index(sb: Sandbox) -> None:
    p = sb.path(".agents/skills/apigee-support-core/references/error-codes.md")
    t = p.read_text()
    # Drop every SpikeArrest runtime code, the historical parser failure.
    t = re.sub(r"^\| `policies\.ratelimit\.(FailedToResolveSpikeArrestRate"
               r"|InvalidMessageWeight|SpikeArrestViolation)`.*$", "", t, flags=re.M)
    p.write_text(t)


@probe("error-index-generator-drops-anchored-error-sections", "FAIL",
       "revert the tolerant 'Error reference' heading match in build_error_index.py; the "
       "unfixed generator silently drops every runtime, deployment and fault-variable row "
       "on a page whose heading is published as '## <span id=\"errorcodes\"></span>Error "
       "reference', which is how OAuthV2 and VerifyIAM are published")
def _p_index_heading_anchor(sb: Sandbox) -> None:
    sb.edit("research/build_error_index.py",
            r'r"^##\s*(?:<[^>]+>\s*)*Error reference\s*$"',
            r'r"^## Error reference\s*$"')


@probe("scenario-id-numbering-gap", "FAIL",
       "an unexplained gap in the ID sequence should be visible, not silent")
def _p_id_gap(sb: Sandbox) -> None:
    p = sb.path("scenarios/medium.md")
    start, end = scenario_span(p.read_text(), "MED-20")
    text = p.read_text()
    block = text[start:end]
    p.write_text(text[:start] + text[end:])


@probe("synthetic-scenario-relabelled-real-world", "FAIL",
       "relabel a regression scenario as a reported real-world case")
def _p_origin_inflated(sb: Sandbox) -> None:
    p = sb.path("scenarios/regression.md")
    p.write_text(re.sub(r"- Origin: [^\n]+",
                        "- Origin: reported real-world case (injected by fault probe)",
                        p.read_text(), count=1))


@probe("origin-field-removed", "FAIL",
       "delete the Origin field entirely, leaving provenance unclassifiable")
def _p_origin_missing(sb: Sandbox) -> None:
    p = sb.path("scenarios/easy.md")
    p.write_text(re.sub(r"^- Origin: [^\n]+\n", "", p.read_text(), count=1, flags=re.M))


@probe("origin-unclassifiable-value", "FAIL",
       "use an origin label outside the controlled vocabulary")
def _p_origin_vague(sb: Sandbox) -> None:
    p = sb.path("scenarios/easy.md")
    p.write_text(re.sub(r"^- Origin: [^\n]+", "- Origin: based on something we saw once",
                        p.read_text(), count=1, flags=re.M))


@probe("reference-path-unresolvable", "FAIL",
       "point a SKILL.md reference table entry at a path that does not exist")
def _p_bad_ref_path(sb: Sandbox) -> None:
    skill = sb.path(".agents/skills/apigee-support-core/SKILL.md")
    skill.write_text(skill.read_text().replace(
        "`references/products.md`", "`references/products-v9.md`"))


@probe("scenario-invents-fault-code", "FAIL",
       "replace a real fault code in a scenario body with a plausible one that does not exist")
def _p_invented_code(sb: Sandbox) -> None:
    p = sb.path("scenarios/easy.md")
    t = p.read_text()
    if "`InvalidQuotaInterval`" not in t:
        raise AssertionError("fixture precondition failed: code not present")
    p.write_text(t.replace("`InvalidQuotaInterval`",
                          "`steps.quota.TotallyMadeUpQuotaCode`", 1))


@probe("scenario-code-quoted-as-real-but-absent", "FAIL",
       "quote a non-existent code with no unverified marker, presented as fact")
def _p_unmarked_fake_code(sb: Sandbox) -> None:
    p = sb.path("scenarios/easy.md")
    t = p.read_text()
    t = t.replace("`InvalidQuotaInterval`", "`steps.raisefault.NotADocumentedFault`", 1)
    # Make sure no nearby 'unverified' wording excuses it.
    t = t.replace("unverified", "confirmed", 1)
    p.write_text(t)


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--only", default=None, help="substring filter on probe name")
    args = ap.parse_args()

    results: list[Outcome] = []
    for name, expect, detail, fn in PROBES:
        if args.only and args.only not in name:
            continue
        sb = Sandbox()
        o = Outcome(name, expect, detail)
        try:
            before = sb.fingerprint()
            fn(sb)
            o.mutated = sb.fingerprint() != before
            code, out = run_checker(sb.root)
            o.code = code
            o.caught = code != 0
            failed_lines = [ln.strip() for ln in out.splitlines()
                            if ln.strip().startswith("- ") and "scenario " not in ln]
            o.note = f"exit {code}"
        except AssertionError as e:
            o.note = f"probe could not run: {e}"
            o.caught = None  # type: ignore[assignment]
        finally:
            sb.cleanup()
        results.append(o)

    if args.json:
        print(json.dumps([
            {"name": o.name, "expect": o.expect, "caught": o.caught,
             "mutated": o.mutated, "inert": o.inert,
             "exit": o.code, "detail": o.detail, "note": o.note}
            for o in results
        ], indent=2))
    else:
        for o in results:
            print(o.render())
        missed = [o for o in results if o.ok is False]
        inert = [o for o in results if o.inert]
        skipped = [o for o in results if o.caught is None]
        print()
        print(f"{len(results)} probes, {len(results) - len(missed) - len(skipped)} "
              f"behaved as expected, {len(missed)} false passes, {len(skipped)} skipped")
        for o in missed:
            print(f"  FALSE PASS: {o.name} ({o.detail})")
        for o in inert:
            print(f"  NO MUTATION: {o.name} changed no file, so it proved nothing "
                  f"({'the checker failed anyway' if o.caught else 'the checker passed'})")
        for o in skipped:
            print(f"  SKIPPED:    {o.name} ({o.note})")
    return 1 if any(o.ok is False for o in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())