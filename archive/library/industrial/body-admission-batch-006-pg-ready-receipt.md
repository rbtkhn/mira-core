# Industrial Library Body Admission Batch 006 PG-Ready Receipt

Status: `admitted`
Era: `industrial`
Date: 2026-08-23
Gate: `operator-review-before-next-admission`
Private text root: `C:\private\mira-library-texts`
Input inspection root: `C:\private\mira-library-texts\inspection\industrial-batch-006-online`

## Authority Boundary

The operator selected admission of the PG-ready Batch 006 bodies. This receipt
records the private-reading admission of Durkheim, Freud, and Einstein bodies
only. It does not stage, commit, push, publish, redistribute, or ingest any
body into the private Archive.

## Batch Result

Authorities admitted: 3
Bodies admitted: 4
Registry mutated: yes
Indexes regenerated: yes
Archive ingestion: no
Staged: no
Committed: no
Pushed: no

## Admitted Bodies

| Body ID | Authority | Work | Source | Bytes | SHA-256 |
| --- | --- | --- | --- | ---: | --- |
| `LIB-INDUSTRIAL-AUTHORITY-034-DURKHEIM-LE-SUICIDE-PG40489` | Emile Durkheim | `Le Suicide: Etude de Sociologie` | Project Gutenberg #40489 | 1122589 | `7b170fe725c164ebbfc6bb83b758b0302c3504003d5e1adf0ee5582fe4b538d3` |
| `LIB-INDUSTRIAL-AUTHORITY-035-FREUD-CIVILIZATION-DISCONTENTS-PG78221` | Sigmund Freud | `Civilization and its discontents` | Project Gutenberg #78221; Joan Riviere translation | 208244 | `5bd503cff493b952e487df18aaafb578baafe277bdb8d63735803b8314536665` |
| `LIB-INDUSTRIAL-AUTHORITY-079-EINSTEIN-RELATIVITY-LAWSON-PG30155` | Albert Einstein | `Relativity: The Special and General Theory` | Project Gutenberg #30155; Robert W. Lawson translation | 210653 | `86ed8156239455cbb6ed33e06097707d3ab7c40d46e9aa5ff32d3c3f94ef68fd` |
| `LIB-INDUSTRIAL-AUTHORITY-079-EINSTEIN-UEBER-RELATIVITAET-PG77850` | Albert Einstein | `Über die spezielle und die allgemeine Relativitätstheorie` | Project Gutenberg #77850; Karl Scheel editor | 165241 | `39f90ee5619fb88c563a731edf1e666dfc26b7cd0e0daae90e7973879d4f643b` |

## Source-Level Corrections

- Durkheim is now `located` with `Le Suicide` admitted; `Division of Labor`
  remains a future exact-route candidate.
- Freud is now `located` with `Civilization and its discontents` admitted;
  selected psychoanalytic writings remain future exact-route candidates.
- Einstein is now `located` with English and German Relativity bodies admitted;
  nuclear-era letters remain future exact-route candidates.

## Validation

Validation was run after index regeneration:

- `tools\run.ps1 library validate --json`
- `tools\run.ps1 library render-index --check --json`
- `tools\run.ps1 test --path tests/test_archive_library.py`
- Direct registry/file SHA-256 comparison for the four newly admitted bodies

Full `library verify-texts` was not run because the verifier is global-only in
this tooling and prior work established unrelated older private-store gaps.

## Re-Entry Point

The next bounded admission decision is the non-PG set: Lenin multi-file HTML,
UDHR/UN Charter HTML-body handling, Mandela text extraction, and Carson fuller
route inspection.
