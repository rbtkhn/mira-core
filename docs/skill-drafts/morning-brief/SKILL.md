---
name: morning-brief
description: "Create an on-demand, source-linked five-minute global morning update from a frozen research receipt and the repository's active judgment and forecast baseline."
---

# Morning Brief

Use `morning-brief` as a local, opt-in research workflow for the Narrative
Geopolitics operator. It is a selective global update, not a comprehensive news
digest, daily synthesis, publication, or automatic cadence handoff.

The human operator is the primary audience. Stable fields and provenance make
the artifact legible to a successor Codex session without turning it into an
agent-state dump.

## Establish the observation contract

Before retrieval, state:

- mode: `scan`;
- exact brief date and RFC3339 as-of time;
- the preceding 24-hour observation window;
- geography: `global`;
- output: `five-minute-selective-global-update`;
- stop condition: four material developments plus one outlier or visibility
  gap, or documented exhaustion of qualifying candidates.

Run only on explicit operator request. Do not schedule or generate it
automatically.

## Build the inherited baseline

Read valid `judgment.md` files from the 30 days before the brief date. A valid
judgment has a completed crisis object and Decision Compression contract. Read
the forecast ledger and retain only hooks that are both `open` and
`accountable: yes`.

The receipt must preserve repository-relative paths and SHA-256 hashes for the
complete qualifying baseline. It may label an open hook's current pressure,
but it never changes or resolves that hook.

## Gather fresh observations

Use World Monitor and broad current search for discovery. Follow the complete
World Monitor contract when that surface is used. Recover an official,
primary, wire, or clearly attributed upstream source before retaining an
observation in the brief.

For every considered candidate, record observation and retrieval time,
geography, domain, discovery surface, upstream provider and URL, source type,
freshness, lineage root, disposition, and exclusion or selection reason.
Discovery surfaces are never evidence. Do not count displays with a shared
lineage root as independent.

Receipt and renderer version `2.1` keeps each candidate atomic. A selected
candidate may reference ordered `related_observations` whose relationship is
`corroborates`, `qualifies`, or `disputes`. Each related observation retains
its own timestamps, upstream provenance, lineage, and optional Reality Check
state. It uses disposition `related`, carries no independent model impact, and
does not consume a development slot. A disagreement must remain explicit in
the selected candidate's confidence boundary.

## Consult Reality Check when risk warrants it

After recovering the fresh upstream observation, search existing lattice claim
records for an exact atomic match. A shared actor, crisis object, geography, or
mechanism is contextual only. For a genuine match, run both commands read-only:

```powershell
.\tools\run.ps1 reality audit CLAIM_ID --json
.\tools\run.ps1 reality impact CLAIM_ID --json
```

Record `exact`, `contextual`, or `none` in the candidate's optional `reality`
object, including controlling claim and assessment IDs, exact lattice state,
repository-relative record paths and SHA-256 hashes, audit time, relationship,
and the resulting confidence constraint. Only `same-observable` may let an
assessment characterize the fresh observation. Context may explain model or
forecast dependency, but it does not verify a new event.

- Canonical support can strengthen confidence but never replace a fresh
  upstream source.
- Contested state requires qualified language and prohibits a stronger causal
  formulation.
- Provisional or unassessed state permits only the narrow observation with a
  provisional interpretation.
- Challenged state requires exclusion or prose that preserves the disagreement.
- An unmatched observation remains eligible when its upstream sourcing and the
  rest of this contract are sufficient.

Never say `verified` unless the same bounded observable has a controlling,
sufficiently signed canonical assessment. Never create claims, evidence,
assessments, investigations, transitions, signatures, or verification packets
from Morning Brief research.

## Select and interpret

When multiple operating priorities compete, rank them by organizational
consequence first, then urgency, dependency, evidence quality, reversibility,
and human authority. A technically closable task does not outrank a more
consequential blocked path merely because it is easier to finish. Translate a
blocked consequential path into its narrowest internal decision or review and
give the technical task an explicit disposition.

Use this compact frame when the ranking is contested:

```text
Priority:
Organizational consequence:
Current dependency:
Narrowest decision available now:
Why delay is justified:
Owner now:
Owner later:
```

- Select at most four fresh developments that materially pressure a named
  inherited judgment or accountable open forecast.
- Label provisional impact `strengthens`, `weakens`, `complicates`, or
  `no-material-effect`; a selected material development cannot use the last
  state.
- Select exactly one consequential outlier or visibility gap. An outlier may
  sit outside active models; a gap must name what its absence weakens.
- Declare at least three reviewed geographies, two domains, three recovered
  upstream providers, and three independent lineage roots.
- Treat all model impact as provisional. Do not rewrite canonical judgment.
- When retrieval is healthy but no candidate clears the threshold, state
  `no material change`, preserve the strongest gap, and generate the brief.
- When timestamps, upstream recovery, baseline hashes, or minimum coverage are
  inadequate, fail closed and generate nothing.

Use the field contract in [receipt-v2.json](assets/receipt-v2.json). Keep the
working receipt outside the canonical output path until research and review are
complete. Store summaries and URLs, never full source bodies or transcript
excerpts.

## Render

```powershell
.\tools\run.ps1 morning-brief --date YYYY-MM-DD --as-of RFC3339_TIMESTAMP --receipt PATH
```

The renderer validates current repository baseline state, canonicalizes the
receipt, and writes one paired artifact:

```text
narrative-geopolitics/work/morning-brief/YYYY-MM-DD.md
narrative-geopolitics/work/morning-brief/YYYY-MM-DD.receipt.json
```

It refuses an existing pair unless `--overwrite` is explicit. The historical
`2026-08-02.md` experiment specimen is protected and must not be rewritten by
this workflow.

Valid output is labeled `experimental-internal-morning-update` and reported as
`Generated`, never `Published`. The renderer leads with reader-facing
observation, materiality, model impact, confidence, and source prose; it moves
IDs, Reality Check state, coverage limitations, lineage metadata, and watch
support references into the Analyst's Note. A rendered brief above 1,000 words
fails closed before either canonical file changes.

Forecast rendering separates observation pressure from review administration
without changing receipt schema `2.1`. Every forecast whose impact is not
`unaffected` must be referenced by a selected material development, and every
forecast referenced by a selected material development must carry a pressure
label. Render pressured claims first, due forecasts with no new pressure in a
separate subsection, and one count of forecasts that are both unaffected and
not due. A due-and-pressured forecast appears only once, under pressure. Order
pressured rows due-first and then by review date and hook ID; order due-only
rows by review date and hook ID. Omit repetitive `not due` prose, preserve the
complete forecast claim before hook metadata, and never infer resolution from
the Morning Brief.

## Authority and pilot boundary

- Do not land or relabel archive evidence.
- Do not edit daily synthesis, judgment, issue, or brief files.
- Do not create verification packets or register, update, or resolve forecasts.
- Do not mutate Reality Check claims, evidence, assessments, investigations,
  transitions, relations, signatures, or generated views.
- Do not publish or treat provisional model impact as operational truth.
- Keep the workflow repository-local; do not add it to the deployable registry
  or synchronize a user-level mirror.

Keep the workflow experimental for its first five valid real-world briefs.
After the fifth, review five-minute readability, upstream recovery, unsupported
claims, model-impact usefulness, signal-to-noise, and the value of the outlier
slot through `coffee`. Separately review whether receipt `2.1` creates recurring
story-composition pressure: multi-observation items, mixed epistemic states,
editorial regrouping, reference-graph pressure, multiple-render demand,
source-to-sentence ambiguity, or repeated schema workarounds. Open a version-3
story/observation design review only when at least two of those triggers recur.
Any source-to-sentence mismatch or Reality Check state applied to the wrong
observable fails the affected brief immediately but does not authorize an
automatic migration. Keep these pilot measurements conversational; do not add
them to the canonical receipt or mutate repository state. Fixture renders prove
mechanics, not operator utility.
