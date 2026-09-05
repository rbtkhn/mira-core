# Archive Density

Archive density is a triage signal for Narrative Geopolitics daily work. It
measures how much manifest-backed source material a day has, then compares that
source base with forecast hooks, operational claims, and issue-story load.

Density does not verify claims, create consensus, or promote archive assertions
into facts. It helps decide where to spend review effort.

## Definitions

- `manifest_sources`: count of central manifest rows for the date.
- `thin`: `0` to `3` manifest sources.
- `normal`: `4` to `6` manifest sources.
- `dense`: `7` or more manifest sources.
- `very_dense`: overlay for `13` or more manifest sources; the primary density
  class remains `dense`.
- `forecast_hooks`: unique hook IDs visible in the daily stack.
- `same_day_hooks`: hook IDs whose date matches the run date.
- `carried_hooks`: hook IDs whose date predates or differs from the run date.
- `opc_claims`: unique `OPC-*` claims visible in the daily stack.
- `issue_stories`: `lead` plus `brief` rows declared in the synthesis `Issue Story Desk`.
- `narrative_load_ratio`: `(forecast_hooks + opc_claims + issue_stories) / manifest_sources`.

When a day has zero manifest sources, the load ratio is reported as `0.0`;
absence of sources is an intake state, not an analytical denominator.

## Triage Labels

- `thin-but-pivotal`: a thin day carries hooks, operational claims, or selected issue stories.
- `dense-synthesis-check`: a dense day deserves voice triangulation and issue-selection review.
- `overclaim-risk`: a thin day has narrative load at least equal to its source count.
- `underuse-risk`: a dense day has two or fewer load-bearing hooks, claims, and stories combined.
- `verification-priority`: any day with `OPC-*` load.

These labels are prompts, not verdicts. A thin day may be correct and pivotal;
a dense day may still have one clear object.

## Benchmark Signals

`archive-audit` also reports benchmark signals for scoped archive health:

- `landed_horizon_completeness_pct`: share of non-future scoped days with at
  least one manifest row.
- `calendar_scope_completeness_pct`: same count divided by the requested
  calendar span, including future/unlanded days.
- `future_unlanded_days`: requested days beyond the manifest horizon; these are
  not coverage gaps.
- `file_presence_pct`: scoped manifest rows whose source files are present.
- `routing_completeness_pct`: scoped rows with at least one voice route.
- `warning_distribution`: warning counts by rule ID.
- `provisional_routing_warnings`: landing-time enrichment debt; not a defect by
  itself.
- `repair_candidate_warnings`: higher-signal warnings such as section metadata
  mismatch or weak Duran/Mercouris provisional metadata.
- `top_voice_share_pct` and `top_3_voice_share_pct`: concentration checks for
  voice balance.
- `top_host_share_pct` and `top_3_host_share_pct`: concentration checks for
  host balance.

Use completeness and fullness to decide review attention, not truth. A complete
and dense day may still be analytically wrong; a thin day may still capture the
decisive object.

## Monthly Completeness Certification

For a Narrative Geopolitics month, `archive-audit --month YYYY-MM` also reads
the frozen contract at `work/coverage/contracts/YYYY-MM.json` and append-only
evidence receipts at `work/coverage/receipts/YYYY-MM.jsonl`.

Certification is additive to structural audit disposition. It remains
`ineligible` when the contract is absent, malformed, cross-shelf, or unfrozen;
`in-progress` until the manifest horizon reaches month end; and otherwise
`pass` or `fail` according to these hard gates:

- structural integrity;
- the manually declared daily, voice-tier, and Tier B channel floors, with
  accepted evidence receipts for justified shortfalls;
- explicit ASR, speaker-attribution, sectioning, and quotation-readiness
  dispositions for every transcript;
- one accepted monthly diversity disposition; and
- issue-stage daily validation for every landed day.

Core voices require five transcripts, rotation voices require two, and watch
voices carry no acquisition quota. Voice membership and Tier B channel floors
are operator-declared; the audit must not infer or optimize them. A late
declaration remains visible but does not prevent a later pass. These rules
apply only to Narrative Geopolitics and must not read or count Singularity
Science, Moonshots, or Innermost Loop collections.

## Layered Monthly Completeness

Monthly completeness has three distinct claims that must not be collapsed or
mistaken for factual verification:

1. Historiographic completeness: whether the month preserves a usable
   historical record.
2. Strategic completeness: whether the month supports mechanism-level
   retrospective judgment.
3. Issue readiness: whether each landed day can produce current, reproducible
   reader-facing issue output.

The diagnostic numeric month score should reflect all three layers. Formal
certification remains stricter: a month may receive `certified-complete` only
when every hard gate passes, including issue readiness and governance.

Historiographic completeness considers continuous calendar horizon,
manifest-backed source coverage, transcript or body availability, provenance,
local file presence, voice and host recurrence, disclosed concentration and
missing perspectives, and processing dispositions for ASR, attribution,
sectioning, and quotation readiness. It answers whether a future reader can
reconstruct what the archive saw, from whom, and with what limits.

Strategic completeness considers continuity of crisis objects across days,
actor constraints and incentives over time, represented rival mechanisms,
forecast or review hooks, operational-claim boundaries where claims matter,
and enough density and recurrence to distinguish signal from one-day noise. It
answers whether the month can support retrospective strategy rather than only
source storage.

Issue readiness should be scored in tiers:

- `issue_ready`: daily validation has no failures; generated issue output is
  current or warnings are nonblocking.
- `issue_repairable`: the daily stack is substantive, but source accounting,
  stale digest, or deterministic rendering repair remains.
- `daily_stack_ready`: canonical daily files exist, but substantive
  placeholders, missing deepening, or incomplete issue-schema work remain.
- `not_ready`: no complete daily stack exists for a manifest-backed day.

For certification, every landed day must reach `issue_ready`; partial credit
does not satisfy the hard gate. For monthly scoring, tiers may receive partial
credit because historiographic and strategic usefulness can survive unfinished
editorial rendering. The recommended diagnostic issue-readiness weights are
`issue_ready = 1.0`, `issue_repairable = 0.6`, `daily_stack_ready = 0.35`, and
`not_ready = 0.0`.

This preserves the publication gate while preventing unfinished issue rendering
from misdescribing the historical corpus as absent or weak.

## Strategy-Notebook Quality

Strategy-notebook quality is an advisory layer above monthly completeness
certification. It assesses the interpretive value of the monthly strategy
notebook as a historical-strategic record. It does not certify archive
completeness, source truth, publication readiness, forecast resolution, or
operational authority.

A high-quality strategy notebook asserts that the month has not only been
processed, but rendered into coherent judgment. A future reader should be able
to reconstruct the sequence of strategic problems, why each day mattered, how
mechanisms evolved, where source convergence appeared, and where verification
boundaries remain.

Use this 0-5 advisory scale:

- `0`: absent.
- `1`: present but mostly boilerplate.
- `2`: usable but uneven notes.
- `3`: solid internal historical-strategic record.
- `4`: strong interpretive synthesis layer.
- `5`: publication-quality strategic apparatus, still source-bounded.

Score the layer separately from certification. A certified-complete month may
still have an uneven strategy notebook, and an excellent notebook cannot cure
missing hard gates. Use the score to guide review priority, rewrite effort, and
month-over-month maturation.

When judging the score, consider:

- strategic specificity: each day identifies a real mechanism, constraint,
  actor problem, or decision-relevant shift rather than summarizing topics;
- historiographic placement: each day explains why the date matters in the
  month sequence;
- source discipline: assertion, convergence, inference, uncertainty, and
  verification need remain distinct;
- comparative usefulness: the notebook helps compare voices, theaters,
  mechanisms, and time slices;
- prose integrity: the writing is coherent enough for serious internal use
  without boilerplate, truncation, or mechanical phrasing.

For August 2026, the advisory quality score after certification repair is
`3.7 / 5`: a solid internal historical-strategic record with coherent daily
placement and preserved evidence boundaries, but not yet a fully mature
interpretive synthesis layer because several generated entries remain less
individually authored than the strongest strategic-memorandum days.

## Operating Use

Use density after source-accounting validation and before synthesis deepening.

- Thin days: check caveat language, hook necessity, and whether issue copy asks too much of the source base.
- Normal days: use density as context, not as an action trigger.
- Dense days: check whether voice comparison, issue selection, and held-story decisions are explicit enough.
- Very dense days: treat the dense-day review as mandatory before deepening,
  especially issue selection and voice triangulation.
- `OPC-*` days: treat density as prioritization only; packet support still controls public factual use and forecast resolution.
- Repair-candidate warnings: reconcile archive/accounting quality before using
  the day as a stable benchmark.
- Provisional routing: track as fullness debt unless another finding names a
  concrete repair candidate.

Run density as part of the canonical archive audit:

```powershell
.\tools\run.ps1 archive-audit --start-date YYYY-MM-DD --end-date YYYY-MM-DD --format markdown
.\tools\run.ps1 archive-audit --month YYYY-MM --format json
```

`archive-density` remains a deprecated compatibility route with its existing
optional `--markdown`, `--csv`, and `--json` artifact outputs. New work should
use stdout from `archive-audit`; neither command alters canonical archive or
daily files.
