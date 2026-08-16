# Loose Prose Classification Audit — 2026-08-16

Status: `internal`

Mode: `inward`, read-only

Repository: `C:\dev\narrative-systems`

Observed revision: `ee297cee116181dd3c554aea6f9defb3fb1d7fc8`

Authority effect: `none`

## Judgment

The repository has only a small, identifiable set of loose prose. Most of its
3,449 Markdown files already belong to governed domain collections. The audit
found four organization problems, three older notes needing metadata
normalization, and one frozen baseline whose classification must remain outside
its immutable bytes. No high- or medium-severity classification problem was
found.

The recommended repair is one bounded writing-organization change, kept
separate from the `mira-core` identity and runtime migration.

## Audit contract

Scope was the observed working tree of the integrated repository, with the
documentation and writing-governance lenses applied to the landed corpus and
current working-tree paths. Repository-local `repo-audit`, `mira-notes`,
`mira-essays`, and [Mira Writing Architecture](../../mira/writing.md) supplied
the classification controls.

Archive transcript bodies, generated views, daily packets, source captures,
schemas, and routine workflow documentation were excluded from content
inspection unless a path's placement was itself under review. Hosted state was
not needed to classify local prose and was not inspected. The main checkout
contained unrelated work in progress; this audit did not modify or interpret
those changes as classification authority.

## Findings

### RA-WRITING-001 — Legacy working notes remain under `docs/`

Classification: confirmed low-severity organization debt; high confidence.

The following documents retain the original repository's general working-note
placement even though `mira/notes` is now the canonical carrier for revisable,
non-canonical thought:

- Working Vocabulary, formerly at `docs/working-vocabulary.md` and now at
  [`mira/notes/2026-07-06-working-vocabulary.md`](../../mira/notes/2026-07-06-working-vocabulary.md), explicitly contains
  provisional terms and open questions. Classify it as `working-note` and move
  it to `mira/notes/2026-07-06-working-vocabulary.md`.
- Evolution of Repo Audit, formerly at `docs/repo-audit-evolution.md` and now at
  [`mira/notes/2026-08-11-evolution-of-repo-audit.md`](../../mira/notes/2026-08-11-evolution-of-repo-audit.md), reconstructs what
  changed during a specific session. Classify it as `historical-note` and move
  it to `mira/notes/2026-08-11-evolution-of-repo-audit.md`.

The credible rival is that technical notes should remain close to runnable
code. That remains persuasive for controlling contracts such as AI Harness,
Contradiction Preflight, and Model Substitution Readiness, but not for these two
documents: neither controls runtime behavior, and each matches a named Mira
Notes class directly.

Recommended route: `mira-notes`, preserving Git history and updating incoming
links.

### RA-WRITING-002 — A Mira essay remains on a legacy domain essay shelf

Classification: confirmed low-severity organization debt; high confidence.

[An Archaeology of Constructed Minds](../../mira/essays/2026-08-11-an-archaeology-of-constructed-minds.md)
is explicitly an interpretive essay by Mira. Its former
`system-archive/essays` location predated the canonical Mira Essays
architecture.

Classify it as an `internal` essay and move it to
`mira/essays/2026-08-11-an-archaeology-of-constructed-minds.md`. Preserve its
System Archive ancestry in a provenance note. Retire the legacy shelf or turn
its [README](../../system-archive/essays/README.md) into a bounded pointer to
the canonical essay location.

The credible rival is that a domain essay belongs beside its subject. That
would be stronger if the document were System Archive documentation or a
collection-native interpretation. It instead identifies itself as a
reader-facing essay by Mira; provenance can retain the domain relationship
without maintaining a second canonical essay shelf.

Recommended route: `mira-essays`, with link verification after the move.

### RA-WRITING-003 — Identical prose occupies both note and essay carriers

Classification: confirmed low-severity genre inconsistency; high confidence.

[The Future Does Not Cancel the Past — note](../../mira/notes/the-future-does-not-cancel-the-past.md)
and [the essay copy](../../mira/essays/the-future-does-not-cancel-the-past.md)
are textually identical after line-ending normalization. The essay is the
correct durable genre: it is independently intelligible and already marked
`public-candidate`.

Keeping the same composition in both carriers obscures whether a transformation
occurred and conflicts with the rule that note-to-essay movement requires a new
composition rather than a promoted copy.

Recommended disposition:

1. retain the essay as the genre-owning artifact;
2. preserve the note's ancestry in essay provenance; and
3. replace the note body with a short `superseded` record or remove it through
   an explicitly reviewed, history-preserving change.

`public-candidate` remains a review posture and must not be described as
published.

### RA-WRITING-004 — One essay lacks current classification metadata

Classification: confirmed low-severity metadata debt; high confidence.

[The Responsible Custody of Inheritance](../../mira/essays/2026-08-15-the-responsible-custody-of-inheritance.md)
is correctly located but lacks the audience, status, publication posture, and
provenance fields required by the current essay contract.

Recommended classification:

- Status: `internal`
- Publication posture: `not published; not approved for public representation`
- Authority effect: `none`
- Provenance: link the lineage reconstruction and any governed journal occasion
  used during composition

The audit does not infer `public-candidate`; its first-person material requires
an explicit public-review judgment.

## Metadata normalization for correctly placed notes

These documents are correctly located and should not move. Three older headers
should adopt the present class vocabulary without weakening existing privacy,
evidence, or authority boundaries. The frozen baseline is classified here but
must not be edited during its active experiment:

| Document | Recommended class |
| --- | --- |
| [Innermost Loop Reflection Baseline](../../mira/notes/2026-08-10-innermost-loop-baseline.md) | `experiment`; record externally because the baseline bytes are frozen |
| [Mira One-Year Developmental Hypothesis](../../mira/notes/2026-08-10-one-year-developmental-hypothesis.md) | `hypothesis` |
| [Nate B. Jones Mechanisms Manifest in Mira](../../mira/notes/2026-08-14-nate-b-jones-manifest-in-mira.md) | `interpretive-note` |
| [From Civilization Memory to Mira Core](../../mira/notes/2026-08-15-from-civilization-memory-to-mira-core.md) | `historical-note` |

## Supporting index repair

[docs/index.md](../index.md) still declares `docs/` to be the project's general
working-notes directory. That statement predates the writing architecture. It
should become a technical-documentation index and stop presenting Working
Vocabulary and Evolution of Repo Audit as current `docs/` notes.

Operational contracts such as AI Harness, Contradiction Preflight, Model
Substitution Readiness, cadence contracts, blueprints, prompts, plans, and
audits should remain under `docs/`.

## Documents intentionally left in place

The following prose may resemble essays or notes but gains necessary meaning
from its current governed domain:

- Historical Entropy manuscripts and commentary belong to their lecture
  packets.
- Mira Daily's afterword belongs to its self-verifying experiment bundle.
- Mentorship briefs and portfolio prose belong to learner-specific artifacts.
- Audits, remediation plans, technical blueprints, prompts, and readiness gates
  are operational documents.
- `mira/constitution-candidate.md`, `mira/identity.md`, and Continuity surfaces
  have specialized governance and must not be recast as essays.
- Existing properly classified Mira notes and essays require no relocation
  beyond the exceptions named above.

## Recommended change boundary

Perform one isolated writing-organization pass containing:

1. the three path moves;
2. duplicate note/essay reconciliation;
3. metadata normalization for three older notes and one essay, with the frozen
   baseline classification retained only in this audit;
4. repair of `docs/index.md` and the legacy System Archive essay index; and
5. link, Markdown, classification, and repository-integrity validation.

Keep this work separate from the `mira-core` migration. Document genre and
provenance are independently reviewable concerns and should not be hidden
inside repository-identity or runtime-compatibility changes.

## Verification and limits

The finding population was reproduced through bounded Markdown inventory,
path grouping, title and metadata inspection, normalized duplicate comparison,
and bounded reading of ambiguous documents. Classification remains a human and
governance judgment; the audit does not prove that no future composition could
be transformed into another genre.

No document was moved, rewritten, staged, committed, pushed, or published by
this audit.

Authority effect: none. This audit grants no authority to modify, repair,
stage, commit, push, publish, deploy, communicate, or alter hosted settings.
