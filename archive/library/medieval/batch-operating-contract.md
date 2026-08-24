# Medieval Library Batch Operating Contract

Status: `project-local-control`
Scope: Medieval Library build, 476–1453
Controlling workflow: `docs/skill-drafts/library-import/SKILL.md`
Authority effect: none by itself

## Purpose

Build the Medieval shelf at approximately Ancient authority-count scale without forcing the operator through one-authority approval loops. This contract organizes already authorized work into reviewable batches while preserving the Library Import workflow's provenance, rights, coverage, private-store, and publication boundaries.

This file governs project execution convenience. It does not override Library Import, authorize admission, or relax evidence standards.

## Default Batch

A normal batch contains **8–12 authorities**. Use a smaller batch only when at least half of its authorities involve composite traditions, manuscripts, multi-volume editions, disputed attribution, difficult formats, or unresolved rights.

Group authorities by implementation behavior rather than civilizational quota:

- clean public-domain or openly licensed text routes;
- multi-volume historical editions;
- composite, recension, or textual-tradition records;
- restricted, metadata-only, or translation-gap records;
- non-text formats requiring a later extraction decision.

One authority may contribute several physical bodies. Batch size is measured by authorities; body count is reported separately.

## One Authorization, One Review Boundary

When the operator executes a named inspection batch, that authorization covers the following reversible work for every authority named in the visible batch scope:

1. recover exact upstream edition and license metadata;
2. download bounded candidate files into the named private inspection root;
3. inspect headers, editions, formats, encoding, structure, rights statements, hashes, byte counts, and coverage limits;
4. preserve rejected, blocked, and unresolved candidates in the batch ledger;
5. write one reconciled Markdown receipt and one JSON receipt; and
6. run read-only reconciliation checks against the roster and actual private files.

Routine source failure does not end the batch and does not require another operator decision. It becomes a ledger disposition.

The batch stops once at the **admission review boundary**. The inspection authorization does not cover:

- adding or changing registry records;
- moving or copying bodies into the configured private Library text store;
- setting `available`, `verified`, or `reviewed` status;
- rendering or changing an era index;
- staging, committing, pushing, publishing, or Archive catalog ingestion.

A later batch-level implementation authorization may cover all passing authorities together, with failures excluded automatically.

## Batch State Machine

| State | Meaning | Durable evidence |
| --- | --- | --- |
| `scoped` | Authorities, candidate routes, ceiling, and private root are named. | Batch plan or accepted roster slice |
| `bound` | Exact upstream files and fallbacks are identified. | Receipt candidate rows |
| `downloaded` | Candidate files exist only in the private inspection root. | Path, URL, bytes, preliminary hash |
| `inspected` | Identity, edition, rights, format, cleanliness, structure, and coverage were checked. | Per-body inspection fields |
| `reconciled` | Counts, IDs, hashes, dispositions, and non-authorizations agree. | Markdown and JSON batch receipts |
| `review-pending` | Batch has reached its one operator review boundary. | Passing/blocking summary |
| `implementation-authorized` | Operator explicitly authorized the visible batch-level registry/import action. | Exact executable selection or direct command |
| `admitted` | Passing bodies were copied through Library Import and registry metadata changed. | Import and validation receipts |
| `closed` | Validation passed and all failures have explicit next actions. | Final batch receipt |

No state transition is inferred from file availability. `downloaded` is not `inspected`; `inspected` is not `admission-ready`; `admitted` is not `verified` or `reviewed`.

## Required Batch Receipts

Each inspection batch produces exactly two repository artifacts:

- `portable-batch-NN-inspection.md` — concise human decision record;
- `portable-batch-NN-inspection.json` — machine-reviewable manifest and receipt.

Do not create separate proposal files for every straightforward authority. Per-authority supplemental receipts are reserved for unusually complex records whose evidence cannot be represented honestly in the batch schema.

The JSON receipt must include:

- batch ID, date, private root, authority count, body count, source ceiling, and mutation boundaries;
- stable candidate and proposed source IDs;
- exact upstream URL, repository, edition, translator/editor, format, private filename, bytes, and SHA-256;
- header, encoding, structure, wrapper, and cleanliness results;
- rights status and jurisdictional uncertainty;
- body-level and authority-level coverage ceilings;
- disposition: `pass`, `blocked`, `rejected`, or `unresolved`;
- blocker and next action for every non-passing body;
- whether a fallback was attempted;
- reconciliation totals; and
- explicit statements that admission, registry mutation, staging, commit, push, and publication did or did not occur.

## Exception Policy

Failures are isolated to their body or authority unless they compromise the batch manifest itself.

| Condition | Disposition |
| --- | --- |
| Download unavailable or unstable | `blocked`; record URL and fallback |
| Header or edition mismatch | `rejected`; do not normalize into compliance |
| Unknown or restricted rights | `blocked`; never propose admission status |
| Unsupported PDF, scan, or HTML | `blocked` unless an already authorized workflow produces a clean provenance-preserving text body |
| Mixed-authority anthology | `blocked` pending separately authorized extraction or a defensible anthology authority boundary |
| Missing volumes or books | `pass` only with a partial body ceiling; otherwise `blocked` |
| Original and translation do not align | preserve both edition identities; prohibit equivalence claims |
| One authority fails | continue every independent batch row |
| Receipt counts or hashes disagree | fail the batch at reconciliation; repair before review |

## Coverage and Maturity Rules

- Body completeness describes only the named physical edition body.
- Authority completeness remains separately governed by source-level coverage.
- Prefer `partial-work`, `selected-passages`, `principal-work`, or `principal-works` over an inflated claim.
- Never infer `complete-surviving-corpus`, English/original-language equivalence, reviewed status, or Level 6 maturity from file presence.
- Admission alone normally establishes only a readable available body. Verification and maturity advancement require their own evidence.
- A rights-clear English body may pass while its original-language counterpart remains an explicit gap.

## Progress Surface

Every batch handoff reports this compact shelf dashboard:

| Measure | Required count |
| --- | ---: |
| Selected roster authorities | yes |
| Edition-triaged authorities | yes |
| Authorities attempted in this batch | yes |
| Candidate bodies attempted | yes |
| Bodies downloaded | yes |
| Bodies inspected | yes |
| Passing bodies | yes |
| Blocked bodies | yes |
| Rejected bodies | yes |
| Authorities ready for batch-level implementation review | yes |
| Authorities admitted | yes |

Report only material exceptions after the dashboard. Internal preflight, tool, and schema detail belongs in receipts unless it changes the decision.

## Interruption Recovery

An interruption preserves every completed state transition supported by durable evidence.

On resume:

1. inspect the existing private batch root and batch artifacts;
2. verify hashes for already downloaded files rather than redownloading them;
3. identify the first incomplete state transition;
4. resume from that transition;
5. do not rerun successful downloads, renders, or inspections merely because the prior conversational turn ended; and
6. state the recovery boundary in one sentence.

If a command returned a live process identifier, resume that process until terminal. If a completed process lost its displayed output, run only the smallest missing diagnostic rather than repeating the workload.

After an unrelated workflow such as Coffee interrupts the project, the next Medieval continuation resumes the suspended batch automatically unless the operator changes scope.

## User-Facing Cadence

During execution, communicate only when one of these occurs:

- the batch is bound;
- a material cross-batch blocker emerges;
- a long-running process continues past the normal update interval;
- the batch reaches reconciliation; or
- the single admission review boundary is ready.

Avoid per-authority approval prompts, repeated statements of unchanged non-authorizations, and internal tool narration. Lead with counts, outcomes, and exceptions.

## Batch-Level Implementation Review

At `review-pending`, present one exact action covering all passing rows. The visible action must name:

- source records to add or update;
- bodies to admit;
- bodies explicitly excluded;
- private text-store destination behavior;
- coverage and status ceilings;
- validation commands; and
- the continuing prohibition on staging, commit, push, publication, and Archive ingestion.

If selected, implement all independent passing rows together. A failed row remains blocked without rolling back successful independent rows, but reconciliation and validation must report the partial result honestly.

## Validation After Authorized Implementation

Run the governing checks once per batch:

```powershell
tools/run.ps1 library validate --json
tools/run.ps1 library render-index --check --json
tools/run.ps1 library verify-texts --json
tools/run.ps1 test --path tests/test_archive_library.py
```

When the accepted Medieval implementation contract adds an era-index drift validator, include it in the same batch validation pass.

## Current Project Application

Portable Batch 03 is the first batch governed prospectively by this contract. Its six authorities are Bede, Procopius, Anna Komnene, the Benedictine Rule tradition, Einhard, and the Magna Carta tradition. Existing private downloads and completed inspections are preserved. The next task is to write its two reconciled receipts and stop at `review-pending`; no admission is implied.
