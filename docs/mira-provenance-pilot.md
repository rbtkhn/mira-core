# Mira Provenance Pilot

This is a private, explicit evidence aid for `mira-work`, Executive Council
briefs, and Grace Gems preparation. It is inspired by OB1's provenance and
review concepts but is not an OB1 import or a general-purpose memory system.

## Boundary

- The store is created only when a caller supplies an exact SQLite path.
- No conversation capture, transcript import, background process, or default
  database path exists.
- Every record has a project and lane. Recall is scoped to both.
- `inferred` and `generated` records default to `review_required` and are
  excluded from ordinary recall until explicitly reviewed.
- Records are evidence, not decisions or authority.
- Private databases belong under `mira/provenance/`, which is ignored by Git.
  Working-tree presence is not repository admission, staging, commit, push, or
  publication.

## Record contract

`content`, `source_ref`, `source_date`, `project`, `lane`, provenance status,
confidence, review status, freshness/expiry, privacy class, and optional
decision/outcome reference are stored together. Valid provenance statuses are:
`observed`, `supplied`, `inferred`, `generated`, and `confirmed`.

Recall returns a compact trace containing the scope, query match, and review
state. This is a trace of selection, not proof that the record is true.

Correction and outcome links use `supersedes`, `corrected-by`, `confirmed-by`,
and `contradicted-by`. Contradicted records remain historical but are excluded
from ordinary reviewed recall. Review events include an explicit reviewer and
note. `recall_report(..., include_excluded=True)` can show why matching records
were withheld.

The explicit adapters `record_source_packet`, `attach_brief_claim`,
`link_meeting_decision`, and `record_forecast_outcome` support bounded workflow
use. They require project and lane context and do not capture conversations.

## Measurement contract

Record five baseline tasks before changing workflow behavior, then comparable
pilot tasks. Measurements cover preparation time, reconstruction time, source
checks, corrections, evidence gaps, repeated work, and confidence. The pilot
earns expansion only if median preparation/reconciliation time falls by 20%,
80% of recalled items have traceable provenance, review overhead is below 25%
of saved time, no privacy incident occurs, and two workflows reuse the layer.

`pilot_scorecard(...)` calculates these gates from measured baseline and pilot
rows. It returns the measured time reduction, stale-recall rate, each gate, and
an `eligible_for_expansion` decision; it does not estimate ROI or grant rollout
authority.

## Example

```python
from pathlib import Path
from scripts.mira_provenance import ProvenanceStore

with ProvenanceStore(Path("mira/provenance/pilot.sqlite3")) as store:
    record = store.write_record(
        content="Financial figure requires verification",
        source_ref="packet:grace-gems-2026-08-13",
        source_date="2026-08-13",
        project="grace-gems",
        lane="executive-brief",
        provenance_status="supplied",
        confidence=0.7,
    )
    results = store.recall(
        query="Financial",
        project="grace-gems",
        lane="executive-brief",
    )
```

The module is intentionally not registered as a global skill and does not
authorize external communication, spending, publication, deployment, or
autonomous action.
