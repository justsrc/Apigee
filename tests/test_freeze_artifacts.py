#!/usr/bin/env python3
"""Test that the run 3 freeze cannot be satisfied by material that moved or vanished.

Why this file exists. `evaluation/results/run-3/freeze_artifacts.py` is what PROTOCOL.md's
Resumption section leans on:

    python3 evaluation/results/run-3/freeze_artifacts.py --verify \
        evaluation/results/run-3/artifact-hashes.json              # stops if artifacts moved

    If the artifact verification fails, the run stops. Mixing material versions inside one
    result is worse than an incomplete run.

Three defects made that promise false, and all three were demonstrated against the real file
on 2026-10-14.

  1. Deletion was a skip. The comparison walked the manifest's keys and compared only what
     the tree still had (`if now is not None and now != v`), and `collect()` built `scripts`
     with `if v.is_file()`, so a removed file simply was not in the section to compare.
     Deleting `evaluation/rubric.md`, an answer key, a packet or a whole scenario file left
     `--verify` at exit 0. Adding a scenario was invisible for the mirror-image reason: the
     walk never visited a key the manifest did not have.

  2. The rules that decide a verdict were outside the freeze. `collect()` hashed five
     harness scripts and the material trees. `PROTOCOL.md`, `grade_run.py`,
     `run_generation.py`, `evaluation/model-eval-protocol.md` and `manifest.json` were not
     hashed at all, so editing any of them verified clean. `grade_run.py` is the sharpest
     one: it holds PASS_AT, MARGINAL_AT and SECOND_GRADER_SAMPLE, it is the only thing in
     the repository that turns anchor counts into PASS / MARGINAL / FAIL, and PROTOCOL.md
     gives the reason for the freeze in its own first paragraph, "so the rules that decide a
     verdict cannot be written after the verdicts are known."

  3. The manifest certified itself. `--write` rebuilds the whole file from the tree, so
     editing every artifact and re-running it satisfied `--verify`. Deleting a section
     un-verified everything that section covered, because `old.get(section, {})` iterated
     nothing. `--verify` also accepted any path, so the recorded freeze could be checked
     against a manifest written anywhere else.

The invariants these cases pin down:

  * A deleted artifact is a verification failure, and so is an added one. The frozen set is
    closed. An addition is not a weaker signal than a movement: the population is pinned at
    103 and full-suite yield is PASS / 103, so a 104th scenario moves the denominator.
  * Every file that decides a verdict is inside the frozen set, including the verifier.
  * `manifest.json` is deliberately outside it, because every batch rewrites it, and this
    case exists so that stays a decision rather than an accident.
  * A manifest that has been gutted, emptied of a section, or edited without re-anchoring
    cannot report success.
  * `--verify` may only be pointed at the recorded manifest.
  * An unchanged tree still verifies at exit 0. Every case here is worthless without that
    control: a verifier that fails everything stops the run just as effectively as one that
    fails nothing, and PROTOCOL.md's rule is about a run that is incomplete, not one that
    is blocked forever.

The cases run against scratch trees, never the real repository. The real freeze is already
red on this branch, for an unrelated and correct reason: commits 4098ec4, 0587bc8 and
30e2876 changed `tests/make_packets.py`, `tests/make_eval_workspace.py` and
`tests/release_gate.py` after the freeze was taken at a25333b. So `--verify` on the real
tree exits 1 legitimately, and a case that asserted exit 0 against it would be asserting
that the harness edits were harmless. Each tree here gets its own git repository, and the
real `freeze_artifacts.py` is copied into it so the script's own `parents[3]` root resolves
to the scratch tree rather than to a path this file has to rewrite.

Usage:
    python3 tests/test_freeze_artifacts.py
    python3 tests/test_freeze_artifacts.py --json
    python3 tests/test_freeze_artifacts.py --only deleted
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FREEZER = ROOT / "evaluation" / "results" / "run-3" / "freeze_artifacts.py"

# Every path the fixed collect() declares. A tree missing one of these is not a tree with
# a deleted artifact, it is a tree where the freeze was taken broken, which is a separate
# case below. The last entry is the copy of freeze_artifacts.py itself, which is frozen for
# the same reason as the grader.
DECLARED = (
    "evaluation/rubric.md",
    "evaluation/model-eval-protocol.md",
    "tests/make_packets.py",
    "tests/make_eval_workspace.py",
    "tests/test_isolation.py",
    "tests/release_gate.py",
    "evaluation/results/run-3/PROTOCOL.md",
    "evaluation/results/run-3/grade_run.py",
    "evaluation/results/run-3/run_generation.py",
)

DISCOVERED = (
    "scenarios/easy.md",
    "scenarios/index.md",
    "evaluation/packets/EASY-01.key.md",
    "evaluation/packets/EASY-01.prompt.md",
    "evaluation/packets/EASY-01.turn2.prompt.md",
    ".agents/skills/apigee-support-core/SKILL.md",
)

GIT_ENV = {"GIT_AUTHOR_NAME": "freeze-test", "GIT_AUTHOR_EMAIL": "freeze@test",
           "GIT_COMMITTER_NAME": "freeze-test", "GIT_COMMITTER_EMAIL": "freeze@test",
           "PATH": "/usr/bin:/bin:/usr/local/bin", "HOME": "/tmp"}

RUN_REL = ("evaluation", "results", "run-3")


class Sandbox:
    """A miniature repository with every path collect() reads, and its own freeze."""

    def __init__(self) -> None:
        self.dir = Path(tempfile.mkdtemp(prefix="apigee-freeze-"))
        self.run = self.dir.joinpath(*RUN_REL)
        for rel in DECLARED + DISCOVERED:
            self.write(rel, f"original bytes of {rel}\n")
        self.write("evaluation/results/run-3/manifest.json",
                   '{"run": "run-3", "scenarios": {}}\n')
        self.script = self.run / "freeze_artifacts.py"
        shutil.copyfile(FREEZER, self.script)
        self.manifest = self.run / "artifact-hashes.json"
        self.anchor = self.run / "artifact-hashes.json.sha256"
        self.git("init", "-q")
        self.git("add", "-A")
        self.git("commit", "-qm", "base")

    def git(self, *args: str) -> None:
        subprocess.run(["git", *args], cwd=self.dir, check=True, capture_output=True,
                       env=GIT_ENV)

    def write(self, rel: str, body: str) -> None:
        p = self.dir / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")

    def read(self, rel: str) -> str:
        return (self.dir / rel).read_text(encoding="utf-8")

    def remove(self, rel: str) -> None:
        (self.dir / rel).unlink()

    def freeze(self) -> subprocess.CompletedProcess:
        p = subprocess.run([sys.executable, str(self.script), "--write"], cwd=self.dir,
                           capture_output=True, text=True, timeout=120)
        assert p.returncode == 0, f"--write failed: {p.stdout}{p.stderr}"
        return p

    def verify(self, path: str | None = None, strict: bool = False,
               bare: bool = False) -> subprocess.CompletedProcess:
        """Verify, naming the manifest by path the way PROTOCOL.md's Resumption block does.

        The explicit path is the documented invocation and is the one every case uses, so
        that a case failure against an older script is about the defect and not about an
        argparse difference. `bare` exercises the bare `--verify` form separately.
        """
        args = [sys.executable, str(self.script)]
        if bare:
            args.append("--verify")
        elif path is not None:
            args += ["--verify", path]
        else:
            args += ["--verify", str(self.manifest)]
        if strict:
            args.append("--strict-head")
        return subprocess.run(args, cwd=self.dir, capture_output=True, text=True,
                              timeout=120)

    def reanchor(self) -> None:
        """Recompute the sidecar: the deliberate editor who keeps the anchor honest.

        Every case that edits the manifest has to call this, or it is only proving that the
        digest check fires. The interesting adversary is the one who re-anchors.
        """
        import hashlib
        raw = self.manifest.read_bytes()
        self.anchor.write_text(
            f"{hashlib.sha256(raw).hexdigest()}  {self.manifest.name}\n", encoding="utf-8")

    def load(self) -> dict:
        return json.loads(self.manifest.read_text(encoding="utf-8"))

    def save(self, m: dict) -> None:
        self.manifest.write_text(json.dumps(m, indent=2), encoding="utf-8")

    def cleanup(self) -> None:
        shutil.rmtree(self.dir, ignore_errors=True)


CASES: list[tuple[str, Callable[[], None]]] = []


def case(name: str) -> Callable[[Callable[[], None]], Callable[[], None]]:
    def deco(f: Callable[[], None]) -> Callable[[], None]:
        CASES.append((name, f))
        return f
    return deco


def assert_fails(sb: Sandbox, needle: str, **kw) -> subprocess.CompletedProcess:
    """The run must stop, and the reason must name the artifact, not just fail."""
    p = sb.verify(**kw)
    assert p.returncode != 0, f"expected a nonzero exit, got 0:\n{p.stdout}"
    assert needle in p.stdout, f"{needle!r} not in output:\n{p.stdout}{p.stderr}"
    return p


# ---------------------------------------------------------------------------
# Control. Without this, every case below could pass by the verifier refusing
# everything, which stops the run as effectively as the defect did.
# ---------------------------------------------------------------------------


@case("an unchanged tree verifies at exit 0")
def _():
    sb = Sandbox()
    try:
        sb.freeze()
        p = sb.verify()
        assert p.returncode == 0, p.stdout + p.stderr
        assert "all frozen artifacts unchanged" in p.stdout, p.stdout
    finally:
        sb.cleanup()


@case("the documented invocation, which names the manifest path, still verifies")
def _():
    sb = Sandbox()
    try:
        sb.freeze()
        p = sb.verify(str(sb.manifest))
        assert p.returncode == 0, p.stdout + p.stderr
        assert "all frozen artifacts unchanged" in p.stdout, p.stdout
    finally:
        sb.cleanup()


@case("the bare --verify form checks the recorded manifest")
def _():
    # Added with the fix. An older script requires an argument here and exits on argparse,
    # which is why this case names the affordance rather than a defect.
    sb = Sandbox()
    try:
        sb.freeze()
        p = sb.verify(bare=True)
        assert p.returncode == 0, p.stdout + p.stderr
        assert "all frozen artifacts unchanged" in p.stdout, p.stdout
    finally:
        sb.cleanup()


# ---------------------------------------------------------------------------
# D1. Absence is drift, in both directions.
# ---------------------------------------------------------------------------


@case("a deleted rubric is a failure, not a skip")
def _():
    sb = Sandbox()
    try:
        sb.freeze()
        sb.remove("evaluation/rubric.md")
        assert_fails(sb, "scripts/evaluation/rubric.md (deleted)")
    finally:
        sb.cleanup()


@case("a deleted answer key is a failure, not a skip")
def _():
    sb = Sandbox()
    try:
        sb.freeze()
        sb.remove("evaluation/packets/EASY-01.key.md")
        assert_fails(sb, "keys/EASY-01.key.md (deleted)")
    finally:
        sb.cleanup()


@case("a deleted turn-2 prompt packet is a failure, not a skip")
def _():
    sb = Sandbox()
    try:
        sb.freeze()
        sb.remove("evaluation/packets/EASY-01.turn2.prompt.md")
        assert_fails(sb, "turn2/EASY-01.turn2.prompt.md (deleted)")
    finally:
        sb.cleanup()


@case("a deleted scenario file is a failure, not a skip")
def _():
    sb = Sandbox()
    try:
        sb.freeze()
        sb.remove("scenarios/easy.md")
        assert_fails(sb, "scenarios/easy.md (deleted)")
    finally:
        sb.cleanup()


@case("a scenario added after the freeze is a failure, not a silent denominator change")
def _():
    sb = Sandbox()
    try:
        sb.freeze()
        sb.write("scenarios/hard.md", "# a 104th scenario\n")
        assert_fails(sb, "scenarios/hard.md (added)")
    finally:
        sb.cleanup()


@case("an answer key added after the freeze is a failure")
def _():
    sb = Sandbox()
    try:
        sb.freeze()
        sb.write("evaluation/packets/EASY-02.key.md", "## Evaluation Rubric\n")
        assert_fails(sb, "keys/EASY-02.key.md (added)")
    finally:
        sb.cleanup()


@case("an edited answer key is a failure, so the deletion rule did not cost the "
      "ordinary case")
def _():
    sb = Sandbox()
    try:
        sb.freeze()
        sb.write("evaluation/packets/EASY-01.key.md", "## Evaluation Rubric\n| changed |\n")
        p = assert_fails(sb, "keys/EASY-01.key.md")
        assert "(deleted)" not in p.stdout, f"a moved file reported as deleted: {p.stdout}"
        assert "(added)" not in p.stdout, f"a moved file reported as added: {p.stdout}"
    finally:
        sb.cleanup()


@case("a freeze taken while the rubric was already absent can never verify clean")
def _():
    # The collect() half of the deletion defect: with `if v.is_file()` the missing file
    # left no record at all. It is recorded as MISSING, so the manifest is visibly a record
    # of a broken tree, and --write says so at the moment it writes it.
    sb = Sandbox()
    try:
        sb.remove("evaluation/rubric.md")
        w = sb.freeze()
        assert "WARNING" in w.stdout, w.stdout
        assert "evaluation/rubric.md" in w.stdout, w.stdout
        assert sb.load()["scripts"]["evaluation/rubric.md"] == "MISSING", sb.load()
        assert_fails(sb, "already absent at freeze time")
    finally:
        sb.cleanup()


# ---------------------------------------------------------------------------
# D2. The rules that decide a verdict are inside the freeze.
# ---------------------------------------------------------------------------


@case("editing the grader after the verdicts are known is a failure")
def _():
    # grade_run.py holds PASS_AT, MARGINAL_AT and SECOND_GRADER_SAMPLE. It is the only
    # thing in the repository that turns anchors into PASS / MARGINAL / FAIL, and it was
    # not hashed while PROTOCOL.md gave the reason for the freeze in its first paragraph.
    sb = Sandbox()
    try:
        sb.freeze()
        sb.write("evaluation/results/run-3/grade_run.py",
                 "PASS_AT, MARGINAL_AT = 0.01, 0.00  # rewritten after the verdicts\n")
        assert_fails(sb, "scripts/evaluation/results/run-3/grade_run.py (changed)")
    finally:
        sb.cleanup()


@case("deleting the grader is a failure")
def _():
    sb = Sandbox()
    try:
        sb.freeze()
        sb.remove("evaluation/results/run-3/grade_run.py")
        assert_fails(sb, "scripts/evaluation/results/run-3/grade_run.py (deleted)")
    finally:
        sb.cleanup()


@case("editing PROTOCOL.md after the freeze is a failure")
def _():
    sb = Sandbox()
    try:
        sb.freeze()
        sb.write("evaluation/results/run-3/PROTOCOL.md", "0.10 or above passes\n")
        assert_fails(sb, "scripts/evaluation/results/run-3/PROTOCOL.md (changed)")
    finally:
        sb.cleanup()


@case("editing run_generation.py after the freeze is a failure")
def _():
    sb = Sandbox()
    try:
        sb.freeze()
        sb.write("evaluation/results/run-3/run_generation.py", "MAX_ATTEMPTS = 999\n")
        assert_fails(sb, "scripts/evaluation/results/run-3/run_generation.py (changed)")
    finally:
        sb.cleanup()


@case("editing evaluation/model-eval-protocol.md after the freeze is a failure")
def _():
    # PROTOCOL.md line 58 resolves the scoring route from this file, so it is a rule and
    # not documentation.
    sb = Sandbox()
    try:
        sb.freeze()
        sb.write("evaluation/model-eval-protocol.md", "Route 2 is canonical\n")
        assert_fails(sb, "scripts/evaluation/model-eval-protocol.md (changed)")
    finally:
        sb.cleanup()


@case("editing freeze_artifacts.py itself is a failure")
def _():
    # A stray edit to the checker, which is what this catches: someone tweaks the comparison
    # while a run is in progress and nothing else notices. Replacing the file outright is
    # NOT covered, and cannot be: the code doing the checking would be the replacement, so
    # it reports whatever it was written to report. That limit is the same one `--write`
    # has, and tests/test_freeze_artifacts.py does not pretend otherwise.
    sb = Sandbox()
    try:
        sb.freeze()
        sb.write("evaluation/results/run-3/freeze_artifacts.py",
                 sb.read("evaluation/results/run-3/freeze_artifacts.py")
                 + "\n# a stray edit to the checker\n")
        assert_fails(sb, "scripts/evaluation/results/run-3/freeze_artifacts.py (changed)")
    finally:
        sb.cleanup()


@case("manifest.json is not frozen, because every batch rewrites it")
def _():
    # The deliberate exclusion, pinned so that it stays a decision. run_generation.py
    # rewrites the manifest on every batch and PROTOCOL.md's Resumption section makes it
    # authoritative for collection state. It records events. A verifier that fails every
    # batch is one the run learns to ignore, and PROTOCOL.md's rule against mixing versions
    # inside one result is a rule against a meaningless verdict too.
    sb = Sandbox()
    try:
        sb.freeze()
        sb.write("evaluation/results/run-3/manifest.json",
                 '{"run": "run-3", "scenarios": {"EASY-01": {"status": "OK"}}}\n')
        p = sb.verify()
        assert p.returncode == 0, p.stdout + p.stderr
        assert "manifest.json" not in sb.load()["scripts"], sb.load()["scripts"]
    finally:
        sb.cleanup()


@case("a moved commit is reported, and gates only under --strict-head")
def _():
    # git_head was collected and never compared. Comparing it would be a weaker check than
    # the content hashes (an edit in the working tree moves the bytes, not the commit) and
    # a noisier one (three commits on this branch moved HEAD without moving a single
    # scenario, key or rubric byte). So it is reported, and gating is opt-in.
    sb = Sandbox()
    try:
        sb.freeze()
        sb.write("CHANGELOG.md", "progress note\n")
        sb.git("add", "-A")
        sb.git("commit", "-qm", "progress note")
        p = sb.verify()
        assert p.returncode == 0, p.stdout + p.stderr
        assert "HEAD moved" in p.stdout, p.stdout
        strict = sb.verify(strict=True)
        assert strict.returncode != 0, strict.stdout
        assert "git_head" in strict.stdout, strict.stdout
    finally:
        sb.cleanup()


# ---------------------------------------------------------------------------
# D3. The manifest cannot certify itself.
# ---------------------------------------------------------------------------


@case("a section deleted from the manifest is a failure, even after re-anchoring")
def _():
    sb = Sandbox()
    try:
        sb.freeze()
        m = sb.load()
        del m["keys"]
        sb.save(m)
        sb.reanchor()
        assert_fails(sb, "keys: absent from the manifest")
    finally:
        sb.cleanup()


@case("a section emptied in the manifest is a failure, even after re-anchoring")
def _():
    sb = Sandbox()
    try:
        sb.freeze()
        m = sb.load()
        m["scripts"] = {}
        sb.save(m)
        sb.reanchor()
        assert_fails(sb, "scripts: present but empty")
    finally:
        sb.cleanup()


@case("a manifest with every section emptied is a failure, even after re-anchoring")
def _():
    # The worst case reachable without re-running --write: every section present, every
    # section empty, anchor recomputed to match. It verified clean before.
    sb = Sandbox()
    try:
        sb.freeze()
        m = sb.load()
        for section in ("skill_files", "scripts", "scenarios", "keys", "turn1", "turn2"):
            m[section] = {}
        sb.save(m)
        sb.reanchor()
        p = assert_fails(sb, "scenarios: present but empty")
        assert "keys: present but empty" in p.stdout, p.stdout
    finally:
        sb.cleanup()


@case("a manifest edited without re-anchoring fails on its digest")
def _():
    sb = Sandbox()
    try:
        sb.freeze()
        m = sb.load()
        m["keys"]["EASY-01.key.md"] = "0" * 64
        sb.save(m)
        assert_fails(sb, "DIGEST MISMATCH")
    finally:
        sb.cleanup()


@case("a manifest with no anchor file is refused rather than believed")
def _():
    sb = Sandbox()
    try:
        sb.freeze()
        if sb.anchor.exists():
            sb.anchor.unlink()
        # Against a script that never writes an anchor there is nothing to remove, so the
        # manifest is unanchored and believed, and this case fails at exit 0. That is the
        # whole defect: a manifest describing nothing but itself reported success.
        assert_fails(sb, "UNANCHORED MANIFEST")
    finally:
        sb.cleanup()


@case("--verify is refused a manifest at any other path")
def _():
    # A copy of the real manifest beside the real one verifies clean against a tree the
    # recorded freeze does not describe, which is the whole of what was wrong with
    # accepting any path.
    sb = Sandbox()
    try:
        sb.freeze()
        other = sb.dir / "attacker-manifest.json"
        shutil.copyfile(sb.manifest, other)
        assert_fails(sb, "REFUSED", path=str(other))
    finally:
        sb.cleanup()


@case("--write records the manifest's digest in a separate file")
def _():
    sb = Sandbox()
    try:
        sb.freeze()
        import hashlib
        assert sb.anchor.is_file(), "--write did not write an anchor"
        assert sb.anchor != sb.manifest, "the anchor is the manifest"
        assert sb.anchor.parent == sb.manifest.parent, "the anchor is not beside it"
        digest = hashlib.sha256(sb.manifest.read_bytes()).hexdigest()
        body = sb.anchor.read_text(encoding="utf-8")
        assert body.split()[0] == digest, body
        assert sb.manifest.name in body, "the anchor is not sha256sum format"
    finally:
        sb.cleanup()


@case("deleting the skill tree is a failure at both granularities")
def _():
    # skill_files names the file and skill_digest moves with it, so the two granularities
    # agree rather than one being stricter than the other. A verifier that caught a skill
    # deletion only by digest would report one line and no file.
    sb = Sandbox()
    try:
        sb.freeze()
        shutil.rmtree(sb.dir / ".agents" / "skills")
        p = assert_fails(sb, "skill_files/.agents/skills/apigee-support-core/SKILL.md")
        assert "skill_digest (changed)" in p.stdout, p.stdout
    finally:
        sb.cleanup()


@case("a manifest holding a JSON list is refused rather than crashing")
def _():
    # json.loads accepts a list, a string or a number. The comparison walks the manifest's
    # sections, so a non-object is not a freeze that failed, it is a file that cannot be
    # read as one, and it has to say so instead of raising.
    sb = Sandbox()
    try:
        sb.freeze()
        sb.manifest.write_text("[]\n", encoding="utf-8")
        sb.reanchor()
        p = assert_fails(sb, "MALFORMED MANIFEST")
        assert "Traceback" not in p.stderr, p.stderr
    finally:
        sb.cleanup()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--only", help="run cases whose name contains this")
    ap.add_argument("--json", action="store_true", help="machine-readable summary")
    a = ap.parse_args()

    passed, failed = 0, []
    for name, fn in CASES:
        if a.only and a.only not in name:
            continue
        try:
            fn()
            passed += 1
            mark, note = "ok  ", ""
        except Exception as e:  # noqa: BLE001
            # Any exception is a case failure, never a reason to abandon the cases after
            # it. A case that raises against an older script is the result, not a crash.
            mark, note = "FAIL", f"  [{type(e).__name__}: {e}]"
            failed.append(f"{name} -- {type(e).__name__}: {e}")
        print(f"{mark} {name}{note}")

    total = passed + len(failed)
    if a.json:
        print(json.dumps({"cases": total, "passed": passed,
                          "failed": len(failed), "failures": failed}, indent=2))
    else:
        print()
        print(f"{total} cases, {passed} passed, {len(failed)} failed")
    for f in failed:
        print(f"  FAILED: {f}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())