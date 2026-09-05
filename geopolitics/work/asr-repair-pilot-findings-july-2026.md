# ASR Repair Pilot Findings

Date:

- `2026-07-09`

Scope:

- Batch A from [asr-repair-pilot-batch-a.txt](asr-repair-pilot-batch-a.txt)

## What We Ran

We executed a bounded pilot using:

```powershell
.\tools\run.ps1 asr-repair --list-file narrative-geopolitics\work\asr-repair-pilot-batch-a.txt
```

This pass force-reran transcript sectioning on the six Batch A files after the
section-label extractor was sharpened.

## Files Reprocessed

- `2026-06-01` Davis warhawks
- `2026-06-01` Dialogue Works Baud
- `2026-06-01` Judging Freedom Sachs
- `2026-06-02` Dialogue Works Helmer
- `2026-06-02` Dialogue Works Wilkerson
- `2026-06-02` Davis / Macgregor

## Immediate Outcome

All six pilot files were successfully reprocessed.

Headline result:

- section labels improved materially across the batch
- the worst phrase-led ASR headings were removed
- the archive is more navigable even before deeper wording repair

## What Improved

The old headings often looked like transcript fragments:

- `Policy For Even A Minute`
- `Such They Started To Bomb`
- `In A Bar On A`

After the rerun, headings shifted toward topical anchors such as:

- `Middle East Ceasefire Hezbollah Lebanon`
- `White House Oil Prices Nuclear Weapon Hormuz`
- `Iran Israel Trump Netanyahu`
- `West Bank East Jerusalem International Law Hezbollah`

This is a meaningful navigation gain.

## What Did Not Improve Enough

Sectioning alone did not fully solve the worst ASR bodies.

Residual signs:

- some headings still contain noisy tails like `It'S` or weak generic tokens
- repeated broad-token clusters can flatten distinct subtopics
- host monologue files with degraded wording still need deeper repair to become quote-strong

Current deepest remaining pain points inside Batch A:

- `2026-06-01` Davis warhawks
- `2026-06-02` Dialogue Works Wilkerson
- `2026-06-02` Davis / Macgregor

These still justify targeted ASR wording repair, not just another section pass.

## Judgment

The pilot supports a two-layer model:

1. rerun sectioning first when headings are the main failure
2. do deeper ASR repair only where wording noise still blocks synthesis or quoting

That means the campaign has already produced permanent utility:

- better headings
- better browseability
- lower synthesis friction

But it also confirms that true wording repair should remain selective and
targeted rather than archive-wide.

## Recommended Next Move

Move to a second bounded pass on only the strongest residual cases:

- `2026-06-01` Davis warhawks
- `2026-06-02` Dialogue Works Wilkerson
- `2026-06-02` Davis / Macgregor

Repair target for that next pass:

- proper nouns
- obvious phrase collisions
- sentence-break clarity
- quote-critical wording
