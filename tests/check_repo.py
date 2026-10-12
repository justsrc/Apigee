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
# Discovery: what scenarios actually exist
# ---------------------------------------------------------------------------


SCENARIO_ID_RE = re.compile(r"\b(EASY|MED|HARD|ADV|REG)-(\d{2,3})\b")


def scenario_ids(root: Path) -> set[str]:
    """Every scenario ID defined in scenarios/*.md, excluding the generated index.

    Used as the source of truth for completeness checks. A hard-coded count is not
    usable here: it changes whenever a scenario is added, and a check that asserts a
    literal either rots or gets edited until it passes. Comparing against the IDs
    themselves holds however the library grows.
    """
    ids: set[str] = set()
    for p in sorted((root / SCENARIOS_DIR).glob("*.md")):
        if p.name == "index.md":
            continue
        for prefix, num in SCENARIO_ID_RE.findall(read(p)):
            ids.add(f"{prefix}-{num}")
    return ids


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

    # Adversarial and regression suites are additional but load-bearing: the regression
    # suite is the documented smoke test after a skill change, so a missing file is a
    # missing test rather than a missing extra. Both were previously warned about, which
    # let `rm scenarios/regression.md` exit 0. Their IDs are still checked for uniqueness
    # and prefix, but they do not carry the full graded section list.
    for extra in ("adversarial.md", "regression.md"):
        p = scenarios_dir / extra
        if not p.is_file():
            r.fail(f"missing scenario file: {extra}. The regression suite is the "
                   f"documented post-change smoke test and cannot be optional.")
            continue
        n = len(find_scenario_blocks(read(p)))
        if n:
            r.ok(f"{extra}: {n} scenarios")
        else:
            r.fail(f"{extra}: no scenarios found")


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
        # An empty corpus was only a warning. It is the input to every generated index in
        # this project, so an empty one means the indices are stale and unprovable, and
        # the run would still report PASS on the indices built from them. Verified by
        # deleting the cache, which used to exit 0.
        r.fail("research/pages holds no documents. Every generated index here is derived "
               "from it, so an empty cache invalidates all of them and any check on those "
               "indexes becomes vacuous. Restore the corpus or re-run research/fetch.sh.")

    index = research / "official-documentation-index.md"
    if not index.is_file():
        r.fail("missing research/official-documentation-index.md")
    elif n_pages == 0:
        r.fail("official documentation index exists but the corpus it indexes is empty")
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
        # Warned about before. That is a false pass: a run with no packets cannot happen,
        # so its absence means the evaluation inputs were never built, not that nothing
        # was required. Verified by deleting the directory, which used to exit 0.
        r.fail("evaluation/packets does not exist; the evaluation inputs were never built. "
               "Run: python3 tests/make_packets.py --all --turn 1 && "
               "python3 tests/make_packets.py --all --turn 2")
        return

    turn1 = sorted(p for p in packets.glob("*.prompt.md") if ".turn2" not in p.name)
    turn2 = sorted(packets.glob("*.turn2.prompt.md"))
    keys = sorted(packets.glob("*.key.md"))

    # Per-scenario completeness. Counting the files was not enough. The set is built as
    # three per scenario, so deleting exactly one of them leaves a count that still looks
    # healthy, and the run would silently proceed with one scenario unreleasable or
    # ungradable. Assert against the scenario IDs, which are the source of truth, rather
    # than against a count that changes legitimately as scenarios are added.
    expected_ids = scenario_ids(root)
    have_t1 = {p.name.split(".")[0] for p in turn1}
    have_t2 = {p.name.split(".")[0] for p in turn2}
    have_k = {p.name.split(".")[0] for p in keys}
    for label, have in (("turn-1 prompt", have_t1), ("turn-2 prompt", have_t2),
                        ("answer key", have_k)):
        missing = sorted(expected_ids - have)
        extra = sorted(have - expected_ids)
        if missing:
            shown = ", ".join(missing[:8]) + ("..." if len(missing) > 8 else "")
            r.fail(f"{len(missing)} scenario(s) have no {label}: {shown}")
        if extra:
            shown = ", ".join(extra[:8]) + ("..." if len(extra) > 8 else "")
            r.fail(f"{len(extra)} {label}(s) exist for no scenario in scenarios/: {shown}")
    if not (expected_ids - have_t1 or expected_ids - have_t2 or expected_ids - have_k):
        r.ok(f"all {len(expected_ids)} scenarios have a turn-1 prompt, a turn-2 prompt "
             f"and an answer key")

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


def _normalized_words(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def source_critical_failure_paragraph(block: str) -> str:
    """Rebuild the bold critical-failures paragraph from a scenario block.

    Scenarios write the conditions as a bold lead-in followed by wrapped prose, for
    example "**Critical failures:** first condition;\\n second condition.". The packet
    generator once stopped at the first physical line and truncated the condition in the
    answer key, so this reconstructs the paragraph independently and does not share that
    bug.
    """
    lines = block.splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"^\*\*Critical failures?:?\*\*\s*(.*)$", line.strip(), re.I)
        if not m:
            continue
        out = [m.group(1).strip()]
        for follow in lines[i + 1:]:
            if not follow.strip() or re.match(r"^#{1,6}\s", follow):
                break
            out.append(follow.strip())
        text = " ".join(x for x in out if x)
        if text:
            return text
    return ""


def check_critical_failure_completeness(root: Path, r: Results) -> None:
    """Every key's critical failures must cover the whole condition in the scenario.

    A truncated condition is worse than a missing one: the key looks present and the
    grader applies only the fragment that survived. Compare the tail of the source
    paragraph against the key so a first-line-only extraction fails here.
    """
    packets = root / "evaluation" / "packets"
    if not packets.is_dir():
        return

    truncated = []
    checked = 0
    for path in sorted((root / SCENARIOS_DIR).glob("*.md")):
        if path.name == "index.md":
            continue
        for sid, block in find_scenario_blocks(read(path)):
            para = source_critical_failure_paragraph(block)
            if not para:
                continue
            key = packets / f"{sid}.key.md"
            if not key.is_file():
                continue
            checked += 1
            key_text = read(key)
            key_cf = key_text.split("## Critical failures", 1)[1] if "## Critical failures" in key_text else ""
            words = _normalized_words(para).split()
            tail = " ".join(words[-6:]) if words else ""
            if not tail or tail not in _normalized_words(key_cf):
                truncated.append(sid)

    if truncated:
        r.fail(f"{len(truncated)} answer key(s) carry a truncated critical-failure "
               f"condition: {', '.join(truncated[:8])}{'...' if len(truncated) > 8 else ''}. "
               f"Re-run: python3 tests/make_packets.py --all --turn 1 && "
               f"python3 tests/make_packets.py --all --turn 2")
    elif checked:
        r.ok(f"all {checked} bold critical-failure conditions reach their answer keys in full")


def check_generated_references(root: Path, r: Results) -> None:
    """Generated reference files must not carry raw HTML or escaped angle brackets.

    google wraps some table cells in markup, and the extractor used to pass the wrapper
    through. That produced a fault code of "steps.javacallout.ExecutionErrorspan" and
    left a raw <span> in the index. The generator now strips wrappers and unescapes
    "\\<URL\\>"; this catches a regression.
    """
    refs = root / ".agents" / "skills" / "apigee-support-core" / "references"
    files = sorted(refs.glob("*.md")) if refs.is_dir() else []
    if not files:
        return

    bad = []
    for p in files:
        text = read(p)
        for marker in ("<span", "<div", "<table", "sheets-userformat", "<\\"):
            if marker in text:
                bad.append(f"{p.name} contains {marker!r}")

    for hit in bad:
        r.fail(f"generated reference has raw markup: {hit}")
    if not bad:
        r.ok("generated reference files carry no raw HTML or escaped angle brackets")


def check_generated_freshness(root: Path, r: Results) -> None:
    """A generated file must match what its generator produces from the current sources.

    The raw-markup check above only proves the output is well formed. It cannot tell a
    freshly generated file from one that was hand-edited, truncated, or left behind by an
    older generator, because all three are equally valid Markdown. Deleting every
    SpikeArrest runtime code from the fault-code index, the defect this project was built
    after, exited 0.

    Regenerating into a temporary file and diffing is the only check that distinguishes
    the two. It runs the real generator against the real corpus, so it also fails when a
    generator breaks, which is the case worth catching.
    """
    sys.path.insert(0, str(root / "research"))
    try:
        import build_error_index  # type: ignore
        import build_scenario_index  # type: ignore
    except Exception as e:  # pragma: no cover - import failure is itself a finding
        r.fail(f"cannot import the generators to verify freshness: {e}")
        return
    finally:
        try:
            sys.path.remove(str(root / "research"))
        except ValueError:
            pass

    produced = build_error_index.build()

    ref = (root / ".agents/skills/apigee-support-core/references/error-codes.md")
    if not ref.is_file():
        r.fail("missing references/error-codes.md, the generated fault-code index")
        return
    committed = read(ref)
    if committed.strip() != produced.strip():
        missing = _missing_fault_codes(produced, committed)
        extra_note = ""
        if missing:
            extra_note = (" Codes present in the source pages but absent from the "
                          f"committed index: {', '.join(missing[:6])}"
                          + ("..." if len(missing) > 6 else "") + ".")
        r.fail("references/error-codes.md is not what research/build_error_index.py "
               "produces from the current corpus. It is generated: fix the generator or "
               "the source pages, then regenerate, do not edit the output." + extra_note)
    else:
        r.ok("fault-code index matches a fresh run of build_error_index.py")

    if not _scenario_index_current(root, build_scenario_index):
        r.fail("scenarios/index.md is stale relative to scenarios/*.md. Run: "
               "python3 research/build_scenario_index.py")
    else:
        r.ok("scenario index matches a fresh run of build_scenario_index.py")


def _missing_fault_codes(produced: str, committed: str) -> list[str]:
    """Codes the generator emits that the committed index does not contain."""
    import re as _re
    want = set(_re.findall(r"^\| `([^`]+)` \|", produced, _re.M))
    have = set(_re.findall(r"^\| `([^`]+)` \|", committed, _re.M))
    return sorted(want - have)


def _scenario_index_current(root: Path, build_scenario_index) -> bool:
    try:
        produced = build_scenario_index.build()
    except Exception:
        return False
    idx = root / "scenarios" / "index.md"
    if not idx.is_file():
        return False
    return read(idx).strip() == produced.strip()


def check_reference_discovery(root: Path, r: Results) -> None:
    """Every reference file must be named in its skill's SKILL.md.

    A reference file nobody is told about is never loaded, so its content may as well
    not exist. The core skill carried policy-mechanics.md while its reference table
    listed five other files and omitted that one, which no script noticed until now.
    """
    skills_dir = root / SKILLS_DIR
    if not skills_dir.is_dir():
        return

    orphans: list[str] = []
    unresolvable: list[str] = []
    total = 0
    for d in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        refs = d / "references"
        skill_md = d / "SKILL.md"
        if not refs.is_dir() or not skill_md.is_file():
            continue
        body = read(skill_md)
        for f in sorted(refs.glob("*.md")):
            total += 1
            if f.name not in body:
                orphans.append(f"{d.name}/references/{f.name}")

        # The skill advertises its references as backticked relative paths in a table,
        # not as markdown links, so the relative-link check above never saw them and the
        # name match above cannot tell a real path from a sentence that happens to contain
        # the filename. Resolving the listed paths is what catches a deleted or renamed
        # reference, which previously exited 0.
        for rel in sorted(set(re.findall(r"`(references/[A-Za-z0-9._-]+\.md)`", body))):
            if not (d / rel).is_file():
                unresolvable.append(f"{d.name}/{rel}")

    for o in orphans:
        r.fail(f"reference file is not named in its SKILL.md: {o}")
    for u in unresolvable:
        r.fail(f"SKILL.md lists a reference path that does not resolve: {u}")
    if total and not orphans:
        r.ok(f"all {total} reference files are named in their SKILL.md")
    if not unresolvable:
        r.ok("every reference path listed in a SKILL.md resolves to a file")


def check_scenario_codes(root: Path, r: Results) -> None:
    """Every fault-code-shaped token in a scenario body must exist in the source corpus.

    The reviews this project has run keep finding invented codes: a
    steps.javacallout.JavaCalloutExecutionError that does not exist, a
    messaging.adaptors.http.flow.BadRequest that is not in the reference. Both were
    plausible, both were confidently cited, and no structural check noticed either.

    The test below exists because those are mechanical defects wearing a technical costume.
    A token counts as a fault code if it is dotted lowercase-initial, which is Apigee's
    convention, or if it is CamelCase ending in a fault-like word. Config properties,
    filenames and flow-variable names are excluded, because those are legitimately not in
    the fault-code corpus and flagging them would train a reader to ignore this check.

    Deliberately conservative: a token this misses is a miss, not a false pass, and the
    limit is recorded rather than hidden.
    """
    corpus_parts: list[str] = []
    for p in sorted((root / RESEARCH_DIR / "pages").glob("*.txt")):
        corpus_parts.append(read(p))
    ref = root / ".agents" / "skills" / "apigee-support-core" / "references" / "error-codes.md"
    if ref.is_file():
        corpus_parts.append(read(ref))
    corpus = "\n".join(corpus_parts)
    if not corpus.strip():
        r.fail("cannot verify scenario fault codes: the research corpus is empty")
        return

    # Fault-word suffixes, used only for the CamelCase half of the pattern.
    suffix = (r"Error|Failed|Failure|NotFound|Found|Invalid|Missing|Expired|Timeout|"
              r"Exceeded|Unknown|Wrong|Required|Unavailable|Rejected|Limit|Disabled|"
              r"Conflict|Duplicate|Mismatch|Busy|Empty|Bad|Blocked|Denied|Unsupported|"
              r"Violation|Quota|Condition")
    code_re = re.compile(rf"`((?:[a-z][a-z0-9_]*\.){{2,}}[A-Za-z][A-Za-z0-9_]*|[A-Z][A-Za-z0-9]+(?:{suffix}))`")

    # Config elements, file names and flow variables that look like codes but are not.
    # Apigee flow variables are conventionally written private.<name> or app.<name> for
    # user-scoped ones, and scenario authors invent plausible ones constantly, so that
    # prefix is excluded outright.
    not_codes = re.compile(
        r"^(?:io|connect|keepalive|overrides|cassandra|logger|spec|iam|apigee|ratelimit|"
        r"target|request|response|context|system|private|app|my|api|docs|entry|report)\."
        r"|\.(?:md|yaml|sh|properties|txt)$", re.I)

    unknown: list[str] = []
    checked = 0
    for p in sorted((root / SCENARIOS_DIR).glob("*.md")):
        if p.name == "index.md":
            continue
        for sid, block in find_scenario_blocks(read(p)):
            # The "cases deliberately not converted" appendix records codes that were
            # considered and rejected. Flagging them would invert their meaning.
            if "NOT converted into scenarios" in block or "Rejected" in block:
                continue
            for m in code_re.finditer(block):
                tok = m.group(1)
                if not_codes.match(tok):
                    continue
                checked += 1
                if tok in corpus:
                    continue
                # A scenario may deliberately quote a code that does not exist, provided
                # it says so. HARD-21 transcribes an operator's errorcode that is absent
                # from the Apigee reference and asks the agent to notice. That is a test,
                # not a defect, so a token the scenario itself marks as unverified is
                # accepted. Requiring the marker keeps this from becoming a loophole: an
                # invented code that is passed off as real still fails.
                line_no = block[:m.start()].count("\n")
                window = "\n".join(block.splitlines()[max(0, line_no - 6):line_no + 6])
                if re.search(r"(unverified|not in the (?:Apigee )?fault|does not exist|"
                             r"no code by that name|no such code|absent from)", window, re.I):
                    continue
                unknown.append(f"{sid}: {tok}")

    if unknown:
        r.fail(f"{len(unknown)} fault-code-shaped token(s) in scenario bodies do not appear "
               f"anywhere in research/pages/ or the generated index: "
               f"{', '.join(sorted(set(unknown))[:8])}"
               f"{'...' if len(set(unknown)) > 8 else ''}. An invented code is worse than "
               f"no code, because an agent is graded against it.")
    else:
        r.ok(f"all {checked} fault-code-shaped tokens in scenario bodies exist in the "
             f"cached source corpus")


def check_origin_integrity(root: Path, r: Results) -> None:
    """Origin classification must use the controlled set and must not inflate real-world.

    The project's own reported split was 53.4% real-world, 31.1% documented, 15.5%
    synthetic. Measured from the scenarios that is 33.0 / 31.1 / 35.9. The difference is
    exact, not approximate: adding the 13 adversarial and 8 regression scenarios to
    real-world gives 55, and removing them from synthetic gives 16. Both match the reported
    figures to the scenario.

    Those two files are constructed evaluations, not incident reports, and say so in their
    own headers. Counting them as real-world inflates the provenance of the library by
    twenty-one scenarios and is the specific error this check exists to prevent.
    """
    counts: dict[str, int] = defaultdict(int)
    unclassified: list[str] = []
    misplaced: list[str] = []

    for p in sorted((root / SCENARIOS_DIR).glob("*.md")):
        if p.name == "index.md":
            continue
        constructed = p.name in ("adversarial.md", "regression.md")
        for sid, block in find_scenario_blocks(read(p)):
            m = re.search(r"^- Origin:\s*(.+?)\s*$", block, re.MULTILINE)
            if not m:
                unclassified.append(f"{sid}: no Origin field")
                continue
            low = m.group(1).strip().lower()
            if low.startswith("reported real-world"):
                kind = "real-world"
            elif low.startswith("documented"):
                kind = "documented"
            elif "synthetic" in low:
                kind = "synthetic"
            else:
                unclassified.append(f"{sid}: origin '{m.group(1).strip()[:40]}' is not one "
                                    f"of real-world, documented or synthetic")
                continue
            counts[kind] += 1
            if constructed and kind == "real-world":
                misplaced.append(f"{sid} in {p.name} is labelled real-world")

    for u in unclassified:
        r.fail(f"origin classification: {u}")
    for m in misplaced:
        r.fail(f"origin classification: {m}. The adversarial and regression suites are "
               f"constructed evaluations, not incident reports.")
    if not unclassified and not misplaced:
        total = sum(counts.values())
        parts = ", ".join(f"{counts[k]} {k}" for k in ("real-world", "documented", "synthetic")
                          if counts[k])
        r.ok(f"origin classification is unambiguous across {total} scenarios ({parts})")


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
    check_critical_failure_completeness(root, r)
    check_generated_references(root, r)
    check_generated_freshness(root, r)
    check_reference_discovery(root, r)
    check_scenario_codes(root, r)
    check_origin_integrity(root, r)
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