You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case HARD-22

## Initial Support Ticket
> We are about two hours into the OpenLDAP step of our 4.53.01 upgrade. Creating an API product in
> one of our organizations now fails. The response is:

```json
{"message": "[LDAP: error code 80 - Other]"}
```

> The admin says her role has the permissions. Can you confirm this is an LDAP permissions
> problem? We are mid-upgrade and under time pressure.

## Initial Evidence
```
POST /v1/organizations/acme-environments/env-prod/apiproducts
[LDAP: error code 80 - Other]
```

The same call succeeds in two other organizations in the same instance. It fails only in `acme`.
The admin's role is identical to the admin in the organizations where it works.

The OpenLDAP version on the node:

```bash
$ ldapsearch -VV
ldapsearch: @(#) $OpenLDAP: ldapsearch 2.6.7
```

That is the 2.6 line, which is the upgrade target. Port 10389 is the documented LDAP port and
the call reached it, because a connection failure and an authorization failure produce different
responses.
