# Follow-up: the path in the error is neither yours nor the bundle's

**Assessment, now with more confidence.** This is not a missing file and it is not your
path being mangled. The path in the error message is derived from something other than the
bundle contents and other than the argument you passed. Something between your create step
and the deployment record is constructing that path.

I am not going to tell you which component without seeing it. What I can do is narrow it to
a small set and give you the test that separates them.

**Product.** Same assumption as before, Apigee X or hybrid control plane. Tell me the version
and the create tool you are using and I can be more specific than "something in the chain".

## What the new evidence rules out

- **File missing from the bundle.** The filename in the error does not match the bundle's own
  XML filename, and the path is not a bundle entry. If the file were simply absent you would
  expect the path to be a bundle-relative path to the expected file.
- **Your `./` prefix being resolved relative to your shell.** You typed `./...`, and the
  recorded path does not begin at the root of the shared flows directory the way a bundle
  path would. Your prefix is not what produced this string.

Your prefix is still worth removing, because a path that only works without it is a real
problem, but it is no longer the lead hypothesis. I am moving it to disfavoured as the cause.

## What remains

| Hypothesis | Supporting | Contradicting | Missing | Test | Status |
| --- | --- | --- | --- | --- | --- |
| The create tool builds the bundle path from its own working directory rather than the argument | recorded path begins at the shared-flows root, not at your argument | none | the tool's source or its verbose output | run the create step with a verbose or trace flag and read what path it sends | plausible, unverified |
| The Management API stores a server-derived path when the submitted path is not recognised as a bundle path | derived path that matches neither input | none | the raw create request body | capture the create request and compare its `path` field with the argument | plausible, unverified |
| The error message is composed from the bundle's declared name rather than its contents | filename mismatch | none | the bundle's XML | read the `<name>` and file name in the bundle root | plausible, unverified |

## The test

Capture the HTTP request your create step sends, specifically the `path` field of the proxy
or shared flow resource, and compare it character by character with the argument you passed.

- If the request carries the path you passed, the transformation happens server side, and the
  next thing to collect is the exact per-instance error string plus the revision and
  environment, because that is what a Google-side investigation needs.
- If the request carries something else, the fault is in your create step or the tool, and you
  can fix it today without waiting for anyone.

Either way you get an unambiguous answer, and it is one step rather than a search.

## Until that is settled

Keep the pipeline change from my first reply, which stands regardless: poll the deployment
record to a final state and fail the build on anything but the success value. That is what
turns this from "someone checked by hand" into a caught failure, and it is worth having even
if the underlying path bug takes a week to pin down.

## What I still could not determine

Which component derives the path, and whether a leading `./` is a supported form for a bundle
path at all. I would want the bundle specification page for your version before telling you
either is supported or unsupported, and I will not assert it from memory.