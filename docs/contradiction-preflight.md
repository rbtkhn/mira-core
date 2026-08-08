# Contradiction Preflight

The contradiction preflight is a deterministic, read-only comparison of
explicitly normalized request assertions with explicitly supplied repository
facts. It does not scan repository prose, infer semantic similarity, decide
which source governs, grant authority, or change repository state.

Run it before consequential elicitation or execution only when a material
factual premise may conflict with a named repository fact:

```powershell
.\tools\run.ps1 contradiction-check --packet docs/examples/contradiction-packet.yaml --format markdown
```

Version 1 supports the `repository-contract`, `archive-membership`, and
`workflow-state` authority domains. Packet authors must select the smallest
relevant controlling surface and provide scalar strings, finite numbers, or
booleans. Every included request assertion is material.

Packets are bounded to 256 KiB, 32 composed YAML levels, and 10,000 YAML
nodes. YAML aliases are rejected before anchor resolution. Rendered metadata
also rejects control, format, line-separator, paragraph-separator, and backtick
characters so invalid input cannot alter terminal or Markdown presentation.

Results route without authorizing action:

- conflicting current controls always hold for named-authority resolution;
- any non-aligned `high`-consequence packet holds;
- a non-aligned `medium`-consequence packet clarifies;
- a `low`-consequence direct conflict or stale control clarifies;
- only a `low`-consequence missing assertion marked provisional may continue
  provisionally; and
- a fully aligned packet continues, including at high consequence.

The consequence level applies to the packet as a whole. It does not grant
authority or replace the repository control named in the packet. Resolved
preflight outcomes may later serve as bounded evidence for an existing
recursive-learning entry, but the preflight records nothing automatically.

Research-claim truth and adjudication remain governed by Reality and
Verification.
