# Medieval Body Admission Batch 13

**Status:** completed with isolated failures
**Date:** 2026-08-20

Batch 13 inspected ten Medieval authorities and admitted eight clean bodies for eight authorities. The Medieval shelf advanced from 102 to 110 bodies (126,149,878 bytes) across 60 authorities. Ancient remains at 193 bodies, leaving an 83-body gap. The JSON companion is the machine-reviewable receipt.

## Admitted bodies

| Authority | Body | Coverage | Bytes |
| --- | --- | --- | ---: |
| Du You | *Tongdian*, Chinese Wikisource, 200 fascicles | complete work; no critical-edition claim | 5,806,920 |
| Su Song | *Xin yixiang fayao*, Siku Wikisource, three fascicles | complete work; no critical-apparatus claim | 39,455 |
| Zhu Xi | *Commentaries on the Four Books*, root-linked Wikisource transcription | complete work; no critical-edition claim | 280,107 |
| Zhu Xi | *Commentaries on the Four Books*, Siku Wikisource transcription | complete work; no critical-apparatus claim | 191,828 |
| Li Qingzhao | surviving ci poetry and prose, Wikisource author collection | partial work; missing links and disputed attributions remain explicit | 46,009 |
| *Song Shi* tradition | *History of Song*, 496 fascicles | complete work; seven upstream illegible markers disclosed | 16,529,915 |
| Mahmud al-Kashgari | *Dîvânü Lugâti't-Türk*, Wikisource excerpts | selected passages only | 29,974 |
| Jnaneshwar | *Jnaneshwari*, eighteen chapters | complete work; possible chapter repetition disclosed | 2,372,568 |

All eight bodies are stored only in `.mira-private/library/texts/`. Each passed file inspection and importer dry-run before admission; exact hashes are recorded in the JSON companion.

## Isolated failures

- Yusuf Khass Hajib and Rashid al-Din remain `body-research-incomplete`: no clean, rights-confirmed portable route was found within this batch.
- Somesvara III received no body: the located Sanskrit *Manasollasa* was a different philosophical work, so it was rejected as an identity collision rather than misattributed.

## Validation and boundary

- Library validation passed.
- Generated indexes were rendered; drift check passed with no stale paths.
- Private-text verification passed: 289 checked, 21 expected missing, zero failures.
- `tests/test_archive_library.py`: 24 passed.
- Registry, private text store, and generated indexes changed. Nothing was staged, committed, pushed, published, or ingested into the Archive catalog.

The exact re-entry point is body research for the two unresolved authorities, or a new failure-isolated admission batch drawn from the remaining bodyless Medieval records.
