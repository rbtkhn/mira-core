# Historical Reference Schema

Every occurrence carries `occurrence_id`, `voice`, `source_id`, `archive_path`, `date`, `title`, `quote`, `reference_id`, `parent_period`, `attribution_confidence`, `mechanism_suggestions`, `crosswalk_suggestions`, `risk_score`, and `review_status`.

Run payloads may also carry a bounded `characterizations` list. Each
characterization records `voice`, `characterization`, `analytical_function`,
`characterization_confidence`, `backtest_sample_count`, `backtest_date_count`, `date_coverage`,
`coverage_gaps`, `falsifier`, `forecast_linkage`, `source_ids`,
`archive_paths`, `pilot_occurrence_ids`, `backtest_occurrence_ids`, and
`backtest_status`. Supported functions are `order-theory`,
`civilizational-endurance`, `strategic-failure-analogy`,
`operational-comparison`, `strategic-precedent`, and
`other-review-required`. Confidence is one of `supported`,
`partially-supported`, `untested`, or `overbroad`.

Backtest inputs are explicit source IDs or archive paths. Missing dates are
coverage gaps, never negative evidence. A characterization is `supported`
only with at least three distinct dated backtest samples; fewer samples are
`partially-supported` or `untested`. Generated `characterization_review_queue`
entries preserve low-confidence characterizations and coverage gaps for review.
Characterization records are
analytical review artifacts and do not adjudicate historical truth or
authorize forecast, publication, or synthesis changes.

Source fingerprints combine source ID, normalized archive path, content SHA-256, taxonomy version, detector version, and mechanism version. Review overrides use `voice|source_id|reference_id|paragraph`.

Graph exports use deterministic node IDs: `voice:<slug>`, `source:<id>`, `reference:<voice>:<id>`, `mechanism:<id>`, `crisis:<id>`, and `forecast:<id>`.
