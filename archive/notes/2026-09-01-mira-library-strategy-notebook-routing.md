# Wiring Mira Library Into Strategy Notebook Composition

Date: `2026-09-01`
Status: `working-note`
Privacy: `repo-local`
Authority effect: `none`

## Purpose

This note preserves the design concept behind wiring Mira Library into
Strategy Notebook composition. It is not a canonical method change, research
evidence, forecast resolution, Library routing-memory activation, or
publication authority.

## Observation

Strategy Notebook is becoming the expert-estimate surface for Geo-Strategy:
less public issue prose, less journal inwardness, more direct judgment for
national-security advisors, geopolitical analysts, and commentators. That
surface naturally wants historical depth. The danger is that historical depth
can sound like evidence when it is only analogy.

Mira Library should therefore enter Strategy Notebook through routing
infrastructure, not through ornamental quotation or free-form search. The
governing distinction is simple:

```text
Geo archive sources establish the present crisis object.
Mira Library pressure-tests the mechanism.
Strategy Notebook adjudicates what, if anything, changes.
```

## Pilot Result

The first August 31 pilot exposed the difference between abstract search and
mechanism routing.

An abstract Library pre-scan for "coercion migrates into the support
substrate" returned `skip`: no governed historical mechanism profile cleared
the relevance floor. Broader read-only Library searches for coercion, access,
and logistics terms also returned no useful candidates.

After the mechanism was rewritten as `maritime access order and coercion
through support substrate`, the governed pre-scan returned `invoke` under the
`passage-legitimacy-order` profile and surfaced candidate families including
Thucydides, Grotius, Kautilya, Ottoman kanun, and Ibn Khaldun. This did not
retrieve passages and did not adopt an analogy; it only proved that named
mechanism handles are the right interface.

The cleanest August 31 handle was:

```text
LIB-COLONIAL-AUTHORITY-065-GROTIUS-MARE-LIBERUM
Mechanism signature: maritime_access_order
Disposition: held
Use: passage through contested water as an order claim, not proof of Hormuz facts
```

## Design Claim

The needed infrastructure is a small mechanism-to-Library-handle registry.
It should map Strategy Notebook mechanisms onto bounded historical handles
with an analytic job, anti-analogy warning, rejection condition, and required
boundary language.

The first registry belongs in:

```text
narrative-geopolitics/method/strategy-notebook-library-routing.md
```

The Strategy Notebook template should include an optional `Library Pressure
Test` section after `Historical Weight`. That section should be omitted or
marked `not-invoked` unless the routing threshold fires.

## Threshold

Library should be mandatory only when at least one of these is true:

- the notebook uses a named historical analogy or anti-analogy;
- the mechanism depends on a recurring statecraft pattern Library can test;
- the intended reader needs historical framing to use the estimate responsibly;
- a metadata pre-scan returns a registered `LIB-*` family with available text
  and a plausible analytic job;
- the estimate's confidence would change if Library exposed an anachronism,
  rival mechanism, structural difference, or missing rejection condition.

If none of those gates fires, Library absence remains absence.

## Guardrail

Every adopted, narrowed, or redirected Library row must state:

- shared mechanism;
- decisive structural difference;
- rejection condition;
- effect on estimate.

`LIB-*` references do not satisfy `SRC-*` coverage, verify `OPC-*` or `NG-*`
claims, resolve forecasts, establish base rates, or authorize public
promotion.

## Implementation State

The first minimal wiring has been drafted in the worktree:

- `narrative-geopolitics/method/strategy-notebook-library-routing.md`
- `narrative-geopolitics/templates/strategy-notebook.md`
- `scripts/validate_daily_run.py`
- `tests/test_daily_run_validation.py`

Focused validation passed after the patch:

```text
tests/test_daily_run_validation.py: 22 passed
daily-validate --date 2026-08-31 --stage issue: ready; failures=0; warnings=1
git diff --check: clean
```

No staging, commit, push, publication, Library routing-memory activation, or
private passage packet admission occurred.

## Implication

Mira Library can give Strategy Notebook gravitas only by becoming more
disciplined than style. It should not make a note sound older, wiser, or more
authoritative. It should make the mechanism harder to fool: expose the wrong
analogy, name the missing difference, sharpen the rejection condition, and
leave the present facts to the evidence systems that own them.
