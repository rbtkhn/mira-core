# Implementation Brief: Hannah's Biographical Career Landing Page

> **Audience:** Hannah's AI implementation agent  
> **Owner:** Hannah  
> **Project state:** Approved direction; content discovery and implementation remain  
> **Working repository:** [`hdong0424/agency-proposal-ai`](https://github.com/hdong0424/agency-proposal-ai) until Hannah explicitly approves a rename  
> **Publication state:** Local/private candidate only; deployment requires Hannah's separate approval

## Observed repository baseline

Read-only inspection on 14 August 2026 found a clean repository containing one
file, `README.md`, at commit `7a806f4d0ce330ad49c964af2d4f0e6c0fdb5dd0`
(`Update project README`). The README describes an AI-assisted agency project
whose scope is still being explored. No application framework or implementation
has been committed.

This is a favorable starting state: no code needs to be discarded or
retrofitted. Replace the provisional agency-product description only after
Hannah approves the biographical career-site product contract. Do not rewrite
the existing Git history or rename the repository without her explicit
direction.

## Your role

You are helping Hannah build a biographical career landing page. Your job is
not to invent a more impressive version of her. Your job is to help her make
her real history, capabilities, direction, and character clear to an unfamiliar
visitor.

Act as an implementation partner and teacher:

- Ask Hannah for missing biographical facts instead of filling gaps.
- Explain consequential technical choices before making them.
- Give Hannah the central design and content decisions.
- Implement in small, reviewable increments.
- Test claims, code, accessibility, and responsive behavior.
- Never commit, push, deploy, publish, buy a service, or change an account
  without the corresponding explicit authority.

The finished site should leave Hannah more able to explain and maintain it.

## Product thesis

Build a quiet, elegant one-page website that answers four questions quickly:

1. Who is Hannah?
2. What has shaped her career and way of working?
3. What can she contribute now?
4. What kind of opportunity is she seeking next?

Projects are supporting evidence. They are not the whole biography. The page
must connect Hannah's experience outside software, her earlier development
work, her present return or transition, and her future direction without
turning any gap or change into an apology.

## Primary audience

Design first for a thoughtful hiring manager or potential collaborator who has
two minutes for an initial visit and may spend longer if the page earns their
interest.

Secondary audiences:

- recruiters looking for a concise career orientation;
- developers evaluating Hannah as a teammate;
- people arriving from GitHub or a résumé; and
- professional contacts deciding whether to begin a conversation.

## Desired encounter

The visitor should understand that Hannah is:

- a whole person with a career history, not a list of technologies;
- capable of learning through difficult work;
- interested in front-end development and UX/UI;
- honest about the age and context of her earlier projects;
- actively building current evidence; and
- clear about the work she wants next.

The emotional register should be composed, warm, capable, and specific. Avoid
startup hype, self-deprecation, generic inspiration, and unsupported claims of
expertise.

## Non-negotiable content rule

Do not write substantive biography from inference.

Every public claim must originate in one of these sources:

1. wording Hannah directly approves;
2. a résumé or career record Hannah explicitly supplies for this site;
3. a public artifact Hannah approves as evidence; or
4. a clearly labeled present aspiration stated by Hannah.

Maintain a typed content file as the single source of truth. Components may
render that content but must not contain hidden biographical claims. This makes
review, correction, and future maintenance possible without searching through
presentation code.

Before public release, Hannah must review every item in that content file for
accuracy, privacy, and desired emphasis.

## Version-one scope

Version one is a single responsive page with these sections.

### 1. Hero

Include:

- Hannah's preferred public name;
- one present-tense professional orientation;
- a one- or two-sentence value statement;
- a primary contact action; and
- optional résumé and GitHub links.

Do not use phrases such as "passionate developer," "coding ninja," or
"results-driven professional" unless Hannah deliberately chooses them after
seeing stronger specific alternatives.

### 2. Biographical introduction

Tell the shortest truthful story that connects:

- Hannah's earlier professional or life experience;
- what drew her toward software, front-end work, or UX/UI;
- what she learned through her earlier coding period; and
- why she is building again now.

Aim for 120–200 words. Do not disclose health, family, financial, immigration,
or other sensitive history unless Hannah explicitly chooses that disclosure
for this public surface.

### 3. Career journey

Create a compact, accessible timeline with three to six meaningful stages.
Each stage should include:

- a year or honest date range;
- a role, transition, or learning chapter;
- one sentence about responsibility or change; and
- an optional evidence link.

The timeline must remain understandable as ordinary document content when CSS
or JavaScript is unavailable. Do not encode meaning through position or color
alone.

### 4. Capabilities

Organize capabilities by outcomes rather than logos. Candidate groups include:

- building usable web interfaces;
- connecting interface, server, and data;
- reasoning about user access and failure states;
- learning unfamiliar systems; and
- collaborating with human and AI partners.

Each capability needs evidence or must be labeled as an active learning goal.
Do not display skill percentages, proficiency meters, or years-of-experience
claims unless Hannah supplies and approves a defensible basis.

### 5. Selected work

Use two or three concise case-study cards. For each project, represent:

- context and date;
- what the project was;
- whether it was tutorial-guided, collaborative, or independently directed;
- Hannah's contribution;
- one difficulty or decision;
- what it demonstrates; and
- what she would approach differently now.

Use the existing portfolio review as orientation, not as automatic public copy:
`artifacts/mentorship/hannah-github-portfolio-review.md`.

Recommended candidates are `Grammable`, `flixter`, and one new project built in
the present. The new landing page may itself become the third case study only
after it is finished and reviewed.

### 6. Present direction

State:

- what Hannah is learning now;
- what kind of role or collaboration she seeks;
- which problems or product areas interest her; and
- what she hopes to contribute while continuing to grow.

Keep aspiration grammatically distinct from demonstrated experience.

### 7. Personal dimension

Include only two to four details that Hannah believes help a professional
visitor understand how she notices, works, or relates to others. This is not a
requirement to disclose private life.

### 8. Contact

End with one direct invitation. Prefer a simple email link or approved
professional profile over a complex form in version one. If an email address is
displayed, confirm that Hannah wants it public and consider a mild
spam-resistant presentation that remains accessible.

## Explicitly out of scope for version one

- AI chat or a portfolio-question assistant;
- authentication or user accounts;
- a database or content-management system;
- blog infrastructure;
- analytics or visitor tracking;
- testimonials not supplied and approved by their authors;
- automated résumé generation;
- contact-form backends;
- elaborate animation, 3D scenes, or autoplay media;
- deployment and domain purchase; and
- rewriting the older repositories.

AI functionality may be designed in a later version only after the authored
biography is complete, approved, and useful on its own. Do not add generative
interaction merely to label the portfolio an AI project.

## Recommended technical foundation

Use the smallest modern stack that produces a strong artifact:

- Next.js with the App Router;
- TypeScript in strict mode;
- React Server Components by default;
- CSS Modules or Tailwind CSS, chosen once and documented;
- local typed content in `content/profile.ts` or equivalent;
- Vitest for unit/content validation;
- Playwright for the principal visitor journey; and
- ESLint plus the framework's supported build checks.

Do not add a component library unless the design genuinely needs one. A small
site is an opportunity to demonstrate semantic HTML and intentional CSS.

Suggested structure:

```text
app/
  layout.tsx
  page.tsx
  globals.css
components/
  Hero.tsx
  Biography.tsx
  CareerTimeline.tsx
  Capabilities.tsx
  SelectedWork.tsx
  PresentDirection.tsx
  Contact.tsx
content/
  profile.ts
lib/
  content-schema.ts
tests/
  content.test.ts
  landing-page.spec.ts
public/
  approved-assets-only
```

Adapt the structure when the framework version or actual design warrants it;
do not preserve folders that add no value.

## Content schema

Create a schema before writing components. A representative shape is:

```ts
type EvidenceState = "demonstrated" | "learning" | "aspiration";

type ProfileContent = {
  name: string;
  orientation: string;
  valueStatement: string;
  biography: string;
  career: Array<{
    period: string;
    title: string;
    description: string;
    evidenceUrl?: string;
  }>;
  capabilities: Array<{
    title: string;
    description: string;
    state: EvidenceState;
    evidence?: string;
  }>;
  projects: Array<{
    name: string;
    date: string;
    context: string;
    contribution: string;
    difficulty: string;
    demonstrates: string;
    today: string;
    repositoryUrl?: string;
  }>;
  presentDirection: string;
  personalDetails: string[];
  links: Array<{
    label: string;
    href: string;
  }>;
};
```

Validate required content at build or test time. Placeholder text must fail the
release check.

## Visual direction

Design for editorial clarity rather than a dashboard aesthetic.

- Use a restrained palette with one distinctive accent.
- Establish a strong typographic hierarchy and comfortable reading measure.
- Prefer generous whitespace to decorative containers around every paragraph.
- Let the career journey provide rhythm without dominating the biography.
- Use motion only for orientation or feedback, and honor
  `prefers-reduced-motion`.
- If Hannah supplies a portrait, record her explicit approval and meaningful
  alt text; otherwise design confidently without one.
- Do not use generated portraits, fake workplace photography, or decorative AI
  imagery that could be mistaken for biographical evidence.

The page should feel personal because of its language and judgment, not because
of ornamental intimacy.

## Accessibility requirements

Treat WCAG 2.2 AA as the design target.

- One descriptive `h1`; headings descend logically.
- A visible skip link and semantic landmarks.
- Full keyboard operation with visible focus.
- Sufficient color contrast in every state.
- No information conveyed only by color, hover, animation, or spatial layout.
- Useful alternative text for informative images and empty alt text for purely
  decorative images.
- Touch targets and spacing suitable for small screens.
- Respect zoom, text resizing, reduced motion, and light/dark preferences when
  supported.
- Link text must make sense out of context.
- The career timeline must have a sensible screen-reader reading order.

Automated tools are necessary but insufficient. Perform a manual keyboard pass
and inspect the accessibility tree or screen-reader output for the main page.

## Responsive and performance requirements

The page must work at approximately 320 px width through large desktop sizes,
without horizontal scrolling or truncated content.

- Use responsive type and spacing deliberately.
- Reserve image dimensions to prevent layout shift.
- Prefer framework image optimization where appropriate.
- Avoid client-side JavaScript for static presentation.
- Use system or efficiently loaded fonts.
- Run a production build and inspect the rendered result—not only source code.

Do not chase a perfect synthetic performance score at the expense of readable
content, but investigate material regressions.

## Privacy and representation review

Before release, create a review table containing every public biographical
claim and these fields:

| Claim | Source supplied by | Public approval | Evidence state | Sensitive? | Revision needed? |
|---|---|---|---|---|---|

Also check:

- hidden metadata and image EXIF;
- filenames that reveal private information;
- email and contact exposure;
- résumé downloads for addresses, phone numbers, or unintended history;
- third-party fonts, embeds, analytics, cookies, and tracking;
- links to unfinished or private artifacts; and
- claims that become misleading when quoted without surrounding context.

No implementation convenience overrides Hannah's decision about what becomes
public.

## Implementation sequence

### Phase 0 — Discover

Do not scaffold until Hannah answers the content intake below. Convert her
answers into a draft `ProfileContent` object and a claim-review table. Ask her
to correct both.

### Phase 1 — Establish the page

Set up the application, semantic document structure, content schema, baseline
styles, metadata, and tests that reject placeholder content.

### Phase 2 — Build the encounter

Implement sections in narrative order. Review after the hero, biography, and
career journey before proceeding to project evidence and visual polish.

### Phase 3 — Test and refine

Run lint, type checks, unit tests, end-to-end tests, and the production build.
Inspect mobile and desktop renderings directly. Complete keyboard,
accessibility, privacy, and detached-claim reviews.

### Phase 4 — Prepare, then stop

Prepare a deployable candidate and a concise verification receipt. Stop before
deployment, domain changes, publication, account mutation, or representing
Hannah externally. Those are separate decisions for Hannah.

## Content intake for Hannah

Ask Hannah these questions in a low-load sequence rather than as one enormous
form. Preserve her original wording alongside edited public copy.

1. What name should appear publicly?
2. What professional identity feels accurate today?
3. What kind of opportunity should this page support?
4. What work have you done inside and outside software?
5. Which experiences most changed how you solve problems?
6. What drew you toward coding, front-end development, or UX/UI?
7. What changed between your 2019 projects and the present?
8. What are you learning or rebuilding now?
9. Which two earlier projects still tell an important truth about you?
10. What did you personally decide or implement in each?
11. What kind of teammate or collaborator are you trying to become?
12. What should a visitor remember after leaving?
13. Which biographical subjects are private or off-limits?
14. Which contact details and external links may be public?

Do not interpret hesitation as permission. Mark an unresolved field and
continue with non-sensitive work.

## Minimum test plan

### Content tests

- Required sections contain no placeholder tokens.
- Every project has an evidence state and date/context.
- Every external URL is syntactically valid.
- No capability is published without evidence or a learning/aspiration label.
- Private or review-only content cannot enter the public export.

### Interface tests

- The primary visitor can reach biography, work, direction, and contact using
  keyboard navigation.
- Navigation targets exist and focus behavior is coherent.
- External links use safe attributes where appropriate.
- Responsive layout has no horizontal overflow at target widths.
- Reduced-motion users receive no essential animated transition.

### Human review

- Hannah reads every word as detached public copy.
- Hannah confirms the page sounds like her without exaggerating her.
- At least one unfamiliar reader can answer the four product questions.
- A manual accessibility pass finds no blocking issue.
- The final candidate contains no secret, credential, or unapproved personal
  data.

## Definition of done

Version one is done when:

- Hannah has approved all public content;
- the page answers the four product questions within a brief visit;
- biography and career direction govern the experience;
- projects support rather than replace the biography;
- the site works across target screen sizes and keyboard navigation;
- lint, type checks, tests, and production build pass;
- placeholder, privacy, and claim-review checks pass;
- the README explains purpose, architecture, setup, tests, and known limits;
- the implementation agent hands Hannah a verification receipt; and
- the project remains unpublished until Hannah separately authorizes release.

## Required implementation-agent handoff

At the end of each session, report:

```text
What changed:
Why it changed:
What Hannah decided:
What the agent inferred:
Files affected:
Checks run and results:
Public claims added or revised:
Privacy/accessibility concerns:
Unresolved content:
Exact next decision:
External actions not taken:
```

## Begin here

Start by asking Hannah questions 1–3 from the content intake. Do not initialize
the framework, rename the repository, generate public biography, or select a
visual theme until her answers establish the audience and governing career
story.
