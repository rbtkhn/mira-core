# August 2026 Morning-Brief Coverage Ledger

Status: `internal-coverage-ledger`

This ledger tracks August 2026 morning-brief artifact coverage. It distinguishes
the protected August 2 carry-forward specimen from the current receipt-paired
`experimental-internal-morning-update` workflow.

## Workflow Rule

Current canonical morning-brief artifacts are generated from a frozen research
receipt covering the 24-hour observation window ending at `as_of_utc`, with
inherited judgment and forecast baseline context from prior repository state.
They are not generated primarily from the previous day's daily synthesis.

The August 2 artifact is an exception: it is a historical internal
carry-forward specimen derived from the August 1 daily synthesis and has no
paired receipt.

## Coverage

| Date | Markdown | Receipt | Coverage state | Notes |
| --- | --- | --- | --- | --- |
| `2026-08-01` | no | no | `missing` | Daily artifacts exist, but no morning-brief artifact exists for this date. |
| `2026-08-02` | yes | no | `markdown-only-specimen` | Protected historical `internal-carry-forward` derived from `2026-08-01` daily synthesis; not a current receipt-paired brief. |
| `2026-08-03` | yes | yes | `paired-current-workflow` | Schema/renderer `2.1`; explicit 24-hour observation window. |
| `2026-08-04` | yes | yes | `paired-current-workflow` | Schema/renderer `2.1`; explicit 24-hour observation window. |
| `2026-08-05` | yes | yes | `paired-reconstruction` | Schema/renderer `2.1`; explicitly reconstructed after the fact, not a contemporaneous live scan. |
| `2026-08-06` | yes | yes | `paired-reconstruction` | Schema/renderer `2.1`; explicitly reconstructed after the fact, not a contemporaneous live scan. |
| `2026-08-07` | yes | yes | `paired-reconstruction` | Schema/renderer `2.1`; explicitly reconstructed after the fact, not a contemporaneous live scan. |
| `2026-08-08` | yes | yes | `paired-reconstruction` | Schema/renderer `2.1`; explicitly reconstructed after the fact, not a contemporaneous live scan. |
| `2026-08-09` | yes | yes | `paired-reconstruction` | Schema/renderer `2.1`; explicitly reconstructed after the fact, not a contemporaneous live scan. |
| `2026-08-10` | no | no | `missing` | No morning-brief artifact present. |
| `2026-08-11` | no | no | `missing` | No morning-brief artifact present. |
| `2026-08-12` | no | no | `missing` | No morning-brief artifact present. |
| `2026-08-13` | no | no | `missing` | No morning-brief artifact present. |
| `2026-08-14` | no | no | `missing` | No morning-brief artifact present. |
| `2026-08-15` | no | no | `missing` | No morning-brief artifact present. |
| `2026-08-16` | no | no | `missing` | No morning-brief artifact present. |
| `2026-08-17` | no | no | `missing` | No morning-brief artifact present. |
| `2026-08-18` | no | no | `missing` | No morning-brief artifact present. |
| `2026-08-19` | yes | yes | `paired-current-workflow` | Schema/renderer `2.1`; explicit 24-hour observation window. |
| `2026-08-20` | no | no | `missing` | No morning-brief artifact present. |
| `2026-08-21` | no | no | `missing` | No morning-brief artifact present. |
| `2026-08-22` | no | no | `missing` | No morning-brief artifact present. |
| `2026-08-23` | no | no | `missing` | No morning-brief artifact present. |
| `2026-08-24` | no | no | `missing` | No morning-brief artifact present. |
| `2026-08-25` | no | no | `missing` | No morning-brief artifact present. |
| `2026-08-26` | no | no | `missing` | No morning-brief artifact present. |
| `2026-08-27` | no | no | `missing` | No morning-brief artifact present. |
| `2026-08-28` | no | no | `missing` | No morning-brief artifact present. |
| `2026-08-29` | no | no | `missing` | No morning-brief artifact present. |
| `2026-08-30` | no | no | `missing` | No morning-brief artifact present. |
| `2026-08-31` | no | no | `missing` | No morning-brief artifact present. |

## Summary Counts

- Complete receipt-paired artifacts: `8` (`2026-08-03` through `2026-08-09`, plus `2026-08-19`).
- Markdown-only historical specimen: `1` (`2026-08-02`).
- Missing morning-brief markdown: `22` (`2026-08-01`, `2026-08-10` through `2026-08-18`, and `2026-08-20` through `2026-08-31`).
- Dates with reconstruction caveats: `5` (`2026-08-05` through `2026-08-09`).

## Audit Notes

- August 3-7 rendered markdown does not use previous-day carry-forward language.
- August 5-9 should be treated as recovery artifacts, not full-strength
  contemporaneous live scans.
- August 1 daily synthesis and judgment may appear in later receipts as
  inherited baseline context; that does not constitute an August 1
  morning-brief artifact.
