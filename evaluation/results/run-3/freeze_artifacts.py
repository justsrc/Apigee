#!/usr/bin/env python3
"""Freeze the artifact hashes for run 3 and verify they have not moved.

Run this before every batch. If a hash changed, the run's materials are no longer the
ones the protocol was frozen against and the run must stop rather than silently mix
versions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Literal, TypedDict, cast

# This file lives at <root>/evaluation/results/run-3/, so the root is four levels up.
ROOT = Path(__file__).resolve().parents[3]


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


class Manifest(TypedDict):
    git_head: str
    skill_digest: str
    skill_files: dict[str, str]
    scripts: dict[str, str]
    scenarios: dict[str, str]
    keys: dict[str, str]
    turn1: dict[str, str]
    turn2: dict[str, str]


SectionName = Literal["skill_files", "scripts", "scenarios", "keys", "turn1", "turn2"]
SECTIONS: tuple[SectionName, ...] = (
    "skill_files", "scripts", "scenarios", "keys", "turn1", "turn2")


def collect() -> Manifest:
    packets = ROOT / "evaluation" / "packets"
    scen = {p.name: sha(p) for p in sorted((ROOT / "scenarios").glob("*.md"))}
    keys = {p.name: sha(p) for p in sorted(packets.glob("*.key.md"))}
    t1 = {p.name: sha(p) for p in sorted(packets.glob("*.prompt.md"))
          if not p.name.endswith(".turn2.prompt.md")}
    t2 = {p.name: sha(p) for p in sorted(packets.glob("*.turn2.prompt.md"))}
    files = {
        "evaluation/rubric.md": ROOT / "evaluation" / "rubric.md",
        "tests/make_packets.py": ROOT / "tests" / "make_packets.py",
        "tests/make_eval_workspace.py": ROOT / "tests" / "make_eval_workspace.py",
        "tests/test_isolation.py": ROOT / "tests" / "test_isolation.py",
        "tests/release_gate.py": ROOT / "tests" / "release_gate.py",
    }
    return {
        "git_head": subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
            text=True).stdout.strip(),
        "skill_digest": skill_digest(ROOT / ".agents" / "skills"),
        "skill_files": {str(p.relative_to(ROOT)): sha(p) for p in
                        sorted((ROOT / ".agents" / "skills").rglob("*"))
                        if p.is_file() and "__pycache__" not in p.parts},
        "scripts": {k: sha(v) for k, v in files.items() if v.is_file()},
        "scenarios": scen,
        "keys": keys,
        "turn1": t1,
        "turn2": t2,
    }


class Args(argparse.Namespace):
    write: bool = False
    verify: str | None = None


def main() -> int:
    ap = argparse.ArgumentParser()
    _ = ap.add_argument("--write", action="store_true", help="write artifact-hashes.json")
    _ = ap.add_argument("--verify", help="compare against an existing manifest")
    a = ap.parse_args(namespace=Args())
    cur = collect()

    if a.write:
        out = ROOT / "evaluation" / "results" / "run-3" / "artifact-hashes.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        _ = out.write_text(json.dumps(cur, indent=2), encoding="utf-8")
        print(f"wrote {out}")
        print(f"  git_head    {cur['git_head'][:12]}")
        print(f"  skill       {cur['skill_digest']}")
        print(f"  scenarios   {len(cur['scenarios'])} files")
        print(f"  turn1/turn2 {len(cur['turn1'])}/{len(cur['turn2'])}")
        print(f"  keys        {len(cur['keys'])}")
        return 0

    if a.verify:
        old = cast("Manifest", json.loads(Path(a.verify).read_text(encoding="utf-8")))
        moved: list[str] = []
        for section in SECTIONS:
            old_sec: dict[str, str] = old[section] if section in old else {}
            cur_sec: dict[str, str] = cur[section] if section in cur else {}
            for k, v in old_sec.items():
                now = cur_sec.get(k)
                if now is not None and now != v:
                    moved.append(f"{section}/{k}")
        if old.get("skill_digest") != cur["skill_digest"]:
            moved.append("skill_digest")
        if moved:
            print("FROZEN ARTIFACTS MOVED, run must stop:")
            for m in moved[:20]:
                print(f"  {m}")
            if len(moved) > 20:
                print(f"  ... and {len(moved) - 20} more")
            return 1
        print(f"all frozen artifacts unchanged (skill {cur['skill_digest']})")
        return 0

    print(json.dumps({k: v for k, v in cur.items()
                      if k in ("git_head", "skill_digest")}, indent=2))
    print(
        f"scenarios={len(cur['scenarios'])} turn1={len(cur['turn1'])} "
        + f"turn2={len(cur['turn2'])} keys={len(cur['keys'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())