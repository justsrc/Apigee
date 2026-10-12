#!/usr/bin/env python3
"""Mechanical checks for the Apigee support skill repository.

This script checks only what a script can honestly check: file presence, Markdown
structure, ID uniqueness, link resolution, and skill frontmatter. It deliberately does
not try to judge whether a scenario's technical content is correct, because a script
cannot tell a real fault code from a plausible-looking invented one.

That limit is the point. When this harness says PASS on structure and a scenario still
teaches the wrong thing, the failure belongs to review, not to the harness. Results are
printed split into MECHANICAL and NEEDS-REVIEW so nobody mistakes one for the other.

Usage:
    python3 tests/check_repo.py [--root .] [--strict]

Exit code 0 if no failures, 1 if any check failed. --strict also treats warnings as
failures.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SKILLS_DIR = Path(".agents/skills")
SCENARIOS_DIR = Path("scenarios")
RESEARCH_DIR = Path("research")

REQUIRED_ROOT_FILES = ["README.md", "CHANGELOG.md"]

# Minimum scenarios per difficulty file, from the project brief.
MIN_PER_DIFFICULTY = 15

# Every scenario must carry these sections. Matched case-insensitively against
# markdown headings, and the section must have non-empty content under it.
REQUIRED_SCENARIO_SECTIONS = [
    "initial support ticket",
    "initial evidence",
    "expected investigation",
    "ground-truth resolution",
    "remediation",
    "verification",
    "common incorrect answers",
    "evaluation rubric",
    "references",
]

# Scenario files and the difficulty each one asserts.
SCENARIO_FILES = {
    "easy.md": "easy",
    "medium.md": "medium",
    "hard.md": "hard",
}

# ID prefixes, so a unique-ID check can also tell you which family an ID belongs to.
ID_PREFIXES = {
    "EASY": "easy",
    "MED": "medium",
    "HARD": "hard",
    "ADV": "adversarial",
    "REG": "regression",
}

SKILL_FRONTMATTER_KEYS = ["name", "description"]

# Directories that are never loaded by the agent, so referencing them from active
# files is a bug: a stale duplicate is worse than no file.
ARCHIVE_MARKERS = re.compile(r"archive/", re.IGNORECASE)

URL_RE = re.compile(r"https?://[^\s\)\]\"'>]+")


# ---------------------------------------------------------------------------
# Result plumbing
# ---------------------------------------------------------------------------


@dataclass
class Results:
    passed: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    warned: list[str] = field(default_factory=list)
    needs_review: list[str] = field(default_factory=list)

    def ok(self, msg: str) -> None:
        self.passed.append(msg)

    def fail(self, msg: str) -> None:
        self.failed.append(msg)

    def warn(self, msg: str) -> None:
        self.warned.append(msg)

    def review(self, msg: str) -> None:
        self.needs_review.append(msg)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def split_frontmatter(text: str) -> tuple[str, str] | None:
    """Return (frontmatter, body) if the file opens with a --- delimited YAML block."""
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    return text[3:end].strip(), text[end + 4 :]


def parse_headings(body: str) -> list[tuple[int, str, int]]:
    """Return (level, text, line_index) for every ATX heading, ignoring fenced code."""
    headings: list[tuple[int, str, int]] = []
    in_fence = False
    for i, line in enumerate(body.splitlines()):
        if re.match(r"^\s*(```|~~~)", line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            headings.append((len(m.group(1)), m.group(2).strip(), i))
    return headings


def find_scenario_blocks(body: str) -> list[tuple[str, str]]:
    """Split a scenario file into (id, block_text).

    A scenario starts at a heading containing a scenario ID, so that
    '### EASY-01. Title' opens a block that runs until the next such heading.
    """
    lines = body.splitlines()
    starts: list[tuple[int, str]] = []
    id_re = re.compile(r"\b(EASY|MED|HARD|ADV|REG)-(\d{2,3})\b")

    in_fence = False
    for i, line in enumerate(lines):
        if re.match(r"^\s*(```|~~~)", line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = re.match(r"^#{2,4}\s+(.*)$", line)
        if m and id_re.search(m.group(1)):
            found = id_re.search(m.group(1))
            assert found
            starts.append((i, found.group(0)))

    blocks: list[tuple[str, str]] = []
    for n, (line_no, sid) in enumerate(starts):
        end = starts[n + 1][0] if n + 1 < len(starts) else len(lines)
        blocks.append((sid, "\n".join(lines[line_no:end])))
    return blocks


def _norm(text: str) -> str:
    """Normalize a heading or a search term the same way on both sides.

    Without this, "Ground-truth resolution" normalizes to "ground truth resolution"
    while the search term keeps its hyphen, and the lookup silently never matches.
    """
    text = re.sub(r"[^a-z ]", " ", text.lower())
    return re.sub(r"\s+", " ", text).strip()


def section_present(block: str, wanted: str) -> tuple[bool, int]:
    """Is `wanted` present as a heading with content under it? Returns (ok, chars).

    The first heading of a block is the scenario title, which is skipped. Without that,
    a title like "JWKS verification fails..." matches the search for "verification",
    the region under it is empty, and a perfectly good scenario is reported as missing
    its section.
    """
    headings = parse_headings(block)
    target = _norm(wanted)
    for idx, (_lvl, text, line_no) in enumerate(headings):
        if idx == 0:
            continue
        norm = _norm(text)
        # Exact match wins over substring, so "Verification" is not shadowed by
        # "Verification of the fix".
        if norm == target or target in norm:
            body_lines = block.splitlines()
            stop = headings[idx + 1][2] if idx + 1 < len(headings) else len(body_lines)
            content = "\n".join(body_lines[line_no + 1 : stop]).strip()
            if len(content) >= 40:
                return True, len(content)
            return False, len(content)
    return False, 0


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------


def check_root_files(root: Path, r: Results) -> None:
    for name in REQUIRED_ROOT_FILES:
        p = root / name
        if p.is_file() and p.stat().st_size > 0:
            r.ok(f"root file present and non-empty: {name}")
        else:
            r.fail(f"missing or empty root file: {name}")


def check_skills(root: Path, r: Results) -> list[str]:
    """Validate every skill. Returns the set of valid skill names."""
    skills_dir = root / SKILLS_DIR
    if not skills_dir.is_dir():
        r.fail(f"no skills directory at {SKILLS_DIR}")
        return []

    names: list[str] = []
    for d in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        skill_md = d / "SKILL.md"
        if not skill_md.is_file():
            r.fail(f"skill {d.name} has no SKILL.md")
            continue

        text = read(skill_md)
        parsed = split_frontmatter(text)
        if parsed is None:
            r.fail(f"{skill_md}: missing or malformed YAML frontmatter")
            continue
        fm, body = parsed

        keys = re.findall(r"^([A-Za-z_-]+):", fm, re.MULTILINE)
        missing = [k for k in SKILL_FRONTMATTER_KEYS if k not in keys]
        if missing:
            r.fail(f"{skill_md}: frontmatter missing {missing}")
            continue

        name_m = re.search(r"^name:\s*(.+)$", fm, re.MULTILINE)
        desc_m = re.search(r"^description:\s*(.+)$", fm, re.MULTILINE)
        name = name_m.group(1).strip() if name_m else ""
        desc = desc_m.group(1).strip() if desc_m else ""

        if name != d.name:
            r.fail(f"{skill_md}: frontmatter name '{name}' does not match directory '{d.name}'")
        elif not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name):
            r.fail(f"{skill_md}: name '{name}' is not lowercase-kebab-case")
        else:
            names.append(name)

        if not desc:
            r.fail(f"{skill_md}: empty description")
        elif len(desc) > 1024:
            r.warn(f"{skill_md}: description is {len(desc)} chars, many loaders cap at 1024")
        elif len(desc) < 40:
            r.warn(f"{skill_md}: description is only {len(desc)} chars, may not trigger reliably")

        if ARCHIVE_MARKERS.search(fm):
            r.fail(f"{skill_md}: frontmatter references an archived skill")

        if len(body.strip()) < 200:
            r.fail(f"{skill_md}: body is only {len(body.strip())} chars, too thin to be operational")

        # Every relative link in the body must resolve.
        for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", body):
            if link.startswith(("http://", "https://", "#", "mailto:")):
                continue
            target = (skill_md.parent / link.split("#")[0]).resolve()
            if not target.exists():
                r.fail(f"{skill_md}: relative link does not resolve: {link}")

        if ARCHIVE_MARKERS.search(body):
            r.warn(f"{skill_md}: body mentions an archive path, check it is not loadable")

    if names:
        r.ok(f"{len(names)} skills have valid frontmatter: {', '.join(sorted(names))}")
    return names


def check_scenarios(root: Path, r: Results) -> None:
    scenarios_dir = root / SCENARIOS_DIR
    if not scenarios_dir.is_dir():
        r.fail(f"no scenarios directory at {SCENARIOS_DIR}")
        return

    all_ids: dict[str, str] = {}
    per_difficulty: dict[str, int] = defaultdict(int)
    missing_section_hits: list[str] = []

    for fname, difficulty in SCENARIO_FILES.items():
        p = scenarios_dir / fname
        if not p.is_file():
            r.fail(f"missing scenario file: {fname}")
            continue

        blocks = find_scenario_blocks(read(p))
        if not blocks:
            r.fail(f"{fname}: no scenarios found (expected headings like '### EASY-01. Title')")
            continue

        per_difficulty[difficulty] += len(blocks)

        for sid, block in blocks:
            expected_prefix = {"easy": "EASY", "medium": "MED", "hard": "HARD"}[difficulty]
            if not sid.startswith(expected_prefix):
                r.fail(f"{fname}: scenario id '{sid}' does not match its file's difficulty")

            if sid in all_ids:
                r.fail(f"duplicate scenario id {sid} in {fname} and {all_ids[sid]}")
            else:
                all_ids[sid] = fname

            for section in REQUIRED_SCENARIO_SECTIONS:
                ok, size = section_present(block, section)
                if not ok:
                    if size:
                        missing_section_hits.append(f"{sid}: '{section}' is present but nearly empty ({size} chars)")
                    else:
                        missing_section_hits.append(f"{sid}: missing section '{section}'")

            urls = URL_RE.findall(block)
            if len(urls) < 1:
                missing_section_hits.append(f"{sid}: References section has no URL")

    for hit in missing_section_hits:
        r.fail(f"scenario {hit}")

    for difficulty, count in sorted(per_difficulty.items()):
        if count >= MIN_PER_DIFFICULTY:
            r.ok(f"{difficulty}: {count} scenarios (minimum {MIN_PER_DIFFICULTY})")
        else:
            r.fail(f"{difficulty}: only {count} scenarios, minimum is {MIN_PER_DIFFICULTY}")

    # Adversarial and regression suites are additional; warn rather than fail.
    for extra in ("adversarial.md", "regression.md"):
        p = scenarios_dir / extra
        if p.is_file():
            n = len(find_scenario_blocks(read(p)))
            if n:
                r.ok(f"{extra}: {n} scenarios")
            else:
                r.fail(f"{extra}: no scenarios found")
        else:
            r.warn(f"{extra} not present, stress-test suite is incomplete")


def check_local_links(root: Path, r: Results) -> None:
    """Every relative markdown link in README and CHANGELOG must resolve."""
    checked = 0
    for name in ("README.md", "CHANGELOG.md"):
        p = root / name
        if not p.is_file():
            continue
        for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", read(p)):
            if link.startswith(("http://", "https://", "#", "mailto:")):
                continue
            if not (root / link.split("#")[0]).exists():
                r.fail(f"{name}: relative link does not resolve: {link}")
            else:
                checked += 1
    if checked:
        r.ok(f"{checked} relative links in README/CHANGELOG resolve")


def check_research(root: Path, r: Results) -> None:
    research = root / RESEARCH_DIR
    if not research.is_dir():
        r.fail(f"no research directory at {RESEARCH_DIR}")
        return

    pages = research / "pages"
    n_pages = len(list(pages.glob("*.txt"))) if pages.is_dir() else 0
    if n_pages:
        r.ok(f"research/pages holds {n_pages} fetched documents")
    else:
        r.warn("research/pages is empty, no documents were fetched")

    index = research / "official-documentation-index.md"
    if not index.is_file():
        r.fail("missing research/official-documentation-index.md")
    else:
        r.ok("official documentation index exists")

    notes = sorted(research.glob("notes-*.md"))
    if notes:
        r.ok(f"{len(notes)} research note files: {', '.join(p.name for p in notes)}")
    else:
        r.warn("no notes-*.md research files found")


def check_code_blocks(root: Path, r: Results) -> None:
    """Every fenced XML and JSON block in the scenarios must parse.

    Invented and malformed markup is the single most common defect class these reviews
    find, and a real fix pass turned up a `<Source ...>` missing its closing bracket that
    no structural check had noticed. A script can catch that much, cheaply, even though it
    cannot tell a real element name from a plausible one.
    """
    import json as _json
    import xml.etree.ElementTree as ET

    xml_total = xml_bad = json_total = json_bad = 0

    for path in sorted((root / SCENARIOS_DIR).glob("*.md")):
        text = read(path)
        for m in re.finditer(r"```xml\n(.*?)(?:^>\s*)?```", text, re.DOTALL):
            xml_total += 1
            body = re.sub(r"^>\s?", "", m.group(1), flags=re.MULTILINE).strip()
            # Fragments use a bare attribute value such as
            # <Source request.header.name>, which is not well-formed XML by design.
            wrapped = f"<root>{body}</root>"
            try:
                ET.fromstring(re.sub(r"<([A-Z][\w.]*)\s+([\w.$-]+)\s*\n", r'<\1 name="\2"/>\n', wrapped))
            except ET.ParseError:
                # Retry with every bare attribute value quoted, which is the usual cause.
                try:
                    fixed = re.sub(r"(<[A-Z][\w.]*)\s+([\w.$-]+)\s*(/?>)",
                                   r'\1 name="\2"\3', wrapped)
                    ET.fromstring(fixed)
                except ET.ParseError as e:
                    xml_bad += 1
                    r.fail(f"{path.name}: XML block does not parse: {e}")

        for m in re.finditer(r"```json\n(.*?)\n(?:>\s*)?```", text, re.DOTALL):
            json_total += 1
            # A fence inside a blockquote carries a "> " prefix on every line. That is
            # valid markdown and the JSON under it is usually fine, but the prefix lands
            # inside the captured group and made three valid payloads look corrupt.
            body = re.sub(r"^>\s?", "", m.group(1), flags=re.MULTILINE)
            try:
                _json.loads(body)
            except ValueError as e:
                json_bad += 1
                r.fail(f"{path.name}: JSON block does not parse: {e}")

    if xml_total or json_total:
        r.ok(f"code blocks parse: {xml_total} XML, {json_total} JSON, "
             f"{xml_bad + json_bad} bad")


def check_packets(root: Path, r: Results) -> None:
    """Generated evaluation packets must exist per turn and must not leak the key.

    The first evaluation run released only turn 1, so most ground truths were
    unreachable and both arms scored low for reasons unrelated to the skill. This check
    exists so a missing turn is caught by the harness rather than discovered in a result
    that gets read as a finding about the skill.
    """
    packets = root / "evaluation" / "packets"
    if not packets.is_dir():
        r.warn("evaluation/packets not generated; run tests/make_packets.py --all --turn 1 and --turn 2")
        return

    turn1 = sorted(p for p in packets.glob("*.prompt.md") if ".turn2" not in p.name)
    turn2 = sorted(packets.glob("*.turn2.prompt.md"))
    keys = sorted(packets.glob("*.key.md"))

    # Staleness. A reviewer caught answer keys that still asserted a ground truth the
    # scenario had been rewritten away from, which would have graded every response
    # against the wrong answer. Editing a scenario without regenerating its packets is
    # silent, so compare mtimes and refuse to call the packets current.
    # Map every scenario ID to the mtime of the FILE that contains it. Keying by
    # filename stem looks right and is not: the file is hard.md and the IDs inside it
    # are HARD-01..HARD-15, so a stem-keyed lookup silently matches nothing and the
    # guard passes vacuously. Verified by deliberately touching a file.
    id_re = re.compile(r"\b(EASY|MED|HARD|ADV|REG)-(\d{2,3})\b")
    id_mtimes: dict[str, float] = {}
    for p in sorted((root / SCENARIOS_DIR).glob("*.md")):
        if p.name == "index.md":
            continue
        for sid in id_re.findall(read(p)):
            key = f"{sid[0]}-{sid[1]}"
            id_mtimes[key] = max(id_mtimes.get(key, 0.0), p.stat().st_mtime)

    stale = []
    for packet in turn1 + turn2 + keys:
        sid = packet.name.split(".")[0]
        src = id_mtimes.get(sid)
        if src is not None and packet.stat().st_mtime < src:
            stale.append(sid)
    if stale:
        uniq = sorted(set(stale))
        r.fail(f"{len(uniq)} packet(s) are older than their scenario and hold a stale "
               f"answer key: {', '.join(uniq[:8])}{'...' if len(uniq) > 8 else ''}. "
               f"Re-run: python3 tests/make_packets.py --all --turn 1 && "
               f"python3 tests/make_packets.py --all --turn 2")
    elif turn1 or turn2:
        r.ok("packets are newer than every scenario they derive from")

    if turn1 and turn2:
        r.ok(f"evaluation packets: {len(turn1)} turn-1, {len(turn2)} turn-2, {len(keys)} keys")
    else:
        missing = "turn 2" if turn1 and not turn2 else "turn 1"
        r.fail(f"evaluation packets incomplete: {missing} prompts missing, so the run would be unusable")

    # Leakage: no prompt may contain a key heading.
    leaked = []
    for p in turn1 + turn2:
        text = read(p)
        for marker in ("Ground-Truth Resolution", "Correct Remediation",
                       "Common Incorrect Answers", "Evaluation Rubric"):
            if marker in text:
                leaked.append(f"{p.name} contains '{marker}'")
                break
    for hit in leaked:
        r.fail(f"packet leakage: {hit}")
    if not leaked and (turn1 or turn2):
        r.ok("no ground truth leaked into any prompt packet")

    # Every key must carry its critical-failure conditions. A grader who cannot see them
    # cannot apply them, and rubric.md requires honouring them. All 22 MED keys were
    # silently missing theirs because the extractor only looked under one heading, so a
    # MED response tripping a condition could still be scored as a pass.
    missing_cf = []
    for k in keys:
        text = read(k)
        ok = False
        if "## Critical failures" in text:
            after = text.split("## Critical failures", 1)[1].strip()
            ok = len(after) >= 20
        if not ok:
            missing_cf.append(k.name.split(".")[0])
    if missing_cf:
        r.fail(f"{len(missing_cf)} answer key(s) carry no critical-failure conditions "
               f"(heading absent or empty): "
               f"{', '.join(missing_cf[:8])}{'...' if len(missing_cf) > 8 else ''}")
    elif keys:
        r.ok(f"all {len(keys)} answer keys carry critical-failure conditions")


def check_unslop_scope(r: Results) -> None:
    """unslop is a writing skill, not a diagnosis skill. Record that explicitly.

    This is a scope check, not a correctness check. It exists so a future editor who
    wires unlop into the Apigee diagnosis path gets told about it.
    """
    r.review(
        "unslop governs prose only. Verify it never overrides exact error strings, "
        "config syntax, or product names in any support answer."
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="repository root")
    ap.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"root is not a directory: {root}")
        return 2

    r = Results()
    check_root_files(root, r)
    check_skills(root, r)
    check_scenarios(root, r)
    check_local_links(root, r)
    check_research(root, r)
    check_code_blocks(root, r)
    check_packets(root, r)
    check_unslop_scope(r)

    def dump(title: str, items: list[str]) -> None:
        if not items:
            return
        print(f"\n{title} ({len(items)})")
        for item in items:
            print(f"  - {item}")

    print("=" * 72)
    print("MECHANICAL CHECKS")
    print("=" * 72)
    print(f"passed {len(r.passed)}   failed {len(r.failed)}   warnings {len(r.warned)}")
    dump("PASS", r.passed)
    dump("FAIL", r.failed)
    dump("WARN", r.warned)

    print()
    print("=" * 72)
    print("NEEDS HUMAN OR MODEL REVIEW (not checkable by script)")
    print("=" * 72)
    for item in r.needs_review:
        print(f"  - {item}")
    print(
        "  - whether each scenario's ground truth is technically correct\n"
        "  - whether each cited URL supports the claim it is attached to\n"
        "  - whether difficulty classifications match the diagnostic work required\n"
        "  - whether any scenario can be solved from its title alone"
    )

    if r.failed:
        print("\nRESULT: FAIL")
        return 1
    if args.strict and r.warned:
        print("\nRESULT: FAIL (strict mode, warnings present)")
        return 1
    print("\nRESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())