# Reviewed browser plans

## Commands and storage

Use an external temporary root checked by `tools/run.ps1 session-preflight`.
The browser bridge saves raw `payload.json`, HTML, text, and a hash receipt;
it does not admit sources. Fill its local form through supported browser tools.
Do not export credentials, use clipboard transport, or inject browser writes.

```powershell
tools/run.ps1 newsletter-capture browser-plan --batch-file C:/private/example/input.json --plan-file C:/private/example/plan.json --json
tools/run.ps1 newsletter-capture browser-land-plan --plan-file C:/private/example/plan.json --json
```

Planning writes an immutable plan and temporary intake bodies, not archive
objects. Use a new plan filename for changed scope. Execution rechecks raw
captures, input and plan digests, actual archive membership, and destinations.
Reusing the same plan resumes verified state even if its completion receipt is
missing. A mismatch following an attempted admission is a run-level failure.
Do not edit a stopped plan to force execution; inspect its recorded failure.

The plan's `.receipt.json` sibling records processed/discovered counts,
per-source outcomes, attempts, verification, and discovery limitations. Its
terminal status is `complete`, `complete-with-gaps`, or `stopped`. Holds and
unresolved candidates are coverage gaps; an exclusion is a documented scope
decision. An unindexed coauthor stays in source/manifest metadata without
creating a new voice shelf.

## Input contract

Supply one JSON object with `discovery` and `candidates`. Capture paths may be
absolute or relative to this input file. Do not place captures/plans inside
the repository. Keep this input unchanged while resuming its plan.

```json
{
  "discovery": {
    "complete": true,
    "candidate_count": 1,
    "boundary": "Publication archive inspected through January 1, 2026"
  },
  "candidates": [{
    "capture_file": "capture-id/payload.json",
    "review": {
      "voice_slugs": ["blumenthal", "wyatt-reed"],
      "publication_date": "2026-03-21",
      "host_slug": "grayzone",
      "publication_url": "https://thegrayzone.substack.com/",
      "classification": "complete-written-article",
      "access_gate": "none",
      "evidence": {
        "authorship": {
          "basis": "publisher-author-index",
          "reference": "Observed author-index URL and quoted coauthor credit"
        },
        "publication_date": "MAR 21, 2026 displayed on article",
        "completeness": "Article body and ending inspected",
        "access_gate": "No gate present",
        "host": "Grayzone publication identity inspected",
        "homepage": "Observed publication homepage link"
      }
    }
  }]
}
```

Raw payload fields include `url`, `title`, `publication` (approved subscription
identifier), `html`, `text`, and timezone-aware `observed_at`. A bridge receipt,
when present, must match all three raw files. Review cannot override raw body,
URL, title, publication, or observation time.

The reviewed `publication_date` is the displayed ISO calendar day, not a day
derived from UTC observation time. Review homepage fields take precedence over
raw homepage fields; `homepage` is the legacy alias for `publication_url`.
All reviewed authors are passed through canonical person-slug aliases. Legacy
`voice_slug` is accepted; simultaneous plural input must agree with it exactly.
An explicit author set in the separate review replaces preliminary raw author
metadata as a whole, without changing the raw capture. Contradictory aliases
within that reviewed set are rejected.

Set raw `media_marked: true` for audio/video-marked candidates. Their review
must contain `evidence.accompanying_text`, documenting actual text inspection.
Use `description-only`, `announcement`, `narration-duplicate`, `guest-authored`,
or legacy `media-only/announcement` with completeness evidence for exclusions.
Set an observed non-`none` access gate for gated candidates. Missing evidence
becomes `unresolved`, never an inferred complete article.

## Editions

For related candidates, assign the same reviewed `work_id`. Add
`edition_kind: original-publisher` or `personal-newsletter` as appropriate.
Provide `edition_evidence` establishing the relationship and original publisher,
and `difference_summary` describing the comparison. These fields are candidate
fields beside `capture_file` and `review`.

The planner chooses one eligible original-publisher edition, otherwise one
eligible personal-newsletter edition. Multiple equally preferred candidates
or missing comparison evidence produce holds. Other eligible editions receive
an exclusion referencing the selected capture. Gated counterparts remain held.
The plan records exact-text, wording-variant, or incomplete-counterpart comparison
against immutable captures; it does not normalize or infer textual equivalence.
Related URLs, comparison evidence, and selection reason enter source provenance.
An already archived related edition prevents automatic replacement.

During destination review, include observed older post-ID URLs in reviewed
`related_urls` when source text and provenance establish the same work. The
planner preserves these aliases across edition selection and checks URLs in
manifest-owned source headers when imported manifest rows omit them. A native
intake duplicate response outside the reviewed match becomes a hold; it never
counts as successful admission or author verification.

Native dry runs also project the destination indexes. Intake projects only the
authors/participants in the planned sources, so unrelated voices sharing the
publication date are not rewritten or repaired. Native result diagnostics are
saved beside the plan; a failed result stops the run before another admission.
Inspect actual source/manifest state and resolve the cause before resuming.

## Legacy entry points

Single JSON payload, JSONL batch, and stdin interfaces remain supported. Review
fields can be supplied in the existing payload or an embedded `review` object.
They use the same planner/executor when `--land` is requested. Missing review
evidence prevents admission. Legacy streams without a discovery declaration
report incomplete discovery coverage. Stdin uses `MIRA_NEWSLETTER_TEMP_ROOT`
when set, otherwise the operating-system temporary directory.

Transport snapshots remain in their explicit temporary location for review and
resumption. Canonical archive bodies and lightweight receipts carry the result;
do not treat the temporary files as another maintained article collection.
