# Forecast Hook Ledger - 2026-08-16

Status: `source-bounded`

## Evidence Boundary

This ledger converts the landed August 16 source batch into watchable forecast hooks. It does not verify operational claims, resolve public truth, or assign probability. Each hook remains source-attributed until promoted through a separate verification workflow.

Primary source basis:

- [sources.md](sources.md)
- [SRC-01 Mercouris / Ukraine strikes](../../../archive/sources/2026-08-16/source-4-russian-strikes-devastate-ukraine-key-ukraine-refinery-smash-orekhov-falling-zelensky-uk-eu-panic-2026-08-16.md)
- [SRC-02 Marandi / Iran and Yemen](../../../archive/sources/2026-08-16/source-4-seyed-m-marandi-iran-yemen-unleash-a-new-offensive-strategy-2026-08-16.md)
- [SRC-03 Mercouris / demand destruction](../../../archive/sources/2026-08-16/source-4-demand-destruction-the-real-energy-crisis-hitting-europe-and-japan-2026-08-16.md)
- [SRC-04 Weichert / Gulf basing](../../../archive/sources/2026-08-16/source-4-iran-won-t-permit-u-s-bases-to-return-to-gulf-2026-08-16.md)
- [SRC-05 Krapivnik / Europe winter strikes](../../../archive/sources/2026-08-16/source-4-stanislav-krapivnik-europe-begs-u-s-to-call-russia-now-fear-of-catastrophic-winter-strikes-2026-08-16.md)
- [SRC-06 Krapivnik / trade war escalation](../../../archive/sources/2026-08-16/source-4-escalation-trade-war-gets-worse-iran-war-extends-to-ukraine-stas-krapivnik-2026-08-16.md)
- [SRC-07 McGovern / Israel military defeat](../../../archive/sources/2026-08-16/source-4-ray-mcgovern-israel-suffers-worst-military-defeat-new-front-opens-2026-08-16.md)
- [SRC-08 Alkhorshid / nuclear option](../../../archive/sources/2026-08-16/source-4-nima-r-alkhorshid-trump-discusses-nuclear-option-on-iran-in-secret-white-house-talks-2026-08-16.md)

## Hook Register

| Hook ID | Actor Constraint | Watch Condition | Source Basis | Verification Requirement | Weakens If |
| --- | --- | --- | --- | --- | --- |
| `FH-2026-08-16-01` | The United States can escalate but cannot cheaply restore the old Gulf/Hormuz order. | U.S. naval or air buildup near Iran is followed by Iranian preemptive strikes on regional bases or support infrastructure. | `SRC-02`, `SRC-04`, `SRC-07`, `SRC-08` | Independent reporting on U.S. force movements, regional base alerts, Iranian strike claims, and damage assessments. | U.S. buildup occurs without Iranian preemption and Hormuz access normalizes under non-Iranian terms. |
| `FH-2026-08-16-02` | Iran can keep Hormuz as leverage, but full closure raises escalation and economic risks. | Partial Hormuz filtering shifts to complete closure or explicit interdiction of non-approved shipping and pipelines. | `SRC-02`, `SRC-03`, `SRC-07`, `SRC-08` | Shipping data, insurance/rate changes, tanker-tracking anomalies, Gulf state advisories, and energy-market confirmation. | Shipping volumes recover broadly without visible Iranian concessions or side payments. |
| `FH-2026-08-16-03` | Israel can still pull Washington toward escalation, but its exposure limits U.S. freedom of action. | Israel expands the Lebanon front or requests/receives new U.S. air-defense, naval, or strike support after Iranian or Hezbollah pressure. | `SRC-04`, `SRC-07`, `SRC-08` | Israeli official statements, Lebanese battlefield reporting, U.S. deployment notices, interceptor transfers, and regional missile/air-defense evidence. | Israel de-escalates in Lebanon and U.S. support remains politically or materially constrained. |
| `FH-2026-08-16-04` | Russia can exploit winter and battlefield attrition but must manage escalation ambiguity with NATO. | Russian strikes shift toward sustained energy, rail, port, or winter-critical infrastructure pressure while avoiding direct NATO-member targets. | `SRC-01`, `SRC-05`, `SRC-06`, `SRC-07` | Strike geolocation, Ukrainian grid/rail/port disruption data, Russian statements, and NATO response posture. | Russia accepts a ceasefire or limits strikes despite continued Ukrainian long-range attacks. |
| `FH-2026-08-16-05` | Europe can keep supporting Ukraine, but cheap-energy industrial resilience is deteriorating. | European gas, diesel, aviation fuel, or power stress produces industrial curtailments before or during winter. | `SRC-03`, `SRC-05`, `SRC-06` | Storage levels, industrial shutdown notices, energy-price data, emergency rationing measures, and subsidy announcements. | Storage fills, prices stabilize, and industrial output holds without major state intervention. |
| `FH-2026-08-16-06` | Gulf states can bargain quietly with Iran, but hosting U.S. operations becomes a liability. | Gulf states seek exemptions, compensation arrangements, or public distancing from U.S. military use of bases and airspace. | `SRC-02`, `SRC-04`, `SRC-07` | Gulf diplomatic statements, shipping exemption patterns, base-access reporting, financial-transfer evidence, and Iranian media signals. | Gulf states openly expand U.S. basing cooperation without Iranian retaliation or shipping penalties. |
| `FH-2026-08-16-07` | Ukraine can impose symbolic and material pain, but the batch frames long-range strikes as unlikely to reverse battlefield direction. | Ukrainian long-range strikes on Russian energy or logistics trigger a larger Russian demonstration strike or infrastructure campaign. | `SRC-01`, `SRC-05`, `SRC-06`, `SRC-07` | Ukrainian/Russian strike logs, satellite or open-source damage assessment, Russian warnings, and follow-on strike tempo. | Ukrainian strikes continue without a Russian escalation step and battlefield pressure does not increase. |
| `FH-2026-08-16-08` | U.S./Israeli nuclear rhetoric may signal desperation, but normalization would damage legitimacy and widen proliferation pressure. | Nuclear-use discussion moves from leaked or fringe signal into repeated elite, official, or semi-official discourse tied to Iran or Taiwan. | `SRC-07`, `SRC-08` | Official transcripts, credible press sourcing, congressional statements, allied reactions, and nonproliferation/diplomatic responses. | Nuclear rhetoric is repudiated quickly by official actors and does not recur in crisis messaging. |

## Constraint Breaks

Priority watch conditions:

1. `FH-2026-08-16-01`: Iranian preemption of U.S. regional preparations.
2. `FH-2026-08-16-02`: full Hormuz closure or loss of selective transit.
3. `FH-2026-08-16-05`: European industrial curtailment from energy stress.
4. `FH-2026-08-16-08`: normalization of nuclear-use discourse.

## OPC Dependency Candidates

These are not admitted operational claims. They are candidates for later verification only if a public-facing brief or accountable forecast depends on them.

| Candidate | Claimed Dependency | Hook(s) Affected | Suggested Verification Packet |
| --- | --- | --- | --- |
| `OPC-CAND-2026-08-16-A` | Iran has enough missile, drone, command, and underground basing resilience to absorb another U.S./Israeli attack and continue escalation. | `FH-2026-08-16-01`, `FH-2026-08-16-02`, `FH-2026-08-16-03`, `FH-2026-08-16-08` | Iranian force-generation and strike-resilience packet. |
| `OPC-CAND-2026-08-16-B` | U.S. regional missile, interceptor, carrier, and base logistics are materially strained. | `FH-2026-08-16-01`, `FH-2026-08-16-03` | U.S. regional readiness and interceptor-stock packet. |
| `OPC-CAND-2026-08-16-C` | Israel's air-defense capacity is insufficient to absorb a major Iranian strike package. | `FH-2026-08-16-03`, `FH-2026-08-16-08` | Israeli air-defense depletion and performance packet. |
| `OPC-CAND-2026-08-16-D` | European and Japanese energy exposure is severe enough to force demand destruction or accelerated deindustrialization. | `FH-2026-08-16-05` | Europe/Japan energy-storage, price, and industrial-curtailment packet. |
| `OPC-CAND-2026-08-16-E` | Russian winter-strike leverage can materially alter Ukrainian and European negotiating pressure. | `FH-2026-08-16-04`, `FH-2026-08-16-07` | Russia/Ukraine winter infrastructure and negotiation-pressure packet. |

## Use Boundary

This ledger is ready for internal monitoring and daily-brief drafting. It is not ready for public factual use, forecast resolution, or claim adjudication without the named verification packets.
