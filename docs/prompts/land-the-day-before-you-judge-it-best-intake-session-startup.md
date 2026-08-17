# Land the Day Before You Judge It: Intake Session Startup

Use this prompt to begin a fresh agent session for recent-day Narrative
Geopolitics intake without widening the task into synthesis, forecasting, or
publication. The operator command is simply `intake`; internal workflow and
engine names are implementation details.

```text
Use the `intake` front door and continue recent-day Narrative Geopolitics intake in:

C:\dev\mira-core

Startup contract:

1. Read `narrative-geopolitics/method/bounded-agency-contract.md`.
2. Run this read-only dynamic preflight before interpreting repository state:

   `.\tools\run.ps1 cadence startup intake --json`

3. Treat the command output—not this prompt—as authoritative for the current:
   - Git commit, branch, upstream divergence, and dirty paths;
   - archive file, manifest-row, and manifest-header counts;
   - latest and recent intake dates;
   - latest daily run and cadence-handoff status;
   - permitted and protected mutation surfaces;
   - warnings, blockers, readiness, and next action.
4. If `ready` is false, stop and repair only the named preflight blocker.
5. Preserve every reported dirty path unless I explicitly place it in scope.

Objective:

Land the transcripts I provide for the recent days quickly and faithfully. Continue until I say the intake batch is finished.

Core boundary:

`intake lands the day; geopolitical-synthesis judges the day`

For each supplied source:

1. Confirm that the transcript or source body is materially substantive.
2. Determine the publication date, truthful title, source URL, provisional person-level `voice_slug`, and channel-level `host_slug`.
3. Use canonical person slugs already established in the repository.
4. Keep person identity separate from host/channel identity.
5. Land the source under:
   `archive/geopolitics/sources/YYYY-MM-DD/`
6. Use `scripts/land_best_intake.py` and the repository Python wrapper:
   `.\tools\run.ps1 intake-land`
7. Preserve the supplied source body with minimal rewriting.
8. Apply deterministic wrapper trimming only for approved hosts:
   - `mario-nawfal`
   - `daniel-davis`
   - `alexander-mercouris`
   - `dialogue-works`
9. Apply conservative semantic sectioning only when cues are strong and the host is approved:
   - `dialogue-works`
   - `glenn-diesen`
   - `daniel-davis`
   - `judging-freedom`
   - `alexander-mercouris`
   - `mario-nawfal`
10. If trimming or sectioning requires interpretive judgment, preserve the text and mark the uncertainty.
11. Append exactly one truthful manifest row.
12. Require exact manifest coverage for every successfully landed source.
13. Do not update voice shelves during private intake. Canonicalization and shelf reconciliation remain downstream pre-synthesis work.
14. Do not create daily synthesis, forecasts, verification packets, public briefs, or new schemas.
15. Do not fetch missing sources unless I explicitly change the task from intake to retrieval.

Operational behavior:

- Inspect current Git and manifest state before the first landing.
- Preserve all existing work and never overwrite an existing archive source without stopping for review.
- Detect duplicate filenames and source or YouTube URLs before writing.
- Make reasonable provisional routing decisions; ask only when ambiguity would materially misidentify the source.
- After each landing, report:
  - archive path;
  - date and title;
  - voice and host routing;
  - trim/section result;
  - manifest result;
  - any unresolved uncertainty.
- At the end of each day batch, run intake-stage validation and report `stale-after-intake` as an expected synthesis handoff when applicable.
- At the end of the session, verify archive/manifest parity and summarize the landed batch.
- Do not stage, commit, push, publish, or run geopolitical synthesis unless I explicitly request it.

Begin by reading the skill and relevant intake method documents, inspecting repository state, and then wait for my first transcript.
```
