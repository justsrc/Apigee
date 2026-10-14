#!/usr/bin/env python3
"""Freeze the artifact hashes for run 3 and verify they have not moved.

Run this before every batch. If a hash changed, the run's materials are no longer the
ones the protocol was frozen against and the run must stop rather than silently mix
versions.

WHAT IS FROZEN, AND WHY THE SET CHANGED ON 2026-10-14.

`collect()` hashed the five scripts that build material and the scenarios, packets, keys
and skill tree. The files that decide a verdict were not in the set at all:
PROTOCOL.md, grade_run.py, run_generation.py, evaluation/model-eval-protocol.md. That is
the sharpest form the defect took. `grade_run.py` holds PASS_AT, MARGINAL_AT and
SECOND_GRADER_SAMPLE, so it is the only thing in the repository that turns anchor counts
into PASS / MARGINAL / FAIL, and it was unhashed while PROTOCOL.md's own second sentence
gave the reason for the freeze: "Commit the protocol before results, so the rules that
decide a verdict cannot be written after the verdicts are known." Rewriting the grader's
thresholds left --verify at exit 0. The four are frozen now, plus this file, because a
checker that decides whether the rules moved is itself a rule that decides the outcome.

`manifest.json` is deliberately NOT frozen. It is the collection state, run_generation.py
rewrites it on every batch, and PROTOCOL.md's Resumption section makes it authoritative for
what has been collected. It records events. Freezing it would fail every batch and teach
the run to ignore a verifier that is always red, which is the same trade the protocol
refuses in the other direction: "mixing material versions inside one result is worse than
an incomplete run" cuts against a verifier whose verdict is meaningless too.

ABSENCE IS DRIFT.

The comparison used to iterate the manifest's keys and skip any key the tree no longer had,
`if now is not None and now != v`, and `collect()` built `scripts` with `if v.is_file()`, so
a deleted rubric, key, packet or scenario was not compared at all: it was skipped, and the
run continued on a tree missing material it had been frozen against. Missing is now recorded
as MISSING and the comparison runs in both directions. Deletion and addition are both
drift, for different reasons, and `drift()` says which is which.

THE MANIFEST CANNOT CERTIFY ITSELF.

`--write` rebuilds the whole file from whatever is on disk, so editing every artifact and
re-running --write satisfied --verify. Deleting a section un-verified everything that
section covered, because `old.get(section, {})` iterated nothing. Three things are required
of a manifest now: every section must be present and non-empty, --verify must be pointed at
the recorded manifest rather than any path the caller likes, and the manifest must carry a
digest of itself in `artifact-hashes.json.sha256`, which is a different file and has to be
committed next to it.

That last one is honest about its own limit and no more than that. An attacker who can edit
the manifest can also run --write, and nothing inside this repository can stop that. What
the sidecar closes is the quiet case: a manifest edited by hand, or one written on a tree
that was already broken, no longer describes itself. The anchor is a separate committed
fact instead of a field inside the thing it anchors. `--write` resetting the freeze is
still available to anyone who runs it, and that is a decision for a human, not a property
this file can have.

GIT_HEAD IS RECORDED, NOT DECIDED.

`git_head` was collected and never compared, which is a bug, but the fix is not to compare
it. Comparing the commit is a weaker check than the content hashes in every case that
matters: an edit in the working tree moves the bytes and leaves the commit alone, so a HEAD
comparison passes exactly where the hashes catch it. It is stricter in one case only, a
history rewritten underneath the run, which is not what this file watches. It is also
noisier than it looks. On this branch HEAD moved from a25333b to 30e2876 across three
commits that touched the harness and not one scenario, key or rubric byte, so a HEAD gate
would have stopped the run for nothing. It is reported on every successful verify, and
--strict-head turns it into a gate for a run that wants the commit pinned as well. Which of
those two a run wants is a policy choice, and this file does not make it silently.

EXIT CODES.

  0  the freeze holds.
  1  it does not hold, or the manifest is structurally incomplete.
  2  it could not be checked: a manifest that is not the recorded one, or one that is
     missing, unreadable or not anchored to a digest outside itself.

Every nonzero code stops the run, which is all PROTOCOL.md's Resumption section promises.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

# This file lives at <root>/evaluation/results/run-3/, so the root is four levels up.
ROOT = Path(__file__).resolve().parents[3]
RUN_REL = Path("evaluation") / "results" / "run-3"


def manifest_path() -> Path:
    return ROOT / RUN_REL / "artifact-hashes.json"


def anchor_path() -> Path:
    """The manifest's own digest, in a different file from the manifest.

    That difference is the entire mechanism. sha256sum format, so
    `shasum -a 256 -c artifact-hashes.json.sha256` runs the same check without this
    script, and the file has to be committed next to the manifest for either to mean
    anything.
    """
    return ROOT / RUN_REL / "artifact-hashes.json.sha256"


# Recorded in place of a digest when an artifact the freeze declares is not there, and when
# git cannot name a commit. Not a sha256, so a MISSING can never be read as a digest that
# matched. 30e2876, "Block A5 when git cannot answer rather than passing on an error", is
# the same rule one level up: a check that cannot reach the thing it asserts says so.
MISSING = "MISSING"

# Sections that must exist, must be a mapping, and must not be empty. An absent or empty
# section previously iterated nothing and reported nothing, so removing it un-verified
# everything it had covered without a word.
FILE_SECTIONS = ("skill_files", "scripts", "scenarios", "keys", "turn1", "turn2")
SCALAR_SECTIONS = ("git_head", "skill_digest")

# Sentinel for "--verify with no path", which means the recorded manifest. Kept distinct
# from None, which means --verify was not asked for at all.
_RECORDED = ""


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def skill_digest(base: Path) -> str:
    """Digest over the operational skill tree: every file, path-sorted, path in the hash."""
    h = hashlib.sha256()
    for p in sorted(base.rglob("*")):
        if p.is_dir() or "__pycache__" in p.parts:
            continue
        h.update(str(p.relative_to(base)).encode())
        h.update(sha(p).encode())
    return h.hexdigest()[:16]


def git_head() -> str:
    """The commit HEAD names, or MISSING when git cannot answer.

    Not the empty string. `git rev-parse` outside a repository prints nothing and exits
    nonzero, and an empty value written into a manifest is indistinguishable from a
    recorded one for as long as nobody checks the exit code.
    """
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                           capture_output=True, text=True)
    except OSError:
        return MISSING
    out = r.stdout.strip()
    return out if r.returncode == 0 and out else MISSING


def collect() -> dict:
    packets = ROOT / "evaluation" / "packets"
    scen = {p.name: sha(p) for p in sorted((ROOT / "scenarios").glob("*.md"))}
    keys = {p.name: sha(p) for p in sorted(packets.glob("*.key.md"))}
    t1 = {p.name: sha(p) for p in sorted(packets.glob("*.prompt.md"))
          if not p.name.endswith(".turn2.prompt.md")}
    t2 = {p.name: sha(p) for p in sorted(packets.glob("*.turn2.prompt.md"))}
    files = {
        # The material the run reads, and the harness that builds it.
        "evaluation/rubric.md": ROOT / "evaluation" / "rubric.md",
        "tests/make_packets.py": ROOT / "tests" / "make_packets.py",
        "tests/make_eval_workspace.py": ROOT / "tests" / "make_eval_workspace.py",
        "tests/test_isolation.py": ROOT / "tests" / "test_isolation.py",
        "tests/release_gate.py": ROOT / "tests" / "release_gate.py",
        # The rules that decide a verdict. Unhashed until 2026-10-14, which is the defect
        # this section exists to record: PROTOCOL.md and model-eval-protocol.md state the
        # route and the thresholds, grade_run.py is the only thing that turns anchors into
        # PASS or FAIL, and run_generation.py decides what was asked and what counts as an
        # answer at all. freeze_artifacts.py is here for the same reason one level up: the
        # check that the rules did not move is itself a rule about the outcome. It catches
        # a stray edit to this file, and it cannot catch this file being replaced, because
        # then the code doing the checking is the replacement. Same limit as `--write`.
        "evaluation/model-eval-protocol.md": ROOT / "evaluation" / "model-eval-protocol.md",
        "evaluation/results/run-3/PROTOCOL.md":
            ROOT / "evaluation" / "results" / "run-3" / "PROTOCOL.md",
        "evaluation/results/run-3/grade_run.py":
            ROOT / "evaluation" / "results" / "run-3" / "grade_run.py",
        "evaluation/results/run-3/run_generation.py":
            ROOT / "evaluation" / "results" / "run-3" / "run_generation.py",
        "evaluation/results/run-3/freeze_artifacts.py":
            ROOT / "evaluation" / "results" / "run-3" / "freeze_artifacts.py",
    }
    return {
        "git_head": git_head(),
        "skill_digest": skill_digest(ROOT / ".agents" / "skills"),
        "skill_files": {str(p.relative_to(ROOT)): sha(p) for p in
                        sorted((ROOT / ".agents" / "skills").rglob("*"))
                        if p.is_file() and "__pycache__" not in p.parts},
        # A declared artifact that is absent is recorded as absent. Dropping it with
        # `if v.is_file()` made a deleted rubric look like a tree that never had one.
        "scripts": {k: sha(v) if v.is_file() else MISSING for k, v in files.items()},
        "scenarios": scen,
        "keys": keys,
        "turn1": t1,
        "turn2": t2,
    }


def integrity_problems(old: object) -> list[str]:
    """What is wrong with the manifest itself, before the tree is looked at.

    A manifest that cannot be trusted cannot certify that the tree held still, so each of
    these is a failure. They were all reachable before: a section could be deleted or
    emptied and the run continued, having verified less than nothing.
    """
    if not isinstance(old, dict):
        return ["manifest is not a JSON object"]

    out: list[str] = []
    for section in SCALAR_SECTIONS:
        v = old.get(section)
        if not isinstance(v, str) or not v:
            out.append(f"{section}: absent from the manifest")
        elif v == MISSING:
            out.append(f"{section}: recorded as {MISSING}, so the freeze never established "
                       "it and cannot be said to hold")
    for section in FILE_SECTIONS:
        v = old.get(section)
        if not isinstance(v, dict):
            out.append(f"{section}: absent from the manifest, so nothing it covered can "
                       "be verified")
            continue
        if not v:
            out.append(f"{section}: present but empty, so nothing it covered can be "
                       "verified")
            continue
        gone = sorted(k for k, h in v.items() if h == MISSING)
        if gone:
            out.append(f"{section}: records {len(gone)} artifact(s) as already absent at "
                       f"freeze time, starting with {', '.join(gone[:3])}")
    return out


def drift(old: dict, cur: dict) -> list[str]:
    """Per-file comparison, in both directions.

    Why symmetric. The old comparison walked the manifest's keys and skipped any key the
    tree no longer had, so a deletion was a skip rather than a finding, and the manifest's
    own key set meant an addition was never visited. Both directions are drift, for
    different reasons:

      deleted  the material this run was frozen against is gone. PROTOCOL.md's rule is
               written about mixing versions, but half a suite is not half a result either,
               and a key that vanished is indistinguishable at grading time from a key that
               was never written.
      added    a scenario, key or packet that was not in the frozen set has joined the run.
               The population is pinned at 103 and full-suite yield is PASS / 103, so a
               104th scenario silently moves the denominator the number is reported
               against, and an added key silently changes what a verdict is measured
               against. An addition is not a weaker signal than a movement; it is the same
               event seen from the other side.
      changed  the ordinary case.

    The skill tree is covered at two granularities on purpose: skill_files names the file
    that moved and skill_digest moves on an addition or a deletion there too, so the rule
    is the same at both levels rather than stricter per file than by digest.
    """
    out: list[str] = []
    for section in FILE_SECTIONS:
        was_all = old.get(section)
        if not isinstance(was_all, dict) or not was_all:
            # Nothing to walk, and integrity_problems already says why. Reporting every
            # file as added on top of that would read as two separate problems.
            continue
        now_all = cur.get(section) if isinstance(cur.get(section), dict) else {}
        for k in sorted(set(was_all) | set(now_all)):
            was, now = was_all.get(k), now_all.get(k)
            if was == now:
                continue
            if now is None or now == MISSING:
                out.append(f"{section}/{k} (deleted)")
            elif was is None:
                out.append(f"{section}/{k} (added)")
            else:
                out.append(f"{section}/{k} (changed)")
    if old.get("skill_digest") != cur.get("skill_digest"):
        out.append("skill_digest (changed)")
    return out


def write_manifest(cur: dict) -> None:
    """Write the manifest and the digest of it that lives outside it.

    Re-running this resets the freeze to whatever is on disk right now. That is the whole
    power it has, and it is why both files are printed for committing: an uncommitted
    anchor protects nothing.
    """
    raw = (json.dumps(cur, indent=2) + "\n").encode("utf-8")
    out, anchor = manifest_path(), anchor_path()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(raw)
    anchor.write_text(f"{hashlib.sha256(raw).hexdigest()}  {out.name}\n", encoding="utf-8")


def report(moved: list[str], lines: list[str]) -> None:
    if moved:
        print("FROZEN ARTIFACTS MOVED, run must stop:")
        for m in moved[:20]:
            print(f"  {m}")
        if len(moved) > 20:
            print(f"  ... and {len(moved) - 20} more")
    if lines:
        print("MANIFEST INTEGRITY PROBLEMS, nothing they cover can be verified:")
        for line in lines:
            print(f"  {line}")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Freeze run 3's material and prove it has not moved since.")
    ap.add_argument("--write", action="store_true", help="write artifact-hashes.json")
    ap.add_argument("--verify", nargs="?", const=_RECORDED,
                    help="verify against the recorded manifest, which is also the default")
    ap.add_argument("--strict-head", action="store_true",
                    help="treat a moved git_head as drift as well (off by default, see "
                         "the module docstring)")
    a = ap.parse_args()
    cur = collect()
    out, anchor = manifest_path(), anchor_path()

    if a.write:
        write_manifest(cur)
        print(f"wrote {out}")
        print(f"wrote {anchor}")
        print("  commit both together; an uncommitted anchor protects nothing")
        print(f"  git_head    {cur['git_head'][:12]}")
        print(f"  skill       {cur['skill_digest']}")
        print(f"  scenarios   {len(cur['scenarios'])} files")
        print(f"  turn1/turn2 {len(cur['turn1'])}/{len(cur['turn2'])}")
        print(f"  keys        {len(cur['keys'])}")
        print(f"  scripts     {len(cur['scripts'])} files")
        if cur["git_head"] == MISSING:
            print("  WARNING: git could not name a commit, so this manifest has no "
                  "provenance record")
        absent = sorted(k for k, v in cur["scripts"].items() if v == MISSING)
        if absent:
            print(f"  WARNING: {len(absent)} declared artifact(s) were absent when the "
                  f"freeze was written, starting with {', '.join(absent[:3])}")
            print("  a freeze taken on an incomplete tree records the wrong tree")
        return 0

    if a.verify is not None:
        given = Path(a.verify) if a.verify else out
        if given.resolve() != out.resolve():
            print(f"REFUSED: {given} is not this run's recorded manifest.")
            print(f"  a freeze may only be checked against {out}")
            print("  verifying a manifest handed in at the call proves nothing about the "
                  "recorded freeze")
            print("  if the freeze is genuinely being reset, --write both files and "
                  "commit them, and record why")
            return 2
        if not out.is_file():
            print(f"NO MANIFEST: {out} does not exist, so nothing was ever frozen.")
            return 2
        try:
            raw = out.read_bytes()
            old = json.loads(raw.decode("utf-8"))
        except (OSError, ValueError) as e:
            print(f"UNREADABLE MANIFEST: {out}: {e}")
            return 2
        if not isinstance(old, dict):
            print(f"MALFORMED MANIFEST: {out} holds a "
                  f"{type(old).__name__}, not an object of sections.")
            print("  nothing about a freeze can be read out of it")
            return 2
        recorded = anchor.read_text(encoding="utf-8").split() if anchor.is_file() else None
        actual = hashlib.sha256(raw).hexdigest()
        if recorded is None:
            unanchored = [f"{anchor} is missing, so {out.name} is not bound to anything "
                          "outside itself"]
        elif not recorded or recorded[0] != actual:
            unanchored = [f"DIGEST MISMATCH: {out.name} hashes to {actual[:16]}, "
                          f"{anchor.name} records "
                          f"{(recorded[0][:16] if recorded else 'nothing at all')}",
                          "the manifest was edited after the anchor was taken, so it is "
                          "not the one that was anchored"]
        else:
            unanchored = []

        lines = integrity_problems(old)
        moved = drift(old, cur)
        if a.strict_head and old.get("git_head") != cur["git_head"]:
            moved.append(f"git_head (moved, --strict-head): "
                         f"{str(old.get('git_head'))[:12]} -> {cur['git_head'][:12]}")
        if unanchored:
            print("UNANCHORED MANIFEST, nothing below is anchored to anything:")
            for line in unanchored:
                print(f"  {line}")
            print("  a manifest that describes only itself can be rewritten to describe "
                  "anything.")
            print("  --write both files, commit them together, and record why the freeze "
                  "is being reset.")
        if lines or moved:
            report(moved, lines)
            print(f"{len(moved)} artifact(s) moved, {len(lines)} manifest problem(s)"
                  + (", against a manifest nothing anchors." if unanchored else "."))
        if unanchored:
            return 2
        if lines or moved:
            return 1

        if cur["git_head"] == MISSING:
            print("note: git could not name a commit, so git_head is unverified. The "
                  "content")
            print("      hashes still bind the material; the commit does not.")
        elif old["git_head"] != cur["git_head"]:
            print(f"note: HEAD moved {old['git_head'][:12]} -> {cur['git_head'][:12]} and "
                  "no frozen byte moved with it")
            print("      not a failure by default; --strict-head makes it one. See the "
                  "module docstring.")
        print(f"all frozen artifacts unchanged (skill {cur['skill_digest']})")
        return 0

    print(json.dumps({k: v for k, v in cur.items()
                      if k in ("git_head", "skill_digest")}, indent=2))
    print(f"scenarios={len(cur['scenarios'])} turn1={len(cur['turn1'])} "
          f"turn2={len(cur['turn2'])} keys={len(cur['keys'])} "
          f"scripts={len(cur['scripts'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())