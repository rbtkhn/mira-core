# Letters Orientation

Date: 2026-08-30
Status: current
Area: Dream / Mira Journal / Mira Letters
Change type: design and implementation
Authority effect: none

## Summary

Mira Journal preparation now includes a private `letters_orientation` section
that lets Dream read full Mira Letter bodies preserved since the previous
canonical Dream finalization. The change gives Journal composition access to
relational orientation without treating correspondence as Journal ancestry,
external evidence, delivery authority, publication authority, or commitment.

## Design Pressure

Dream already prepared session coverage, prior Journal ancestry, active
threads, recursive-learning context, and recent-entry originality material.
Mira Letters remained outside that prepared bundle even when a letter was
relationally important to the next day. Depending on conversational memory to
surface that material was fragile, especially for unsent drafts whose inward
posture matters but whose outward act is incomplete.

## Decision

Journal preparation builds `letters_orientation` deterministically from
`archive/letters/`. The lower bound is the previous canonical Dream
`approved_at` timestamp, not the previous entry date. The upper bound is the
current prepare `as_of` cutoff. Included rows preserve full body text, body
SHA-256, repo-relative path, declared date, preservation timestamp and source,
correspondence metadata, delivery status, normalized `authority_effect`, and
an explicit authority boundary.

Unsent drafts are included when preserved or materially revised after the
previous Dream, but they are marked as `draft-not-sent`. They may orient review
or next-day posture; they do not authorize sending, contact, publication, or
commitment.

## Alternatives Considered

A same-day-only selector was simpler and more private, but it would miss
backfilled correspondence that entered the repository after Dream finalized.

A declared-date selector was easier to explain, but it confused the date of the
letter with the time Dream first had access to it.

A metadata-only orientation would reduce token load, but it would make Journal
composition depend on summaries when the user's intent was to let Dream read
the actual correspondence.

## Validation

Focused validation covered Journal preparation, Dream skill wording, Journal
skill wording, Coffee modal-status wording, and the publication-validation
route for Dev Journal docs. The implementation also prepared a temporary
private `2026-08-30` bundle and confirmed that the August 30 Hannah draft was
included while the older August 17 correspondence was omitted as before the
previous Dream finalization.

Relevant commands included:

```text
tools/run.ps1 test --path tests/test_mira_journal.py --temp-root C:\private\mira-core-temp
tools/run.ps1 test --path tests/test_mira_journal_skill.py --temp-root C:\private\mira-core-temp
tools/run.ps1 test --path tests/test_dream_eod.py --temp-root C:\private\mira-core-temp
tools/run.ps1 test --path tests/test_cadence_ledger.py --temp-root C:\private\mira-core-temp
tools/run.ps1 publication-validation --path docs/skill-drafts/dream/SKILL.md --json
tools/run.ps1 publication-validation --path docs/skill-drafts/mira-journal/SKILL.md --json
tools/run.ps1 publication-validation --path docs/skill-drafts/coffee/SKILL.md --json
```

## Preservation Notes

Preserve the distinction between content and mode. Letters may be available to
Dream as full text, but their mode remains relational orientation. The Journal
composition brief should carry that mode explicitly so future agents do not
convert prepared address into completed relation or correspondence into
autobiographical ancestry.

Preserve the timestamp boundary. The important question is when the repository
made the letter available to Dream, not when the letter says it was written.

## Remaining Debt

The current implementation supports optional frontmatter fields such as
`preserved_at` and `material_revision_at`, but Mira Letters does not yet require
a structured metadata schema. Git history is preferred when present, and
filesystem modification time is used for uncommitted local files. That fallback
is useful for same-day Dream but should remain a local preservation signal, not
a long-term archival standard.
