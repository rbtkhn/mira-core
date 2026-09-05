# Aftervoice - 2026-08-21

Status: `internal`
Evidence posture: `x-reported-unverified`
Source packet: `narrative-geopolitics/work/daily/2026-08-21`
Run ID: `aftervoice-20260821-demo`

This aftervoice pass supplements the Aug. 21 transcript packet with bounded X
signals from confirmed or investigated accounts. It does not add verified
facts, resolve forecasts, or change the eight-source synthesis set. X material
is used only as voice-context, source-lead, provenance-lead, contradiction-lead,
revision-lead, or no-signal context.

## Accounts Checked

| Voice / role | Handle | Account status | Checked window | Result |
|---|---|---|---|---|
| Daniel Davis | `@DanielLDavis1` | `confirmed` | Aug. 21 visible same-day posts/search | Useful direct voice-context signal found. |
| Scott Ritter | `@RealScottRitter` | `confirmed` | Aug. 21 visible same-day posts/search | No direct voice-authored same-day signal captured; repost/video circulation leads found. |
| Alexander Mercouris | `@AMercouris` | `confirmed` | Profile-level check | Confirmed account for future aftervoice use; no Aug. 21 same-day signal captured in this demo. |
| Alex Christoforou | `@AXChristoforou` | `candidate` | Profile-level check | Likely Duran-linked account; held out of confirmed aftervoice use pending external confirmation. |
| Alastair Crooke | `@AWCrooke`, `@AlastairCrooke` | `ambiguous` | Profile-level check | Two plausible accounts; held out pending external confirmation. |
| Larry Johnson | none confirmed | `not-confirmed` | User/profile search | Generic-name search produced likely wrong/noise account; do not use for aftervoice until confirmed. |
| Chas Freeman | none found | `not-found` | User/profile search | No plausible account found. |
| Nima Alkhorshid | none found | `not-found` | User/profile search | No plausible account found. |
| Glenn Diesen | `@Glenn_Diesen` | `confirmed` | Profile-level check | Confirmed host/channel account for future provenance checks. |
| Robert Barnes | `@barnes_law` | `confirmed` | Profile-level check | Confirmed account for future recon, not part of the Aug. 21 transcript source set. |

## Useful Aftervoice Signals

| Capture ID | Voice | Post URL | Lead type | Claim / signal | What it changes | Evidence status | Next route |
|---|---|---|---|---|---|---|---|
| `XCAP-20260821-001` | Daniel Davis | https://x.com/DanielLDavis1/status/2091004603571589334 | `voice-context` | Davis publicly argued that Western observers may be misreading Iranian economic-alarm statements as capitulation signals. | Supplements `SRC-02` by showing Davis's same-day public framing of economic pressure as a possible Western interpretive error, not merely a transcript theme. | `x-reported-unverified` | `geo-strategy` |
| `XCAP-20260821-002` | Larry Johnson ecosystem | https://x.com/tekotaro_12/status/2091019249204752422 | `provenance-lead` | A same-day X post circulated a Johnson video framed around the contradiction between claims that Iran/Hormuz are beaten and escalation of economic war. | Supplements `SRC-03` and `SRC-08` as circulation/provenance context only; not voice-authored evidence because Johnson's account is not confirmed. | `x-reported-unverified` | `backlog` |
| `XCAP-20260821-003` | Scott Ritter ecosystem | https://x.com/K1G11F106_dx/status/2091004764784112008 | `source-lead` | A same-day X post circulated a Ritter video using "Economic D-Day" / sanctions-fantasy framing. | Supplements `SRC-07` as a source-lead and circulation marker; no factual or voice-authored claim is adopted. | `x-reported-unverified` | `backlog` |
| `XCAP-20260821-004` | Chas Freeman ecosystem | https://x.com/7wiseone/status/2090983861270483232 | `source-lead` | A same-day X post circulated the Freeman Israel/Turkey video with broad anti-war framing. | Supplements `SRC-01` as circulation context only; not an independent source or Freeman-authored statement. | `x-reported-unverified` | `backlog` |
| `XCAP-20260821-005` | Glenn Diesen / Freeman circulation | https://x.com/Alzhacker/status/2090964595704016905 | `provenance-lead` | A Japanese-language post quoted Glenn Diesen's Freeman video post and reframed Israel/Turkey as U.S. credibility/order-collapse pressure. | Adds local-language circulation/provenance context around `SRC-01`; may be useful if tracking international spread of the frame. | `x-reported-unverified` | `backlog` |

## Provenance Links

| Capture ID | Linked source | Transcript claim or frame it may source | Next route |
|---|---|---|---|
| `XCAP-20260821-001` | Iran International post/article quoted by Davis | Iranian economic-alarm statements and Western interpretation of pressure/capitulation. | `reality-check` only if the underlying Iran International claim becomes public-use relevant. |
| `XCAP-20260821-002` | YouTube link in X post | Johnson economic-war contradiction frame. | `archive-query` / existing source check before any new intake. |
| `XCAP-20260821-003` | YouTube link in X post | Ritter "Economic D-Day" sanctions critique. | `archive-query` before any new intake. |
| `XCAP-20260821-004` | YouTube link in X post | Freeman Israel/Turkey escalation frame. | Already represented by `SRC-01`; no intake action from X alone. |
| `XCAP-20260821-005` | Glenn Diesen quoted post / YouTube link | Freeman Israel/Turkey frame and local-language circulation. | `backlog` unless circulation analysis becomes a specific objective. |

## Contradiction / Revision Leads

No direct correction, retraction, or self-revision was captured in this demo
pass. The main useful pressure signal is Davis's interpretive caution in
`XCAP-20260821-001`: he warns against reading Iranian economic-alarm statements
as capitulation. That is not a contradiction of the transcript packet; it
sharpens the overclaim boundary around Iran economic-stress claims.

## No-Signal / Held Accounts

| Voice | Account state | Why it matters |
|---|---|---|
| Freeman | `not-found` | Do not attribute X circulation of Freeman videos to Freeman himself. |
| Alkhorshid | `not-found` | No same-day account-level aftervoice available; use transcript only. |
| Crooke | `ambiguous` | Hold both plausible accounts until externally confirmed; do not use either as official aftervoice yet. |
| Johnson | `not-confirmed` | Do not treat Johnson-related video reposts as Johnson-authored public context. |
| Christoforou | `candidate` | Do not use `@AXChristoforou` for official aftervoice until externally confirmed. |
| Mercouris | `confirmed`, no same-day signal captured | Confirmed account is available for future aftervoice passes, but this demo does not add a Mercouris Aug. 21 signal. |

## Held Claims

- X posts about Iran's economic condition, Hormuz, NPT decisions, base damage,
  or U.S./Israeli defeat remain `x-reported-unverified`.
- Reposts of YouTube videos are circulation/provenance context, not independent
  support for the transcript claims.
- Voice-authored X posts may clarify how a voice framed a claim, but they do
  not verify the claim's factual content.

## Run Receipt

- Operator-authorized scope: demonstrate how confirmed or investigated X
  accounts can supplement the Aug. 21 transcript packet.
- Surface: logged-in in-app browser, read-only visible X state.
- Searches/accounts inspected: Daniel Davis, Larry Johnson, Scott Ritter, Chas
  Freeman, Nima Alkhorshid, Alastair Crooke, Alexander Mercouris, Alex
  Christoforou, Trita Parsi, Max Blumenthal, Aaron Mate, Glenn Diesen, Robert
  Barnes.
- Captures retained: 5.
- Captures ignored or held: generic/noise accounts, ambiguous Crooke accounts,
  candidate Christoforou account, not-found Freeman/Alkhorshid, not-confirmed
  Johnson account.
- Private/sensitive surfaces encountered: none intentionally inspected.
- Social actions taken: none.
- Forecast or claim status changed: none.
