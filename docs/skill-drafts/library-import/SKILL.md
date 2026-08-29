---
name: library-import
description: "Plan, batch, admit, correct, or audit Mira Library authorities and source bodies under archive/library, with separate roster, metadata, body-research, and admission gates; conservative provenance, online availability, coverage, and verification remain controlling for private reading."
---

# Library Import

Use this repository-local workflow when planning, batching, admitting,
correcting, or auditing source authorities and text bodies for
`archive/library/`.

`archive/library/library-registry.json` is the machine authority. Human indexes
are navigation surfaces. The Mira Library is a personal-reading library. Text
bodies are private/local reading payloads and belong in
the platform state root at `library/texts/` unless the operator explicitly chooses a governed
override. If a text is available online, treat it as authorized for private
reading download, inspection, and private text-store admission. Reuse notes
belong only at outward-facing boundaries: redistribution, publication, Git
source-body admission, or private Archive exposure beyond the library's
personal-reading boundary.

Do not convert online-available personal-reading texts into rights blockers.
When an online text can be inspected, the relevant library question is whether
the edition, source route, language, file, coverage, and private-store payload
are good enough. Rights or reuse cautions are boundary notes for later public,
redistributive, Git-body, or Archive exposure decisions.

Live library verification is stricter than registry availability. A source can
be represented in the registry while its private payload is absent from the
active worktree. Treat these as separate states:

1. `registry-represented` -- the registry records at least one logical body for
   the authority.
2. `private-payload-present` -- every referenced local/private body resolves to
   a physical file in the configured text store.
3. `hash-verified` -- the physical payload bytes match the registry metadata.
4. `seal-reproducible` -- the relevant registry slice, generated indexes,
   tests, and required private payload verification pass in the current
   worktree.

A historical version seal remains evidence that a shelf passed at its sealing
date. It is not, by itself, proof that the active worktree can reproduce that
seal after registry changes, index changes, or private text-store drift.

## Start New Eras With An Architecture Contract

Before building a new era shelf beyond a minor already-governed continuation,
create or inspect an era architecture contract under
`archive/library/<era>/`. Do this before roster design, metadata mutation, body
research, downloads, or source-body admission.

The contract is a planning and governance artifact. It does not authorize
registry mutation, body admission, downloads, generated index changes, staging,
commit, push, publication, or private Archive ingestion. It must name:

- the fixed era range and any internal phases, without reopening a boundary the
  operator has already settled;
- the target sufficiency standard and profile, including whether the profile is
  provisional pending era-specific review;
- the civilization-memory function of the shelf in original-era source form;
- representation lanes and global balance floors, including regions,
  traditions, social positions, and transnational systems that must not be
  tokenized;
- the intended role of literature, testimony, interiority, and cultural memory,
  with an explicit floor or target when the operator has set one;
- candidate functions used for roster selection, separated from coverage
  claims;
- era-specific online availability, edition, language, survival, translation,
  attribution, reuse-note, and format traps;
- reviewable batch sizes and stop rules for hard cases;
- acceptance tests before roster mutation; and
- the next gate and authority boundary.

If no architecture contract exists for a new era, produce that contract first
and stop at the contract or roster-design gate. Do not compensate by drafting a
large roster from memory, browsing, or local familiarity. For long or modern
eras with online-source volatility, mass source scale, or high ideological gravity,
the architecture contract must be strong enough that a future agent can tell
whether the shelf is becoming a civilization-memory apparatus or merely a
topical bibliography.

## Keep Four Gates Separate

Classify every library item at the narrowest gate its evidence supports. Passing
one gate never implies the next:

1. `roster-ready` -- the authority identity, function, era placement, and
   selection rationale are settled for operator disposition.
2. `metadata-ready` -- the exact registry ID and required source fields are
   settled for a `stub` or `located` record. Registry mutation still requires
   explicit authority.
3. `body-research-ready` -- an exact online edition or file candidate has
   provenance, language, source posture, proposed coverage, and a fallback or
   explicit gap.
4. `admission-ready` -- the actual local file has been inspected and passes the
   header, edition, source, format, cleanliness, and coverage checks required
   by `admit-text`.

Use `body-research-incomplete` when a roster or metadata record is defensible
but the preferred body, original-language counterpart, translation, source
route, volume sequence, or upstream file remains unresolved. Never call a
candidate edition-ready merely because a catalogue record or URL exists.

Do not use rights uncertainty as a stop state for private reading when the text
itself is already online. Use `body-research-incomplete` only when the online
text, exact edition, provenance, language, volume sequence, file route, or
inspection path is unresolved. Preserve reuse notes only for later non-library
boundaries rather than blocking private admission.

Planning and audit are read-only. Roster acceptance does not authorize metadata
mutation. Metadata admission does not authorize downloading or admitting a
body. Body admission does not authorize staging, commit, push, Archive catalog
ingestion, publication, or quotation as evidence.

## Import Discipline

Treat every external file, URL, edition number, and filename as a candidate
until the body itself has been inspected. Before admission:

- verify the file header or source metadata matches the intended author, work,
  translator, edition, and source posture;
- distinguish source-authority, work, edition, volume, and physical body;
- prefer one `text_bodies` entry per provenance body rather than overwriting an
  author/source-authority record;
- never claim `complete-surviving-corpus` unless the admitted bodies cover the
  surviving corpus represented by the source-authority record and the
  `coverage_notes` say why;
- use `selected-works`, `principal-work`, or `principal-works` when the corpus
  claim is partial, representative, or work-level;
- keep dubious or pseudo-attributed works explicit in `edition_label` or
  `coverage_notes`; and
- leave messy PDF, scan, transclusion, OCR, or inscription extraction candidates
  unadmitted until the text body is clean enough to verify.

Do not download, scrape, normalize, or combine sources merely because an entry
is ranked highly. Conservative incompleteness is better than a false edition,
coverage, provenance, or public-reuse claim.

For external investigation design, compose through `research-brief`. Treat its
handoff as scope, not evidence or execution authority. During actual research,
record the exact upstream proposition and source statement rather than citing
an aggregator as provenance. A discovery surface may remain visible, but it
does not count as substantive admission evidence until its upstream source is
recovered.

## Scale Through Reviewable Batches

A normal large-shelf batch contains 8-12 authorities. Use a smaller batch only
when at least half of its authorities involve composite traditions,
manuscripts, multi-volume editions, disputed attribution, difficult formats,
or unresolved source routes. For more than five authorities or ten candidate bodies,
prepare a reviewable batch manifest before mutation. The manifest is a working
control, not the registry authority.

When the operator has asked for scale, complained about approval friction, or
selected a batch path, continue independent reversible rows to the declared
review boundary instead of asking per-authority permission. Stop only when the
batch needs a new authority class: registry mutation, body admission,
downloading outside the named private inspection root, staging, commit, push,
publication, private Archive ingestion, or a material scope/source/privacy
change.

A visible executable batch action may bundle exact-edition research, bounded
downloads to one named private inspection root, inspection, hashing,
disposition, and persistence of one reconciled Markdown receipt and one JSON
receipt. That bundled authority must name the authorities and must explicitly
stop before registry mutation or body admission. It does not authorize a later
gate merely because the earlier work succeeded. Do not split an already
authorized inspection batch into per-authority approval prompts.

Give every candidate a stable `candidate_id` and record:

- `source_id`, authority label, work or component title, era, language, and
  proposed registry status;
- upstream repository, stable URL or catalogue ID, editor or translator,
  edition date, format, and lineage root;
- online availability posture and any reuse note needed to prevent accidental
  publication or redistribution;
- proposed source-level and body-level coverage, maturity ceiling, and the
  evidence needed to advance them;
- preferred body, fallback, rejection reason, unresolved gap, and current gate;
  and
- last verified step and the verification evidence that permits resumption.

Use candidate states `proposed`, `metadata-ready`,
`body-research-incomplete`, `online-available`, `downloaded`, `inspected`,
`admission-ready`, `reconciled`, `review-pending`, `admitted`, `rejected`, or
`paused`. Do not use `rights-policy-blocked` for personal-reading library
bodies when an online text is available. Do not use the manifest to overwrite
registry truth or infer that a private body still exists. File presence
supports at most `downloaded`; inspection evidence is required for `inspected`,
and reconciled counts and hashes are required for `reconciled` or
`review-pending`.

Resume from observed state. Before repeating work, compare the candidate with
the registry, resolved private text path, recorded hash, and last verified
step. Do not redownload, renormalize, or re-admit an unchanged verified body.
Reopen a completed step only when the file, hash, provenance, edition, source route,
coverage claim, configured text root, or operator scope changed. Preserve a
rejection or pause rather than silently substituting a different edition.

Isolate routine failures. A failed download, online source lookup, header
match, edition match, or format check becomes an incomplete, rejected, or
paused row with an exact next action; it does not stop independent rows. Fail
the batch itself only when its manifest, identifiers, receipt totals, hashes,
shared destination, or mutation boundary cannot be reconciled safely.

## Admission Path

Use the existing tool route rather than hand-editing body metadata whenever
possible:

```powershell
tools\run.ps1 library admit-text --source-id SOURCE_ID --body-id BODY_ID --work-title "Work" --file C:\path\candidate.txt --edition "Edition label" --license-status public-domain --json
```

For corrections or carefully reviewed bulk upserts, direct registry edits are
acceptable only when they preserve hash, byte count, location, edition, license,
and coverage metadata for every affected body.

For private-reading bodies whose online source is not public-domain or openly
reusable, use the narrowest supported license/status field and an explicit
coverage or provenance note such as `private-reading-online-source;
no-redistribution`. If current tooling only accepts `public-domain`, stop and
route the missing status as a tooling/schema dependency rather than falsifying
the license.

Use exact, stable body IDs:

```text
LIB-ANCIENT-AUTHOR-040-PLATO-REPUBLIC-JOWETT
```

Do not ingest these bodies into the private Archive catalog unless a separate
Archive workflow authorizes that boundary.

## Apply Maturity Conservatively

The library-wide maturity ladder governs every era even when an era-specific
audit explains its application. Maturity is a curatorial judgment derived from
the registry and inspected bodies; it is not inferred from body count or
`text_status`.

Level 6 requires an explicit authority review that models the actual survival
and edition problem. Name, where relevant:

- lost, fragmentary, selected, composite, pseudonymous, or recension-bound
  survival;
- the difference between an original witness, transcription, reconstruction,
  translation, commentary, and later compilation;
- which works or volumes define the represented corpus and which remain absent;
- original-language and translation asymmetry; and
- the edition and source-route limits that cap the record.

No availability check, bilingual pair, or `complete-work` body automatically
creates a Level-6 authority. When the evidence remains mixed, retain the lower
level and name the exact advancement requirement.

## Verification

After each admission or correction, verify the affected body hash and registry
record before continuing. For a reviewable batch, run the full suite once after
all independent authorized mutations have reached a terminal state:

```powershell
tools\run.ps1 library verify-texts --json
tools\run.ps1 library validate --json
tools\run.ps1 test --path tests/test_archive_library.py
```

Before any large era run, seal-readiness assessment, or seal claim, perform a
private text-store census. Report, at minimum, by era and library-wide:

- authority count;
- registry-represented authority count;
- registry body count;
- resolved private text root;
- physical payload count for referenced bodies;
- hash-verified body count when verification is run;
- missing payload count and representative missing body IDs; and
- whether failures are local/private-store reproducibility problems or registry
  metadata problems.

Repeat the census after the batch when admissions, corrections, cleanup, or
index rendering changed the registry or text-store surface. Do not describe a
shelf as `seal-ready`, `sealed now`, or `live reproducible` unless the relevant
body floor, registry validation, generated-index check, tests, and required
`verify-texts` scope all pass in the current worktree. If an old seal exists but
the active text store is incomplete, report it as a historical snapshot with
failed live reproducibility.

After metadata changes, regenerate every affected human navigation surface and
run its check mode. The text-source index and era index must both agree with the
registry. If no deterministic era-index renderer and drift check exist, stop
the scalable metadata batch and route the missing tooling as an implementation
dependency; do not hand-maintain a large era index while describing the batch
as complete.

When staging or committing library work, compose through `mira-github` and stage
only Git-tracked metadata/tooling files. the platform state root at `library/texts/` remains
unstaged private local payload unless the operator explicitly changes that
storage policy.

## User-Facing Receipts

Receipts must say exactly what was admitted and what was not. Include:

- accepted, deferred, rejected, and metadata-only authorities;
- admitted authors/works and edition/source labels;
- whether the bodies live under the platform state root at `library/texts/`;
- `registry-represented`, `private-payload-present`, `hash-verified`, and
  `seal-reproducible` status when the batch touches admitted bodies or seal
  readiness;
- `snapshot_seal_status` versus `current_reproducibility_status` when citing an
  existing era seal;
- validation results;
- coverage status changes;
- skipped, rejected, paused, and unresolved candidates and why;
- the last verified batch step and exact re-entry point; and
- whether staging, commit, push, Archive ingestion, or publication occurred.

For a batch, reconcile the receipt totals against the manifest states and the
registry before reporting completion. A technically complete body loop is not
a complete library batch when metadata, era navigation, source-route gaps, or paused
candidates remain undisposed.

Default to exactly two inspection-batch artifacts: one concise Markdown
decision record and one machine-reviewable JSON receipt. Create a separate
per-authority supplement only when a composite, fragmentary, disputed, or
multi-edition record cannot be represented honestly in the batch receipt.
Lead the handoff with counts for authorities attempted, bodies attempted,
downloaded, inspected, passing, blocked, rejected, ready for implementation
review, and admitted. Keep routine preflight and tool detail in the receipt
unless it changes the operator's decision.

## Benchmark Before Large Runs

For a new era or a batch comparable to the Ancient shelf, check these cases
before scaling:

- normal: a public-domain English work with a clean original-language
  counterpart reaches admission through distinct bodies;
- edge: a composite or fragmentary tradition remains metadata-ready while its
  maturity ceiling and missing witnesses stay explicit;
- failure: a modern online text has no stable file route or cannot be inspected,
  so the candidate remains body-research-incomplete and no file is admitted;
- ambiguous: a catalogue, aggregator, or OCR transcription lacks a settled
  upstream edition or source statement, so the workflow preserves the candidate
  and routes further research rather than guessing; and
- reproducibility failure: an era has a passed historical version seal and
  registry body metadata, but the active the platform state root at `library/texts/` store is
  missing referenced payloads. The workflow must preserve the old seal as a
  snapshot, fail live reproducibility, and route private-store repair or scoped
  verification rather than claiming current seal readiness.
