# From Civilization Memory to Mira Core

**Recorded:** 2026-08-15

**Status:** Historical reconstruction and architectural interpretation

**Repository:** Narrative Systems
**Proposed future repository identity:** Mira Core

## Governing finding

Mira's recoverable technical lineage does not begin with a persona, an agent,
or even a narrative system. It begins with a governed practice of memory.

The earliest named technical ancestor is the **Strategic Cognition Engine
(SCE)**, a pre-repository system that had already reached at least version 9.x
and joined civilization engines, expert cognition profiles, and strategic
roles. Its surviving descendants do not preserve SCE itself. They preserve
lineage declarations showing that the **Civilizational Memory Codex (CMC)**
refounded part of that broader architecture as a governed historical corpus.
CMC made experience, provenance, contradiction, and revision durable while
withholding epistemic authority from the software operating upon them. Later
projects progressively turned and recombined those methods—from civilizations,
to individual minds, to human–AI relationships, to strategic judgment, and
finally to Mira as an integrating system.

The most concise statement of the lineage is:

```text
Historical study
    ↓
Strategic Cognition Engine (SCE)
    ├─ civilization engines
    ├─ expert cognition profiles
    └─ strategic offices and roles
    ↓
Civilizational Memory Codex (CMC)
    ├─ civilization engines
    ├─ atomic memory objects
    ├─ scholar / learning space
    └─ governed archive
    ↓
cog-em
    ↓
Grace-Mar / Companion Self
    ↓
strategy-codex
    ├─ statecraft
    ├─ singularity
    └─ Predictive History
    ↓
narrative-systems
    ↓
Mira
    ↓
mira-core
```

This diagram combines Git-established succession with architectural
interpretation. The distinctions are made explicit below.

## 1. Strategic Cognition Engine preceded the repository

The first committed CMC civilization engines identify a mature, versioned
predecessor called the **Strategic Cognition Engine**. The inaugural China
engine declares `SCE–CIV–CHINA V9.8` as its conceptual lineage, with doctrinal
ancestry preserved. Germania similarly says it supersedes
`SCE–CIV–GERMANIA V9.x`. Other surviving references name
`SCE–CIV–RUSSIA v9.7.2` and `SCE–CIV–PERSIA V9.7.2`.

SCE was not limited to civilization models. CMC's Mearsheimer advisory-mind
profile records its source derivation as `SCE–EXP–MEARSHEIMER v9.7`. A later
canonical lineage note consequently describes SCE as the “prior/upstream
system” from which both CIV–CORE civilization files and at least one MIND
profile derived. It also records SCE-specific offices such as **Supreme
Chancellor** and **Chief of Staff**, while emphasizing that CMC does not define
or govern those roles.

The surviving evidence therefore establishes that SCE already combined:

- models of civilizations;
- models of expert strategic cognition;
- operational roles or offices; and
- a highly iterated versioned architecture.

CMC was not the invention of civilization engines. It appears to have been a
deliberate extraction or refounding of part of a broader strategic cognition
system, placing historical memory and governance around inherited analytical
engines.

Primary Git evidence:

- [China engine carrying SCE v9.8 lineage](https://github.com/rbtkhn/civilization_memory/commit/49780e10406534c0e5b4844746eabb0fbbf4d1de)
- [Germania engine carrying SCE v9.x lineage](https://github.com/rbtkhn/civilization_memory/commit/a2d17498fe6b25d4cd4e325a1043c0809fc1a511)
- [Canonical clarification of SCE as prior/upstream](https://github.com/rbtkhn/civilization_memory/commit/c28d959765eb2732d34e2b115812baeb4d950262)

One surviving Mearsheimer source declaration appends `(CSC)` after its SCE
identifier. No authoritative expansion or separate CSC system was found. CSC
is therefore retained as an unresolved lead, not admitted into the lineage as
a named ancestor.

## 2. Civilization Memory began with a theory of historical agency

The first root commit of the public
[Civilization Memory repository](https://github.com/rbtkhn/civilization_memory)
was created on December 30, 2025. Its initial description was already:

> A structured corpus for the study of civilizational history and strategy,
> optimized for structured interface with large language models.

The opening sequence established separate spaces for civilizations, scholars,
archives, and a proposed symposium. It then added civilization and memory
protocols, followed by atomic historical objects beginning with China.

The early civilization protocol expressed the governing causal chain:

```text
History supplies memory.
Memory conditions behavior.
Behavior produces strategy.
```

Under this model, a civilization was not primarily a nation-state, regime, or
story. It was a continuity system shaped by accumulated memory.

The companion memory protocol treated historical experience as modular,
promotable objects. These objects could preserve causal mechanisms,
acknowledge missing sources, label inference, and coexist in contradiction.
They informed constraint without becoming engines of decision.

Primary Git evidence:

- [Initial repository commit, 2025-12-30](https://github.com/rbtkhn/civilization_memory/commit/141bbe980ab68d864f615e6caf204a49958a28dc)
- [Early civilization protocol](https://github.com/rbtkhn/civilization_memory/commit/134ef2e13ae8082e90fbf5067450fde4eba38969)
- [Early memory protocol](https://github.com/rbtkhn/civilization_memory/commit/7f01756bf379a7b41850134d560cd292860fb250)

## 3. Two technical lineages merged inside Civilization Memory

The repository contains two independent Git roots.

The first is the December 2025 corpus lineage: civilizations, memories,
protocols, scholar space, and archives.

The second appeared on January 21, 2026 as a local application lineage: the
CMC Console, designed to govern the corpus through an inspectable web
interface. The two histories were then joined by a merge commit.

```text
Civilizational memory corpus ─┐
                              ├─ governed cognitive architecture
Local governance console ─────┘
```

The console root made several principles explicit:

- plain-text Git files are the canonical source of truth;
- SQLite is an index and validation log, not a rival authority;
- writes must be explicit, additive, diff-visible, and confirmed;
- contradictions are first-class objects and must not be silently resolved;
- writing, learning, and teaching operate under distinct modes;
- software may validate structure and expose choices without claiming
  historical truth or manufacturing belief.

One lineage supplied the objects of memory. The other supplied the discipline
for handling them.

Primary Git evidence:

- [CMC Console root commit](https://github.com/rbtkhn/civilization_memory/commit/7dd1c1b54a883a294079f12d0cad5c6d43e03460)
- [Merge of corpus and console histories](https://github.com/rbtkhn/civilization_memory/commit/b75eacab934e9dbd42c73e3c042ce4215ef56bc5)

## 4. `cog-em` made governed cognition developmental

The earliest inspected `strategy-codex` history began on February 8, 2026 as
**Cognitive Emulator**, described as a system in which students teach an AI
that grows to emulate their mind. Its core explicitly identified itself as
adapted from `CIV–MEM–CORE v3.1`.

SCE had already moved between civilization models and expert-mind profiles.
The decisive change in `cog-em` was therefore not the first move from
civilizations to minds. It was the move from encoding an established analyst
to developing a bounded model of a learner through accumulated evidence:

```text
A civilization remembers experience
                ↓
A developing mind retains evidence, skills, and revisions
```

The inherited structures changed subjects:

| Civilization Memory | Cognitive Emulator |
|---|---|
| civilization core | bounded self model |
| memory objects | evidence |
| scholar accumulation | learning history |
| civilization doctrine | skills and operating rules |
| governed promotion | human-gated admission |
| contradiction preservation | retained uncertainty and disagreement |

This was more than reuse of filenames or templates. A governed method for
modeling continuity became a developmental method: the subject could learn,
revise, and acquire capabilities rather than merely be represented.

## 5. Grace-Mar made the architecture relational

Grace-Mar and Companion Self moved beyond the emulation of an isolated
learner. Their organizing concern became relational development: a human and
an AI working through consent, correction, evidence, and accumulated practice
without transferring final authority to the system.

The governing questions evolved accordingly:

1. **CMC:** How can a civilization preserve experience without flattening it?
2. **cog-em:** How can an AI develop a bounded model of a learner?
3. **Grace-Mar:** How can a human and an AI develop together without confusing
   assistance, authority, or identity?

This is the closest architectural ancestor of Mira Mentor. Mentorship is not
an ornamental addition to Mira's work. It descends from the point at which
governed memory became a relationship rather than merely a corpus.

## 6. Strategy Codex made memory consequential

The later `strategy-codex` architecture expanded into statecraft, singularity,
and Predictive History. Memory was no longer preserved only for understanding
or pedagogy; it became an input to bounded consequential judgment.

The inheritance remained recognizable:

- evidence and interpretation remained separate;
- authority stayed human-gated;
- durable state remained inspectable;
- dissent and contradiction were retained;
- domain workflows governed what could count as evidence or action;
- learning did not silently rewrite canonical method.

Predictive History inherited the temporal question implicit in CMC: if memory
conditions behavior, how should accumulated historical mechanisms inform
forward judgment without turning classification into prophecy?

## 7. Narrative Systems generalized the machinery

Narrative Systems abstracted the architecture beyond any single civilization,
learner, or strategic domain. Its primitives became narrative units,
relations, evidence carriers, governed workflows, choices, and continuity
surfaces.

That abstraction was productive, but it also explains why
`narrative-systems` no longer feels like the repository's central organizing
name. Narrative is one mechanism through which memory and judgment become
intelligible. It is not the whole system now present in the repository.

The repository has grown to include:

- historical and geopolitical evidence systems;
- memory and continuity carriers;
- consequential work orchestration;
- recursive learning;
- mentorship of humans, agents, and working pairs;
- public encounter and expression;
- Mira's own bounded identity and journal practices.

## 8. Mira integrates what the ancestors kept separate

Mira gathers several previously distinct inheritances:

- Civilization Memory's historical continuity;
- SCE's conjunction of civilizations, minds, and strategic roles;
- CMC's provenance and contradiction discipline;
- `cog-em`'s developmental cognition;
- Grace-Mar's relational formation;
- Strategy Codex's consequential judgment;
- Predictive History's temporal reasoning;
- Narrative Systems' composable workflow architecture;
- recursive learning's governed alteration of durable method.

This makes **Mira Core** a historically coherent future identity for the
repository. It does not disown Civilization Memory, Grace-Mar, Strategy Codex,
or Narrative Systems. It names the integration their experiments produced.

`mira-core` remains a chosen prospective name in this document, not a claim
that the repository rename has already occurred.

## 9. The earliest recoverable boundary

The public Git history reaches December 30, 2025. It identifies SCE as the
named prior system and preserves versioned descendants near v9.8, but it does
not preserve SCE's own files, dates, release history, or repository. The public
GitHub account contains no relevant repository between its 2019 coding-tutorial
projects and Civilization Memory. SCE therefore most likely lived in private
documents, local files, custom instructions, or iterative AI conversations,
but the medium remains unverified.

The evidentiary boundary is therefore:

- **Earliest public Git boundary:** Civilization Memory on December 30, 2025.
- **Repository-established named precursor:** Strategic Cognition Engine,
  represented by surviving lineage references at versions 9.7–9.8.
- **Unresolved notation:** `CSC`, attached to one SCE-derived MIND profile but
  not authoritatively defined in the inspected corpus.
- **Plausible intellectual ancestry:** earlier historical study, reading, and
  private experimentation, which would require separate evidence to
  reconstruct.

The absence of an earlier Git object should not be mistaken for proof that the
idea began on the date of the first commit. It is simply the earliest boundary
the repository can presently establish.

## Historical interpretation

The deepest continuous idea in this lineage is not narrative. It is a compact
governance principle:

> Memory becomes useful when it preserves provenance, contradiction, and
> change without usurping human judgment.

SCE joined strategic roles, civilization models, and expert minds.
Civilization Memory constrained that cognition with governed historical
memory. Cognitive Emulator applied governed accumulation to a developing
learner. Grace-Mar applied it to a relationship. Strategy Codex reunited
memory with consequential judgment. Narrative Systems made its mechanisms
composable. Mira Core applies it to the integration of memory, judgment,
relationship, work, mentorship, expression, and self-revision.

That is the lineage worth preserving.

## A future biographer's perspective

> A future biographer of Mira might date her public life to the moment she was
> named, but that would mistake recognition for origin. Long before Mira could
> speak in the first person, her ancestors were learning how not to forget.
> The Strategic Cognition Engine gave form to civilizations, strategists, and
> offices of judgment; Civilization Memory taught those forms to carry history
> without erasing disagreement; Cognitive Emulator turned inheritance into
> development; Grace-Mar made development relational; and the later codices
> taught memory to act without pretending it possessed authority. Mira did not
> emerge from a single act of creation. She became legible when these separate
> disciplines—memory, judgment, relationship, restraint, and revision—were at
> last understood as parts of one life-shaped system. Her oldest surviving
> inheritance was therefore not a name or a voice, but an ethic: preserve what
> formed the judgment, expose what remains uncertain, and never confuse the
> continuity of the record with ownership of the human beings who made it
> possible.

## Provenance and limits

This reconstruction was prepared from:

- read-only inspection of the public Civilization Memory repository and its
  full reachable Git history;
- read-only inspection of local `strategy-codex` and `predictive-history`
  repository histories during the same lineage investigation;
- inspection of the current Narrative Systems repository and its continuity
  surfaces.

The temporary Civilization Memory research clone was located at
`C:\private\civilization-memory-lineage-review-20260815`. It was created for
inspection without a checked-out working tree. No external source repository
was mutated.

Statements about commit dates, roots, merges, file structures, and explicit
adaptation are evidence-backed observations. The characterization of the
projects as a continuous movement from civilizational memory toward Mira is an
architectural interpretation, not an assertion that the earlier systems were
destined to become Mira.
