---
title: "Colonial Library Seal Gap Plan"
date: 2026-08-22
status: planning-complete
target_standard: MIRA-LIBRARY-ERA-SUFFICIENCY-V1
target_profile: BOUNDED-HISTORICAL-SHELF-V1
---

# Colonial Library Seal Gap Plan

## Current State

The Colonial shelf now uses an expanded, Russia-aware 77-authority roster. This is a better civilizational boundary than the earlier 72-authority roster, but it raises the seal threshold denominator.

| Metric | Current | Required | Result | Gap |
| --- | ---: | ---: | --- | ---: |
| Authority count | 77 | 56 | pass | 0 |
| Represented-authority ratio | 68.83% | 90.00% | fail | +17 represented authorities |
| Represented-authority count | 53 | 56 | fail | +3 represented authorities |
| Available body count | 65 | 100 | fail | +35 bodies |
| Available bodies per authority | 0.84 | 1.70 | supporting fail | +66 bodies for density |
| Available-authority ratio | 68.83% | 70.00% | fail | +1 represented authority |
| Non-metadata coverage ratio | 66.23% | 40.00% | pass | 0 |
| Registry/index/focused tests | passed | pass | pass | 0 |

The controlling gap is represented-authority fullness. Colonial needs 70 of 77 authorities represented to pass the 90% fullness floor. Body mass also needs 35 additional bodies. Body density remains a supporting concern, but it cannot substitute for authority representation.

## Remaining Missing Authorities

| Lane | Source IDs |
| --- | --- |
| Spanish/Andean law and memory | `LIB-COLONIAL-AUTHORITY-052-LEYES-NUEVAS`, `LIB-COLONIAL-AUTHORITY-017-INCA-GARCILASO` |
| Tokugawa Japan literature/legal | `LIB-COLONIAL-AUTHORITY-027-BASHO`, `LIB-COLONIAL-AUTHORITY-028-SAIKAKU`, `LIB-COLONIAL-AUTHORITY-029-CHIKAMATSU`, `LIB-COLONIAL-AUTHORITY-030-UEDA-AKINARI`, `LIB-COLONIAL-AUTHORITY-031-TAKUAN-SOHO`, `LIB-COLONIAL-AUTHORITY-061-TOKUGAWA-EDICTS`, `LIB-COLONIAL-AUTHORITY-062-TOKUGAWA-IEYASU-PUBLICATION` |
| Indo-Persian/Persian/Ottoman | `LIB-COLONIAL-AUTHORITY-035-MIR-TAQI-MIR`, `LIB-COLONIAL-AUTHORITY-070-OTTOMAN-KANUN`, `LIB-COLONIAL-AUTHORITY-071-SAFAVID-COURT-CHRONICLE` |
| Qing China | `LIB-COLONIAL-AUTHORITY-057-QING-IMPERIAL-EDICTS`, `LIB-COLONIAL-AUTHORITY-059-QIANLONG-MACARTNEY`, `LIB-COLONIAL-AUTHORITY-060-QINGSHIGAO` |
| Company rule / Bengal | `LIB-COLONIAL-AUTHORITY-040-CLIVE-PLASSEY`, `LIB-COLONIAL-AUTHORITY-041-BENGAL-REVENUE-SETTLEMENT` |
| Indigenous-British / Indigenous America | `LIB-COLONIAL-AUTHORITY-049-GB-INDIAN-DEPARTMENT-PAPERS`, `LIB-COLONIAL-AUTHORITY-050-MEHERRIN-PETITION` |
| Jesuit/China transmission | `LIB-COLONIAL-AUTHORITY-055-MATTEO-RICCI` |
| Russia/Eurasia | `LIB-COLONIAL-AUTHORITY-073-SOBORNOE-ULOZHENIE`, `LIB-COLONIAL-AUTHORITY-074-PETER-TABLE-RANKS`, `LIB-COLONIAL-AUTHORITY-075-CATHERINE-NAKAZ`, `LIB-COLONIAL-AUTHORITY-077-RUSSIAN-SIBERIAN-EXPANSION` |

## Seal Strategy

The shelf should aim for at least 18 additional represented authorities rather than exactly 17. That creates one-authority slack for a late rejection or integrity problem. It should aim for at least 40 additional bodies rather than exactly 35, because several expected wins are single-document admissions and density remains thin.

The right shape is four reviewable batches:

1. **Batch 015: Russia Recovery**
   - Target: `SOBORNOE-ULOZHENIE`, `PETER-TABLE-RANKS`, `CATHERINE-NAKAZ`, `RUSSIAN-SIBERIAN-EXPANSION`.
   - Goal: 3-4 represented authorities, 4-8 bodies.
   - Rationale: The Russia lane was newly added and is the freshest balance debt. `Nakaz` and Petrine service-state documents are likely high-value if clean public-domain bodies can be recovered. Keep Sobornoye/Siberian rows deferred if only modern summaries or unreviewed scans appear.

2. **Batch 016: Company / Indigenous / Spanish America**
   - Target: `CLIVE-PLASSEY`, `BENGAL-REVENUE-SETTLEMENT`, `GB-INDIAN-DEPARTMENT-PAPERS`, `MEHERRIN-PETITION`, `LEYES-NUEVAS`, `INCA-GARCILASO`.
   - Goal: 5-6 represented authorities, 8-12 bodies.
   - Rationale: These rows are likely to yield public-domain administrative, treaty, legal, petition, or OCR bodies. They also preserve the shelf's colonial-rule and Indigenous-contact center of gravity.

3. **Batch 017: Qing / Jesuit / Diplomatic China**
   - Target: `MATTEO-RICCI`, `QING-IMPERIAL-EDICTS`, `QIANLONG-MACARTNEY`, `QINGSHIGAO`.
   - Goal: 3-4 represented authorities, 6-10 bodies.
   - Rationale: Ricci and Qianlong-Macartney are likely more feasible than broad Qing edict/history corpora. Admit selected packets where edition and rights are clear; preserve broad Qing bodies as debt if needed.

4. **Batch 018: Literature and Hard Asian/Ottoman Recovery**
   - Target: Japanese literature/legal rows, `MIR-TAQI-MIR`, `OTTOMAN-KANUN`, `SAFAVID-COURT-CHRONICLE`.
   - Goal: 6-8 represented authorities, 12-18 bodies.
   - Rationale: This is the culturally most important and technically hardest wave. It should include original-language recovery where feasible and accept older public-domain translations only when edition and rights are defensible.

## Acceptance Tests Before Sealing

Colonial should not be considered sealable until all of these hold:

- at least 70 of 77 authorities represented;
- at least 100 available Colonial bodies;
- all body records have stable `body_id`, edition label, language, license status, byte count, and SHA-256;
- `tools\run.ps1 library validate --json` passes;
- `tools\run.ps1 library render-index --check --json` passes;
- focused archive-library tests pass;
- `library verify-texts --json` either passes for the configured Colonial text root or any cross-era private-store limitation is resolved before sealing;
- every remaining missing authority is listed in the seal debt ledger with conservative coverage notes;
- no body count is inflated by artificial splitting.

## Recommendation

Proceed with Batch 015 Russia Recovery first. It directly pays down the newly created civilizational debt and should yield at least Catherine/Peter coverage if the public-domain source bodies can be recovered. If Russia stalls after one bounded search pass, switch immediately to Batch 016, because Colonial now needs authority-count progress more than perfect completion of any single lane.
