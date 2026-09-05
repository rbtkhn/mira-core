# The Bypass Was Real; Its Command Chain Remains Unproven

Verification ID: `VER-20260710-01`

Status: `assessed`

Assessment outcome: `operationally_contested`

Opened: `2026-07-10`

Closed: `none`

Claim: `A US-backed attempt to route vessels through an Oman-side Hormuz corridor without Iranian coordination produced Iranian coercive action and renewed US strikes.`

Why it matters: `The claim appears to instantiate both the trigger and response in accountable forecast NG-20260708-F02.`

Affected forecast hooks: `NG-20260708-F02`

Affected artifacts: `narrative-geopolitics/work/daily/2026-07-10/synthesis.md, narrative-geopolitics/work/daily/2026-07-10/forecast.md, narrative-geopolitics/work/daily/2026-07-10/daily-brief.md`

Research minutes: `18`

Evidence chains examined: `5`

Judgment changed: `yes—incident occurrence strengthened; command-chain claim narrowed`

Further automation justified: `no—one packet does not justify feeds or generalized collection`

## Required Observables

- [x] Vessel identities and approximate incident locations; full tracks were unavailable.
- [x] General Iranian navigation warnings; vessel-specific warning records were unavailable.
- [x] Attack evidence and competing attribution claims.
- [x] Damage and continuation records; final arrival records were unavailable.
- [x] Timing of renewed US strikes relative to vessel incidents.
- [x] Evidence of US encouragement for the Oman-side route; operation-specific command evidence was unavailable.

## Evidence Records

| Evidence ID | Registry source ID | URL | Retrieved at | Event time | Source type | Origin chain | Direction | Translation provenance | Limitation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `EVID-01` | `VSRC-MAR-UKMTO` | https://www.ukmto.org/-/media/ukmto/products/update-068-jmic-advisory-note-07-july.pdf?rev=274817fc31674a1296b6ea6b3dd6ac7d | `2026-07-11` | `2026-07-07` | `observational_registry` | `CHAIN-UKMTO` | `supports` | `not_required` | Confirms three tanker attacks and damage near Oman-side locations, but withholds vessel names and attributes projectiles to unknown actors. |
| `EVID-02` | `VSRC-MAR-IMO` | https://www.imo.org/en/mediacentre/hottopics/pages/middle-east-highlighted-incidents.aspx | `2026-07-11` | `2026-07-06/07` | `multilateral_primary` | `CHAIN-IMO` | `supports` | `not_required` | Names AL REKAYYAT, WEDYAN, and CYPRUS PROSPERITY and confirms damage; does not identify attacker, intent, warning sequence, or command chain. |
| `EVID-03` | `VSRC-RPT-AP` | https://apnews.com/article/iran-us-israel-war-oil-4732228810c9839a1258309ad43b8289 | `2026-07-11` | `2026-07-07` | `independent_professional_reporting` | `CHAIN-AP` | `supports` | `not_required` | Reports all three vessels used the Oman-side route, Iranian state media said one ignored warnings, Qatar blamed Iran, and US strikes followed; incident details partly derive from UKMTO and interested officials. |
| `EVID-04` | `VSRC-RPT-AP` | https://apnews.com/article/iran-strait-hormuz-oil-route-us-shipping-de981ef87afe8da617076fe494c37482 | `2026-07-11` | `2026-07-02` | `independent_professional_reporting` | `CHAIN-AP` | `context_only` | `not_required` | Establishes Iran's public force warning and the competing Oman-side route, plus Lloyd's traffic context; predates the July incidents and does not prove vessel-specific notice. |
| `EVID-05` | `VSRC-RPT-LEMONDE` | https://www.lemonde.fr/en/international/article/2026/07/10/strait-of-hormuz-deadlock-could-lead-trump-into-sporadic-war-with-iran_6755331_4.html | `2026-07-11` | `2026-07-07/08` | `independent_professional_reporting` | `CHAIN-LEMONDE` | `supports` | `official_english_edition` | Reports that the US Navy encouraged Oman-side routing, Iran treated it as provocation, vessels were fired upon, and hostilities resumed; does not disclose operational evidence for a coordinated bypass mission. |
| `EVID-06` | `VSRC-RPT-AXIOS` | https://www.axios.com/2026/07/07/iran-resumes-hormuz-attacks-us-officials | `2026-07-11` | `2026-07-07` | `independent_professional_reporting` | `CHAIN-US-OFFICIAL` | `supports` | `not_required` | A US official attributes attacks to Iran and anticipated retaliation; attribution is interested and underlying intelligence is unavailable. |

## Independence Analysis

The six URLs represent five labeled evidence chains, but they are not five fully independent confirmations. AP and Axios reuse UKMTO incident reporting while adding Qatari, Iranian-state-media, and US-official claims. IMO independently identifies vessels and damage but may ultimately rely on maritime incident reports from the same operating chain. Le Monde adds the strongest published claim that the US Navy encouraged Oman-side routing, yet it does not expose operation-specific orders or tracking evidence. The packet therefore separates strong convergence on incident occurrence from weaker, interested attribution and unproven command intent.

## Perspective and Coverage Audit

| Coverage floor | Status | Registry sources or waiver |
| --- | --- | --- |
| Closest registry, sensor, or original document | `covered` | `VSRC-MAR-UKMTO`, `VSRC-MAR-IMO` |
| Affected-region or local source | `waived` | Oman MSC and regional notices were sought; no incident-specific public record added a discriminating observable. |
| Claimant official position | `waived` | No operation-specific CENTCOM or US government release establishing command of a bypass was located. |
| Challenged actor position or denial | `waived` | Iranian warning language appeared through reporting, but no direct incident-specific Iranian official record was used. |
| Two professional reporting chains from different geopolitical environments | `covered` | `VSRC-RPT-AP` and `VSRC-RPT-LEMONDE` |
| Commercial or observational evidence when applicable | `waived` | Full AIS tracks and proprietary commercial movement records were unavailable; incident registries established damage but not route intent. |

## Assessment

Conclusion: Three commercial vessels were damaged in or near the Oman-side Hormuz route on July 6–7, general Iranian warnings against unapproved routing were public, and renewed US strikes followed. The available evidence does not establish that the vessels formed a coordinated US-backed bypass operation, that each received and ignored a specific warning, or that Iran attacked them because of such an operation. Both forecast elements are plausible and partially evidenced, but the full causal sequence is not operationally established.

Confidence boundary: `operationally_contested` is the strongest responsible outcome because incident occurrence and damage have official maritime support, while attribution, deliberate bypass intent, and trigger-response causality depend on interested officials and reporting whose underlying operational evidence is unavailable.

Downstream effect: Keep `NG-20260708-F02` open. Strengthen confidence that the forecast named a real class of event, but do not score it as a hit. Narrow July 10 prose from an unqualified US-backed bypass operation to documented Oman-side incidents with contested attribution and command intent.

## Research Record

Research was bounded to maritime advisories, named vessels, routing warnings, attack attribution, damage or continuation records, strike timing, and bypass intent. Searches prioritized UKMTO/JMIC, IMO, US official releases, major wire reporting, and independent international reporting. No July 7 CENTCOM or White House release establishing the claimed operation was found. Full AIS tracks, vessel-specific VHF recordings, military orders, and underlying intelligence were unavailable. Research stopped once additional results repeated the same originating reports rather than adding a new discriminating observable.
