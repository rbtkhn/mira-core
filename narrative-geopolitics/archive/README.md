# Narrative Geopolitics Archive

`archive/` owns imported source truth for Narrative Geopolitics.

Authority effect: `none`.

Sources are stored centrally because one source may involve multiple voices.
Voice and channel records link to the central archive instead of duplicating
source bodies.

## Authority

[source-manifest.json](source-manifest.json) is the sole authoritative index
for archive membership, source identity, dates, local paths, voice routing,
host routing, and import state.

This README is navigation guidance. Voice indexes, channel indexes, audit
reports, and other derived views do not add or remove archive membership.

## Boundary

```text
archive/  = imported source truth and canonical membership
voices/   = person continuity and derived source routing
channels/ = host, show, and channel conditioning
work/     = analysis and daily synthesis
public/   = authorized published products
```

## Layout

```text
archive/
|-- README.md
|-- source-manifest.json
|-- voice-routing-audit.md
|-- derived/
`-- sources/
    `-- YYYY-MM-DD/
        `-- source-*.md
```

## Find or Change Archive State

| Need | Workflow |
| --- | --- |
| Land a new source | `intake` using the canonical `archive-intake` workflow |
| Find existing sources or resolve membership | `archive-query` |
| Assess parity, routing, coverage, or repair candidates | `archive-audit` |
| Correct an existing manifest-backed source | digest-bound `archive-repair` |

Query corpus counts, dates, voices, and hosts from the manifest. Do not copy
volatile corpus totals into this README.

Audit findings and query results grant no mutation authority.

## Routing

Use `voice_slugs` for whole-source person continuity. One source may route to
multiple voices.

Use `host_slug` for host- or channel-conditioned analysis.

Use [voice-routing-audit.md](voice-routing-audit.md) when reviewing whether a
shared source should carry more than one voice route.

Voice and channel indexes are derived navigation surfaces. When they disagree
with the manifest, the manifest controls and the disagreement should be
audited.

## Import Rule

Preserve imported source truth. Add interpretation, comparison, routing
analysis, and synthesis outside the source body.

A source belongs to the archive only when its manifest membership and local
path agree.

## Coverage Language

Full-source parity means that the intended source corpus is represented in the
manifest and its derived routes.

First-slice parity means that a bounded initial corpus has manifest coverage,
local source files, complete routing for that slice, and sufficient retrieval
context. It does not claim full-corpus coverage.
