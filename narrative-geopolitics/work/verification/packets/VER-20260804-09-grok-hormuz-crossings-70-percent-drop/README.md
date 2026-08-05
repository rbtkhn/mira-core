# Verification Packet: VER-20260804-09 — grok-hormuz-crossings-70-percent-drop

Verification ID: `VER-20260804-09`

Status: `requested`

Assessment outcome: `not_investigated`

Opened: `2026-08-04`

Closed: `none`

Claim: `Hormuz crossings fell by approximately 70 percent and traffic shifted toward an Iranian route.`

Why it matters: `[Judgment, publication, promotion, or forecast consequence.]`

Affected forecast hooks: `none`

Affected artifacts: `none`

Research minutes: `0`

Evidence chains examined: `4`

Judgment changed: `no`

Further automation justified: `no`

## Required Observables

- [x] A commercial maritime-data report gives a dated percentage change and route split.
- [x] Independent maritime reporting describes the same traffic decline and route concentration.
- [ ] Raw vessel-level AIS data and the complete Kpler methodology are available in this collection.

## Evidence Records

| Evidence ID | Registry source ID | URL | Retrieved at | Event time | Source type | Origin chain | Direction | Translation provenance | Limitation |
| `EVID-01` | `VSRC-TRK-KPLER` | https://www.kpler.com/blog/strait-of-hormuz-crossings-drop-70-as-tanker-traffic-shifts-almost-entirely-to-the-iranian-route | `2026-08-04` | `2026-07` | `commercial_operational_data` | `Kpler-Hormuz-202607` | `supports` | `not_required` | Proprietary commercial data; exact denominator, filtering, and treatment of dark/unknown vessels require access to the underlying methodology. |
| `EVID-02` | `VSRC-RPT-REUTERS` | https://www.investing.com/news/commodities-news/hormuz-vessel-crossings-fall-further-as-security-concerns-linger-4804603 | `2026-08-04` | `2026-07-22` | `independent_professional_reporting` | `Reuters-20260722-Kpler` | `supports` | `not_required` | Reports Kpler vessel data and individual vessel examples; shares Kpler as the underlying data chain. |
| `EVID-03` | `VSRC-RPT-AP` | https://apnews.com/article/6587f90f2ab5beec373ce5fabf637541 | `2026-08-04` | `2026-08-04` | `independent_professional_reporting` | `AP-20260804` | `supports` | `not_required` | Reports a proposed Iranian/Omani route arrangement and fees; supports route governance context, not the 70% historical denominator. |
| `EVID-04` | `VSRC-RPT-PORTNEWS` | https://en.portnews.ru/news/print/394652/ | `2026-08-04` | `2026-07-24` | `independent_professional_reporting` | `PortNews-20260724-Kpler` | `supports` | `not_required` | Reports three crossings per day on July 22–24 and approximately 90% Iranian-route concentration, explicitly attributing the figures to Kpler; same quantitative lineage, not independent replication. |

Source types and translation values must match `source-registry.md`.

Allowed directions: `supports`, `challenges`, `context_only`.

## Independence Analysis

Kpler is the primary quantitative chain. Reuters and PortNews are separate reporting outlets but both rely on Kpler for the numerical traffic claims, so they are not independent quantitative confirmations. AP is a separate reporting chain and supports contested route governance on August 4, not the precise 70% figure. The comparison reinforces the direction and severity of the decline while leaving the exact denominator and full-period percentage dependent on Kpler's method.

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

Conclusion: `The evidence supports a substantial, dated decline in recorded Hormuz crossings and concentration of observed traffic on an Iranian route during the cited July window. It does not establish that crossings were continuously down 70%, that all traffic was captured by AIS, or that Iran exercised uncontested operational control.`

Confidence boundary: `Moderate confidence in the direction of the traffic decline; low-to-moderate confidence in the exact 70% magnitude and route share because the underlying proprietary data, dark-fleet treatment, and denominator are not independently available.`

Downstream effect: `Use only as a bounded Kpler estimate with its date window and methodology caveat. Do not state that Hormuz was fully closed or that Iran held an absolute veto over all transit.`

## Research Record

`Search boundary: July traffic reporting and August 4 route-governance reporting, retrieved August 4, 2026. Kpler, Reuters, PortNews, and AP were compared. Raw AIS, independent tracker data, and insurer data remain outstanding.`
