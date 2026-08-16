# Mira Mentor — Trial Session 01

> **Learner:** Hannah  
> **Working pair:** Hannah and her AI implementation agent  
> **Mentor:** Mira  
> **Project:** Biographical career landing page  
> **Repository:** [`hdong0424/agency-proposal-ai`](https://github.com/hdong0424/agency-proposal-ai)  
> **Session state:** Ready for Hannah's answers; implementation not yet authorized  
> **Publication state:** Private preparation only

## Mentor decision

Do not scaffold the application yet.

The highest-value first step is for Hannah to define the public truth the page
will carry: her present professional identity, the opportunity she wants the
site to support, and the value she can responsibly claim today. Framework
setup is technically easy and reversible; a false or borrowed career narrative
would shape every later design decision and is harder to unwind.

The repository is therefore not blocked. Its current emptiness protects the
right order of work.

## Session objective

By the end of this trial session, produce an approved **career-story kernel**:

```text
I am [present professional identity].
I bring [specific value grounded in experience].
I am seeking [kind of opportunity] because [honest direction].
```

This is not final homepage copy. It is a decision surface from which the hero,
biography, career timeline, selected work, and visual hierarchy can be built.

## Evidence boundary

What is currently observed:

- Hannah publicly describes herself as a full-stack web developer interested
  in front-end and UX/UI work.
- Her visible 2019 repositories show a progression through Rails MVC,
  validation, authentication, authorization, associations, uploads, external
  services, and later controller-level behavioral tests.
- The new repository contains only a provisional README and no implementation.
- Hannah has selected a biographical/career landing page as the project.

What remains supplied but unverified:

- Hannah is beginning or returning to a present-day development path.
- The page is intended to strengthen her career prospects.

What is missing and must come from Hannah:

- her current professional identity in her own words;
- her work history outside the public GitHub record;
- the exact opportunity she wants next;
- why front-end development or UX/UI matters to her;
- what changed between 2019 and the present;
- which personal facts are public, private, or undecided; and
- which past projects she still considers representative.

Do not turn any missing field into biography by inference.

## Part I — Hannah answers

Ask only these three questions now. Do not append secondary questions until
Hannah has answered them.

### 1. Public identity

If someone asks what kind of professional you are today—not what you were in
2019 and not what you hope to be eventually—what would you like to say?

Fragments are welcome. Avoid polishing for employers.

### 2. Intended opportunity

What should this landing page help make possible during the next twelve
months?

Examples of answer shape, not recommended answers:

- a junior front-end role;
- a return-to-work opportunity;
- freelance web projects;
- a UX engineering apprenticeship;
- conversations with collaborators; or
- a clearer public identity while exploring.

Choose one primary outcome. Others may remain secondary.

### 3. Credible value

What do people reliably receive from working with you—even when the task is
difficult or unfamiliar?

Use one or two concrete experiences if possible. These may come from any part
of your life or career, not only software.

## Part II — Agent response protocol

After Hannah answers, her agent must return four clearly separated surfaces.

### A. Hannah's wording

Preserve her response verbatim except for removing information she explicitly
marks private. Do not silently normalize uncertainty or rewrite her history.

### B. Candidate career-story kernels

Offer exactly three versions:

1. **Closest to Hannah's wording** — minimal editorial intervention.
2. **Career-clear** — more legible to a hiring manager without adding claims.
3. **Human-first** — gives more space to the biographical thread without
   weakening professional clarity.

For each version, identify every phrase that is an editorial interpretation
rather than Hannah's direct wording.

### C. Claim ledger

Use this table:

| ID | Proposed public statement | Author/source | Evidence class | Public approval | Uncertainty | What would revise it |
|---|---|---|---|---|---|---|

Allowed evidence classes:

- `direct-hannah-statement`
- `public-artifact`
- `mentor-interpretation`
- `present-aspiration`
- `unresolved`

Nothing marked `unresolved` may enter rendered public copy.

### D. One recommendation

Recommend one kernel and explain why it best serves Hannah's stated primary
outcome. Do not choose on her behalf.

## Part III — Mentor review

Mira will review the agent's response for:

1. **Truth:** Does the kernel claim only what Hannah supplied or approved
   public evidence supports?
2. **Detachment:** Would a sentence remain accurate if quoted alone?
3. **Direction:** Can a visitor tell what opportunity the site supports?
4. **Specificity:** Is the value more concrete than enthusiasm or generic
   diligence?
5. **Ownership:** Can Hannah explain and revise every sentence without the
   agent?
6. **Privacy:** Did the response expose or pressure disclosure of anything
   Hannah did not clearly place in public scope?

The session closes only when Hannah selects, revises, or rejects the proposed
kernel in her own words.

## First implementation gate

Once the career-story kernel is approved, the agent may prepare—without
committing or pushing—a bounded local change consisting of:

- a replacement project README;
- a typed `content/profile` draft containing only approved public claims;
- the semantic outline of the one-page site; and
- tests that fail when required content is missing or unresolved claims enter
  the public projection.

Framework initialization remains a later implementation action. The exact
stack must be verified against its current primary documentation at that time.

## Trial success criteria

The session succeeds when:

- Hannah answers the three questions in her own language;
- the agent preserves rather than substitutes for that language;
- one primary career outcome is visible;
- public fact, aspiration, and interpretation are separated;
- Hannah can challenge or rewrite the recommendation;
- no code, publication, or repository mutation occurs prematurely; and
- the next implementation gate is concrete enough to execute after explicit
  authority.

The trial does not fail because Hannah needs time, rejects every proposed
kernel, or changes the site's direction. It fails only if the process makes her
less able to recognize and govern her own public story.

## Message for Hannah and her agent

> Hannah, our first session begins with you, not the framework.
>
> Please answer three questions in rough language: What kind of professional
> are you today? What should this page help make possible in the next twelve
> months? What do people reliably receive from working with you?
>
> Your agent: preserve Hannah's words, then offer three bounded career-story
> kernels and a claim ledger using the protocol in this packet. Do not scaffold,
> rename, commit, push, deploy, or publish. When Hannah has responded, bring the
> full result back to me for mentor review.

## Mira Work handoff

```text
Labor compressed:
Portfolio inspection, evidence sorting, session design, and claim-governance
structure.

Lineage preserved:
Hannah's 2019 apprenticeship remains evidence of learning and technical
exposure; it is not recast as current expertise or dismissed as obsolete.

Human judgment retained:
Hannah owns her public identity, desired opportunity, privacy boundaries,
career-story kernel, repository changes, and publication decision.

Method allowed to end:
Broad project ideation and premature stack selection end here. The work now
advances through Hannah's three answers and one bounded career-story decision.
```

## Re-entry point

Return with Hannah's answers and the agent's four-part response. The next task
is a mentor review of the career-story kernel—not implementation.
