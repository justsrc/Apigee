# Shared flow deploy reports success, revision is in ERROR

**Assessment, and how confident I am.** This is a deployment error that your pipeline is not
reading. The deploy call returned a deployment object, which means the Management API
accepted the request, not that the deployment succeeded. The asynchronous deployment then
failed, and nothing in your pipeline compared the deployment `state` against the value you
expect. That part I am confident about; it follows from your own evidence.

What I cannot yet confirm is why the file is not found. The pattern you describe, failure
only when the bundle path starts with `./`, points at how the bundle path is resolved, but I
have not seen the bundle or the per-instance error text, so I am calling that a strong
hypothesis rather than a cause.

**Product.** Your wording (deployments resource, bundle, shared flow directory) reads as
Apigee X or hybrid through the Management API. I see no Edge for Private Cloud markers. If
this is a hybrid control plane the fix is the same, but tell me the version, because the
deploy response shape has changed between releases.

## Established

- The create succeeded and the deploy returned a response naming an environment, proxy,
  revision and start time.
- A direct query of that revision's deployment returns `state` of `ERROR`.
- The per-instance error names a file under the shared flows directory that is not in the
  bundle.
- The failure occurs only when the bundle path passed to the create step starts with `./`.

## Assumed, not yet checked

- That your tooling ignores the deployment state after the call returns.
- That the bundle really does contain the file at the path the error names, and the
  resolver is looking somewhere else.

## Ledger

| Hypothesis | Supporting | Contradicting | Missing | Test | Status |
| --- | --- | --- | --- | --- | --- |
| Pipeline never reads deployment state | ERROR revision visible only because someone looked | none | the deploy step's post-check | read the deploy step and the CI log for any state check | strongly supported |
| `./` prefix breaks bundle path resolution | failure is conditional on the prefix | none | the create step's exact argument | deploy the identical bundle with and without the prefix | plausible, unverified |
| File genuinely missing from the bundle | error names a file that is not there | failure is conditional on the prefix, a missing file would fail always | the bundle listing | list the bundle contents against the error's path | disfavoured |

## What to do now

1. Make the pipeline fail on a non-OK deployment state. Whatever deploy tool you use, poll
   the deployments resource for that revision until the state is final and exit non-zero
   unless it is the success value. This is the fix that stops the next one going unnoticed,
   and it is independent of the underlying cause.
2. Remove the `./` prefix from the bundle path in the create step and deploy again. If that
   alone clears it, hypothesis two is confirmed and you have your cause.
3. If it still fails with the prefix removed, send me the bundle listing and the exact
   per-instance error text. At that point the file is either missing from the bundle or the
   shared flow reference inside it is wrong, and those have different fixes.

## How to confirm

Deploy to a scratch environment, query the deployment record until it reaches a final state,
and assert on that state rather than on the exit code of the deploy command. A revision that
reports ERROR is a failed deploy even when the command printed a response body and returned
zero.

## What I could not determine

Whether the resolver treats `./` differently from an absolute path, which I would want to
confirm from the bundle specification before telling you it is a supported or unsupported
form. I am not going to assert that from memory.