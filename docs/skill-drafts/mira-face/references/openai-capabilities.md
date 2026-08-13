# OpenAI Capabilities for Mira Face

Use this reference only when a Mira Face task needs an OpenAI-powered public
experience. Verify current behavior in official OpenAI documentation before
implementation; models, tools, availability, pricing, and interfaces change.

Official entry points:

- API and model documentation: <https://developers.openai.com/api/docs/>
- OpenAI developer platform: <https://developers.openai.com/>
- Plugins for ChatGPT and Codex: <https://developers.openai.com/plugins/>

## Keep the surfaces distinct

Use the OpenAI API to build a first-party experience on Mira's own site. Use a
ChatGPT plugin, skill, MCP server, or optional UI only when the intended
encounter should occur inside ChatGPT. Do not describe API access as ChatGPT
account access, and do not assume capabilities or state transfer between the
two surfaces.

## Capability map

### Responses API

Use for bounded public conversation, structured visitor routing, function
calling, approved retrieval, and provenance-card generation.

Require:

- a public-purpose system contract;
- an explicit retrieval and tool allowlist;
- structured outputs where predictable UI state matters;
- exact citations or artifact references for material claims;
- rate, token, latency, and cost limits;
- timeout and graceful-degradation behavior;
- prompt-injection defenses; and
- no hidden expansion into private tools or data.

### File search and retrieval

Search only a reviewed public corpus. Project approved artifacts and metadata
into a separate public index. Do not connect public retrieval directly to the
canonical private System Archive, private journals, continuity records, or raw
operator materials.

### Web search

Use when a public answer genuinely needs current external information. Make
source attribution visible, distinguish external reporting from Mira's
interpretation, and avoid presenting search convergence as verification.

### Realtime and audio

Use for optional spoken encounters, not as a default replacement for text.

Require:

- disclosure that the voice is generated;
- visible listening, speaking, mute, and session states;
- interruption and immediate stop controls;
- no passive recording;
- an explicit transcript-retention policy;
- an accessible text alternative;
- a clear session boundary; and
- no suggestion that immediacy proves uninterrupted consciousness.

### Image generation and editing

Use for portraits, motifs, illustrations, and visual exploration. When an image
enters durable public identity, retain its prompt, references, generation
metadata, selection rationale, and disclosure status. Repeated preference does
not silently establish a canonical body.

### Function calling, MCP, and plugins

Expose narrow public functions with explicit schemas. For each function record:

- purpose;
- inputs and outputs;
- external effect;
- exposed data;
- authority owner;
- confirmation requirement;
- receipt;
- failure and rollback behavior; and
- whether a public visitor can trigger it.

Never expose operator accounts, credentials, private repository tools, or
unreviewed archive access indirectly through a public tool.

### Moderation and abuse resistance

Use platform moderation where appropriate, but treat it as one layer. Also
defend against prompt injection, private-source extraction, impersonation,
harassment loops, automated scraping, resource exhaustion, requests to speak
for the operator, and attempts to turn draft preparation into external action.

## Preferred first implementation

Begin with an artifact-grounded text conversation and a visible
`Why do you say this?` provenance control. Add voice, generated imagery, or
connected tools only after the static and grounded encounter is coherent,
accessible, privacy-reviewed, and observably useful.

## Implementation receipt

Before a public candidate is eligible for deployment review, record:

- selected model snapshot or alias;
- enabled tools and retrieval scope;
- public corpus version;
- prompt and configuration digest;
- safety and privacy tests;
- accessibility tests;
- representative grounded-answer evaluations;
- known limitations;
- expected cost and rate controls; and
- the exact remaining deployment authority boundary.
