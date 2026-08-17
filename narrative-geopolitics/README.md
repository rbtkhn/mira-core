# Narrative Geopolitics

Narrative Geopolitics is a source-grounded dialogical workbench for geopolitical
judgment. It curates a constellation of intellectual voices and makes their
distinct frameworks available for bounded inquiry, disagreement, synthesis,
and forecasting.

It uses `strategy-codex/statecraft` as its source basis and predecessor system, but its goal is not to copy that inherited operator machinery. Its goal is to distill the best parts of statecraft into a cleaner public model that can stand beside Predictive History.

```text
statecraft = source basis and operator ancestor
narrative-geopolitics = source-grounded intellectual council and judgment model
predictive-history = public historical/civilizational reading model
```

## Purpose

Narrative Geopolitics turns transcripts, expert claims, current crises, actor
incentives, legitimacy claims, historical memory, and competing narratives into
realistic dialogue with a curated constellation of intellects. It then permits
a separate moderator to produce bounded geopolitical judgment.

It is not an oracle, a generic news summary, or a system for impersonating
living people. A reconstructed voice represents what the authorized corpus
supports as of a stated date. Direct support, close paraphrase, characteristic
inference, extrapolation, contradiction, and absence of evidence remain visibly
different.

Daily synthesis and public briefs are important operating modes, but they are
not the whole product. The central long-term capability is disciplined inquiry
across voices without flattening their disagreements into a house view.

Internal corpus analytics are collected under [analytics/](analytics/), including
the [cross-voice historical-reference density report](analytics/cross-voice-historical-reference-density.md).

## Operating Modes

All operating modes inherit [The Repository Remembers; the Agent Receives a
Mandate](method/bounded-agency-contract.md), the canonical contract for
authority, phase ownership, invariants, stop conditions, and handoffs.
Across those modes, the provisional [Epistemic Constitution](method/epistemic-constitution.md)
governs how claim state and consequences travel without allowing downstream
repetition or presentation to manufacture evidentiary warrant.
The [Reality Verification Lattice](method/reality-verification-lattice.md)
provides structured, multilingual, human-signed adjudication for claims
explicitly migrated into that layer.

The proven daily judgment loop is:

```text
best-intake through the day
-> archive/geopolitics/sources/YYYY-MM-DD/source-*.md
-> archive/geopolitics/source-manifest.json
-> geo-strategy
-> work/daily/YYYY-MM-DD/sources.md
-> work/daily/YYYY-MM-DD/synthesis.md
-> work/daily/YYYY-MM-DD/daily-brief.md
-> work/daily/YYYY-MM-DD/forecast.md
-> work/daily/YYYY-MM-DD/judgment.md
-> work/daily/YYYY-MM-DD/issue.md (generated internal reader edition)
-> work/reality/ (claim, evidence, outcome, and transition graph where migrated)
-> work/forecasts/forecast-ledger.md
-> public/briefs/daily/YYYY-MM-DD.md (only when intentionally promoted)
```

The experimental council loop is:

```text
bounded question + as-of date
-> archive source floor
-> selected voice records and claim maps
-> channel conditioning where relevant
-> separately reconstructed voice responses
-> explicit disagreements and cross-examination
-> independent moderator synthesis
-> fidelity review
-> optional forecast or public promotion
```

Use [method/dialogue-contract.md](method/dialogue-contract.md) for the epistemic
boundary and [work/dialogues/](work/dialogues/README.md) for manual experiments.
Do not automate reconstructed dialogue until the council value test demonstrates
that it adds value without sacrificing fidelity.

## Directory Map

```text
narrative-geopolitics/
├── README.md
├── archive/
│   ├── README.md
│   ├── source-manifest.json
│   └── sources/
├── channels/
│   ├── README.md
│   ├── channel-index.md
│   └── _template.md
├── method/
│   ├── narrative-statecraft.md
│   └── voice-continuity.md
├── public/
│   ├── README.md
│   └── briefs/
│       └── daily/
├── templates/
│   ├── sources.md
│   ├── synthesis.md
│   ├── daily-brief.md
│   └── forecast.md
├── voices/
│   ├── README.md
│   └── _template.md
└── work/
    ├── README.md
    ├── daily/
    └── forecasts/
        └── forecast-ledger.md
```

## Source Basis

The first source basis is `strategy-codex/statecraft`, especially its daily transcript intake and synthesis responsibilities.

V1 should use a manual manifest for each run. Automated extraction can come later.

Imported source truth lives in [archive/](archive/README.md). Voice records link into that central archive instead of duplicating transcripts or essays per voice.

## Intake Contract

Default source landing should follow [method/best-intake.md](method/best-intake.md).

Use `intake` to land same-day source truth quickly without pretending that provisional routing is final interpretation. Internally, `intake` uses the smart-intake workflow and best-intake engine.

See [method/intake-speedup.md](method/intake-speedup.md) for the current speedup plan and [../scripts/land_best_intake.py](../scripts/land_best_intake.py) for the first helper that automates archive-file creation plus manifest append.

Once the day batch is materially real, use `geo-strategy` as the
single evening synthesis command. It supports live and intentional
retrospective runs. Dates without manifest-backed intake remain absent.

## Voice Continuity

Narrative Geopolitics uses [voices/](voices/README.md) for durable voice records. A voice can be a speaker, writer, essayist, interview guest, social poster, or mixed-format analyst.

Voice continuity means remembered interpretive pattern across sources and time.
It supports both daily synthesis and corpus-bounded dialogue. A voice is an
evidentiary reconstruction, not a persona or stylistic imitation. Voice records
are internal first; public summaries or dialogues can come later after a record
is stable enough to share.

## Channel Conditioning

Narrative Geopolitics uses [channels/](channels/README.md) for host, show, and channel conditioning. Open this layer when the real question is how a host frames, pressures, selects, amplifies, compresses, or translates a guest's claims.

Pape remains the analyst voice. Pape-on-host sources route through channel shelves when host context changes interpretation.

## Public Voice

The public voice should be a calm public analyst:

- source-heavy and quote-aware
- willing to make bounded judgments
- careful with uncertainty in normal prose
- committed to at least one forecast or review hook per brief
- readable without becoming thin

## First Value Test

The July 2026 controlled value test compared a day-source-only Hormuz note with
a system-assisted note using voice continuity, channel conditioning, older
mechanism sources, and forecast review. The assisted note passed the publication
rubric, while a thin Europe-Russia diagnostic showed that the full method does
not yet generalize safely to underdeveloped crisis objects.

Current decision: `narrow`.

- Use the full method for deep crisis objects where continuity changes judgment
  or falsifiability.
- Use a lighter source-bounded workflow where evidence and continuity surfaces
  are thin.
- See [the public Hormuz brief](public/briefs/hormuz-transit-governance-2026-07-09.md)
  and [the internal findings](work/experiments/2026-07-value-test/milestone-findings.md).
- Use [the public watch surface](public/watch.md) to distinguish the active
  dossier from trigger-bound, unranked watch candidates.
