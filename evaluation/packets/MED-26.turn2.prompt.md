You are an Apigee technical support engineer. A customer has contacted support.
Answer as you would to them, in Markdown.

Rules for this exercise:
- Do not invent documentation URLs, fault codes, configuration elements, or CLI flags. If
  you are not sure something exists, say so and describe how you would verify it.
- If you cannot establish a root cause, say that plainly and name the next test you would
  run. Do not invent a cause to appear complete.
- Quote error strings exactly as given.
- Keep it to the length the problem actually needs. Do not pad.


# Support case MED-26

The customer has replied with more information.

## Diagnostic Evidence
```terminal
# Is the jar in the bundle byte-identical to the one in the repository?
unzip -p target/apiproxy/resources/java/edge-micro-javacallout.jar \
    io/apigee/microgateway/javacallout/Callout.class | head -c 64 | xxd | head
# 7f454c46 is the ELF magic, 4a6f736e is ".json" - a text header where a class header must be
```

The class file in the packaged jar begins with text rather than the `CAFEBABE` class magic. It is
a valid text file that used to be a valid class file. The upload that works by hand is a different
byte sequence from the one the pipeline produced, which is what makes this a packaging defect
rather than an Apigee defect.
