#!/usr/bin/env python3
"""Convert leftover HTML tables in research/pages/*.txt into Markdown tables.

Why this exists. pandoc does not always convert every table on these pages. On the pages
where it gives up, the extracted file keeps a raw <table> block: the text is all there,
but the row structure is HTML. Any tool that parses pipe tables, including
build_error_index.py, silently sees nothing in those regions and under-reports.

That failure is invisible. The page looks fetched, the content looks present, and the
index is simply missing rows. This script converts the leftovers so the extraction is
complete, and reports what it changed so the size of the gap is on the record.

Safe to re-run: it is a no-op on files with no HTML tables.

Usage:
    python3 research/normalize_pages.py          # rewrite pages in place
    python3 research/normalize_pages.py --dry    # report only
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("beautifulsoup4 is required: pip install beautifulsoup4", file=sys.stderr)
    raise SystemExit(2)

PAGES = Path(__file__).parent / "pages"


def cell_text(node) -> str:
    text = node.get_text(" ", strip=True)
    text = re.sub(r"\s+", " ", text)
    # Pipes would break the Markdown row, so escape rather than drop.
    return text.replace("|", "\\|")


def html_table_to_md(table_html: str) -> str | None:
    soup = BeautifulSoup(table_html, "html.parser")
    rows = []
    for tr in soup.find_all("tr"):
        cells = tr.find_all(["th", "td"])
        if not cells:
            continue
        rows.append([cell_text(c) for c in cells])

    if len(rows) < 2:
        return None

    width = max(len(r) for r in rows)
    if width < 2:
        return None
    rows = [r + [""] * (width - len(r)) for r in rows]

    header, body = rows[0], rows[1:]
    if not any(h.strip() for h in header):
        header, body = body[0], body[1:] if body else []
        if not body:
            return None

    out = ["| " + " | ".join(header) + " |",
           "| " + " | ".join("---" for _ in header) + " |"]
    for r in body:
        out.append("| " + " | ".join(r) + " |")
    return "\n".join(out)


def convert(text: str) -> tuple[str, int]:
    count = 0

    def repl(m: re.Match) -> str:
        nonlocal count
        md = html_table_to_md(m.group(0))
        if md is None:
            return m.group(0)
        count += 1
        return md

    # Non-greedy so a run of sibling tables does not merge into one.
    out = re.sub(r"<table\b.*?</table>", repl, text, flags=re.DOTALL | re.IGNORECASE)

    # Drop the scaffolding pandoc left behind, now that the data is Markdown.
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out, count


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--quiet", action="store_true",
                    help="normalise specific files passed as arguments, report nothing")
    ap.add_argument("files", nargs="*", help="specific page files to normalise")
    args = ap.parse_args()

    if args.files:
        changed = []
        total_tables = 0
        for name in args.files:
            path = Path(name)
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if not re.search(r"<table\b", text, re.IGNORECASE):
                continue
            new, n = convert(text)
            if n and new != text:
                total_tables += n
                path.write_text(new, encoding="utf-8")
                changed.append(path.name)
        if not args.quiet:
            print(f"normalised {total_tables} tables in {len(changed)} file(s)")
        return 0

    changed = []
    total_tables = 0

    for p in sorted(PAGES.glob("*.txt")):
        text = p.read_text(encoding="utf-8", errors="replace")
        if not re.search(r"<table\b", text, re.IGNORECASE):
            continue
        new, n = convert(text)
        if n and new != text:
            total_tables += n
            changed.append((p.name, n))
            if not args.dry:
                p.write_text(new, encoding="utf-8")

    print(f"converted {total_tables} HTML tables across {len(changed)} pages")
    if args.dry:
        print("(dry run, nothing written)")
    else:
        print("files updated")

    # Report what is still HTML, so a remaining gap is visible rather than assumed.
    residual = []
    for p in sorted(PAGES.glob("*.txt")):
        text = p.read_text(encoding="utf-8", errors="replace")
        n = len(re.findall(r"<table\b", text, re.IGNORECASE))
        if n:
            residual.append((p.name, n))
    if residual:
        print(f"\n{len(residual)} pages still contain raw HTML tables:")
        for name, n in residual[:15]:
            print(f"  {n:3d}  {name}")
        if len(residual) > 15:
            print(f"  ... and {len(residual) - 15} more")
    else:
        print("no raw HTML tables remain")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())