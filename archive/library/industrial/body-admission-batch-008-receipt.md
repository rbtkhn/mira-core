# Industrial Library Body Admission Batch 008 Receipt

Date: 2026-08-23

## Authority Boundary

This batch admitted private-reading text bodies only. It did not stage, commit,
push, publish, ingest source bodies into the private Archive, or admit any body
to Git. The active private text root was:

`C:\private\mira-library-texts`

## Scope

- Authorities attempted: 2
- Bodies attempted: 3
- Bodies downloaded/derived before admission: 3
- Bodies inspected: 3
- Bodies admitted: 3
- Authorities newly registry-represented: 2
- Deferred Industrial authorities remaining missing: 2

## Admitted Bodies

| Source ID | Body ID | Work | Edition / Source | Bytes | SHA256 |
| --- | --- | --- | --- | ---: | --- |
| `LIB-INDUSTRIAL-AUTHORITY-054-LUXEMBURG` | `LIB-INDUSTRIAL-AUTHORITY-054-LUXEMBURG-REFORM-REVOLUTION-MIA` | `Reform or Revolution` | Marxists Internet Archive HTML component pages, Social Reform or Revolution, Militant Publications 1986 source; private-reading derivative, accessed 2026-08-23 | 160893 | `694a18bb90d85c2b0023bfdebbeba3ff0c3031074635c61ed151246c9214f755` |
| `LIB-INDUSTRIAL-AUTHORITY-054-LUXEMBURG` | `LIB-INDUSTRIAL-AUTHORITY-054-LUXEMBURG-JUNIUS-PAMPHLET-MIA` | `The Junius Pamphlet: The Crisis of German Social Democracy` | Marxists Internet Archive HTML component pages; Dave Hollis translation; GFDL copy/distribution statement; private-reading derivative, accessed 2026-08-23 | 261068 | `72aa920ee29cc756f7a498f529f9b31bc91acf4c88d5de704440e6f1817924f9` |
| `LIB-INDUSTRIAL-AUTHORITY-033-WEBER` | `LIB-INDUSTRIAL-AUTHORITY-033-WEBER-PROTESTANT-ETHIC-WIKISOURCE-DERIVED` | `The Protestant Ethic and the Spirit of Capitalism` | English Wikisource component HTML pages for 1930 Talcott Parsons translation with R. H. Tawney foreword; private-reading derivative, accessed 2026-08-23 | 604903 | `0ab0d7f25520352e615c113426ee8ba706059c979be16217b1621851e5f36ec0` |

## Inspection Notes

- Luxemburg `Reform or Revolution` preserved the MIA index, introduction, and chapters 1-10.
- Luxemburg `Junius Pamphlet` preserved the MIA index and chapters 1-8.
- Weber preserved the Wikisource component order: translator's preface, foreword,
  author's introduction, parts, chapters 1-5, and notes. Some harmless Wikisource
  navigation residue remains in the private-reading derivative; the body is
  structurally usable and not a corrupted or truncated extraction.

## Deferred / Not Attempted

- `LIB-INDUSTRIAL-AUTHORITY-051-FUKUZAWA` remains missing. No source route was
  downloaded, derived, or admitted in this batch.
- `LIB-INDUSTRIAL-AUTHORITY-078-CARSON` remains missing. No source route was
  downloaded, derived, or admitted in this batch.

## Validation

- `library validate --json`: passed
- `library render-index --check --json`: passed
- `tools/run.ps1 test --path tests/test_archive_library.py`: passed, 26 tests
- Direct private-store hash readback for all three newly admitted bodies: passed

## Census After Batch

Industrial current-state census with `MIRA_CORE_LIBRARY_TEXT_ROOT=C:\private\mira-library-texts`:

- Industrial authorities: 68
- Registry-represented Industrial authorities: 66
- Industrial registry bodies: 114
- Industrial referenced private bodies: 114
- Industrial physical private payloads: 114
- Industrial missing private payloads: 0

Library-wide live reproducibility was not claimed. The same census reports
expected missing private payloads in other eras from the active text-store
configuration, so this receipt makes only the scoped Industrial post-batch claim.

## Re-entry Point

The next Industrial admission candidates are Fukuzawa Yukichi and Rachel Carson.
Fukuzawa is the better next private-reading research target because the source
route is likely to be text/scan-edition tractable. Carson remains important, but
should be handled as a modern online-edition inspection case with careful
source-route preservation and no redistribution claim.
