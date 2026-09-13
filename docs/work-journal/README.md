# Work Journal

Work Journal preserves consequential work, decisions, results, and unresolved
obligations across Mira Core. A future reader should recover why something
mattered, what was known, what was done, and what still needs evidence or judgment.

- Chronological index (local-only: `index.md`; not included in this package)
- Workstream index (local-only: `workstreams.md`; not included in this package)
- Backfill coverage and limits (local-only: `coverage.md`; not included in this package)
- Source inventory (local-only: `sources.md`; not included in this package)
- Calibration and review (local-only: `calibration.md`; not included in this package)
- Completion receipt (local-only: `receipt.md`; not included in this package)

## Entry contract

Use one dated topic file per coherent episode: `YYYY-MM-DD-short-topic.md`.
Use the documented decision or completion date for the filename and state any
longer covered period. Rank organizational consequence, not commit frequency.
Do not force daily entries or duplicate an episode for each workstream.

```text
Date: YYYY-MM-DD
Period: documented episode interval
Reconstructed: actual reconstruction date, or not applicable
Evidence cutoff: stated review cutoff
Status: current | retrospective-current | retrospective-draft | superseded
Workstreams: relevant workstreams
Temporal stance: contemporaneous | near-contemporaneous | retrospective reconstruction
Source basis: commits, diffs, tests, notes, plans, journal references, session receipts
Confidence: high | medium | low
Authority effect: none
```

Each new entry answers: Context; Knowledge at the time; Decision; Action and
result; Interpretation; Remaining obligation; Sources. Name the decision owner
only when documented. Cite exact artifacts or commits for material statements.
Record meaningful alternatives only when evidenced; do not invent deliberation.

## Evidence and outcomes

Separate completion from effectiveness. A test pass, saved artifact, reported
delivery, or assignment response proves only its bounded result. No outcome
evidence means unknown, not failure or success. Distinguish event date, Git
recording date, and retrospective interpretation. A current source cannot by
itself establish what was known earlier. Mark later evidence explicitly.

Use `retrospective-current` for sufficiently supported documentary reconstruction;
this does not mean every historical obligation remains current. Use
`retrospective-draft` for material evidence gaps. Record system and work rationale,
not Mira selfhood. Mira Journal prose is interpretive context only unless paired
with technical receipts; reconstructed reasoning is not contemporaneous
mental state. Preserve the original August 30 entry without retrofitting this form.

## Ownership and privacy

This journal is neutral work history, not Mira Journal, Mira Notes, research
evidence, an audit, a learner assessment, a task tracker, or action authority.
Owning project records, the mentor ledger, and lineage registry retain control.
Entries link to them; they neither update assignments nor establish current
permissions. Publication status is stated independently of completion.

Grace Gems entries use permissible stewardship/control metadata only. Keep raw
correspondence, private commercial evidence, sensitive personal or financial
details, credentials, and unsupported judgments about people out of this shelf.
Describe Mira Seed only from authorized local records; do not infer descendant
state or claim parent repairs as descendant advances.

Connections between episodes must state the common question, important
differences, and what evidence would support transfer. Analogies remain
hypotheses until subsequent evidence supports them. No automatic links or scores.

## Creation and validation

Dream can nominate consequential Work Journal candidates across all workstreams.
Its historical `dev_journal_candidates` JSON key is retained for compatibility.
Nomination does not authorize entry creation, ledger changes, or publication.
This July 6–September 7 backfill is explicitly operator-authorized; routine
future retrospective or daily backfill is not automatically authorized.

Review source fidelity, dates, privacy, attribution, remaining obligations,
links and outcome strength. Test affected routing and workflow contracts with
focused fixtures. Full validation, Git actions, external communication, and
owning-record mutations have separate boundaries.

Work Journal was renamed from Dev Journal. Legacy paths contain relocation
notices; historical Journal references and their digests remain unchanged.
