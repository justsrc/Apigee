# How to verify an Apigee documentation URL in this project

This exists because guessed URLs are the main source of fabricated citations, and
guessed URLs fail often here. Out of 39 plausible-looking paths tried during initial
setup, 22 returned 404. The real page is `basic-authentication-policy`, not
`basic-auth-policy`. `debug-runtime-errors` does not exist. Never cite a URL you have
not checked.

## Use the fetch script

```bash
cd /Users/justinjacob/Projects/Work/Apigee/research
./fetch.sh <doc-path-without-extension> [output-name]
```

It prints `STATUS<TAB>BYTES<TAB>URL`, saves clean Markdown to `pages/<name>.txt`, and
exits non-zero on anything other than 200. Read the saved file with Read/Grep.

The equivalent by hand:

```bash
curl -sL -o /tmp/p.html -w "%{http_code}\n" "https://cloud.google.com/apigee/docs/<path>"
pandoc -f html -t gfm --wrap=none /tmp/p.html | awk '/^# / && !s {s=1} s {print} /Except as otherwise noted/ {exit}'
```

Do not use `lynx -dump` on these pages. It preserves the navigation sidebar and drops
the element tables that most policy pages are built from.

## Find real URLs instead of guessing

Every fetched page contains the real link tree. Discover URLs from it:

```bash
grep -oE '/apigee/docs/[a-zA-Z0-9/._-]+' pages/<file>.txt | sort -u
```

Seed this with a page you have already fetched. Good seeds:

- `api-platform/reference/policies/error-code-reference`
- `api-platform/get-started/compare-apigee-products`

## Two things the docs do not do what you expect

**The policy error reference page is a pointer, not a table.** It carries no fault
codes itself. It says to read the individual policy documents. Real fault codes live
in each policy page under `## Error reference`, with subsections `### Runtime errors`,
`### Deployment errors`, and `### Fault variables`. Search for `^## Error reference`.

**Runtime and deployment errors are different failure modes.** A deployment error
means the proxy revision was rejected at upload. A runtime error means the revision
deployed and then failed while serving traffic. These produce completely different
symptoms and the skill must never conflate them.

## Evidence levels

Label every fact you write down:

- **documented**: stated on a page you fetched, at a URL you checked.
- **observed**: something you executed or reproduced yourself.
- **reported**: a community claim you have read but not reproduced.
- **hypothesis**: your inference. Say so.

Never promote a hypothesis to documented. If you could not verify something, write
that it is unverified rather than omitting it.