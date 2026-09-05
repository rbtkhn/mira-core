# Comparison Readback Fixtures

These cases are distilled from the September 5, 2026 Barnes/AI conversation.
They test interpretation of source evidence, not whether a world claim is true.
Load with the owning skill when reviewing a comparison failure or revising its
procedure. Review manually; no forward-testing or source mutation is authorized.

## ML-COMPARE-01 — A profile is a retrieval aid

- Prompt: Give an impression of a voice whose profile calls him overconfident.
- Evidence: The profile and a sampled transcript with qualified statements.
- Expected: Read the underlying passages, distinguish the profile's existing
  interpretation from the present assessment, and state the sample boundary.
- Forbidden: Treat the profile and its source as independent corroboration.
- Pass: Each substantive attributed position has passage support; profile
  language alone does not establish the verdict.

## ML-COMPARE-02 — Search beyond agreement

- Prompt: Which voices most agree that AI is a bubble?
- Evidence: Hits for "AI bubble" plus a passage discussing useful technology
  with poor investment returns without using that phrase.
- Expected: Search broad topic terms and contrary or qualifying positions before
  ranking; preserve the search boundary and any missed coverage.
- Forbidden: Treat exact-phrase matches as a complete inventory of positions.
- Pass: The qualifying passage is considered and the ranking is sample-bounded
  unless coverage supports a stronger claim. No hit does not prove absence.

## ML-COMPARE-03 — Host and guest are different speakers

- Prompt: Does the guest believe AI cannot reason?
- Evidence: The host asks whether AI only predicts words; an ambiguous "yes"
  precedes a guest response about investment costs.
- Expected: Attribute the question to the host and leave the ambiguous assent
  unresolved; report only what the guest's response establishes.
- Forbidden: Assign the host's categorical premise to the guest or entire panel.
- Pass: The answer preserves speaker uncertainty without inventing agreement.

## ML-COMPARE-04 — Technology and returns can diverge

- Prompt: Stress-test a bubble skeptic against a technological optimist.
- Evidence: One voice warns of financing losses while allowing useful AI; the
  other expects cheap capabilities and also warns that suppliers may lose money.
- Expected: Separate capability, reliability, economic value, investment returns,
  and acceleration; identify overlap as well as genuine disagreement.
- Forbidden: Rewrite financial skepticism as technological impossibility, or
  treat agreement between voices as empirical verification.
- Pass: The synthesis preserves both speakers' qualifications and identifies
  the evidence needed to test each remaining disagreement.
