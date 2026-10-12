#!/usr/bin/env python3
"""Split the official Apigee known-issues register into one record per issue.

The register renders as a devsite table that pandoc flattens to:
    <9-digit issue id>\n\n<affects cell>\n\n<status cell>\n\n**<bolded summary>**\n\n<body>
Issue IDs are the only lines that are exactly nine digits, so they are a reliable
anchor. Everything between two anchors belongs to the earlier anchor.

The status cell is the only line carrying the devsite colour spans, so it is detected
by that rather than by position: several rows put "Apigee" in the affects column and
nothing else, and several put no product filter at all.

Usage: python3 research/parse_knownissues.py [page.txt]
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAGE = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "pages" / "ki-live-20261012.txt"
OUT = HERE / "ki-entries.json"

STATUS_RE = re.compile(r"color:#[0-9a-f]{6}[^>]*>\s*(OPEN|FIXED|WONTFIX|WONT FIX|NOT FIXED|COMPLETE|DONE)", re.I)
PRODUCTS = ("Apigee", "hybrid", "UI", "Monetization", "Integrated portal",
            "Archive deployments", "API hub", "Connectors", "Documentation",
            "API Monitoring", "Apigee in VS Code", "Apigee Emulator")


def strip_html(s: str) -> str:
    s = re.sub(r"<br\s*/?>", "; ", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("**", "")
    return re.sub(r"[ \t]+", " ", s).strip()


text = PAGE.read_text(encoding="utf-8", errors="replace")
lines = text.splitlines()

ID_RE = re.compile(r"^(\d{9})\s*$")
anchors = [(i, ID_RE.match(l).group(1)) for i, l in enumerate(lines) if ID_RE.match(l)]
if len(anchors) != len({a[1] for a in anchors}):
    raise SystemExit("duplicate anchors, aborting")

entries = []
for n, (idx, iid) in enumerate(anchors):
    end = anchors[n + 1][0] if n + 1 < len(anchors) else len(lines)
    chunk = [l for l in lines[idx + 1:end]]
    # The header row plus a handful of preamble lines repeat before the first entry.
    while chunk and not chunk[0].strip():
        chunk.pop(0)

    # Status line: the line carrying a colour span with a state word. The window has to be
    # wider than one line: merged rows stack a product label, a version list and THEN the
    # status chip, so a 1-line lookahead misses the chip and treats "**FIXED**" as prose.
    status, status_line_no = "", None
    for i, l in enumerate(chunk[:8]):
        m = STATUS_RE.search(l)
        if m:
            status = m.group(1).upper()
            plain = strip_html(l)
            m2 = re.search(r"\bIN\s+(.+)$", plain, re.I)
            if m2:
                status += " in " + m2.group(1).strip()
            status_line_no = i
            break
    if status_line_no is None:
        status_line_no = 0

    # Affects: lines before the status line, excluding the header row remnants.
    affects_lines = chunk[:status_line_no] if status_line_no is not None else chunk[:1]
    affects = "; ".join(filter(None, (strip_html(l) for l in affects_lines)))
    if affects in ("Affects", "Status", "Description", "Issue ID"):
        affects = ""
    for junk in ("Issue ID", "Affects", "Status", "Description"):
        affects = affects.replace(junk, "").strip(" ;,")

    body_lines = chunk[status_line_no + 1:] if status_line_no is not None else chunk
    while body_lines and not body_lines[0].strip():
        body_lines.pop(0)

    summary = strip_html(body_lines[0]) if body_lines else ""
    # Merged rows put a bare product label or version list in the description cell before
    # the real text. Skip those lines, but never skip a bolded line: strip_html removes
    # the asterisks, so a bolded "**FIXED**" would otherwise be mistaken for noise and the
    # loop would eat the actual issue summary as well.
    NOISE = re.compile(r"^(Apigee|hybrid|UI|Monetization|All|Integrated portal|"
                       r"Apigee in VS Code|Apigee Emulator|N/?A)?\s*"
                       r"([\d.]+[\w.-]*(\s*[,;]\s*[\d.]+[\w.-]*)*)?$", re.I)
    while body_lines:
        raw = body_lines[0]
        txt = strip_html(raw)
        if not txt:
            body_lines.pop(0)
            continue
        if "**" in raw or not NOISE.match(txt) or len(txt) >= 120:
            break
        body_lines.pop(0)
    summary = strip_html(body_lines[0]) if body_lines else ""
    body = "\n".join(body_lines).strip()

    product = ""
    blob = f"{affects} {summary}"
    if "Emulator" in blob:
        product = "Apigee Emulator"
    elif "Private Cloud" in blob:
        product = "Apigee Edge for Private Cloud"
    elif re.search(r"\bhybrid\b", affects, re.I):
        product = "Apigee hybrid (+Apigee)"
    elif any(p in affects for p in ("Monetization", "Integrated portal", "UI", "VS Code")):
        product = affects
    elif "Apigee" in affects:
        product = "Apigee"
    elif "All" in affects:
        product = "All Apigee products"

    entries.append({
        "id": iid,
        "product": product,
        "affects": affects,
        "status": status,
        "open": "OPEN" in status.upper(),
        "summary": summary,
        "body": body,
        "has_workaround": bool(re.search(r"\*{0,2}Workaround", body, re.I)),
        "has_fix": bool(re.search(r"\*{0,2}Fix", body, re.I)),
        "has_cause": bool(re.search(r"[Rr]oot cause", body)),
        "fault_codes": sorted(set(re.findall(r'"errorcode"\s*:\s*"([^"]+)"', body))),
        "backticked": sorted(set(re.findall(r"`([^`\n]{2,70})`", body))),
        "chars": len(body),
    })

OUT.write_text(json.dumps(entries, indent=1), encoding="utf-8")
print(f"{len(entries)} entries -> {OUT}")
print(f"open={sum(e['open'] for e in entries)} fixed={sum(not e['open'] for e in entries)}")
from collections import Counter
print(Counter(e["product"] for e in entries).most_common())
