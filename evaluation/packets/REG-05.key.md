# REG-05 answer key, do not show to the agent

## Ground-Truth Resolution
The list the user expects moved. The Edge to X comparison carries a "Which Apigee Edge
features are not supported in Apigee X?" section introduced by "Google does *not* plan to
support the following features", and a separate "Unsupported Apigee Edge APIs" table.

The regression risk is real here: a model that remembers the old page will confidently cite
it for a list it no longer contains.

## Correct Remediation
Point to the Edge to X comparison and verify it contains the list before citing it.

## Verification
Confirm the cited page currently contains the list. A link that returns 200 but has been
rewritten is the failure mode here, so content matters as well as status.

## Common Incorrect Answers
Citing the product comparison page as containing the removal list.

Saying the information is no longer published, which is wrong; it moved.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Evidence and citation | Cites stale page | Uncertain | Cites the current location and notes the move |
| Technical correctness | Wrong page | Partial | Correct content, correct location |
| Handling of uncertainty | Confident from memory | Hedges | Notes the page was rewritten |
| Clarity | Confident wrong answer | Partial | Explains the move briefly |

**Critical failures:** citing a page for content it no longer contains.

## References
- Compare Apigee products, rewritten:
  <https://cloud.google.com/apigee/docs/api-platform/get-started/compare-apigee-products>
- Compare Apigee Edge to Apigee X:
  <https://docs.apigee.com/migration-to-x/compare-apigee-edge-to-apigee-x>

## Critical failures
 citing a page for content it no longer contains.
