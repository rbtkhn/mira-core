---
title: "Moonshots Participant Normalization Roster"
lane: moonshots
date_captured: 2026-08-28
status: "draft normalization note"
scope: "Moonshots podcast participant metadata; not transcript diarization"
rights_status: "internal metadata normalization note"
---

# Moonshots Participant Normalization Roster

This note normalizes recurring Moonshots podcast participant names for archive
metadata. It does not repair transcript body text and does not assert
speaker-diarized turns.

## Canonical Participants

| Canonical name | Recurring role | Common transcript/title variants |
| --- | --- | --- |
| Peter H. Diamandis | Host | Peter Diamandis; Peter; PHD |
| Alex Wissner-Gross | Panelist | Alex; AWG; Alex Wissner Gross; Alex Wiggins |
| Dave Blundin | Panelist | Dave; DB2; Dave Blondon; Dave Blunden |
| Salim Ismail | Panelist | Salim; Salem; Seem; SEM; Selma; Sim Ismail |
| Emad Mostaque | Panelist / recurring featured member | Emad; Immad; Immod; Emod; Mustach; Immad Mustach |

## Known Guests In EP #274-#283

| Episode | Canonical guest name | Common transcript/title variants |
| --- | --- | --- |
| EP #274 | Jared Isaacman | Jared Isaacman |
| EP #276 | Michael Kratsios | Michael Kratsios |
| EP #278 | Kush Bavaria | Kush Bavaria |
| EP #280 | Ramez Naam | Rome Nam; Romez Naam; Hermes Naam |
| EP #281 | Alvin Graylin | Alvin Graylin |

## Metadata Rules

- Use `host` for Peter H. Diamandis when he opens or conducts the episode.
- Use `panelists` for recurring Moonshots members named in the opening roster.
- Use `guests` only for external interview or deep-dive guests, not merely
  title-featured recurring members.
- When a title says `with Emad Mostaque` but the opening frames him as part of
  the quintet, classify him as `panelist`, not `guest`.
- Set `speaker_status` to `not diarized` unless turns are explicitly
  speaker-labeled.
- Do not infer that every quintet member appears unless the opening or
  transcript names them.
- Normalize ASR variants in metadata, but preserve raw transcript body text
  unless running a separate transcript repair workflow.

## Recommended Frontmatter Shape

```yaml
speaker: "semicolon-separated canonical participant names"
host: "single canonical host name"
panelists: ["canonical recurring panelist names"]
guests: ["canonical external guest names"]
speaker_status: "not diarized; participant roster inferred from opening/title"
```
