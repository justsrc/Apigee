#!/usr/bin/env python3
"""Build a consolidated fault-code index from the policy pages in research/pages.

Why this exists. Apigee's "Policy error reference" page carries no fault codes of its
own, it just points you at the individual policy pages. So the codes are scattered
across roughly 40 documents and no one holds the whole set. Diagnosing a response
means matching an `errorcode` against something, and this script is what makes that
lookup possible.

Each policy page has an `## Error reference` section with `### Runtime errors` and
`### Deployment errors` tables. Runtime error rows are (fault code, HTTP status, cause).
Deployment error rows are (error name, cause) with no status.

Usage:
    python3 research/build_error_index.py            # write error-codes.md
    python3 research/build_error_index.py --stdout   # print instead

The output is a mechanical extraction. It is a pointer to the source page, not a
substitute for it: the cause text is truncated here, so an agent must open the policy
page before asserting why a code fired.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

PAGES = Path(__file__).parent / "pages"
OUT = Path(__file__).parent.parent / ".agents/skills/apigee-support-core/references/error-codes.md"

# Map fetched filenames back to their canonical doc URLs. The fetch script saves as
# <path with slashes replaced by underscores>.txt, so this is a pure function.
def url_for(stem: str) -> str | None:
    stem = stem.replace("_", "/")
    if stem.startswith("https:"):
        return None
    return f"https://cloud.google.com/apigee/docs/{stem}"


def rows_of(block: str) -> list[list[str]]:
    """Parse a markdown pipe table into cell lists, dropping the header."""
    out = []
    for line in block.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        if cells and cells[0].lower() in ("fault code", "error name", "variables", "field"):
            continue
        out.append(cells)
    if out:
        return out
    return rows_of_loose(block)


def rows_of_loose(block: str) -> list[list[str]]:
    """Parse a table that pandoc rendered one cell per line instead of as pipes.

    Not hypothetical. On the SpikeArrest page the Runtime errors table renders with each
    cell on its own line separated by blank lines, while the Deployment errors table on
    the same page renders as a normal pipe table. A pipe-only parser silently returns
    nothing for the first and the second looks fine, so the index looks complete while
    having dropped every SpikeArrest runtime code. That is exactly the failure this
    project exists to catch, so it gets an explicit parser.

    Strategy: split into blank-line-separated paragraphs. The leading paragraphs are the
    column labels; their count gives the column width. Everything after is chunked by
    that width. If the shape does not fit, return nothing rather than guessing, because a
    wrong parse is worse than a missing one and the caller reports coverage either way.
    """
    paras = [p.strip() for p in re.split(r"\n\s*\n", block) if p.strip()]
    if len(paras) < 4:
        return []

    # First data cell is a backticked code. The column labels sit immediately above it,
    # but they are preceded by intro prose, so walk back only over short non-bold
    # paragraphs to find where the label run starts. Counting every preceding paragraph
    # as a column is wrong: the SpikeArrest block opens with two lines of prose.
    data_start = None
    for i, p in enumerate(paras):
        if re.match(r"^`[A-Za-z][\w.]*`\s*$", p):
            data_start = i
            break
    if data_start is None or data_start == 0:
        return []

    header_start = data_start
    while header_start > 0:
        cand = paras[header_start - 1]
        if len(cand) <= 40 and not cand.startswith("*") and not cand.endswith("."):
            header_start -= 1
        else:
            break
    ncols = data_start - header_start
    if ncols < 2:
        return []

    # Split into rows on the code cells rather than chunking by a fixed width. Rows are
    # ragged: the last SpikeArrest runtime row has no Fix cell, so a table of 3 four-wide
    # rows arrives as 11 paragraphs and any fixed-width chunking misaligns every row
    # after the first. A new row begins wherever a backticked code appears.
    body = paras[data_start:]
    rows: list[list[str]] = []
    for p in body:
        if re.match(r"^`[A-Za-z][\w.]*`", p) or rows == []:
            rows.append([p])
        else:
            rows[-1].append(p)
    return rows


def clean(cell: str) -> str:
    cell = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", cell)   # links -> text
    # pandoc escapes angle brackets in some cells as "\<URL\>". Unescape them so the
    # cause text reads cleanly instead of carrying stray backslashes.
    cell = cell.replace("\\<", "<").replace("\\>", ">")
    # google wraps some table cells in markup such as
    # <span sheets-...>steps.javacallout.ExecutionError</span>. A tag that has
    # attributes, or a closing tag, is a wrapper rather than an Apigee element
    # reference, so drop it whole. Leaving the closing tag to the element-name rule
    # below produced the fault code "steps.javacallout.ExecutionErrorspan" and kept a
    # raw <span> in the generated index.
    cell = re.sub(r"<[A-Za-z][A-Za-z0-9_.-]*\s[^>]*>", "", cell)   # tag with attributes
    cell = re.sub(r"</[A-Za-z][A-Za-z0-9_.-]*\s*>", "", cell)      # closing tag
    # Keep a bare element name. Cause text frequently reads "specified in the <Allow>
    # element", and blanking the tag leaves a sentence with a hole in it.
    cell = re.sub(r"<([A-Za-z][A-Za-z0-9_.-]*)>", r"\1", cell)
    cell = re.sub(r"\*\*", "", cell)
    # The same wrapper splits a code span into "` `value`". Merge the broken opener so
    # the value renders as one span instead of one holding a leading space.
    cell = re.sub(r"`\s+`", "`", cell)
    cell = cell.replace("``", "`")
    return re.sub(r"\s+", " ", cell).strip()


def untick(cell: str) -> str:
    """Drop backticks so the caller can re-wrap the value in its own."""
    return clean(cell).replace("`", "").strip()


def truncate(text: str, limit: int = 150) -> str:
    text = clean(text)
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def parse_policy_page(text: str) -> dict | None:
    """Pull runtime and deployment error tables out of one policy page."""
    m = re.search(r"^## Error reference\s*$", text, re.MULTILINE)
    if not m:
        return None

    rest = text[m.end():]
    # Stop at the next top-level section.
    nxt = re.search(r"^## ", rest, re.MULTILINE)
    if nxt:
        rest = rest[: nxt.start()]

    out: dict = {"runtime": [], "deployment": [], "fault_vars": []}

    for kind, key in (("Runtime errors", "runtime"), ("Deployment errors", "deployment")):
        km = re.search(rf"^### {kind}\s*$", rest, re.MULTILINE)
        if not km:
            continue
        block = rest[km.end():]
        nxt3 = re.search(r"^#{2,3} ", block, re.MULTILINE)
        if nxt3:
            block = block[: nxt3.start()]
        out[key] = rows_of(block)

    fv = re.search(r"^### Fault variables\s*$", rest, re.MULTILINE)
    if fv:
        block = rest[fv.end():]
        nxt3 = re.search(r"^#{2,3} ", block, re.MULTILINE)
        if nxt3:
            block = block[: nxt3.start()]
        out["fault_vars"] = rows_of(block)

    return out


def title_of(text: str) -> str:
    m = re.search(r"^#\s+(.*)$", text, re.MULTILINE)
    if not m:
        return ""
    return re.sub(r"<[^>]+>", "", m.group(1)).replace("*", "").strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stdout", action="store_true")
    args = ap.parse_args()

    policies = sorted(PAGES.glob("*.txt"))
    runtime: list[tuple[str, str, str, str]] = []   # code, status, cause, url
    deployment: list[tuple[str, str, str]] = []    # name, cause, url
    fault_vars: list[tuple[str, str, str]] = []    # var, description, url
    empty: list[str] = []                           # pages with a section but no rows

    for p in policies:
        text = p.read_text(encoding="utf-8", errors="replace")
        parsed = parse_policy_page(text)
        if not parsed:
            continue
        url = url_for(p.stem)
        if not url:
            continue
        title = title_of(text) or p.stem

        if not (parsed["runtime"] or parsed["deployment"]):
            # The page documents an error reference but the parser produced nothing.
            # That combination means the table shape changed, not that the page is
            # empty, so record it instead of letting the index look complete.
            empty.append(f"{title}  ({url})")

        for cells in parsed["runtime"]:
            if len(cells) < 2:
                continue
            code = untick(cells[0])
            if not code or ".." in code or code.startswith("*"):
                continue
            status = clean(cells[1]) if len(cells) > 1 else ""
            cause = clean(cells[2]) if len(cells) > 2 else ""
            runtime.append((code, status, cause, url))

        for cells in parsed["deployment"]:
            if not cells:
                continue
            name = untick(cells[0])
            if not name or name.startswith("*"):
                continue
            cause = clean(cells[1]) if len(cells) > 1 else ""
            deployment.append((name, cause, url))

        for cells in parsed["fault_vars"]:
            if len(cells) < 2:
                continue
            var = untick(cells[0])
            if not var or var.startswith("*") or "Where" == var:
                continue
            fault_vars.append((var, clean(cells[1]), url))

    # Dedupe by fault code, keeping the first occurrence.
    def dedupe(rows, key):
        seen, out = set(), []
        for row in rows:
            k = key(row)
            if k in seen:
                continue
            seen.add(k)
            out.append(row)
        return out

    runtime = dedupe(runtime, lambda r: r[0])
    deployment = dedupe(deployment, lambda r: r[0])
    fault_vars = dedupe(fault_vars, lambda r: r[0])

    lines: list[str] = []
    A = lines.append

    A("# Policy fault codes")
    A("")
    A("Mechanically extracted from the `## Error reference` section of each policy page in")
    A("`research/pages/`. Regenerate with `python3 research/build_error_index.py`.")
    A("")
    A("Read this as an index, not as an answer. It tells you which policy owns a code and")
    A("roughly why it fires. Open the policy page before telling someone what happened, because")
    A("the cause text here is truncated.")
    A("")
    A("## Runtime errors, meaning a deployed revision failed while serving a request")
    A("")
    A("| Fault code | HTTP | Cause | Source |")
    A("| --- | --- | --- | --- |")
    for code, status, cause, url in sorted(runtime, key=lambda r: (r[0].split(".")[0], r[0])):
        A(f"| `{code}` | {status} | {truncate(cause, 130)} | [{url.rsplit('/', 1)[-1]}]({url}) |")
    A("")
    A("## Deployment errors, meaning the revision was rejected at upload")
    A("")
    A("These have no HTTP status because no request ever ran. The old revision keeps serving.")
    A("")
    A("| Error name | Cause | Source |")
    A("| --- | --- | --- |")
    for name, cause, url in sorted(deployment):
        A(f"| `{name}` | {truncate(cause, 130)} | [{url.rsplit('/', 1)[-1]}]({url}) |")
    A("")
    A("## Fault variables set when a policy errors")
    A("")
    A("| Variable | Meaning | Source |")
    A("| --- | --- | --- |")
    for var, desc, url in sorted(fault_vars):
        A(f"| `{var}` | {truncate(desc, 130)} | [{url.rsplit('/', 1)[-1]}]({url}) |")
    A("")
    A("## How to use this")
    A("")
    A("1. Take the `errorcode` from the response body, not the `faultstring` prose. Google")
    A("   states the text can change between releases, so matching on it is fragile.")
    A("2. Look the code up above and note which policy owns it.")
    A("3. Open that policy page and read the full cause before proposing a fix.")
    A(f"4. If the code is absent here, the policy page may not have been fetched. Check")
    A(f"   `research/pages/` and re-run `research/fetch.sh` on the policy's doc path.")
    A("")
    A(f"Coverage: {len(runtime)} runtime codes, {len(deployment)} deployment errors, "
      f"{len(fault_vars)} fault variables, from {len(pages := sorted(PAGES.glob('*.txt')))} fetched pages.")
    A("")
    if empty:
        A("## Pages with an error section that parsed to nothing")
        A("")
        A("These pages document an error reference but produced no rows. The usual cause is")
        A("a table shape this extractor does not handle, not an empty section. Each one is")
        A("a gap in the index above, so treat a missing code as possibly a parser gap rather")
        A("than as a code that does not exist.")
        A("")
        for title in sorted(empty):
            A(f"- {title}")
        A("")

    body = "\n".join(lines)
    if args.stdout:
        print(body)
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(body, encoding="utf-8")
    print(f"wrote {OUT}")
    print(f"  {len(runtime)} runtime codes, {len(deployment)} deployment errors, {len(fault_vars)} fault variables")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())