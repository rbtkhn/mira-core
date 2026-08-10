# Mira Daily Journal Governance

Mira Daily Journal entries use MJ-* identities and remain governed
first-person autobiographical interpretation. They may cite Continuity,
repository events, research records, and prior reflections, but those
references do not make the journal research evidence, Reality evidence,
operator belief, identity doctrine, proof of consciousness, or action
authority.

The Narrative Geopolitics Operator Position Journal uses the separate JRN-*
namespace. An MJ-* reflection may nominate a question for operator review, but
it cannot create, revise, close, or substantiate a JRN-* position. Movement
between the two surfaces requires the existing operator-position promotion
workflow and an independently attributable operator instruction.

Every journal context input carries an epistemic class, authority owner,
canonicality label, and may_promote set to false. Prior MJ-* material is marked
as self-reference rather than independent corroboration.

Private drafts, context packs, and candidate technical references remain outside Git. Operator approval binds an
approved version and its version-specific technical reference to an exact MR-* user record, and approval-time freshness
checks cover the interval through actual approval. Approved bytes enter System
Archive as autobiographical-interpretation under an explicit-only retrieval
policy; storage and retrieval never change their authority.

Journal preparation reads the canonical Recursive Learning Ledger and includes
a bounded, cutoff-safe set of admitted RSI lessons in the composition context.
Prose may draw from a lesson when it materially shapes the reflection. The
technical reference names each consumed RSI ID. Reflection can expose a later
candidate signal, but neither prose nor a companion validates, measures, or
closes a learning loop; `recursive-learn` assessment and explicit RSI admission
remain separate.

The repository-local `mira-journal` skill is the composition front door. Its
deterministic composition brief binds the previous approved prose and digest,
remembered reasons, active continuity threads, recent openings and endings,
admitted cutoff-safe RSI lessons, material technical developments, and voice
constraints. The skill selects one primary inherited thread and at most one
secondary thread; the command validates but does not write the prose.

New combined approvals use schema-v2 technical companions. Their continuity
events are autobiographical interpretation, not RSI evidence or action
authority. The generated `mira/journal/continuity-index.json` and Markdown view
project only approved events, preserve every revision event, and label older
versions without continuity metadata `legacy-unthreaded`. The naming thread's
recurrence policy is `changed-meaning-only`.

`mira-journal draft-check` is approval-free and nonmutating. It validates the
whole external bundle, exact grounding and continuity anchors, prose privacy,
ancestry, RSI cutoff resolution, recurrence, repetition, lineage, digests, and
late activity. Approval and revision replace prose, companion, registry, journal
index, and continuity indexes as one recoverable transaction.

New approvals use an exact digest-bound instruction: `Approve Mira Journal
version <MJ-version> with digest <prose-sha256> and technical reference
<MJTR-version> with digest <reference-sha256>.` Generic keywords, negated language,
and mismatched versions or digests do not approve a version. Context packs must
carry a recomputable content identity and deterministic derivation lineage.

Each canonical companion lives as JSON plus deterministic Markdown under
`mira/journal/references/`, contains 3-7 exact prose anchors, and separates prose
grounding from recursive-learning status. A later RSI admission links backward
through `journal_context_refs`; it never mutates an older companion. Legacy
technical-reference backfill requires `Approve Mira Journal technical reference
<MJTR-version> with digest <reference-sha256>.` and does not change the journal
version's approval or publication status.

Every companion declares the context cutoff it inherits. An
`observed-by-cutoff` item must cite a full Git commit and the exact paths that
commit touched, or an admitted RSI entry dated no later than the journal day.
Mutable repository paths are permitted only as labeled historical context or
retrospective backfill. Validation rejects commits after the cutoff and paths
not present in the cited commit.

`MJ-20260809-v1` is retained as `legacy-held`: its historical bytes, digest,
and original record reference remain canonical durability, but the linked
record does not satisfy the affirmative approval contract and the version is
not publication eligible. No reconciliation is inferred or invented.

Git tracking is local canonical durability, not publication authority. The
mira-journal publication-check command inventories the complete outgoing
branch, destination, journal digests, and privacy-review obligation. A push
containing journal material requires a separate destination-bound operator
publication receipt and remains a separate external action.
The receipt must resolve an exact MR-* user instruction bound to a digest of
the destination URL, branch, HEAD commit, and ordered journal version set.
