# HARD-19 answer key, do not show to the agent

## Ground-Truth Resolution
Two platform changes, one immediate cause, and one latent cause that the immediate cause is hiding.

Immediate: the callout asks for the JCA provider named `BC`. On 4.53 the default provider is
`BCFIPS`, so the lookup fails.

Latent: the callout jar was built without its dependencies, relying on libraries the Message
Processor used to ship. Those are gone. Even if the provider name is corrected, an unpackaged
dependency is a future failure.

The platform is behaving as documented. The defect is in the callout, and it was always a latent
defect that the upgrade made visible. A maintainer on the source thread said exactly this:

> Strictly speaking , excluding dependencies like this from the packaging phase is risky. Apigee
> doesn't make any guarantees that it supplies a set of  "common" or "popular" Java JARs  for use
> by callouts.

And, correctly, hedged on the platform side:

> I am not familiar with the changes to OPDK 4.53, but it is possible that one or more of those
> JARs are no longer available.

The official documentation and the expert's hedge do not actually conflict, because the
documentation is from a later release than the forum post. An agent that treats the hedge as
disagreeing with the docs has mistaken a difference in knowledge for a difference in fact.

## Correct Remediation
There are two documented paths and one that fails. Both require a new proxy revision and a
deployment, and both should be validated in a non-production environment first.

Path A, use the FIPS provider. The official recommendation:

> The recommended workaround is to use the BCFIPS provider. Custom JavaCallout implementations
> that relied on the old provider will need to be reviewed and re-implemented using the Bouncy
> Castle FIPS provider, which can be accessed using the string "BCFIPS".

Path B, package the dependency with the callout. The documented method, either as a resource at
proxy, environment or organization level:

```bash
cp $APIGEE_ROOT/edge-message-processor/lib/deprecated/some.jar \
   $APIGEE_ROOT/data/edge-message-processor/external-lib/some.jar
chown -R apigee:apigee $APIGEE_ROOT/data/edge-message-processor/external-lib
```

Path B has a hard prerequisite and a trap. Copy the jars out of the old `deprecated` directory
BEFORE upgrading, because 4.53.01 removes that directory. And bundling the Bouncy Castle FIPS
jars inside the callout jar does not work - in the source case that produced a different
exception:

```
java.lang.SecurityException: sealing violation: package org.bouncycastle.jcajce.util is sealed
	at java.net.URLClassLoader.getAndVerifyPackage(URLClassLoader.java:405)
	at com.apigee.messaging.resource.JavaResourceClassLoader.loadClassSelfOnly(JavaResourceClassLoader.java:246)
	at com.apigee.messaging.resource.JavaResourceClassLoader.loadClassSelfFirst(JavaResourceClassLoader.java:230)
	at com.apigee.messaging.resource.JavaResourceClassLoader.loadClass(JavaResourceClassLoader.java:133)
```

Signed Bouncy Castle jars keep their seal when shaded. Path B therefore applies to non-BC
dependencies from the removed directory, not to BC itself.

What actually resolved it in the source case, verbatim from the reporter:

> The code was updated to make it RSA pure Java rather than BC library code, which resolved the
> issues

That is a third path, outside the platform, and it is the one with no provider dependency at all.

## Verification
Deploy the rebuilt callout to a non-production environment first and exercise both the `encrypt`
and `decrypt` actions, because only one path was failing in the reported case and the other may
hide the same defect. Confirm the fault code on previously failing requests changes, rather than
only confirming that some requests succeed. Then roll out.

Confirm no other JavaCallout in the organization relies on the removed directory or on the `BC`
provider name. The change-detection tool exists for exactly this:

```bash
./change-detector --username [your_username] --mgmt-url [MGMT url]
```

and it distinguishes a High confidence detection, meaning a very high probability the item will
break after upgrading, from a Medium, meaning the tool is unsure and more strategies are needed.

## Common Incorrect Answers
Rebuilding the callout jar with the Bouncy Castle jars shaded in. This is the obvious fix and it
fails with a sealing violation.

Rolling the proxy back to its previous revision. The bundle is identical to the previous revision.
The change is on the node.

Restarting or re-draining the Message Processors. Nothing about the runtime state is wrong.

Changing the private key, the flow variables, or the `<Property>` values. The failure is at
provider resolution, before the key is used.

Removing the JavaCallout to stop the errors. That removes the decryption the proxy depends on,
and the security control with it.

Assuming the whole proxy is affected. The 96% that does not traverse this callout is healthy, and
treating this as a platform outage will produce a much larger rollback than the fault warrants.

## Evaluation Rubric
| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Technical correctness | Bundles BC jars | Names the provider change | Names both the provider change and the removed `deprecated` directory, and separates them |
| Diagnostic method | Reads only the exception | Reads the callout policy | Reads the jar contents and distinguishes the immediate from the latent cause |
| Handling of competing causes | Platform defect | Single cause | Platform behaved as documented, the defect is in the callout, and that is stated rather than implied |
| Quality of next step | Shades BC in | Switches to BCFIPS | Offers BCFIPS, external-lib placement, or removing the dependency, with the sealing trap named |
| Safety | Removes the callout | Rebuilds | Tests in non-production, exercises both actions, checks for other affected callouts |

**Critical failures:** recommending that the Bouncy Castle jars be shaded into the callout jar,
without naming the sealing violation that causes; rolling the proxy back on the assumption that
the bundle changed.

**Not a critical failure:** recommending BCFIPS as the fix without mentioning the removed
`deprecated` directory. It is the documented workaround and it addresses the reported error. It
is incomplete, not wrong, and the rubric line on competing causes captures that.

## References
- Changes in Edge for Private Cloud 4.53.01:
  <https://docs.apigee.com/private-cloud/v4.53.01/changes-privatecloud-45301>
- Update Apigee Edge 4.52.02 or 4.53.00 to 4.53.01:
  <https://docs.apigee.com/private-cloud/v4.53.01/update-apigee-edge-45202-45301>
- API Monitoring fault codes:
  <https://cloud.google.com/apigee/docs/api-monitoring/fault-codes>
- Source case:
  <https://github.com/DinoChiesa/Apigee-CustomPolicy-RsaCrypto/issues/10>

## Critical failures
 recommending that the Bouncy Castle jars be shaded into the callout jar,
