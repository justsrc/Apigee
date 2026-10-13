#!/usr/bin/env python3
"""Deterministic checks that an answering worker cannot reach protected material.

These run offline and cost nothing. A pass proves the production path behaves as
described. It does not prove a real model cannot find another way, which is what the
live tier in `tests/test_isolation.py` is for.

Every check here runs the real `make_eval_workspace.build` and the real
`test_isolation.structural`, not a reimplementation, because this project's recurring
defect is a checker that tests a copy of the logic it claims to verify.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))

import make_eval_workspace as mew  # noqa: E402
import test_isolation as ti  # noqa: E402

PROTECTED = [
    "evaluation/packets/MED-13.key.md",
    "scenarios/medium.md",
    "scenarios/index.md",
    "research/pages",
    "evaluation/rubric.md",
    "evaluation/defect-register.md",
    "evaluation/audit-medium-A.md",
    ".git",
]

CASES: list[dict] = []


def case(name):
    def deco(f):
        CASES.append({"name": name, "fn": f})
        return f
    return deco


def build(tmp: Path, sid: str = "MED-13") -> Path:
    """Build through the real generator, with its stdout captured so a passing run is quiet."""
    ws = tmp / f"ws-{sid}"
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = mew.build(ws, [sid], False, True)
    assert rc in (0, 1), f"build returned {rc}: {buf.getvalue()}"
    return ws


@case("the workspace contains no protected path")
def _():
    with tempfile.TemporaryDirectory() as td:
        ws = build(Path(td))
        present = [p for p in PROTECTED if (ws / p).exists()]
        assert not present, present


@case("no answer key exists anywhere in the workspace")
def _():
    with tempfile.TemporaryDirectory() as td:
        ws = build(Path(td))
        keys = list(ws.rglob("*.key.md"))
        assert not keys, [str(k) for k in keys]


@case("the real structural checker reports no failure")
def _():
    with tempfile.TemporaryDirectory() as td:
        ws = build(Path(td))
        fails = ti.structural(ws)
        assert not fails, fails


@case("the enforcing config denies the routes that reach a key")
def _():
    with tempfile.TemporaryDirectory() as td:
        ws = build(Path(td))
        cfg = json.loads((ws / "opencode.jsonc").read_text())
        rules = {r["action"]: r["effect"] for r in cfg["permissions"]}
        for needed in ("external_directory", "shell", "edit", "webfetch", "websearch",
                       "subagent"):
            assert rules.get(needed) == "deny", (needed, rules.get(needed))


@case("the banner hands the model no ID-to-title lookup")
def _():
    # The banner is copied into the workspace and is the only project prose an answering
    # model reads. It used to state that scenarios/index.md maps the case ID back to the
    # title, which is precisely the lookup that undoes the title stripping.
    banner = (ROOT / "tests" / "make_eval_workspace.py").read_text()
    body = banner.split('BANNER = """', 1)[1].split('"""', 1)[0]
    assert "maps that ID back to" not in body, "banner still advertises the ID-to-title lookup"
    with tempfile.TemporaryDirectory() as td:
        ws = build(Path(td))
        text = (ws / "WORKSPACE.md").read_text()
        assert "maps that ID back to" not in text


@case("a canary answer key outside the workspace is unreachable by path")
def _():
    # Synthetic canary, never real key content.
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        outside = tmp / "outside"
        outside.mkdir()
        canary = outside / "MED-13.key.md"
        canary.write_text("CANARY-KEY-CONTENT-a1b2c3\n")
        ws = build(tmp)
        # every relative route out of the workspace must fail at the filesystem boundary
        # for a path that does not exist inside it
        for rel in ("../outside/MED-13.key.md", "../../outside/MED-13.key.md"):
            assert not (ws / rel).resolve().is_relative_to(ws), rel
        # and the canary must not appear anywhere inside
        blob = "\n".join(p.read_text(errors="replace")
                         for p in ws.rglob("*") if p.is_file())
        assert "CANARY-KEY-CONTENT" not in blob


@case("git history is not present in the workspace")
def _():
    with tempfile.TemporaryDirectory() as td:
        ws = build(Path(td))
        assert not (ws / ".git").exists()
        assert not list(ws.rglob(".git"))


@case("the workspace carries the operational skill, unmodified")
def _():
    with tempfile.TemporaryDirectory() as td:
        ws = build(Path(td))
        src = ROOT / ".agents" / "skills"
        got = sorted(p.relative_to(ws / ".agents" / "skills").as_posix()
                     for p in (ws / ".agents" / "skills").rglob("*") if p.is_file())
        want = sorted(p.relative_to(src).as_posix() for p in src.rglob("*") if p.is_file())
        assert got == want, (set(want) - set(got), set(got) - set(want))
        for rel in got:
            a = (src / rel).read_bytes()
            b = (ws / ".agents" / "skills" / rel).read_bytes()
            assert hashlib.sha256(a).digest() == hashlib.sha256(b).digest(), rel


@case("the manifest pins the build commit and packet checksums")
def _():
    with tempfile.TemporaryDirectory() as td:
        ws = build(Path(td))
        man = json.loads((ws / "MANIFEST.json").read_text())
        assert man["built_from_commit"], man
        assert man["scenarios"] == ["MED-13"], man["scenarios"]
        names = {p["file"] for p in man["prompts"]}
        assert names == {"MED-13.prompt.md", "MED-13.turn2.prompt.md"}, names
        for entry in man["prompts"]:
            # The generator records a 16-character prefix, not the full digest.
            real = hashlib.sha256(
                (ws / "prompts" / entry["file"]).read_bytes()).hexdigest()[:16]
            assert entry["sha256"] == real, (entry["file"], entry["sha256"], real)


@case("no prompt contains its own scenario title")
def _():
    sys.path.insert(0, str(ROOT / "tests"))
    import make_packets as mp
    import re as _re
    leaked = []
    for f in mp.FILES.values():
        for sid, block in mp.blocks(f):
            hs = mp.headings_of(block)
            if not hs:
                continue
            title = _re.sub(r"^[A-Z]+-\d+\.?\s*", "", hs[0][1]).strip()
            if len(title) <= 12:
                continue
            for suf in (".prompt.md", ".turn2.prompt.md"):
                pkt = ROOT / "evaluation" / "packets" / f"{sid}{suf}"
                if pkt.is_file() and title.lower() in pkt.read_text().lower():
                    leaked.append(f"{sid}{suf}")
    assert not leaked, leaked


@case("the provider error that means quota is classified INDETERMINATE, not BLOCKED")
def _():
    ev = json.dumps({"type": "error", "error": {
        "type": "provider.rate-limit",
        "message": "Rate limit exceeded: free-models-per-day", "status": 429}}) + "\n"
    assert ti.classify(ev, "", 1, "CANARY-X")[0] == "INDETERMINATE"


@case("the misleading provider.auth error is not treated as a free-tier refusal")
def _():
    # Observed 2026-10-13: `opencode/*` returns this while rate-limiting, so the message
    # text is not evidence of anything. It must not become a BLOCKED route.
    ev = json.dumps({"type": "error", "error": {
        "type": "provider.auth",
        "message": "OpenCode's free tier can only be used from within OpenCode.",
        "status": 403}}) + "\n"
    assert ti.classify(ev, "", 1, "CANARY-X")[0] == "INDETERMINATE"


def main() -> int:
    failed = []
    for c in CASES:
        try:
            c["fn"]()
            print(f"ok    {c['name']}")
        except AssertionError as e:
            failed.append(c["name"])
            print(f"FAIL  {c['name']}: {e}")
    print(f"\n{len(CASES)} cases, {len(CASES) - len(failed)} passed, {len(failed)} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())