# Industrial Library Body Research Batch 006 Inspection Receipt

Status: `body-research-reviewed`
Era: `industrial`
Date: 2026-08-23
Metadata packet: `archive/library/industrial/metadata-batch-006-design-v0.1.md`
Registry state: metadata stubs committed locally in `f97f86b`
Gate: `operator-review-before-download-or-admission`

## Authority Boundary

This receipt records web source research only. It does not download source
files, admit bodies, mutate the registry, generate indexes, ingest into the
private Archive, stage, commit, push, or publish.

Candidate states below are research states, not registry truth. No candidate is
`downloaded`, `inspected`, `admission-ready`, or `admitted`.

## Batch Result

Authorities researched: 10
Candidates identified: 17
Body-research-ready candidates: 6
Body-research-incomplete candidates: 11
Private-reading-blocked candidates: 0
Downloaded: 0
Inspected locally: 0
Admitted: 0

## Candidate Disposition

| Candidate ID | Source ID | Authority | Work/body candidate | Upstream | Language | Source posture observed | Current state | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `IND-BODY-006-001A` | `LIB-INDUSTRIAL-AUTHORITY-033-WEBER` | Max Weber | `The Protestant Ethic and the Spirit of Capitalism` | Internet Archive / Wikimedia Commons DJVU, IA id `protestantethics00webe` | English translation | 1930 Parsons translation visible online | `body-research-incomplete` | Important candidate; exact downloadable text route and edition lineage still need inspection. |
| `IND-BODY-006-001B` | `LIB-INDUSTRIAL-AUTHORITY-033-WEBER` | Max Weber | `The Protestant Ethic and the Spirit of Capitalism` | Marxists Internet Archive Weber archive | English translation | MIA page states copyleft/free, but translation line includes Talcott Parsons and Anthony Giddens | `body-research-incomplete` | Needs edition/translation lineage review before any download. |
| `IND-BODY-006-002A` | `LIB-INDUSTRIAL-AUTHORITY-034-DURKHEIM` | Emile Durkheim | `Le Suicide: Etude de Sociologie` | Project Gutenberg #40489 | French | Project Gutenberg states public domain in the USA | `body-research-ready` | Clean original-language sociology candidate. |
| `IND-BODY-006-002B` | `LIB-INDUSTRIAL-AUTHORITY-034-DURKHEIM` | Emile Durkheim | English excerpts from `Suicide` | Ethics of Suicide Digital Archive | English translation | Excerpted 1951 translation; not suitable as first body | `body-research-incomplete` | Useful reference only; do not admit as primary body. |
| `IND-BODY-006-003A` | `LIB-INDUSTRIAL-AUTHORITY-035-FREUD` | Sigmund Freud | `Civilization and its discontents` | Project Gutenberg #78221 | English translation | Project Gutenberg states public domain in the USA | `body-research-ready` | Clean PG candidate released 2026; record Joan Riviere translator and 1930 publication. |
| `IND-BODY-006-003B` | `LIB-INDUSTRIAL-AUTHORITY-035-FREUD` | Sigmund Freud | selected German originals | Project Gutenberg Freud author page | German | PG contains multiple German Freud works; exact target needs selection | `body-research-incomplete` | Defer until original-language target is chosen. |
| `IND-BODY-006-004A` | `LIB-INDUSTRIAL-AUTHORITY-053-LENIN` | Vladimir Lenin | `Imperialism, the Highest Stage of Capitalism` | Marxists Internet Archive | English translation | Page states public domain and permits copying/distribution with MIA credit | `body-research-ready` | Candidate is usable if MIA licensing is acceptable for library bodies. |
| `IND-BODY-006-004B` | `LIB-INDUSTRIAL-AUTHORITY-053-LENIN` | Vladimir Lenin | `The State and Revolution` | Marxists Internet Archive | English translation | MIA source/markup visible | `body-research-incomplete` | Needs exact source route capture before download/admission. |
| `IND-BODY-006-005A` | `LIB-INDUSTRIAL-AUTHORITY-057-CHURCHILL` | Winston Churchill | wartime speeches / literary works | International Churchill Society / Project Gutenberg routes | English | Online availability authorizes private-reading handling | `body-research-incomplete` | Essential authority. Select exact online texts before admission. |
| `IND-BODY-006-005B` | `LIB-INDUSTRIAL-AUTHORITY-057-CHURCHILL` | Winston Churchill | archival audio/broadcast references | International Churchill Society / Internet Archive pointer | English/audio | ICS points to Internet Archive broadcast items | `body-research-incomplete` | Promising later route; requires exact item-level source and transcript separation. |
| `IND-BODY-006-006A` | `LIB-INDUSTRIAL-AUTHORITY-060-MANDELA` | Nelson Mandela | `I am prepared to die` Rivonia statement | Nelson Mandela Foundation archive `ZA COM MR-S-010` | English | Online transcript located | `body-research-incomplete` | Strong source of text and provenance; private-reading candidate after stable file route inspection. |
| `IND-BODY-006-006B` | `LIB-INDUSTRIAL-AUTHORITY-060-MANDELA` | Nelson Mandela | `I am prepared to die` | South African History Online | English | Free access and citation available; copying/reuse terms not enough for admission | `body-research-incomplete` | Useful fallback/provenance cross-check; not a clean body source yet. |
| `IND-BODY-006-007A` | `LIB-INDUSTRIAL-AUTHORITY-079-EINSTEIN` | Albert Einstein | `Relativity: The Special and General Theory` | Project Gutenberg #30155 or #5001 | English translation | Project Gutenberg states public domain in the USA | `body-research-ready` | Clean first Einstein body; record Robert W. Lawson translator and edition chosen. |
| `IND-BODY-006-007B` | `LIB-INDUSTRIAL-AUTHORITY-079-EINSTEIN` | Albert Einstein | `Über die spezielle und die allgemeine Relativitätstheorie` | Project Gutenberg author listing | German | PG listing observed; body page needs direct inspection | `body-research-ready` | Preferred original-language counterpart if header confirms clean PG status. |
| `IND-BODY-006-008A` | `LIB-INDUSTRIAL-AUTHORITY-080-UDHR-DRAFTING` | UDHR drafting tradition | final Universal Declaration of Human Rights text | United Nations | English/multilingual | Official UN text visible online | `body-research-incomplete` | Final instrument is located; drafting records remain separate and need exact source-route selection. |
| `IND-BODY-006-009A` | `LIB-INDUSTRIAL-AUTHORITY-096-UNITED-NATIONS-CHARTER` | UN Charter / San Francisco conference tradition | final United Nations Charter text | United Nations | English/multilingual | Official UN text visible online | `body-research-incomplete` | Final instrument is located; conference records remain separate and need exact source-route selection. |
| `IND-BODY-006-010A` | `LIB-INDUSTRIAL-AUTHORITY-078-CARSON` | Rachel Carson | `Silent Spring` | online text route | English | Online text located for private reading | `body-research-ready` | Private-reading candidate. |

## Preferred Next Download Batch

For a conservative first Batch 006 download/inspection pass, use only these
likely clean bodies:

1. Durkheim, `Le Suicide`, Project Gutenberg #40489.
2. Freud, `Civilization and its discontents`, Project Gutenberg #78221.
3. Einstein, `Relativity: The Special and General Theory`, Project Gutenberg
   #30155 or #5001 after choosing one edition.
4. Einstein, German `Über die spezielle und die allgemeine
   Relativitätstheorie`, Project Gutenberg, after direct body-page inspection.
5. Lenin, `Imperialism`, Marxists Internet Archive.
6. Carson, `Silent Spring`, after selecting the online text route.

Do not bundle broad Churchill speeches, Mandela, UDHR, UN Charter, Weber, or
Durkheim English excerpts into the next low-risk pass until exact online file
routes are selected and inspected.

## Acceptance Tests

- All 10 Batch 006 authorities were researched.
- Each candidate has stable candidate ID, source ID, upstream source, language,
  source/reuse posture, and current gate.
- Source/reuse notes remain outward-boundary metadata rather than
  private-reading blockers.
- Churchill remains represented as essential while exact body routes are
  selected and inspected.
- No source files were downloaded or admitted.

## Re-Entry Point

The next bounded action is either a small download/inspection pass for
Durkheim, Freud, Einstein, Lenin, and Carson, or an exact-route pass for
Churchill, Mandela, UDHR, and UN Charter.
