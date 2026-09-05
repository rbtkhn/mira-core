# Strategy Codex Voice Import Migration Receipt

Status: `completed-frozen`

The one-time per-voice import programs that copied already-authorized source
captures from `C:\dev\strategy-codex` into the central Narrative Geopolitics
archive have been retired from the active tool surface.

The imported archive files, manifest rows, voice routes, and channel routes are
preserved. Private intake does not depend on these programs.

## Imported Voices

| Voice | Retired program | Originating commit |
| --- | --- | --- |
| Aguilar | `import_aguilar_from_strategy.py` | `69404e9` |
| Barnes | `import_barnes_from_strategy.py` | `69404e9` |
| Baud | `import_baud_from_strategy.py` | `69404e9` |
| Blumenthal | `import_blumenthal_from_strategy.py` | `69404e9` |
| Crooke | `import_crooke_from_strategy.py` | `69404e9` |
| Freeman | `import_freeman_from_strategy.py` | `69404e9` |
| Helmer | `import_helmer_from_strategy.py` | `69404e9` |
| Hoh | `import_hoh_from_strategy.py` | `69404e9` |
| Jermy | `import_jermy_from_strategy.py` | `69404e9` |
| Karaganov | `import_karaganov_from_strategy.py` | `69404e9` |
| Krainer | `import_krainer_from_strategy.py` | `69404e9` |
| Martyanov | `import_martyanov_from_strategy.py` | `69404e9` |
| Maté | `import_mate_from_strategy.py` | `69404e9` |
| Matlock | `import_matlock_from_strategy.py` | `69404e9` |
| McGovern | `import_mcgovern_from_strategy.py` | `69404e9` |
| Parsi | `import_parsi_from_strategy.py` | `69404e9` |
| Postol | `import_postol_from_strategy.py` | `69404e9` |
| Ritter | `import_ritter_from_strategy.py` | `7fd5641` |
| Sachs | `import_sachs_from_strategy.py` | `69404e9` |
| Weichert | `import_weichert_from_strategy.py` | `69404e9` |
| Wilkerson | `import_wilkerson_from_strategy.py` | `69404e9` |

## Recovery Boundary

Git history is the authoritative recovery path for the retired programs. Use
the commit listed above to inspect or restore a historical importer if an audit
requires it. Do not revive bulk migration as normal intake; any future source
must enter through the current archive-first intake contract.
