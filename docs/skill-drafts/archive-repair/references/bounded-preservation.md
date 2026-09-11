# Bounded preservation checks

Use only for an authorized preservation or reconciliation batch, including
resumption after interruption. Keep mutation, verification, and receipts
separately observable; this reference grants no transfer or broader audit authority.

- Freeze the selected logical paths, expected hashes and prior version IDs.
  Recheck current state before writing; preserve both versions when reconciling.
- Verify decompressed object bytes against the frozen source hash and byte count
  in each required store. Verify retained prior objects separately.
- Build the record/version-to-FTS-rowid mapping once for the bounded batch.
  Compare each indexed body to the expected decoded source text, then use a
  supported search expression constrained to that rowid. Avoid a full-catalog
  join or independent full-text scan for every record.
- Keep three results distinct: object-byte integrity, indexed-text equality,
  and query retrieval. A tokenization or query-syntax failure does not prove
  body loss; record the failed probe, correct its semantics, and rerun only the
  affected verification. Do not silently replace a failed required search test
  with a weaker one.
- After interruption, inspect committed store state before retrying. Reuse
  matching objects and versions; add only absent work. Verify parity before
  writing a success receipt. Missing receipts prove neither success nor failure.

Reuse existing backend validators where they cover the bounded claim. These
checks establish preservation and retrieval, not transcript accuracy, rights,
event verification, Library review status, or independent off-device backup.
