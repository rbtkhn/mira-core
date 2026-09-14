# Mind and Study composition links

Mind owns strategic assessment and Notebook composition. Study composes essays
and letters; notes preserve provisional ideas. Composition is optional and may
return a question or objection to Mind without adopting a correction.

When an authorized composition arises from a strategic inquiry, include one
optional JSON block in its Markdown. References use repository-relative POSIX
paths and SHA-256 of the exact file bytes, not a contribution's internal digest:

```text
<!-- mira-composition
{"schema":"mira-composition-v1","kind":"essay","origins":[{"ref":"mira/strategy-notebook/contributions/ORIGIN.json","sha256":"EXACT_BYTE_SHA256"}],"summary":"How this composition develops the inquiry","return_question":"What should Mind reconsider?"}
-->
```

Replace placeholders before validation. Kind is `note`, `essay`, or `letter`,
matching its existing shelf. Origins may contain multiple distinct notebook
references. Summary is required; return_question is optional. Keep the prose
independently intelligible and preserve privacy and evidence qualifications.

Read-only interfaces:

```text
tools/run.ps1 strategy-notebook composition-validate --artifact-ref PATH --json
tools/run.ps1 strategy-notebook composition-search --artifact-ref PATH --json
tools/run.ps1 strategy-notebook composition-search --notebook-ref PATH --json
```

Search returns bounded handles, exact original bindings, current integrity
status, recorded responses, gaps, and omissions. Read full relevant artifacts
before use. Recover the origin's current corrections through `strategy-notebook
context --date DATE --focus QUESTION --json`; later corrections remain later
context, not evidence available at the earlier date. A changed artifact is not
the version originally reviewed. Missing history is not absence of correction.

An authorized new Mind contribution may carry `composition_refs`: a list of
objects with `ref`, byte `sha256`, `effect` (`considered`, `changed`, `no-change`),
and an authored `reason`. Changed judgment requires a substantive assessment,
delta, and a correction link to an originating notebook. Responses append;
they never rewrite an earlier contribution or automatically adopt a question.

Use owner-native retrieval directly when the owner is known. Mira Memory routes
unclear recall requests; no routine memory inventory or private-store access is
required. Consult Library Journal only when reading history or failed transfer
materially affects this inquiry.

This metadata is separate from Library metadata. Robert may select essays and
notes for Library inclusion; writing or linking grants no membership, governed
relationship, evidence promotion, sending, or publication authority. Legacy
artifacts remain valid without metadata. Do not backfill or infer links.
