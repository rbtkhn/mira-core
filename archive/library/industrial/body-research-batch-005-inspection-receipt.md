# Industrial Library Body Research Batch 005 Inspection Receipt

Status: `body-research-reviewed`
Era: `industrial`
Date: 2026-08-23
Metadata packet: `archive/library/industrial/metadata-batch-005-design-v0.1.md`
Registry state: metadata stubs committed locally in `cbdd15f`
Gate: `operator-review-before-download-or-admission`

## Authority Boundary

This receipt records web source research only. It does not download source
files, admit bodies, mutate the registry, generate indexes, ingest into the
private Archive, stage, commit, push, or publish.

Candidate states below are research states, not registry truth. A candidate is
`body-research-ready` only when the source page, likely file target, rights
posture, language, edition issue, and fallback are clear enough for a later
bounded download/inspection batch. No candidate is `admission-ready` because no
local body bytes were downloaded or inspected.

## Batch Result

Authorities researched: 10
Candidates identified: 16
Body-research-ready candidates: 13
Body-research-incomplete candidates: 3
Downloaded: 0
Inspected locally: 0
Admitted: 0
Rejected: 0

## Candidate Disposition

| Candidate ID | Source ID | Authority | Work/body candidate | Upstream | Language | Rights posture observed | Current state | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `IND-BODY-005-001A` | `LIB-INDUSTRIAL-AUTHORITY-019-MACHADO-DE-ASSIS` | Machado de Assis | `Dom Casmurro` | Project Gutenberg author listing | Portuguese | PG listing; body page still needs direct inspection before download | `body-research-ready` | Preferred original-language principal-work candidate. |
| `IND-BODY-005-001B` | `LIB-INDUSTRIAL-AUTHORITY-019-MACHADO-DE-ASSIS` | Machado de Assis | `Memorias Posthumas de Braz Cubas` / `Memórias póstumas de Brás Cubas` | Project Gutenberg #54829 via catalogue mirrors | Portuguese | PG edition indicated; direct PG body page still needs inspection | `body-research-ready` | Preferred original-language candidate; preserve historical title spelling in edition label. |
| `IND-BODY-005-002A` | `LIB-INDUSTRIAL-AUTHORITY-028-SOJOURNER-TRUTH` | Sojourner Truth textual tradition | `Narrative of Sojourner Truth; a bondswoman of olden time` | Library of Congress item `05020876` | English | Library of Congress states the collection books are public domain and free to use/reuse | `body-research-ready` | Preferred scan/PDF source for 1875 edition; extraction must preserve Gilbert/Titus attribution. |
| `IND-BODY-005-002B` | `LIB-INDUSTRIAL-AUTHORITY-028-SOJOURNER-TRUTH` | Sojourner Truth textual tradition | `Narrative of Sojourner Truth, a Northern Slave` | Wikisource transcription | English | Wikisource marks pre-1931 publication and author-life basis public domain | `body-research-incomplete` | Useful transcription fallback, but edition/transcription lineage should be checked against scan before admission. |
| `IND-BODY-005-003A` | `LIB-INDUSTRIAL-AUTHORITY-040-FARADAY` | Michael Faraday | `The Chemical History of a Candle` | Project Gutenberg #14474 | English | Project Gutenberg states public domain in the USA | `body-research-ready` | Preferred clean public-science lecture body; Crookes editor must be recorded. |
| `IND-BODY-005-004A` | `LIB-INDUSTRIAL-AUTHORITY-064-CONRAD` | Joseph Conrad | `Heart of Darkness` | Project Gutenberg #219 via Online Books Page | English | PG source indicated; direct PG body page/license needs inspection | `body-research-ready` | Preferred principal-work candidate. |
| `IND-BODY-005-004B` | `LIB-INDUSTRIAL-AUTHORITY-064-CONRAD` | Joseph Conrad | `Lord Jim` | Project Gutenberg #5658 via Online Books Page | English | PG source indicated; direct PG body page/license needs inspection | `body-research-ready` | Preferred second principal-work candidate. |
| `IND-BODY-005-005A` | `LIB-INDUSTRIAL-AUTHORITY-081-SCHREINER` | Olive Schreiner | `The Story of an African Farm` | Project Gutenberg #1441 | English | Project Gutenberg states public domain in the USA | `body-research-ready` | Preferred literary/social-witness candidate; pseudonym Ralph Iron appears in body and should be noted. |
| `IND-BODY-005-006A` | `LIB-INDUSTRIAL-AUTHORITY-082-STANTON` | Elizabeth Cady Stanton | `Eighty Years and More; Reminiscences 1815-1897` | Project Gutenberg #11982 | English | Project Gutenberg states public domain in the USA | `body-research-ready` | Better first admission than unattributed convention-only text because authorship is cleaner. |
| `IND-BODY-005-006B` | `LIB-INDUSTRIAL-AUTHORITY-082-STANTON` | Elizabeth Cady Stanton | `Declaration of Sentiments` | Self.Gutenberg / History Is A Weapon mirror | English | Public-domain likely, but source is not preferred for admission | `body-research-incomplete` | Keep as later supplement after a stronger upstream scan or convention-source edition is located. |
| `IND-BODY-005-007A` | `LIB-INDUSTRIAL-AUTHORITY-084-ZITKALA-SA` | Zitkala-Sa | `American Indian Stories` | Project Gutenberg #10376 | English | Project Gutenberg states public domain in the USA | `body-research-ready` | Preferred first candidate; includes autobiographical stories, legends, and essays. |
| `IND-BODY-005-008A` | `LIB-INDUSTRIAL-AUTHORITY-093-WASHINGTON` | Booker T. Washington | `Up from Slavery` | Project Gutenberg #2376 | English | PG body page observed; direct catalogue/license details need body-header inspection | `body-research-ready` | Contains the Atlanta Exposition address as Chapter XIV; one body can support both target lanes. |
| `IND-BODY-005-009A` | `LIB-INDUSTRIAL-AUTHORITY-036-NIETZSCHE` | Friedrich Nietzsche | `The Genealogy of Morals` | Project Gutenberg #52319 | English translation | Project Gutenberg states public domain in the USA | `body-research-ready` | English translation by Horace B. Samuel, with J. M. Kennedy fragment; original German counterpart still preferred later. |
| `IND-BODY-005-009B` | `LIB-INDUSTRIAL-AUTHORITY-036-NIETZSCHE` | Friedrich Nietzsche | `Thus Spake Zarathustra` | Project Gutenberg #1998 | English translation | PG source indicated; body-header/license needs inspection | `body-research-ready` | Thomas Common translation likely; verify translator in body header before admission. |
| `IND-BODY-005-009C` | `LIB-INDUSTRIAL-AUTHORITY-036-NIETZSCHE` | Friedrich Nietzsche | German originals including `Also sprach Zarathustra` and `Zur Genealogie der Moral` | Projekt Gutenberg-DE | German | Site availability observed; reuse/download rights require separate review | `body-research-incomplete` | Do not admit until German source reuse terms and clean export route are settled. |
| `IND-BODY-005-010A` | `LIB-INDUSTRIAL-AUTHORITY-054-LUXEMBURG` | Rosa Luxemburg | `Reform or Revolution`; `The Junius Pamphlet` | Marxists Internet Archive | English translation | Mixed MIA rights signals: `Reform or Revolution` source says 1986 no copyright; `Junius Pamphlet` grants GFDL copy/distribution | `body-research-incomplete` | Roster-valid, but not clean enough for automatic admission; needs explicit license/translation review and likely separate body policy. |

## Preferred Next Download Batch

For a low-risk first Batch 005 download/inspection pass, use these 10 bodies:

1. Machado de Assis, `Dom Casmurro`, Project Gutenberg.
2. Machado de Assis, `Memorias Posthumas de Braz Cubas`, Project Gutenberg #54829.
3. Sojourner Truth textual tradition, 1875 `Narrative`, Library of Congress.
4. Michael Faraday, `The Chemical History of a Candle`, Project Gutenberg #14474.
5. Joseph Conrad, `Heart of Darkness`, Project Gutenberg #219.
6. Joseph Conrad, `Lord Jim`, Project Gutenberg #5658.
7. Olive Schreiner, `The Story of an African Farm`, Project Gutenberg #1441.
8. Elizabeth Cady Stanton, `Eighty Years and More`, Project Gutenberg #11982.
9. Zitkala-Sa, `American Indian Stories`, Project Gutenberg #10376.
10. Friedrich Nietzsche, `The Genealogy of Morals`, Project Gutenberg #52319.

Defer Luxemburg, Stanton `Declaration of Sentiments`, Sojourner Wikisource, and
Nietzsche German originals until rights and edition lineage are clearer.

## Acceptance Tests

- All 10 Batch 005 authorities were researched.
- Each candidate has a stable candidate ID, source ID, upstream source, language,
  rights posture, and current gate.
- No candidate claims `downloaded`, `inspected`, `admission-ready`, or
  `admitted`.
- Speech/transcription candidates preserve attribution and edition debt.
- Translation candidates preserve translator and original-language debt.
- Luxemburg remains incomplete rather than being forced through a mixed-license
  admission path.
- No source files were downloaded or admitted.

## Re-Entry Point

The next bounded action is a download/inspection batch for the 10 low-risk
preferred candidates above, writing only to the configured private library text
inspection root and stopping before registry body admission.
