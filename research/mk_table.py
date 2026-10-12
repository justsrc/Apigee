#!/usr/bin/env python3
"""Emit the register table as Markdown rows with every field the brief asks for."""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
E = json.loads((HERE / "ki-entries.json").read_text())
USED = {"465834046", "479872706", "543171828", "471125841"}

# A LIMITATION is documented design behaviour that stays true after the entry closes.
# A BUG is something that was fixed. The register's own wording is the tell: "does not
# support", "by design", "is expected", "harmless", "not enforced" describe design;
# "regression", "will fail", "crash", "stuck" describe defects.
LIMIT_PAT = re.compile(
    r"does not support|does not validate|not supported by|is not supported|"
    r"by design|current design|no known workaround|is expected to|"
    r"this is expected|harmless condition|does not indicate any risk|"
    r"enforcing a temporary limit|are limited to|is limited to \d+|"
    r"will not support|does not function as expected|"
    r"security requirements are not enforced|"
    r"only supports TLS|are expected", re.I)
BUG_PAT = re.compile(
    r"regression|will fail|crash.?loop|stuck|not honored|not honoured|"
    r"times? out|fails? with|error|wedge|race condition|leak|"
    r"not scheduled|not created|does not complete|incompatible|"
    r"impossible to|broken", re.I)


def clean(s, n=260):
    s = re.sub(r"\n<div>\s*\n</div>\n", " ", s)
    s = re.sub(r"``` devsite-[a-z-]+\n", " ", s)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    s = s.replace("**", "").replace("`", "")
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"^[A-Z][^:]{0,40}:\s*", "", s)  # drop merged-row header residue
    return s if len(s) <= n else s[:n - 1].rstrip() + "…"


def kind(e):
    b = f"{e['summary']} {e['body']}"
    fixed = re.search(r"FIXED", e["status"], re.I)
    lim, bug = LIMIT_PAT.search(b), BUG_PAT.search(b)
    if lim and not bug:
        return "LIMITATION"
    if lim and bug:
        return "LIMITATION*"   # design statement carrying an operational symptom
    return "BUG"


def resolution(e):
    b = e["body"]
    if e["open"]:
        return "none published; issue still OPEN"
    if e["has_workaround"]:
        return f"workaround published; {e['status'] or 'FIXED'}"
    return f"{e['status'] or 'FIXED'}; no workaround published"


for e in sorted(E, key=lambda x: -int(x["id"])):
    status = e["status"] or "FIXED"
    k = kind(e)
    if k == "LIMITATION*":
        k = "LIMITATION+symptom"
    print(f"| {e['id']} | {e['product']} | {clean(e['affects'], 90)} | "
          f"{status}; {'OPEN' if e['open'] else 'closed'} | **{k}** | "
          f"{clean(e['summary'], 210)} | {clean(resolution(e), 90)} | "
          f"{'used' if e['id'] in USED else 'NEW'} |")
