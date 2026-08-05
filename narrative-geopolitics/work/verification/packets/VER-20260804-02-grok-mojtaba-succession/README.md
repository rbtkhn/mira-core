# Verification Packet: VER-20260804-02 — grok-mojtaba-succession

Verification ID: `VER-20260804-02`

Status: `requested`

Assessment outcome: `not_investigated`

Opened: `2026-08-04`

Closed: `none`

Claim: `Mojtaba Khamenei was named successor around 8 March 2026.`

Why it matters: `[Judgment, publication, promotion, or forecast consequence.]`

Affected forecast hooks: `none`

Affected artifacts: `none`

Research minutes: `0`

Evidence chains examined: `4`

Judgment changed: `no`

Further automation justified: `no`

## Required Observables

- [x] A contemporaneous record identifies the selection of Mojtaba Khamenei by Iran's Assembly of Experts.
- [x] A regional professional report and an Iranian state-linked report provide separate attribution chains.
- [ ] Independent primary documentation from the Assembly of Experts is available in this collection.

## Evidence Records

| Evidence ID | Registry source ID | URL | Retrieved at | Event time | Source type | Origin chain | Direction | Translation provenance | Limitation |
| `EVID-01` | `VSRC-RPT-AJ` | https://www.aljazeera.com/news/2026/3/8/iran-names-khameneis-son-as-new-supreme-leader-after-fathers-killing-2 | `2026-08-04` | `2026-03-08` | `independent_professional_reporting` | `AJ-20260308` | `supports` | `official_english_available` | Reports the Assembly of Experts named Mojtaba successor; does not itself establish the underlying vote record. |
| `EVID-02` | `VSRC-RPT-REUTERS` | https://www.reuters.com/world/middle-east/iran-defies-trump-elevates-khameneis-son-mojtaba-successor-2026-03-08/ | `2026-08-04` | `2026-03-08` | `independent_professional_reporting` | `Reuters-20260308` | `supports` | `not_required` | Attributes the selection to Iranian state media and describes the succession; source chain is independent from Al Jazeera's report but shares the underlying official announcement. |
| `EVID-03` | `VSRC-RPT-TASNIM` | https://www.tasnimnews.ir/en/news/2026/03/09/3535308/ayatollah-seyed-mojtaba-khamenei-named-leader-of-islamic-revolution | `2026-08-04` | `2026-03-09` | `state_affiliated_reporting` | `Tasnim-20260309` | `supports` | `official_english_available` | Iranian state-linked report directly says the Assembly of Experts named Mojtaba leader; interested-source limitation applies. |
| `EVID-04` | `VSRC-RPT-TASNIM` | https://www.tasnimnews.ir/fa/news/1404/12/18/3535388/جزئیاتی-از-جلسه-حضوری-مجلس-خبرگان-برای-انتخاب-رهبر-انقلاب | `2026-08-04` | `2026-03-08` | `state_affiliated_reporting` | `Tasnim-20260308-fa` | `supports` | `operator_translation_required` | Persian account says the Assembly met in person and selected Mojtaba by a decisive vote; it remains an interested official narrative, not independent proof. |

Source types and translation values must match `source-registry.md`.

Allowed directions: `supports`, `challenges`, `context_only`.

## Independence Analysis

Al Jazeera and Reuters are separate professional reporting chains but both rely materially on the Iranian announcement. Tasnim's Persian and English records are one Iranian state-linked chain, not two confirmations. The claim that an announcement occurred is strongly supported across regional, professional, and Iranian records; the vote procedure and constitutional legitimacy remain only officially described.

## Perspective and Coverage Audit

| Coverage floor | Status | Registry sources or waiver |
| --- | --- | --- |
| Closest registry, sensor, or original document | `waived` | [State what was sought and why unavailable.] |
| Affected-region or local source | `waived` | [State what was sought and why unavailable.] |
| Claimant official position | `waived` | [State what was sought and why unavailable.] |
| Challenged actor position or denial | `waived` | [State what was sought and why unavailable.] |
| Two professional reporting chains from different geopolitical environments | `waived` | [State what was sought and why unavailable.] |
| Commercial or observational evidence when applicable | `not_applicable` | [Explain applicability.] |

## Assessment

Conclusion: `The evidence supports the narrow claim that Mojtaba Khamenei was publicly named as Iran's new Supreme Leader/successor around March 8–9. It does not independently establish the Assembly of Experts' internal vote, the legality of the succession, or the degree of IRGC influence.`

Confidence boundary: `High confidence that the announcement was made; moderate confidence in the reported institutional attribution; low confidence regarding the undisclosed internal selection process.`

Downstream effect: `The Grok claim may be used as a reported succession event with attribution. Do not phrase the institutional process or political legitimacy as independently established.`

## Research Record

`Search boundary: contemporaneous March 8–9 reporting and available English-language regional/state-linked records, retrieved August 4, 2026. Research stopped because the Assembly of Experts primary vote record was not located in the bounded search.`
