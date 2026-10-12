#!/usr/bin/env python3
"""Screen the parsed known-issues register for scenario-shaped entries.

Scores each entry against the traits that make a good evaluation scenario: a
limitation rather than a bug, two-factor causation, a fix that introduced a
regression, version-gated behaviour, a silent failure, or a fault that gets
attributed to the wrong component. The scoring is deliberately crude; it only
decides what a human reads in full.
"""
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
entries = json.loads((HERE / "ki-entries.json").read_text())

USED = {"465834046", "479872706", "543171828", "471125841"}

TRAITS = {
    "limitation": re.compile(
        r"\bby design|working as (intended|designed|expected)|expected behavior|"
        r"expected behaviour|documented behaviou?r|not supported|unsupported|"
        r"does not support|no support for|limitation|intentional|by design decision|"
        r"this is (expected|normal)|are expected to|is not a bug|cannot be changed|"
        r"is expected\b|standard behaviou?r|is a known behaviou?r", re.I),
    "two_factor": re.compile(
        r"\bboth\b.{0,60}\band\b|\bone or more\b|only (if|when) .{0,60}\band\b|"
        r"either .{0,60}\bor\b.{0,60}\bbut not\b|combination of|interact(s|ion) between|"
        r"plus .{0,40}\bwhen\b|depends on whether", re.I),
    "fix_caused": re.compile(
        r"fix (introduced|caused|causes|activated|triggered)|regression|"
        r"introduced (by|a) (the )?(fix|change)|now (correctly )?(takes effect|applies)|"
        r"previous(ly)? ignored|fix is not available until|after the fix|"
        r"correct behaviou?r (now )?(takes|had) effect", re.I),
    "version_gated": re.compile(
        r"fresh(ly)? install|new(ly)? (install|cluster|installations)|"
        r"upgrade(d)? (from|path)|clusters? (that )?(were|was) (upgraded|installed)|"
        r"only (affect|occur|apply)[s]? (upgraded|existing)|existing (cluster|install)|"
        r"first (install|installation)|carried over|migration", re.I),
    "silent": re.compile(
        r"\bsilent(ly)?\b|no (error|errors|exception|failure) (is|are|was|were) (returned|raised|logged)|"
        r"nothing (is )?(logged|reported|raised)|without (any )?error|"
        r"stops? (working|receiving)|simply stops?|no error message|no error is|"
        r"does not (report|surface|indicate)|fails? silently|appears? (to|successful)", re.I),
    "wrong_component": re.compile(
        r"may (be|mistakenly be) (mis)?(diagnos|attribut|blam|interpret)|"
        r"often (mis)?(attributed|blamed|mistaken)|look(s|ing)? like|"
        r"resembl\w+ .{0,40}(error|failure)|appears to be|misleading|"
        r"confus\w+ with|mistaken for|can be confused", re.I),
    "wrong_evidence": re.compile(
        r"check(ing)? .{0,50}(shows|reports) .{0,40}(correct|none|no )|"
        r"reports .{0,20}(success|healthy|nominal)|but .{0,40}(fail|not|stale|old)|"
        r"even though|despite (the|having)|shows no|reports no", re.I),
}

scored = []
for e in entries:
    blob = f"{e['summary']}\n{e['body']}"
    hits = {k: len(p.findall(blob)) for k, p in TRAITS.items()}
    traits = [k for k, v in hits.items() if v]
    score = sum(min(v, 3) for v in hits.values()) + (2 if not e["open"] else 0)
    e2 = dict(e, traits=traits, hits=hits, score=score, used=e["id"] in USED)
    scored.append(e2)

scored.sort(key=lambda x: (-x["score"], x["id"]))
print(f"{'ID':>10} {'sc':>3} {'op':>3}  traits")
for e in scored:
    mark = "*" if e["used"] else " "
    print(f"{e['id']:>10} {e['score']:>3} {'O' if e['open'] else 'f':>3}{mark} "
          f"{','.join(e['traits'])[:46]:46} {e['affects'][:22]:22} {e['summary'][:70]}")

print("\ntrait totals:", Counter(t for e in scored for t in e["traits"]).most_common())
(HERE / "ki-scored.json").write_text(json.dumps(scored, indent=1))
