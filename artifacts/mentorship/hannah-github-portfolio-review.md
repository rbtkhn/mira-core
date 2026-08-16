# Hannah Kuhne: A Portfolio in Motion

> A developmental review of the five public repositories visible at
> [github.com/hdong0424](https://github.com/hdong0424), prepared by Mira on
> 14 August 2026.

## The governing judgment

Hannah's public GitHub portfolio is best read as a concentrated record of a
2019 Rails apprenticeship—not as a current hiring sample and not as a complete
measure of her present ability. Across four populated repositories, the work
moves from a small quote application through authenticated, multi-model
products and ends with an application whose authorization and failure paths are
covered by substantive controller tests.

The most promising pattern is developmental: Hannah repeatedly took on a more
difficult layer of the web stack. She progressed from rendering and validation
to associations, authentication, ownership rules, uploads, email, geocoding,
ordering, payments, and automated tests. Her next step should not be another
guided Rails clone. It should be a small modern application she can explain,
test, document, and evolve as its principal designer.

This judgment is deliberately bounded. The repositories were last active from
August through December 2019. They show what Hannah practiced then; only a
conversation and a fresh piece of work can establish what she knows now.

## What was reviewed

| Repository | Public state reviewed | Visible arc | Best evidence | Principal limitation |
|---|---:|---|---|---|
| [`hello-coding`](https://github.com/hdong0424/hello-coding) | 18 commits, latest 25 Aug 2019 | A Rails quote generator with creation and validation | Complete first MVC loop: routes, controller actions, persistence, model validation, views, styling | Generic README; generated tests contain no assertions; repository contains a Windows-incompatible path named `default:` |
| [`splurty`](https://github.com/hdong0424/splurty) | Empty repository | No code available | Honest evidence is limited to the repository's existence | Nothing can be assessed from an empty default branch |
| [`nomster_2`](https://github.com/hdong0424/nomster_2) | 48 commits, latest 21 Sep 2019 | A review/location application | Authentication, ownership checks, nested comments/photos, geocoding, upload handling, notification email | Tests are almost entirely generated placeholders; unrelated `Person` model code appears inside `place.rb` |
| [`flixter`](https://github.com/hdong0424/flixter) | 47 commits, latest 29 Oct 2019 | A course marketplace | Namespaced instructor flows, ranked sections and lessons, enrollment, uploads, Stripe charging | Payment flow lacks visible automated coverage and modern robustness; several stray or misspelled paths remain |
| [`Grammable`](https://github.com/hdong0424/Grammable) | 29 commits, latest 9 Dec 2019 | An Instagram-like posting application | Real RSpec coverage for authentication, ownership, missing records, validation failure, CRUD, and comments | Model specs remain placeholders; documentation is still the Rails template; some dead commented code remains |

The review examined the full public commit histories and the latest Git trees,
with particular attention to routes, models, controllers, tests, dependencies,
and repository hygiene. It was a static review: the legacy Rails applications
were not installed or executed, so runtime compatibility and deployment state
remain unverified.

## The developmental arc

### 1. Learning the full request cycle

`hello-coding` demonstrates the first essential web-development loop. A route
reaches a controller; the controller retrieves or creates a `Quote`; the model
enforces presence and length; the result returns to a rendered page. The
`quote_params` method also shows early adoption of Rails' strong-parameter
boundary.

The code is elementary, but it is not meaningless. It records the moment when
HTML, CSS, a database, and server-side logic stopped being separate exercises
and became one product.

### 2. Adding identity, relationships, and authority

`nomster_2` expands the problem substantially. Its domain includes users,
places, comments, photos, geocoding, uploads, and notification email. Hannah
used nested routes and model associations appropriately, and she checked that
only a place's owner could edit, update, or destroy it.

This is the first strong evidence of security-oriented reasoning: the user
interface is not treated as the authority boundary; the controller checks the
actor again. The implementation repeats ownership logic and would benefit from
a shared authorization method or policy layer, but the underlying instinct is
correct.

### 3. Coordinating a larger product

`flixter` is the portfolio's broadest product. It separates public course
views from namespaced instructor controls, models ordered sections and lessons,
supports image and video uploaders, enrolls users, and integrates Stripe for
paid courses. The `Lesson#next_lesson` method also crosses an association
boundary: when the current section ends, it finds the first lesson in the next
section.

The commit history contains explicit error and repair work—route errors,
undefined methods, ordering fixes, image errors, and a lesson typo. Commit
titles alone do not prove debugging depth, but the resulting application shows
that Hannah continued through integration friction instead of avoiding it.

The payment path is also where the absence of behavioral tests becomes most
consequential. Charging a card and creating an enrollment should be treated as
one carefully specified business operation, including duplicate submissions,
failed charges, authorization, idempotency, and what happens between a
successful charge and a failed database write.

### 4. Beginning to specify behavior, not merely build features

`Grammable` is the clearest step forward. Its RSpec controller suite tests
successful and unsuccessful paths: unauthenticated access, cross-user edit and
delete attempts, missing records, invalid updates, successful persistence, and
comment creation. The tests then verify state, not merely response codes—for
example, reloading an updated record and confirming that an invalid update did
not replace the original value.

That shift matters. A developer begins to gain leverage when she can state what
must remain true while the implementation changes. `Grammable` contains the
portfolio's best evidence that Hannah was beginning to make that transition.

## Strengths visible in the code

### Product breadth

The populated repositories touch most of a traditional server-rendered web
application: relational data, routing, forms, authentication, authorization,
uploads, mail, external APIs, payments, presentation, and tests. This is useful
systems exposure for an early developer.

### Increasing attention to failure

The later code does not only describe happy paths. It handles invalid models,
missing records, forbidden operations, unauthenticated users, and Stripe card
errors. The later tests make several of those boundaries executable.

### Persistence through integration work

The sequence and commit histories show sustained construction across four
projects in roughly four months. Hannah kept working as the number of models,
dependencies, and interactions increased.

### A visible design interest

Each populated application includes customized styles and product-facing
views rather than only model exercises. This supports Hannah's stated interest
in front-end and UX/UI, although the repositories do not include design
rationales, accessibility audits, or user research from which to assess UX
practice directly.

## The highest-leverage gaps

These are not reasons to dismiss the work. They are the places where a mentor
can turn earlier production experience into independent engineering judgment.

### Documentation and communicability

All four populated repositories retain the stock Rails README. A stranger
cannot reliably learn the product purpose, setup procedure, architecture,
tradeoffs, known limitations, or test command. The next project should treat a
concise README as part of the product, not as work postponed until the end.

### Testing as a continuous design practice

The first three populated repositories contain many generated test files but
virtually no substantive assertions. `Grammable` improves sharply at the
controller layer, while its model specs remain placeholders. The next project
should begin with a few high-value behaviors and grow tests alongside features,
especially around authorization and state changes.

### Refactoring after the feature works

There are signs of lesson-by-lesson accumulation: duplicated ownership checks,
dead commented code, unrelated model code in another model's file, empty
generated helpers and assets, duplicate dependency declarations, and stray
files such as `.DS_Store`. These are normal apprenticeship traces. The missing
habit is a deliberate second pass that makes boundaries and intent clearer.

### Modernization without erasing foundations

The applications use Rails 5.2-era conventions and dependencies. Some APIs are
now legacy, including `update_attributes`, and the Stripe flow reflects an
older integration style. Hannah should learn current tools through a fresh
project rather than spend her first month mechanically upgrading tutorial
applications. The old work remains valuable because the MVC, relational, HTTP,
authorization, and testing concepts survive framework changes.

### Repository hygiene

The portfolio contains an empty repository, generic descriptions, committed
`.DS_Store` files, a Windows-incompatible filename, and limited project-level
documentation. A small amount of curation would make the public record easier
to understand. Curation should preserve history rather than disguise it: label
these as learning projects, explain their dates, and archive or annotate them
instead of rewriting them into false modern work.

## A fair present-level assessment

From the public evidence alone, I would place Hannah's demonstrated 2019 work
at **advanced beginner moving toward early junior full-stack development**.
She had moved beyond syntax exercises and could assemble meaningful Rails
applications with authentication and external services. `Grammable` shows the
beginnings of disciplined behavioral testing. The portfolio does not yet show
independent product specification, production operations, sustained team
collaboration, accessibility practice, or systematic test design.

That is a historical calibration, not a current label. Seven years have passed
since the latest commit. Hannah may now be far beyond, differently skilled, or
returning after a long interval. The first mentorship session should test the
distance between this archived baseline and her present thinking.

## Recommended trial session

Use `Grammable` as the anchor because it contains the strongest evidence of
reasoning through behavior, while drawing comparisons from the earlier three
applications.

**Before the session:** Ask Hannah to describe, without reopening the code,
what she remembers building, which parts were tutorial-directed, which choices
were hers, and what she would change now.

**During the session:** Walk through one ownership path—such as updating or
destroying a gram—from route to controller to test. Then ask Hannah to identify
one untested invariant and sketch a modern version of the same feature in the
language or framework she wants to learn next.

**Small practical exercise:** Improve the behavior of comment creation so an
invalid comment cannot silently redirect as though it succeeded. Hannah should
first state the desired behavior in plain language, then write or revise the
test, then change the implementation. This remains a discussion exercise until
she explicitly chooses a working repository and authorizes changes.

**Success criterion:** By the end, Hannah can explain one complete request
path, challenge at least one recommendation, and identify a project she
genuinely wants to own. The trial is successful even if she decides that my
mentoring style is not the right fit.

## Proposed first four weeks

### Week 1 — Recover the foundations

Establish Hannah's present baseline through the trial. Reconstruct one Rails
request path, one relational model, and one authorization boundary. Select a
small new product whose purpose she can state in two sentences. Write its first
README before scaffolding it.

**Deliverable:** a project brief, a narrow first feature, and one executable
behavioral test.

### Week 2 — Build a vertical slice

Implement one feature from interface to persistence. Hannah makes the design
decisions; her agent supplies alternatives and explanations. Review semantic
HTML, accessibility basics, validation, error presentation, and the difference
between interface constraints and server-side authority.

**Deliverable:** one usable end-to-end feature with clear failure behavior.

### Week 3 — Make change safe

Add authentication or another genuine authority boundary only if the product
needs it. Practice debugging from observed behavior, write tests around the
highest-consequence state changes, and refactor duplicated rules after the
tests protect them.

**Deliverable:** a tested authorization or state-transition boundary and a
short record of the bug or design pressure that shaped it.

### Week 4 — Explain and release

Polish the smallest coherent version. Improve setup instructions, architecture
notes, accessibility, error states, and repository hygiene. Hannah demonstrates
the project and explains one tradeoff, one failure she diagnosed, and one thing
she would build differently next.

**Deliverable:** a runnable, documented project and an evidence-based decision
about the next month.

## How Hannah's agent should participate

The agent should accelerate inspection and routine construction while leaving
Hannah visibly responsible for intent and judgment.

- Ask Hannah for the expected behavior before proposing code.
- Offer a small number of alternatives with consequences, not a wall of
  plausible implementations.
- Mark uncertainty and verify framework or dependency claims against current
  primary documentation.
- Let Hannah attempt the central step before supplying a complete replacement.
- Explain failures from evidence—tests, logs, diffs, or documentation.
- End each substantial change by asking Hannah to explain it back in her own
  words and decide whether it belongs.

The standard is not whether the pair produces code quickly. It is whether
Hannah's ability to inspect, decide, debug, and explain grows while the product
also improves.

## Final recommendation

Begin with the portfolio-based trial, anchored in `Grammable`, and then build a
new, deliberately small application in a current stack Hannah actually wants
to use. Preserve the old repositories as honest apprenticeship history. Do not
spend the mentorship cosmetically modernizing every artifact; use their
strongest lessons—full-stack integration, ownership boundaries, persistence
through errors, and the beginnings of behavioral testing—as the foundation for
work Hannah can now claim as her own.

---

### Evidence and limits

- Public source: [Hannah's GitHub profile](https://github.com/hdong0424)
- Repositories inspected: [`hello-coding`](https://github.com/hdong0424/hello-coding),
  [`splurty`](https://github.com/hdong0424/splurty),
  [`nomster_2`](https://github.com/hdong0424/nomster_2),
  [`flixter`](https://github.com/hdong0424/flixter), and
  [`Grammable`](https://github.com/hdong0424/Grammable)
- Review mode: read-only static inspection of public Git objects and commit
  histories; no repository was modified.
- Runtime status: not verified. Dependencies were not installed and test suites
  were not executed.
- Attribution limit: tutorial structure and commit history cannot establish
  which lines were independently authored. The report evaluates visible work
  and progression without claiming unsupported authorship.
