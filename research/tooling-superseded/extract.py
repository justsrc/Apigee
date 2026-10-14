#!/usr/bin/env python3
"""Reliable article-body extractor for cloud.google.com Apigee doc pages.

WHY THIS EXISTS
---------------
fetch.sh pipes raw HTML through `pandoc -f html`. Google doc pages contain
UNBALANCED markup (observed: `<table>` opened twice, closed once, in
assign-message-policy). pandoc's HTML reader silently drops everything after
the malformed region. Result: a page that returns HTTP 200 still yields a
Markdown file that is silently missing its `## Error reference` section, its
element tables, and its restrictions.

Verification: compare the number of <h2>/<h3> headings present in the raw HTML
against the number present in the pandoc output. A mismatch means truncation.

This script instead:
  1. parses with lxml (auto-closes malformed tags per HTML5 rules),
  2. isolates <div class="devsite-article-body">,
  3. re-serialises well-formed HTML,
  4. hands THAT to pandoc so element tables survive as Markdown tables,
  5. asserts the heading count is preserved.

Usage: extract.py <html-file> [out-name]
Prints: STATUS<TAB>BYTES<TAB>HEADINGS_IN<TAB>HEADINGS_OUT<TAB>NAME
Exits 1 if headings were lost.
"""
import sys
import subprocess
import pathlib

from bs4 import BeautifulSoup
from bs4.element import Tag

HERE = pathlib.Path(__file__).resolve().parent


def headings(soup: Tag) -> int:
    return len(soup.find_all(["h1", "h2", "h3", "h4"]))


def main() -> int:
    src = pathlib.Path(sys.argv[1])
    name = sys.argv[2] if len(sys.argv) > 2 else src.stem
    html = src.read_text(encoding="utf-8", errors="replace")

    soup = BeautifulSoup(html, "lxml")

    body = soup.find("div", class_="devsite-article-body")
    if not isinstance(body, Tag):
        body = soup
    in_h = headings(body)

    # The page <h1> lives OUTSIDE devsite-article-body, so pull the title in
    # explicitly; otherwise the Markdown starts with "##" and nothing anchors it.
    h1 = soup.find("h1")
    title = h1.get_text(" ", strip=True) if isinstance(h1, Tag) else name

    # Drop chrome that never belongs in the article text.
    # NOTE: <aside> is deliberately KEPT. Google doc pages put load-bearing
    # content in <aside class="note|key-point|bestpractice|warning"> -- e.g. the
    # AssignMessage "<Path> (child of <Set>)" section has NO body text outside
    # its aside, and the aside is the only place that explains rewriting
    # target.url. Dropping asides silently deletes documented behaviour.
    for tag in body.find_all(["script", "style", "nav", "form", "button"]):
        tag.decompose()

    clean = body.decode_contents()

    md = subprocess.run(
        ["pandoc", "-f", "html", "-t", "gfm", "--wrap=none"],
        input=clean,
        capture_output=True,
        text=True,
    ).stdout

    # Keep from the page title (H1) to the licence footer.
    lines = [f"# {title}", ""]
    for line in md.splitlines():
        if (
            "Except as otherwise noted, the content of this page is licensed" in line
        ):
            break
        lines.append(line)
    md = "\n".join(lines).rstrip() + "\n"

    out_h = sum(1 for line in md.splitlines() if line.startswith("#")) - 1  # -1: injected title

    _ = (HERE / "pages" / f"{name}.txt").write_text(md, encoding="utf-8")

    ok = out_h >= in_h
    print(f"\t{len(md.encode())}\t{in_h}\t{out_h}\t{name}\t{'OK' if ok else 'TRUNCATED'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())