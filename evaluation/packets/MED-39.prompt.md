You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# MED-39: Every client call times out, and the Kubernetes object at fault is in another namespace

## Initial Support Ticket
> Since we rebuilt our Apigee hybrid cluster yesterday, every API call from outside the
> cluster times out. Nothing returns, not even a 4xx. From inside the cluster the
> message processors look healthy and the backend is reachable.
>
> The errors we can see are:
>
> ```
> * Connection failed
> * connect to 34.84.67.39 port 443 failed: Operation timed out
> * Failed to connect to example.apis.com port 443: Operation timed out
> * Closing connection 0
> curl: (7) Failed to connect to example.apis.com port 443: Operation timed out
> ```
>
> We also still have errors from the install:
>
> ```
> Error from server (Invalid): error when applying patch:
> ... Name: "istio-init-crd-10-1.4.6", Namespace: "istio-system"
> The Job "apigee-resources-install" is invalid : spec . template : Invalid value : core . PodTemplateSpec { ObjectMeta : v1 . ObjectMeta { Name : "apigee-resources-install" , ...
> ```
>
> We have checked the backend, the DNS records and our own network. Where do we start?

## Initial Evidence
All client calls fail to connect, with no HTTP response of any kind. This is a connection
failure before any Apigee policy runs, which already rules out most of the policy fault
catalogue. Installation-time errors reference Jobs in the `istio-system` namespace. The
customer has already done the application-layer checks.
