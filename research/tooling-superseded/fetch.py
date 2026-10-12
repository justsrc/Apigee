#!/usr/bin/env python3
"""fetch.py <url> [outfile] -- print HTTP status, save html, print extracted main text."""
import sys, os, re, subprocess, html
from html.parser import HTMLParser

url = sys.argv[1]
out = sys.argv[2] if len(sys.argv) > 2 else None

status = subprocess.run(
    ["curl", "-sL", "-o", "/tmp/_f.html", "-w", "%{http_code}", url],
    capture_output=True, text=True).stdout.strip()
print(f"### STATUS {status}  {url}")

if status != "200":
    sys.exit(0)

data = open("/tmp/_f.html", encoding="utf-8", errors="replace").read()
if out:
    open(out, "w", encoding="utf-8").write(data)

class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = 0
        self.buf = []
        self.links = []
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "svg", "nav", "head"):
            self.skip += 1
        if tag == "a":
            href = dict(attrs).get("href", "")
            if href:
                self.links.append(href)
        if tag in ("p", "div", "li", "tr", "h1", "h2", "h3", "h4", "pre", "br", "td", "th"):
            self.buf.append("\n")
        if tag == "code" or tag == "pre":
            self.buf.append("\n```\n")
    def handle_endtag(self, tag):
        if tag in ("script", "style", "svg", "nav", "head"):
            self.skip = max(0, self.skip - 1)
        if tag in ("code", "pre"):
            self.buf.append("\n```\n")
    def handle_data(self, d):
        if not self.skip:
            self.buf.append(d)

p = P()
p.feed(data)
text = "".join(p.buf)
text = re.sub(r"[ \t]+", " ", text)
text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
text = "\n".join(l.strip() for l in text.split("\n"))
sys.stdout.write(text)

# also dump discovered links
seen = set()
with open("/tmp/_links.txt", "w") as fh:
    for h in p.links:
        if h not in seen:
            seen.add(h)
            fh.write(h + "\n")