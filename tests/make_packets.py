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


def scenario_files(scen: Path) -> dict[str, Path]:
    """The five scenario files, for whichever directory is being read."""
    return {
        "easy": scen / "easy.md",
        "medium": scen / "medium.md",
        "hard": scen / "hard.md",
        "adversarial": scen / "adversarial.md",
        "regression": scen / "regression.md",
    }


FILES = scenario_files(SCEN)

ID_RE = re.compile(r"\b(EASY|MED|HARD|ADV|REG)-(\d{2,3})\b")

# What the agent may see, by turn.
TURN1 = ["initial support ticket", "initial evidence"]
TURN2 = ["diagnostic evidence"]
KEY = ["ground-truth resolution", "correct remediation", "verification",
       "common incorrect answers", "evaluation rubric", "references"]

# Sections that state a graded boundary and so belong in the key even though they are not
# remediation steps. Two scenarios carry a "Not a critical failure" ruling that explicitly
# clears an answer the grader would otherwise fail, and neither reached the answer key,
# because KEY never named the heading. A grader working from the key could not see the
# scenario's own decision not to fail something.
KEY_EXTRA = ["not a critical failure"]

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


def matches(heading: str, wanted: str, prefix: bool = False) -> bool:
    """Does this heading name the section that was asked for?

    Exact on the normalized text, unless the caller says the heading carries a subject
    after the marker. The old test was `target in norm(text)`, which matched a wanted
    section inside any heading that merely contained the phrase: `references` was
    satisfied by "Fault-code verification ledger references", and `verification` by any
    heading with the word in it. A packet or a key built from a section the scenario
    never wrote is worse than one missing, because it looks complete.

    `prefix=True` is for the one heading shape that is genuinely a prefix:
    `#### Not a critical failure: <subject>`, where the subject is the ruling.
    """
    text = norm(heading)
    return text == norm(wanted) or (prefix and text.startswith(norm(wanted)))


def section(block: str, wanted: str, headings: list, prefix: bool = False) -> str | None:
    """First section whose heading names `wanted`.

    First match only. That is right for the held-back material, where one section per
    heading is enough. It is NOT enough for `Not a critical failure`: MED-09 carries two
    rulings and this returned only the first, so the second never reached the key. That
    second ruling was written by `cb057df` specifically to stop the grader failing a
    documented-correct caveat, so dropping it reinstated the defect that commit fixed.
    `sections()` handles the repeat case.
    """
    body = block.splitlines()
    for idx, (_lvl, text, ln) in enumerate(headings):
        if idx == 0:
            continue
        if matches(text, wanted, prefix):
            stop = headings[idx + 1][2] if idx + 1 < len(headings) else len(body)
            return "\n".join(body[ln + 1:stop]).strip()
    return None


def sections(block: str, wanted: str, headings: list, prefix: bool = False) -> list[str]:
    """Every section whose heading names `wanted`, keeping the heading's own subject.

    A `#### Not a critical failure: <subject>` heading states the ruling in the heading
    line itself. Returning only the body yields a key section that begins mid-sentence
    with no antecedent, which a grader cannot apply: MED-11's key opened with "finding, not
    a wrong answer. It becomes wrong only when..." and never said which finding. Each match
    comes back as `<heading text minus the marker>` followed by the body, and repeats are
    kept rather than collapsed.
    """
    body = block.splitlines()
    out = []
    for idx, (_lvl, text, ln) in enumerate(headings):
        if idx == 0:
            continue
        if matches(text, wanted, prefix):
            stop = headings[idx + 1][2] if idx + 1 < len(headings) else len(body)
            inline = re.sub(r"^#{1,6}\s*", "", text).strip()
            inline = re.sub(r"^Not a critical failure\b[:\s]*", "", inline, flags=re.I).strip()
            rest = "\n".join(body[ln + 1:stop]).strip()
            out.append(f"{inline}\n{rest}".strip() if inline else rest)
    return out


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

    # Bold body text under the rubric, for example "**Critical failures:** ...". The
    # conditions usually wrap onto several physical lines. Stopping at the first line
    # that was not itself the bold label truncated the paragraph, so a key held only the
    # first line of the condition and a grader could not apply the rest. Collect the
    # paragraph instead: take every line until a blank line or the next heading.
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


def packet_texts(scen: Path, wanted: set[str] | None = None) -> dict[str, str]:
    """Render every packet to text, keyed by the file name it is written under.

    Split out of main() so that a checker can ask what this generator would produce
    without writing anything. Writing is main()'s job; deciding what is correct is not,
    and a freshness check that has to write in order to compare cannot safely run
    against a working tree it is only meant to inspect.

    Read-only. `wanted` limits the render to those scenario ids, None means all of them.
    Both turns and the answer key are produced, because the key does not depend on the
    turn and the caller decides which of the three to keep.
    """
    files = scenario_files(scen)
    out: dict[str, str] = {}
    for path in files.values():
        for sid, block in blocks(path):
            if wanted is not None and sid not in wanted:
                continue
            hs = headings_of(block)

            for turn, visible in ((1, TURN1), (2, TURN2)):
                # The scenario title is deliberately NOT put in the prompt.
                #
                # Regression titles are statements of the correct disposition: "The safest
                # recommendation is to change nothing", "Root cause cannot be established",
                # "The right answer is a question". Handing those to the agent hands it the
                # grading criterion, so the suite that exists to catch a skill drifting
                # inaccuracy measures nothing. The same applies to any title phrased as a
                # conclusion rather than a symptom.
                #
                # A real support request arrives as a ticket, not as a headline that states
                # the answer, so dropping the title makes the packets more realistic as well
                # as harder to cheat. The title stays in the answer key for the grader.
                prompt = [PREAMBLE, f"# Support case {sid}", ""]
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
                out[f"{sid}{suffix}.prompt.md"] = "\n".join(prompt)

            answer = [f"# {sid} answer key, do not show to the agent", ""]
            # KEY_EXTRA comes first: it qualifies how the critical failures below are read,
            # so a grader should see the exception before the list it excepts.
            #
            # KEY_EXTRA uses sections() rather than section() because a scenario may carry
            # more than one ruling, and MED-09 does. Taking only the first silently dropped
            # the second, which was the ruling cb057df added.
            for sec in KEY_EXTRA + KEY:
                if sec in KEY_EXTRA:
                    pieces = sections(block, sec, hs, prefix=True)
                else:
                    one = section(block, sec, hs)
                    pieces = [one] if one else []
                for content in pieces:
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
            out[f"{sid}.key.md"] = "\n".join(answer)

    return out


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

    rendered = packet_texts(SCEN, wanted)
    # A turn writes its own prompt and the key, and never the other turn's prompt. The
    # two invocations together produce all three files, which is how the documented
    # `--all --turn 1` then `--all --turn 2` pair has always behaved. Matching on
    # ".prompt.md" is not enough to separate them, because the turn-2 name ends in that
    # too, so the two are told apart by the marker itself.
    written = 0
    for name, text in sorted(rendered.items()):
        is_turn2 = ".turn2." in name
        if not name.endswith(".key.md") and is_turn2 != (turn == 2):
            continue
        (OUT / name).write_text(text, encoding="utf-8")
        written += 1

    if written == 0:
        print("no matching scenario ids", file=sys.stderr)
        return 1
    # A count of scenarios, which is what this used to report, no longer matches what
    # was written: a turn also writes the answer key.
    print(f"wrote {written} files for turn {turn} to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())