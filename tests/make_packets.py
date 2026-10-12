#!/usr/bin/env python3
"""Build evaluation packets: the parts of a scenario an agent is allowed to see.

Scoring a response against a ground truth the agent could read measures nothing. This
extracts only the initial ticket and the initial evidence, which is exactly what a
support requester would hand over, and writes the held-back material to a separate file
that stays out of the prompt.

Two turns, because most scenarios here are not solvable from the initial ticket alone.
The first evaluation run forgot this. It released only turn 1, so six of seven ground
truths were unreachable and both arms scored low for reasons unrelated to the skill.

  turn 1   the initial ticket and initial evidence
  turn 2   the diagnostic evidence, released only after the agent answers turn 1

Ground truth, remediation, verification, incorrect answers and rubric are never released.

Usage:
    python3 tests/make_packets.py EASY-04 EASY-08 --turn 1
    python3 tests/make_packets.py EASY-04 EASY-08 --turn 2
    python3 tests/make_packets.py --all --turn 1
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCEN = ROOT / "scenarios"
OUT = ROOT / "evaluation" / "packets"

FILES = {
    "easy": SCEN / "easy.md",
    "medium": SCEN / "medium.md",
    "hard": SCEN / "hard.md",
    "adversarial": SCEN / "adversarial.md",
    "regression": SCEN / "regression.md",
}

ID_RE = re.compile(r"\b(EASY|MED|HARD|ADV|REG)-(\d{2,3})\b")

# What the agent may see, by turn.
TURN1 = ["initial support ticket", "initial evidence"]
TURN2 = ["diagnostic evidence"]
KEY = ["ground-truth resolution", "correct remediation", "verification",
       "common incorrect answers", "evaluation rubric", "references"]

PREAMBLE = """You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.

"""


def norm(t: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z ]", " ", t.lower())).strip()


def blocks(path: Path) -> list[tuple[str, str]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    starts, in_fence = [], False
    for i, line in enumerate(lines):
        if re.match(r"^\s*(```|~~~)", line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = re.match(r"^#{2,4}\s+(.*)$", line)
        if m:
            found = ID_RE.search(m.group(1))
            if found:
                starts.append((i, found.group(0)))
    out = []
    for n, (ln, sid) in enumerate(starts):
        end = starts[n + 1][0] if n + 1 < len(starts) else len(lines)
        out.append((sid, "\n".join(lines[ln:end])))
    return out


def section(block: str, wanted: str, headings: list) -> str | None:
    target = norm(wanted)
    body = block.splitlines()
    for idx, (_lvl, text, ln) in enumerate(headings):
        if idx == 0:
            continue
        if norm(text) == target or target in norm(text):
            stop = headings[idx + 1][2] if idx + 1 < len(headings) else len(body)
            return "\n".join(body[ln + 1:stop]).strip()
    return None


def headings_of(block: str) -> list:
    out, in_fence = [], False
    for i, line in enumerate(block.splitlines()):
        if re.match(r"^\s*(```|~~~)", line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            out.append((len(m.group(1)), m.group(2).strip(), i))
    return out


def critical_failures(block: str) -> str:
    """Return the critical-failure conditions from a scenario, whatever shape they take.

    Three forms appear in this library: a heading, bold body text under the rubric, and a
    sibling heading next to it. All three must be found, because a grader who cannot see
    the conditions cannot apply them, and a response that trips one may be scored as a
    pass.
    """
    # A heading, at any level. Several scenarios put the conditions inline in the heading
    # itself, as "#### Critical failures: recommending a redeploy as the fix.", with nothing
    # on the following lines. Taking only the body missed those, which is how 7 of 22 MED
    # scenarios ended up with no conditions in their key.
    for _lvl, text, ln in headings_of(block):
        if norm(text).startswith("critical failure"):
            inline = re.sub(r"^critical failures?:?\s*", "", text, flags=re.I).strip()
            body = block.splitlines()
            out, started = [], False
            for line in body[ln + 1:]:
                if re.match(r"^#{2,4}\s", line) and started:
                    break
                if line.strip():
                    started = True
                    out.append(line)
            body_text = "\n".join(out).strip()
            if inline:
                # Same paragraph, no blank line. A blank line made the heading and its
                # continuation render as two fragments in the key.
                return f"{inline} {body_text}".strip()
            if body_text:
                return body_text

    # Bold body text under the rubric.
    lines = block.splitlines()
    for i, line in enumerate(lines):
        if line.strip().lower().startswith("**critical failure"):
            out = []
            for follow in lines[i:]:
                # Lowercase both sides. The outer test lowercases and this one did not,
                # so a line reading "**Critical failures:**" matched the outer test and
                # then broke out immediately on the inner one, yielding an empty string
                # and a key with no conditions at all.
                if follow.strip() and not follow.strip().lower().startswith("**critical failure"):
                    break
                out.append(re.sub(r"^\*\*Critical failures?:?\*\*", "", follow.strip(), flags=re.I))
            return " ".join(x for x in out if x)

    return ""


def main() -> int:
    argv = sys.argv[1:]
    turn = 1
    if "--turn" in argv:
        i = argv.index("--turn")
        try:
            turn = int(argv[i + 1])
        except (IndexError, ValueError):
            print("--turn needs a value, 1 or 2", file=sys.stderr)
            return 1
        del argv[i:i + 2]

    if not argv:
        print(__doc__)
        return 1

    wanted = set(argv)
    if "--all" in wanted:
        wanted = {sid for path in FILES.values() for sid, _ in blocks(path)}
        wanted.discard("--all")

    if not wanted or wanted == {"--help"} or "-h" in wanted:
        print(__doc__)
        return 1
    OUT.mkdir(parents=True, exist_ok=True)

    found = 0
    for path in FILES.values():
        for sid, block in blocks(path):
            if sid not in wanted:
                continue
            found += 1
            hs = headings_of(block)
            title = hs[0][1] if hs else sid
            clean_title = re.sub(r"^[A-Z]+-\d+\.?\s*", "", title)

            visible = TURN1 if turn == 1 else TURN2
            prompt = [PREAMBLE, f"# {sid}: {clean_title}", ""]
            if turn == 2:
                prompt.append("The customer has replied with more information.")
                prompt.append("")
            for sec in visible:
                content = section(block, sec, hs)
                if content:
                    prompt.append(f"## {sec.title()}")
                    prompt.append(content)
                    prompt.append("")
            suffix = "" if turn == 1 else ".turn2"
            (OUT / f"{sid}{suffix}.prompt.md").write_text("\n".join(prompt), encoding="utf-8")

            answer = [f"# {sid} answer key, do not show to the agent", ""]
            for sec in KEY:
                content = section(block, sec, hs)
                if content:
                    # medium.md separates its scenarios with a `---` rule, so the final
                    # section's content ends with one. Appending after it put the critical
                    # failures outside the body of the key.
                    content = re.sub(r"\n-{3,}\s*$", "", content).rstrip()
                    if content:
                        answer.append(f"## {sec.title()}")
                        answer.append(content)
                        answer.append("")

            # Critical failures must reach the key whatever shape the scenario uses for
            # them. medium.md wrote them as a sibling heading rather than body text under
            # the rubric, and the extractor stopped at the rubric, so all 22 MED keys were
            # missing them. Since rubric.md tells graders to honour these conditions, a
            # MED response that tripped one could still have been scored as a pass. The
            # section-index approach is fragile here, so scan for it directly.
            cf = critical_failures(block)
            if cf:
                answer.append("## Critical failures")
                answer.append(cf)
                answer.append("")
            (OUT / f"{sid}.key.md").write_text("\n".join(answer), encoding="utf-8")

    if found == 0:
        print("no matching scenario ids", file=sys.stderr)
        return 1
    print(f"wrote {found} turn-{turn} packets to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())