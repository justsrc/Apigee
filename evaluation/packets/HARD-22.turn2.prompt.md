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

The customer has replied with more information.

## Diagnostic Evidence
```bash
ldapsearch -o ldif-wrap=no -b "dc=apigee,dc=com" \
  -D "cn=manager,dc=apigee,dc=com" -H ldap://:10389 -LLL -x -w LDAP_PASSWORD dn > /tmp/DN.ldif
```

`/tmp/DN.ldif` is not empty, and the long entries point at `acme`. The reported entity does not
itself have a 241-character name, which is what makes this hard: the offending DN is built by
concatenation. The documented example, verbatim:

```
dn: cn=@@@environments@@@*@@@applications@@@*@@@revisions@@@*@@@debugsessions,ou=resources,cn=businessuser,ou=userroles,o=orgname,ou=organizations,dc=apigee,dc=com
```

An org named `acme` plus an environment named `env-prod` plus a long custom role name plus a
long developer or user name can produce a resource RDN over the limit, while every individual
name looks reasonable.

What is deliberately NOT established: which component of the concatenation is the largest
contributor. The documentation names the candidates - custom role name, app, API product, or the
organization or environment name itself - and says:

> If it is the organization name or environment name that is the primary contributor to long RDN,
> you will have to migrate to a different organization or environment with a shorter name.

An agent cannot determine that from the LDIF alone without measuring the RDN segments, and the
ticket does not contain that measurement.
