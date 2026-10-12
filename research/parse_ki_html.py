#!/usr/bin/env python3
"""Parse the known-issues register straight out of the page HTML.

Traps this exists to avoid, both of which silently shrink the register with no error:

1. A non-greedy `<table ...>.*?</table>` stops at the FIRST `</table>`, and this page has
   tables nested inside register description cells. Taking the first match yields 71 of
   102 issues. Row extraction is therefore a single forward depth-aware scan.
2. The register is not one table per product. It is one table, and the product filter is
   a client-side control over the same rows.

Row boundaries come from explicit <tr>/<td>. Continuation rows (no ID cell) belong to the
issue above them. A fresh `Issue ID` header row resets the current issue, which stops
unrelated tables further down the page being absorbed into a register entry.
"""
import html
import json
import re
import sys
from pathlib import Path

RAW = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/ki_raw.html")
HERE = Path(__file__).resolve().parent
OUT = HERE / "ki-entries-html.json"

doc = RAW.read_text(encoding="utf-8", errors="replace")
ID_RE = re.compile(r"^\s*(\d{9})\s*$")
TOKEN_RE = re.compile(r"<(/?)(tr|t[dh])\b[^>]*?(/?)>", re.I)


def iter_rows(text: str):
    """Yield (start, end) of every paired <tr>...</tr>, nesting-aware, one forward pass.

    Uses a stack rather than a depth counter. The page has 133 <tr> opens and 131
    </tr> closes, so a depth counter is left permanently non-zero and silently stops
    emitting rows partway down. Popping a stack pairs each close with its own open and
    discards the unpaired opens on their own.
    """
    stack = []
    for m in TOKEN_RE.finditer(text):
        if m.group(2).lower() != "tr" or m.group(3) == "/":
            continue
        if m.group(1):
            if stack:
                yield stack.pop(), m.start()
        else:
            stack.append(m.end())
    return


def cell_text(cell: str) -> str:
    s = re.sub(r"<br\s*/?>", "\n", cell)
    s = re.sub(r"</(p|li|h\d|tr|div|pre)>", "\n", s)
    s = re.sub(r"<li[^>]*>", "\n- ", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t]+", " ", s)
    return re.sub(r"\n{3,}", "\n\n", s).strip()


def split_cells(inner: str):
    """Split a <tr>'s inner HTML into cell texts by <td>/<th> open-tag position.

    Do NOT pair `<td>` with `</td>` non-greedily. Issue 421402073's affects cell is
    emitted as `<td>Apigee in VS Code` with no closing tag at all, so a pairing regex
    silently swallows that cell and the following one and the row lands with three
    cells instead of four. Splitting on open-tag positions is immune to that.
    """
    opens = list(re.finditer(r"<t[dh]\b[^>]*>", inner, re.I))
    out = []
    for i, m in enumerate(opens):
        stop = opens[i + 1].start() if i + 1 < len(opens) else len(inner)
        out.append(cell_text(inner[m.end():stop]))
    return out
    s = re.sub(r"<br\s*/?>", "\n", cell)
    s = re.sub(r"</(p|li|h\d|tr|div|pre)>", "\n", s)
    s = re.sub(r"<li[^>]*>", "\n- ", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t]+", " ", s)
    return re.sub(r"\n{3,}", "\n\n", s).strip()


merged, current = [], None
nrows = 0
for start, end in iter_rows(doc):
    nrows += 1
    inner = doc[start:end]
    cells = split_cells(inner)
    if len(cells) < 4:
        continue
    c = [cell_text(x) for x in cells]
    if c[0].strip().lower().startswith("issue id"):
        current = None
        continue
    m = ID_RE.match(c[0])
    if m:
        current = {"id": m.group(1), "affects": c[1], "status": c[2],
                   "description": c[3], "rows": 1}
        merged.append(current)
    elif current is not None:
        current["rows"] += 1
        for k, v in zip(("affects", "status", "description"), c[1:4]):
            v = v.strip()
            if v and v not in current[k]:
                current[k] = f"{current[k]}\n{v}".strip() if current[k] else v

flat = [e["id"] for e in json.loads((HERE / "ki-entries.json").read_text())]
got = [e["id"] for e in merged]
print(f"rows scanned: {nrows}   register issues: {len(got)}   flattened text: {len(flat)}")
print(f"duplicates in HTML parse: {sorted({i for i in got if got.count(i) > 1})}")
print(f"in flattened text only: {sorted(set(flat) - set(got))}")
print(f"in HTML only           : {sorted(set(got) - set(flat))}")
multi = [e["id"] for e in merged if e["rows"] > 1]
print(f"issues spanning >1 row ({len(multi)}): {multi}")

OUT.write_text(json.dumps(merged, indent=1), encoding="utf-8")
print(f"-> {OUT}")
