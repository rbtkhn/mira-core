# Historical Reference Schema

Every occurrence carries `occurrence_id`, `voice`, `source_id`, `archive_path`, `date`, `title`, `quote`, `reference_id`, `parent_period`, `attribution_confidence`, `mechanism_suggestions`, `crosswalk_suggestions`, `risk_score`, and `review_status`.

Source fingerprints combine source ID, normalized archive path, content SHA-256, taxonomy version, detector version, and mechanism version. Review overrides use `voice|source_id|reference_id|paragraph`.

Graph exports use deterministic node IDs: `voice:<slug>`, `source:<id>`, `reference:<voice>:<id>`, `mechanism:<id>`, `crisis:<id>`, and `forecast:<id>`.
