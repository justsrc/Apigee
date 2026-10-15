#!/usr/bin/env python3
"""Classify every URL cited in the skills, references and scenarios.

The previous checker was a two-line shell script: fetch, look at the status, grep the body
for one phrase. It worked against the specific failures it was written for, and it could
not distinguish the cases it was supposed to distinguish. A 403 from a bot-blocking host
is reported as BROKEN. A timeout is reported as BROKEN. A redirect is followed silently,
so a citation that has moved and whose new location says something else is reported OK.
And a corpus containing zero URLs exits 0, which is a passing URL audit that verified
nothing.

This version classifies rather than guesses. Each URL gets exactly one status:

    VERIFIED                 200 and the body is the document that was cited
    REDIRECTED_AND_VERIFIED  3xx chain resolved and the final document matches
    SOFT_404                 200 but the body is Google's "does not exist" stub
    NOT_FOUND                404 or 410 from the origin
    ACCESS_RESTRICTED        401/403: the resource exists, robots are blocking the fetch
    RATE_LIMITED             429, or a captcha/interstitial page
    TRANSIENT_FAILURE        timeout, DNS, TLS, 5xx, connection reset
    INVALID_URL              malformed, or a scheme this tool will not fetch
    CONTENT_MISMATCH         200, real page, but it is not the document that was cited
    UNVERIFIED               nothing conclusive; needs a human

The distinction that matters most is the one the old script could not make. A citation
that resolves to a different page is not a passing citation. cloud.google.com will happily
return 200 with the wrong article, and so will a redirect to a renamed section.

Content matching is the weak point and is treated as such. A match on the final path
segment plus the page <title> is a reasonable signal, not proof, so CONTENT_MISMATCH is a
finding for a human rather than a silent pass, and the evidence is kept.

Fixtures make the behaviour testable without a network. --fixtures runs the classifier over
recorded responses with known answers, including the soft-404 stub, so a change to the
detection logic that loses the ability to spot a soft 404 fails the suite instead of
quietly passing every live fetch.

Usage:
    python3 tests/check_urls.py                 # audit the live corpus
    python3 tests/check_urls.py --targets scenarios README.md
    python3 tests/check_urls.py --fixtures      # offline, deterministic
    python3 tests/check_urls.py --json          # machine-readable
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import re
import subprocess
import sys
import time
from collections import Counter
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Protocol, TypedDict, cast
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parent.parent

DEFAULT_TARGETS = [".agents/skills", "scenarios", "README.md", "CHANGELOG.md"]

# Statuses that mean "the citation is broken" or "we could not confirm it".
FAILING = {
    "SOFT_404", "NOT_FOUND", "INVALID_URL", "CONTENT_MISMATCH", "UNVERIFIED",
}
# Statuses that are neither a pass nor a defect: an environment problem, reported as such.
ENVIRONMENTAL = {"ACCESS_RESTRICTED", "RATE_LIMITED", "TRANSIENT_FAILURE"}

# No custom User-Agent. curl's default is what the previous checker used and it reached
# every page. A "Mozilla/5.0 (compatible; ...)" string is exactly the shape Google's bot
# detection looks for, and setting one made 154 valid citations return an interstitial.
# Identified by running the audit, not by reading this file.
TIMEOUT = 25
RETRIES = 2
RETRY_SLEEP = 2.0

# Placeholder URLs are illustrative paths, not citations. These are real documented API
# paths with the identifiers substituted, so fetching them un-substituted returns 401 and
# tells us nothing about whether the endpoint exists.
PLACEHOLDER_RE = re.compile(
    r"[<>{}]|\$[A-Z_]+|YOUR_[A-Z_]+|<host>|\bORG_NAME\b|%[A-Z_]+%")

SOFT_404_MARKERS = (
    "equivalent page does not exist in apigee",
    "the equivalent page does not exist",
    "page not found",
)
# Interstitial detection has to key on prose that only appears on a block page. The
# first version matched the bare word "captcha", which appears in Google's own
# feature-flag blobs on perfectly normal documentation pages, and classified 154 of 168
# valid citations as rate-limited. Every marker here is a phrase no article body contains.
RATELIMIT_MARKERS = (
    "our systems have detected unusual traffic",
    "detected unusual traffic from your computer network",
    "please complete the following captcha",
    "before you continue to google cloud",
    "to continue, please type the characters",
)


@dataclass
class Result:
    url: str
    status: str
    detail: str = ""
    http: int | None = None
    chain: list[str] = field(default_factory=list)
    title: str = ""
    occurrences: int = 1
    evidence: str = ""


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def strip_fences(text: str) -> str:
    """Remove fenced code blocks.

    A citation lives in prose. A URL inside a code sample is part of a string literal, and
    extracting it produced a citation with a trailing apostrophe that broke the fetch.
    """
    out: list[str] = []
    fenced = False
    for line in text.splitlines():
        if re.match(r"^\s*(```|~~~)", line):
            fenced = not fenced
            continue
        if not fenced:
            out.append(line)
    return "\n".join(out)


URL_RE = re.compile(r"https?://[^\s\)\]\"'`>]+")


def discover(targets: list[str]) -> tuple[list[str], Counter[str]]:
    """Return (sorted unique URLs, per-URL occurrence counts)."""
    chunks: list[str] = []
    for t in targets:
        p = ROOT / t
        if p.is_dir():
            for md in sorted(p.rglob("*.md")):
                chunks.append(strip_fences(md.read_text(encoding="utf-8",
                                                         errors="replace")))
        elif p.is_file():
            chunks.append(strip_fences(p.read_text(encoding="utf-8", errors="replace")))
        else:
            print(f"WARNING target does not exist, nothing read from it: {t}",
                  file=sys.stderr)

    counts: Counter[str] = Counter()
    for chunk in chunks:
        for raw in cast(list[str], URL_RE.findall(chunk)):
            url = raw.rstrip("'\".,;")
            if PLACEHOLDER_RE.search(url):
                continue
            counts[url] += 1
    return sorted(counts), counts


# ---------------------------------------------------------------------------
# Fetch
# ---------------------------------------------------------------------------


def fetch_with_redirect_chain(url: str) -> tuple[int | None, str, list[str]]:
    """Fetch while recording every hop, so a moved citation keeps its evidence."""
    import tempfile
    chain: list[str] = []
    current = url
    for _ in range(6):
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as fh:
            body_path = fh.name
        try:
            proc = subprocess.run(
                ["curl", "-s", "-o", body_path,
                 "-w", "%{http_code}\t%{redirect_url}",
                 "--max-time", str(TIMEOUT), current],
                capture_output=True, text=True, timeout=TIMEOUT + 10,
            )
            parts = (proc.stdout or "").strip().split("\t")
            # curl writes 000 when it never got a response at all: DNS failure, refused
            # connection, TLS abort, timeout. Treating that as "HTTP 0" let it fall
            # through to UNVERIFIED instead of TRANSIENT_FAILURE, so a flaky read was
            # reported as an unconfirmable citation rather than something to retry. One
            # GitHub issue was reported UNVERIFIED on a URL that returns 200.
            code = None
            if parts and parts[0].isdigit() and int(parts[0]) > 0:
                code = int(parts[0])
            nxt = parts[1] if len(parts) > 1 else ""
            try:
                body = Path(body_path).read_text(encoding="utf-8", errors="replace")
            except OSError:
                body = ""
            if nxt and nxt != current:
                chain.append(nxt)
                current = nxt
                continue
            return code, body, chain
        except subprocess.TimeoutExpired:
            return None, "", chain
        except Exception:
            return None, "", chain
        finally:
            try:
                Path(body_path).unlink()
            except OSError:
                pass
    return None, "", chain


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------


def page_title(body: str) -> str:
    m = re.search(r"<title[^>]*>(.*?)</title>", body, re.S | re.I)
    if not m:
        return ""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1))).strip()


def is_soft_404(body: str) -> bool:
    # Use every marker declared in SOFT_404_MARKERS rather than a handful of
    # hard-coded phrases, so a body carrying any declared soft-404 marker is
    # recognised (including Google's "page not found" stub).
    low = body.lower()
    return any(marker.lower() in low for marker in SOFT_404_MARKERS)


def expected_slug(url: str) -> str:
    path = urlsplit(url).path
    tail = [s for s in path.split("/") if s]
    return unquote(tail[-1]) if tail else ""


def slug_appears(body: str, slug: str) -> bool:
    # An empty slug matches nothing: it must not be treated as "present in any
    # body", otherwise a root URL with arbitrary content would verify.
    if not slug:
        return False
    needle = re.escape(slug.lower())
    return bool(re.search(needle, body.lower()))


def classify(url: str, code: int | None, body: str, chain: list[str]) -> Result:
    """Assign exactly one status. The order matters: soft-404 before content mismatch."""
    # Defend here as well as in the fetcher. curl reports 000 for "no response at all",
    # and if that reaches this function as 0 it must be treated as no response rather
    # than as an uninterpretable HTTP status. Pinned by the "curl-zero-no-response" fixture.
    if code is not None and code <= 0:
        code = None

    res = Result(url=url, status="UNVERIFIED", chain=chain, http=code)
    res.title = page_title(body)

    if not urlsplit(url).netloc or urlsplit(url).scheme not in ("http", "https"):
        res.status = "INVALID_URL"
        res.detail = "not an absolute http(s) URL"
        return res

    if code is None:
        # curl wrote nothing usable: timeout, DNS, TLS, or a refused connection.
        res.status = "TRANSIENT_FAILURE"
        res.detail = "no response: timeout, DNS, TLS or connection failure"
        return res

    if code in (404, 410):
        res.status = "NOT_FOUND"
        res.detail = f"HTTP {code} from the origin"
        return res

    if code == 429:
        res.status = "RATE_LIMITED"
        res.detail = "HTTP 429"
        return res

    if code in (401, 403):
        res.status = "ACCESS_RESTRICTED"
        res.detail = f"HTTP {code}: the origin refused the fetch, which is not evidence "\
                     + "the document is missing"
        return res

    if code >= 500:
        res.status = "TRANSIENT_FAILURE"
        res.detail = f"HTTP {code}"
        return res

    if 200 <= code < 300:
        low = body.lower()
        if any(m in low for m in RATELIMIT_MARKERS):
            res.status = "RATE_LIMITED"
            res.detail = "body is an interstitial or captcha page, not the document"
            res.evidence = res.title[:120]
            return res
        if is_soft_404(body):
            res.status = "SOFT_404"
            res.detail = "HTTP 200 with Google's 'equivalent page does not exist' body"
            res.evidence = res.title[:120]
            return res
        if not body.strip():
            res.status = "TRANSIENT_FAILURE"
            res.detail = "HTTP 200 with an empty body"
            return res

        # Match the slug of the URL we actually landed on, not the one we asked for.
        # Checking the original slug after a redirect reported every moved citation as a
        # mismatch, because the original slug naturally does not appear on the
        # replacement page. The fixture "redirect-to-replacement" is what caught it.
        landed = chain[-1] if chain else url
        slug = expected_slug(landed)
        if not slug:
            # A URL with no path tail has nothing to match against the body, so it
            # cannot be content-verified by this tool's slug signal.
            res.status = "UNVERIFIED"
            res.detail = "HTTP 200 but the URL has no path slug to match against the body"
            res.evidence = res.title[:120]
            return res
        if not slug_appears(body, slug):
            res.status = "CONTENT_MISMATCH"
            res.detail = (f"HTTP 200 but the page does not mention '{slug}', so it is "
                          f"probably not the cited document")
            res.evidence = res.title[:120]
            return res

        res.status = "REDIRECTED_AND_VERIFIED" if chain else "VERIFIED"
        if chain:
            res.detail = (f"HTTP {code} after {len(chain)} redirect(s); "
                          f"'{expected_slug(url)}' is now '{slug}'")
        else:
            res.detail = f"HTTP {code}"
        return res

    res.status = "UNVERIFIED"
    res.detail = f"HTTP {code}, not a status this tool can interpret"
    return res


# ---------------------------------------------------------------------------
# Stack Overflow: 403 to curl, confirmed through the API instead
# ---------------------------------------------------------------------------


class _StackExchangeItem(TypedDict, total=False):
    title: str


class _StackExchangeResponse(TypedDict, total=False):
    items: list[_StackExchangeItem]


def verify_stackexchange(url: str, code: int) -> Result:
    res = Result(url=url, status="ACCESS_RESTRICTED", http=code)
    m = re.search(r"/questions/(\d+)", url)
    if not m:
        res.detail = f"HTTP {code} and not a Stack Overflow question URL"
        return res
    qid = m.group(1)
    try:
        proc = subprocess.run(
            ["curl", "-sL", "--max-time", "20",
             f"https://api.stackexchange.com/2.3/questions/{qid}"
             + "?site=stackoverflow&filter=default"],
            capture_output=True, text=True, timeout=30)
        payload = cast(_StackExchangeResponse, json.loads(proc.stdout or "{}"))
        items = payload.get("items") or []
        if items:
            res.status = "VERIFIED"
            res.title = items[0].get("title", "")
            res.detail = "HTTP 403 to curl, confirmed to exist via the Stack Exchange API"
        else:
            res.detail = "HTTP 403 and the Stack Exchange API returned no such question"
            res.status = "UNVERIFIED"
    except Exception as e:
        res.status = "UNVERIFIED"
        res.detail = f"HTTP 403 and the API check failed: {e}"
    return res


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


def audit(urls: list[str], workers: int) -> list[Result]:
    def one(u: str) -> Result:
        code, body, chain = fetch_with_redirect_chain(u)
        res = classify(u, code, body, chain)
        if res.status == "ACCESS_RESTRICTED" and res.http in (401, 403) \
                and "stackoverflow.com/questions/" in u:
            res = verify_stackexchange(u, res.http or 403)
        return res

    out: list[Result] = []
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for r in ex.map(one, urls):
            out.append(r)
    return out


RETRYABLE = {"TRANSIENT_FAILURE", "UNVERIFIED"}


def with_retries(urls: list[str], workers: int, retries: int) -> list[Result]:
    """Retry the classifications that a second attempt could improve.

    Only TRANSIENT_FAILURE and UNVERIFIED. A 404 retried is still a 404, and a soft 404
    retried is still a soft 404, so retrying those would only slow the audit down while
    hammering a host that has already answered definitively.
    """
    results = audit(urls, workers)
    for attempt in range(retries):
        again = [r for r in results if r.status in RETRYABLE]
        if not again:
            break
        time.sleep(RETRY_SLEEP * (attempt + 1))
        by_url = {r.url: r for r in results}
        for r in audit([x.url for x in again], workers):
            old = by_url[r.url]
            r.chain = r.chain or old.chain
            if r.status == old.status and old.chain:
                r.detail += " (still inconclusive on retry)"
            elif r.status != "TRANSIENT_FAILURE":
                r.detail += f" (first attempt gave {old.status})"
            by_url[r.url] = r
        results = [by_url[u] for u in urls]
    return results


# ---------------------------------------------------------------------------
# Fixtures: deterministic classification with no network
# ---------------------------------------------------------------------------


class _Fixture(TypedDict):
    name: str
    url: str
    code: int | None
    chain: list[str]
    body: str
    expect: str


FIXTURES: list[_Fixture] = [
    {
        "name": "genuine-documentation-page",
        "url": "https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy",
        "code": 200,
        "chain": [],
        "body": "<html><head><title>Quota policy | Apigee docs</title></head><body>"
                + "<h1>Quota policy</h1><p>quota-policy</p></body></html>",
        "expect": "VERIFIED",
    },
    {
        "name": "google-soft-404-stub",
        "url": "https://cloud.google.com/apigee/docs/api-platform/reference/policies/nope-policy",
        "code": 200,
        "chain": [],
        "body": "<html><head><title>Apigee docs</title></head><body>"
                + "<div>The equivalent page does not exist in Apigee.</div></body></html>",
        "expect": "SOFT_404",
    },
    {
        "name": "soft-404-capitalisation-variant",
        "url": "https://cloud.google.com/apigee/docs/api-platform/reference/policies/nope-policy",
        "code": 200,
        "chain": [],
        "body": "<html><body>THE EQUIVALENT PAGE DOES NOT EXIST IN APIGEE</body></html>",
        "expect": "SOFT_404",
    },
    {
        "name": "genuine-404",
        "url": "https://cloud.google.com/apigee/docs/api-platform/nope/nope",
        "code": 404,
        "chain": [],
        "body": "<html><body>Not Found</body></html>",
        "expect": "NOT_FOUND",
    },
    {
        "name": "redirect-to-replacement",
        "url": "https://cloud.google.com/apigee/docs/api-platform/reference/policies/old-name",
        "code": 200,
        "chain": ["https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy"],
        "body": "<html><head><title>Quota policy</title></head><body>quota-policy</body></html>",
        "expect": "REDIRECTED_AND_VERIFIED",
    },
    {
        "name": "access-restricted-403",
        "url": "https://stackoverflow.com/questions/21615609",
        "code": 403,
        "chain": [],
        "body": "<html><body>blocked</body></html>",
        "expect": "ACCESS_RESTRICTED",
    },
    {
        "name": "rate-limited-429",
        "url": "https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy",
        "code": 429,
        "chain": [],
        "body": "slow down",
        "expect": "RATE_LIMITED",
    },
    {
        "name": "server-error-503",
        "url": "https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy",
        "code": 503,
        "chain": [],
        "body": "<html>maintenance</html>",
        "expect": "TRANSIENT_FAILURE",
    },
    {
        "name": "timeout-no-response",
        "url": "https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy",
        "code": None,
        "chain": [],
        "body": "",
        "expect": "TRANSIENT_FAILURE",
    },
    {
        "name": "wrong-document-200",
        "url": "https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy",
        "code": 200,
        "chain": [],
        "body": "<html><head><title>SpikeArrest policy</title></head>"
                + "<body>This page explains rate limiting with SpikeArrest.</body></html>",
        "expect": "CONTENT_MISMATCH",
    },
    {
        "name": "malformed-url",
        "url": "not-a-url",
        "code": 200,
        "chain": [],
        "body": "<html><body>anything</body></html>",
        "expect": "INVALID_URL",
    },
    {
        # curl writes 000 when it never got a response. Mapping that to "HTTP 0" let it
        # fall through to UNVERIFIED instead of TRANSIENT_FAILURE, so a transient network
        # blip was reported as an unconfirmable citation instead of something to retry.
        "name": "curl-zero-no-response",
        "url": "https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy",
        "code": 0,
        "chain": [],
        "body": "",
        "expect": "TRANSIENT_FAILURE",
    },
    {
        # "captcha" occurs in Google's own feature-flag blobs on normal article pages.
        # Keying interstitial detection on the bare word classified 154 of 168 valid
        # citations as rate-limited.
        "name": "normal-page-mentions-captcha-word",
        "url": "https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy",
        "code": 200,
        "chain": [],
        "body": "<html><head><title>Quota policy</title></head><body>quota-policy"
                + "<script>var f={DevPro__enable_devsite_captcha:false};</script>"
                + "</body></html>",
        "expect": "VERIFIED",
    },
    {
        "name": "real-interstitial",
        "url": "https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy",
        "code": 200,
        "chain": [],
        "body": "<html><body>Our systems have detected unusual traffic from your "
                + "computer network. Please try your request again later.</body></html>",
        "expect": "RATE_LIMITED",
    },
    {
        # After a redirect the slug to match is the one we landed on, not the one we asked
        # for. Checking the original slug reported every moved citation as a mismatch.
        "name": "redirect-then-soft-404",
        "url": "https://cloud.google.com/apigee/docs/api-platform/reference/policies/gone",
        "code": 200,
        "chain": ["https://cloud.google.com/apigee/docs/api-platform/reference/policies/gone"],
        "body": "<html><body>The equivalent page does not exist in Apigee.</body></html>",
        "expect": "SOFT_404",
    },
    {
        # Regression: Google's declared "page not found" marker must count as a
        # soft 404 even though the URL slug also appears in the body.
        "name": "page-not-found-marker",
        "url": "https://cloud.google.com/apigee/docs/api-platform/reference/policies/quota-policy",
        "code": 200,
        "chain": [],
        "body": "<html><body>quota-policy. Page not found.</body></html>",
        "expect": "SOFT_404",
    },
    {
        # Regression: a root URL with an empty path slug must not verify just
        # because the body is arbitrary content.
        "name": "empty-path-slug",
        "url": "https://example.com/",
        "code": 200,
        "chain": [],
        "body": "<html><body>hello world</body></html>",
        "expect": "UNVERIFIED",
    },
]


def run_fixtures() -> int:
    print("URL classifier fixtures (offline, no network)\n")
    bad = 0
    for fx in FIXTURES:
        got = classify(fx["url"], fx["code"], fx["body"], fx["chain"]).status
        ok = got == fx["expect"]
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {fx['name']:<38} "
              + f"expected {fx['expect']:<26} got {got}")
    print()
    print(f"{len(FIXTURES) - bad}/{len(FIXTURES)} fixtures classified correctly")
    return 1 if bad else 0


# ---------------------------------------------------------------------------


class _Args(Protocol):
    paths: list[str]
    fixtures: bool
    json: bool
    workers: int
    retries: int


def main() -> int:
    ap = argparse.ArgumentParser()
    _ = ap.add_argument("paths", nargs="*", help="files or directories to read")
    _ = ap.add_argument("--fixtures", action="store_true",
                        help="run the offline classifier fixtures and exit")
    _ = ap.add_argument("--json", action="store_true")
    _ = ap.add_argument("--workers", type=int, default=8)
    _ = ap.add_argument("--retries", type=int, default=RETRIES)
    args = cast(_Args, cast(object, ap.parse_args()))

    if args.fixtures:
        return run_fixtures()

    targets = list(args.paths) or list(DEFAULT_TARGETS)

    urls, counts = discover(targets)
    if not urls:
        # A URL audit that found nothing to check has verified nothing. Exiting 0 here is
        # how the first version of this checker reported a pass having checked zero URLs.
        print("ERROR: no URLs found in the given targets. A URL audit with no inputs is "
              + "not a passing audit.")
        print(f"targets read: {', '.join(targets)}")
        return 2

    print(f"auditing {len(urls)} unique URLs from {sum(counts.values())} citation "
          + f"occurrences in: {', '.join(targets)}")

    results = with_retries(urls, args.workers, args.retries)
    for r in results:
        r.occurrences = counts.get(r.url, 1)

    tally = Counter(r.status for r in results)
    failing = [r for r in results if r.status in FAILING]
    env = [r for r in results if r.status in ENVIRONMENTAL]

    if args.json:
        print(json.dumps({"unique_urls": len(urls),
                          "citation_occurrences": sum(counts.values()),
                          "tally": dict(tally),
                          "results": [asdict(r) for r in results]}, indent=2))
    else:
        print()
        for status, n in sorted(tally.items(), key=lambda kv: -kv[1]):
            print(f"  {status:<26} {n}")
        if failing:
            print(f"\nBROKEN OR UNCONFIRMED CITATIONS ({len(failing)}):")
            for r in sorted(failing, key=lambda x: x.url):
                print(f"  [{r.status}] {r.url}")
                print(f"      {r.detail}")
                if r.evidence:
                    print(f"      evidence: {r.evidence}")
        if env:
            print(f"\nENVIRONMENTAL, NOT A DEFECT IN THE CITATION ({len(env)}):")
            for r in sorted(env, key=lambda x: x.url):
                print(f"  [{r.status}] {r.url}  {r.detail}")
        redirects = [r for r in results if r.status == "REDIRECTED_AND_VERIFIED"]
        if redirects:
            print(f"\nREDIRECTED AND VERIFIED ({len(redirects)}):")
            for r in redirects:
                print(f"  {r.url}")
                for hop in r.chain:
                    print(f"      -> {hop}")

    if failing:
        print(f"\nRESULT: FAIL, {len(failing)} of {len(urls)} URLs are broken, are a "
              + "soft 404, or could not be confirmed")
        return 1
    if env:
        print(f"\nRESULT: PASS with {len(env)} URL(s) unverifiable from this environment. "
              + "Those are not confirmed citations.")
        return 0
    print(f"\nRESULT: PASS, all {len(urls)} unique URLs verified "
          + f"({sum(counts.values())} citation occurrences)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())