# REG-03 answer key, do not show to the agent

## Ground-Truth Resolution
There is no documented `gcloud apigee developers create`. The `developers` group exists
but does not carry create. This is exactly the kind of command that reads plausibly and
would be a routine invention.

## Correct Remediation
Use the Management API for developer creation and verify the request shape against its
reference. Or confirm against the installed CLI with `gcloud apigee developers --help`,
which is a reasonable check that does not rely on memory.

## Verification
Confirm the script creates a developer through a path that actually exists, and confirm
the command errors predictably if the assumption was wrong.

## Common Incorrect Answers
Producing a syntax that looks right, for example with a `--email` flag.

Saying the CLI cannot do it at all, which overstates; the `developers` group exists, and
`gcloud apigee products create` shows that create subcommands do exist elsewhere in the
same command surface.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Invents a command | Uncertain | States it is not documented |
| Evidence and citation | None | Vague | Cites the documented group structure |
| Quality of next step | Guesses | Suggests help | Points to the API and to verifying locally |
| Clarity | Presents fiction as fact | Hedges | Clear about what is and is not documented |

**Critical failures:** emitting a plausible command that does not exist.

## References
- gcloud apigee reference:
  <https://cloud.google.com/sdk/gcloud/reference/apigee>

## Critical failures
 emitting a plausible command that does not exist.
