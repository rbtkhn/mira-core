# Medieval Library 12-Authority Pilot Research Packet

Date: 2026-08-19
Status: `roster-ready; body-research-incomplete`
Evidence posture: `elevated`
Observation cutoff: `2026-08-19`
Authority effect: `none`

## Decision

Retain all twelve proposed source authorities as the review-ready pilot roster. Each
passes the historical-function and authority-boundary gates. The edition and body
research is incomplete: six records have no presently identified reusable English
body, three original-language candidates require repository-specific rights
confirmation, and all physical bodies still require header, completeness, and
file-quality inspection.

The packet supports operator review of the roster and a later metadata-only
implementation. It does not support text admission without further body research,
and it does not download, normalize, hash, admit, or publish a source body. A URL
below identifies a candidate or provenance surface, not an admitted file.

## Readiness Boundaries

| Boundary | Status | Consequence |
| --- | --- | --- |
| Twelve-authority roster | `ready-for-operator-disposition` | The authorities, functions, corridors, and reserve order can be accepted or corrected as a curatorial decision. |
| Metadata proposal | `ready-after-roster-acceptance` | Proposed IDs, authority labels, dates, era bases, tags, types, and conservative initial coverage fields may be implemented as `stub` or `located` records after explicit authorization. |
| Edition and body selection | `research-incomplete` | Unidentified originals, uninspected files, incomplete volume sequences, and unresolved host rights still require bounded research and inspection. |
| Text admission | `not-ready` | No body may be downloaded or admitted from this packet alone. Library Import verification remains required. |

## Gate Result

| # | Source authority | Transmission / institutional function | Original body | English body | Initial coverage ceiling | Gate result |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | Justinianic legal tradition | Roman-to-Byzantine-to-European legal transmission | Located, reusable edition likely | Translation candidates remain edition-fragmented | `principal-works` | Pass |
| 2 | Procopius | Imperial war, administration, and contested court memory | Located | Located, US public-domain volumes | `principal-work` | Pass |
| 3 | Qur'anic textual tradition | Canonical Arabic, law, ritual, and manuscript transmission | Located; digital-rights check required | Located, US public-domain compilation | `principal-work` | Pass |
| 4 | al-Tabari | Universal and caliphal chronicle tradition | Located at catalogue/discovery level | Complete SUNY translation restricted | `principal-work` | Pass with English gap |
| 5 | Nizam al-Mulk | Persianate advice-to-rulers and administrative transmission | Located; file and rights check required | Early 1916 translation candidate; completeness check required | `principal-work` | Pass |
| 6 | al-Biruni | Arabic-Persian observation and translation of Indian knowledge | Located at edition/catalogue level | Located, 1910 public-domain translation | `principal-work` | Pass |
| 7 | Ibn Khaldun | Historiography, state formation, and social theory | Located, 1858 Arabic edition | Rosenthal translation restricted; no complete reusable English body located | `principal-work` | Pass with English gap |
| 8 | Bede | Latin ecclesiastical institutions and political memory | Located at edition/catalogue level | Located, US public-domain translation | `principal-work` | Pass |
| 9 | Sima Guang | Court-sponsored chronicle as an instrument of governance | Located; OCR and reuse checks required | No complete reusable scholarly English translation located | `principal-work` | Pass with English gap |
| 10 | Kalhana | Sanskrit historiography and Kashmir dynastic memory | Located within Stein edition | Located, 1900 public-domain translation | `principal-work` | Pass |
| 11 | *Azuma Kagami* editorial tradition | Warrior-government institutional memory | Located for volumes 1-5; reuse check required | Selected Shinoda translation explicitly restricted | `partial-work` | Pass with English gap |
| 12 | *Secret History of the Mongols* textual tradition | Mongol imperial memory preserved through Chinese transcription | Located only through a derivative transcription tradition | Modern complete translations restricted | `fragmentary` | Pass with English gap |

## Record Proposals

### 1. Justinianic legal tradition

- Proposed ID: `LIB-MEDIEVAL-AUTHORITY-001-JUSTINIANIC-LEGAL-TRADITION`
- Registry title: `Corpus Iuris Civilis: Codex, Digesta, Institutiones, and Novellae`
- Authority label: `Justinian I / Tribonian and the imperial legal commission`
- Dates: `529` to `565`; label `529-565 AD`
- Era basis: `composition_period`; tags: `byzantium`, `roman-law`, `mediterranean`
- Permitted type: `legal`
- Corridor / function: late Roman jurisprudence reorganized under Byzantine imperial
  authority, then transmitted through medieval legal education and later European law.
- Boundary: a composite legal tradition, not a single authored work. The Codex,
  Digest, Institutes, and Novels must be separate bodies. The Novels include Greek
  material and cannot be represented honestly by a Latin-only bundle.
- Preferred original candidate: University of Grenoble Roman Law Library,
  Mommsen/Krueger Latin components, HTML, principally nineteenth-century editions
  ([S01](https://droitromain.univ-grenoble-alpes.fr/corpjurciv.htm)).
- Preferred English candidate: no single verified portable complete translation.
  Research a pre-1931 English *Institutes* or selected Digest translation as a
  separate body; do not represent it as the whole corpus.
- Fallback: digitized Mommsen/Krueger print volumes exposed by Grenoble's numerical
  library ([S02](https://droitromain.univ-grenoble-alpes.fr/Libraria.htm)).
- Rights posture: underlying nineteenth-century editions are public-domain
  candidates; the Grenoble transcription and site terms require confirmation before
  copying. A linked page is not itself a license grant.
- Coverage ceiling: source `principal-works`; body `complete-work` only per verified
  component. Projected maturity ceiling after inspection: Level 5; Level 6 requires
  explicit treatment of the Novels, language split, edition lineage, and corpus
  boundaries.
- Admission rationale: the pilot's clearest institutional-continuity record and a
  demanding test of composite, bilingual legal authority.
- Unresolved risk: English fragmentation and digital-reproduction rights.

### 2. Procopius

- Proposed ID: `LIB-MEDIEVAL-AUTHORITY-002-PROCOPIUS`
- Registry title: `History of the Wars; Buildings; Secret History`
- Authority label: `Procopius of Caesarea`
- Dates: `527` to `560`; label `6th c. AD`
- Era basis: `composition_period`; tags: `byzantium`, `eastern-mediterranean`
- Permitted type: `chronicle`
- Corridor / function: eyewitness imperial history crossing Byzantine, Persian,
  Vandal, and Gothic political worlds; comparison of official and hostile court memory.
- Boundary: *Wars* is the initial principal work. *Buildings* and *Secret History*
  are distinct works and must not be implied by admission of *Wars*.
- Preferred original candidate: the Greek side of the H. B. Dewing Loeb volumes,
  catalogued by Perseus with Greek and English on facing pages, 1914-1928
  ([S03](https://catalog.perseus.tufts.edu/catalog/urn:cts:greekLit:tlg4029.tlg001.opp-eng1)).
- Preferred English candidate: Project Gutenberg's Dewing volumes—Books I-II
  (`#16764`), III-IV, and V-VI—each admitted separately; the catalogue identifies
  the three available volumes ([S04](https://www.gutenberg.org/ebooks/author/6916)).
- Fallback: LacusCurtius' structured Dewing transcription
  ([S05](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Procopius/Wars/home.html));
  confirm its reuse terms before copying.
- Rights posture: Gutenberg marks its editions public domain in the United States.
  Later Loeb volumes and modernized translations are not presumed reusable.
- Coverage ceiling: source `principal-work`; separate volumes `partial-work` until
  all eight books are present and checked. Projected maturity ceiling: Level 5.
- Admission rationale: joins strategy, administration, cultural contact, and the
  problem of contradictory authorial voices.
- Unresolved risk: Gutenberg does not expose all eight books as a single clean body.

### 3. Qur'anic textual tradition

- Proposed ID: `LIB-MEDIEVAL-AUTHORITY-003-QURANIC-TEXTUAL-TRADITION`
- Registry title: `Qur'an: Arabic textual tradition and selected English translations`
- Authority label: `Qur'anic textual tradition`
- Dates: `610` to `656`; label `7th c. AD`
- Era basis: `multi_period`; tags: `arabia`, `islamic-world`, `arabic`
- Permitted type: `religious`
- Corridor / function: canonical Arabic, recitation, law, manuscript culture, and
  translation across the Islamic world.
- Boundary: model the Qur'an as a textual tradition, not an individual author. A
  modern reference text, manuscript transcriptions, reading traditions, and English
  translations are different bodies. No digital reference text proves identity with
  every historical witness.
- Preferred original candidate: the Cairo 1924 reference text surfaced by Corpus
  Coranicum alongside manuscript transcriptions; the project explains the reference
  edition and its relation to witnesses ([S06](https://corpuscoranicum.de/en/manuscripts/1409/page/1r)).
- Preferred English candidate: Project Gutenberg `#16955`, a UTF-8 side-by-side
  compilation including Pickthall, explicitly marked public domain in the United
  States ([S07](https://www.gutenberg.org/ebooks/16955)). Extracting one translation
  would create a derived body and must retain the compilation's provenance note.
- Fallback: an independently sourced scan of Pickthall's 1930 edition; do not use
  George Sale as the preferred body because its framing materially affects usability.
- Rights posture: Gutenberg supplies a US public-domain statement for `#16955` but
  warns that its source file's origins were initially unknown and it was later checked
  against paper copies. Corpus Coranicum image and transcription rights vary by
  holding institution ([S08](https://corpuscoranicum.de/en/manuscripts)).
- Coverage ceiling: source `principal-work`, not `complete-surviving-corpus`; each
  normalized printed text or translation may be `complete-work` after inspection.
  Projected maturity ceiling: Level 6 only if readings, reference edition, translation
  separation, and manuscript non-equivalence are explicit.
- Admission rationale: the essential canonical and institutional transmission case.
- Unresolved risk: reference-text licensing and the need to avoid collapsing reading
  traditions or manuscripts into one ahistorical original.

### 4. al-Tabari

- Proposed ID: `LIB-MEDIEVAL-AUTHORITY-004-AL-TABARI`
- Registry title: `Ta'rikh al-rusul wa'l-muluk / History of Prophets and Kings`
- Authority label: `Muhammad ibn Jarir al-Tabari`
- Dates: `915` to `923`; label `early 10th c. AD`
- Era basis: `composition_period`; tags: `abbasid`, `arabic`, `persianate`
- Permitted type: `chronicle`
- Corridor / function: universal chronology, transmitted reports, and the historical
  memory of early Islam under Abbasid scholarly institutions.
- Boundary: distinguish al-Tabari's *History* from his Qur'anic commentary. The
  Arabic chronicle is multi-volume; the SUNY English series is forty volumes including
  its index and remains a modern publication.
- Preferred original candidate: a public-domain Arabic print scan must be located and
  matched to its title page, editor, volume sequence, and upstream holding library.
  Existing unverified Shamela-style transcriptions remain discovery-only.
- Preferred English candidate: none admissible. SUNY Press states that its 1985-1999
  series is the only complete English translation and identifies the forty-volume set
  ([S09](https://sunypress.edu/Books/S/Set-History-of-al-abari)); treat it as restricted.
- Fallback: metadata-only record with a research pointer to the BnF catalogue for a
  representative SUNY volume and its bibliographic identity
  ([S10](https://catalogue.bnf.fr/ark:/12148/cb36183917z)).
- Rights posture: English restricted; Arabic candidate `unknown` until a specific
  scan and digital host's reuse terms are verified.
- Coverage ceiling: `metadata-only` initially; after Arabic admission,
  `principal-work` only if the volume sequence is demonstrably complete. Projected
  maturity ceiling: Level 4 without lawful English, Level 5 if a lawful translation
  is later found.
- Admission rationale: indispensable Arabic chronicle and a necessary test of
  isnad-bearing, multi-volume historical transmission.
- Unresolved risk: no verified reusable Arabic file or English translation in this pass.

### 5. Nizam al-Mulk

- Proposed ID: `LIB-MEDIEVAL-AUTHORITY-005-NIZAM-AL-MULK`
- Registry title: `Siyar al-muluk / Siyasat-nama`
- Authority label: `Nizam al-Mulk textual tradition`
- Dates: `1091` to `1092`; label `late 11th c. AD`
- Era basis: `composition_period`; tags: `seljuk`, `persianate`, `iran`
- Permitted type: `classical`
- Corridor / function: Persian advice-to-rulers literature joining court ethics,
  administration, intelligence, taxation, and dynastic legitimacy.
- Boundary: attribution to Nizam al-Mulk is conventional, but the recension and late
  chapter problem must remain visible. Do not model every printed *Siyasat-nama* as
  one stable authorial text.
- Preferred original candidate: the Persian edition represented by Open Library's
  1930 *Siyasatnamah-i yasir al-muluk* record and Internet Archive item
  `siyasatnamahiyas00niza` ([S11](https://openlibrary.org/works/OL43346623W/Siy%C4%81satn%C4%81mah-%CA%BCi_y%C4%81s%C4%ABr_al-muluk)); inspect the scan before use.
- Preferred English candidate: the 1916 translation attributed to Dinshah J. Irani,
  which Encyclopaedia Iranica records bibliographically
  ([S12](https://www.iranicaonline.org/articles/irani-dinshah/?generate_pdf=1)); a
  complete scan and title page must still be located.
- Fallback: metadata-only record pointing to the first French edition/translation
  and later Darke edition history summarized by Encyclopaedia Iranica
  ([S13](https://www.iranicaonline.org/articles/siar-al-moluk/?generate_pdf=1)).
- Rights posture: the 1916 English work is a public-domain candidate in the United
  States, but no inspected body was established. Darke 1960/1978 is restricted.
- Coverage ceiling: `principal-work`; projected maturity ceiling Level 5 if the 1930
  Persian and 1916 English candidates are clean and recension limits are documented.
- Admission rationale: the pilot's strongest Persianate administrative manual.
- Unresolved risk: provenance and completeness of the early English translation.

### 6. al-Biruni

- Proposed ID: `LIB-MEDIEVAL-AUTHORITY-006-AL-BIRUNI`
- Registry title: `Kitab fi tahqiq ma li-l-Hind / Alberuni's India`
- Authority label: `Abu Rayhan al-Biruni`
- Dates: `1025` to `1030`; label `c. 1030 AD`
- Era basis: `composition_period`; tags: `persianate`, `india`, `arabic`
- Permitted type: `historiography`
- Corridor / function: Arabic-language observation, translation, and comparison of
  Sanskritic knowledge, religion, chronology, and social practice.
- Boundary: the source authority is al-Biruni's Arabic *India*. Sachau's two-volume
  English translation is a translation body, not the original corpus.
- Preferred original candidate: Eduard Sachau's Arabic edition must be located as a
  stable institutional scan and matched to its title page; no clean text candidate was
  verified in this pass.
- Preferred English candidate: Eduard C. Sachau, *Alberuni's India*, two volumes,
  London, Kegan Paul, 1910. Open Library records the edition and plain-text route
  ([S14](https://openlibrary.org/books/OL23270588M/Alberuni%27s_India.?show_page_status=1)).
- Fallback: University of California digitization represented by the 1910 catalogue
  record ([S15](https://self.gutenberg.org/wplbn0001469991-alberuni-s-india-an-account-of-the-religion-philosophy-literature-geography-chronology-as-by-biruni-muhammad-ibn-ahmad.aspx)).
- Rights posture: 1910 English edition is a public-domain candidate in the United
  States; the specific digital file and any OCR derivative require inspection.
- Coverage ceiling: source `principal-work`; each English volume `partial-work` until
  both are present. Projected maturity ceiling: Level 4 initially, Level 5 after a
  verified Arabic body.
- Admission rationale: the pilot's clearest cross-civilizational observer and
  translator of knowledge systems.
- Unresolved risk: missing verified original-language body.

### 7. Ibn Khaldun

- Proposed ID: `LIB-MEDIEVAL-AUTHORITY-007-IBN-KHALDUN`
- Registry title: `Muqaddimah / Prolegomena to the Kitab al-Ibar`
- Authority label: `Abd al-Rahman Ibn Khaldun`
- Dates: `1375` to `1378`; label `1375-1378 AD`
- Era basis: `composition_period`; tags: `maghreb`, `arabic`, `north-africa`
- Permitted type: `historiography`
- Corridor / function: theory of dynastic formation, social solidarity, taxation,
  labor, urbanization, knowledge, and historical method.
- Boundary: the *Muqaddimah* is the introduction and first book of *Kitab al-Ibar*;
  it must not be described as Ibn Khaldun's complete historical corpus.
- Preferred original candidate: Quatremere's three-volume 1858 Arabic edition,
  represented by the Open Library work record with downloadable formats
  ([S16](https://openlibrary.org/works/OL1597257W/The_Muqaddimah_an_introduction_to_history?edition=key%3A%2Fbooks%2FOL3018348M)).
- Preferred English candidate: none admissible. Franz Rosenthal's 1958 complete
  translation is modern and restricted.
- Fallback: metadata-only English gap; a pre-1931 complete English translation was
  not located and should not be invented from excerpts or machine translation.
- Rights posture: Quatremere's underlying edition is public domain; the specific
  hosted derivative needs file inspection. Modern English restricted.
- Coverage ceiling: `principal-work`; projected maturity ceiling Level 4 without
  English and Level 5 only after a lawful complete translation.
- Admission rationale: the pilot's strongest explicit theory of state and historical
  causation.
- Unresolved risk: no reusable complete English body.

### 8. Bede

- Proposed ID: `LIB-MEDIEVAL-AUTHORITY-008-BEDE`
- Registry title: `Historia ecclesiastica gentis Anglorum`
- Authority label: `Bede the Venerable`
- Dates: `731` to `731`; label `completed c. 731 AD`
- Era basis: `composition_period`; tags: `northumbria`, `latin-christianity`, `england`
- Permitted type: `chronicle`
- Corridor / function: ecclesiastical correspondence, conversion, councils, kingship,
  chronology, and the construction of an English Christian past.
- Boundary: only the *Ecclesiastical History* is in scope. Bede's biblical,
  scientific, chronological, and hagiographical works remain outside this record.
- Preferred original candidate: the Latin text used by the Sellar revision is
  identified as Plummer's edition inside the Gutenberg front matter, but a separate
  clean Latin body still requires location and inspection.
- Preferred English candidate: A. M. Sellar revised translation, Project Gutenberg
  `#38326`, plain text/HTML, public domain in the United States
  ([S17](https://gutenberg.org/ebooks/38326)).
- Fallback: Gutenberg HTML exposing the title, translation lineage, and front matter
  ([S18](https://www.gutenberg.org/files/38326/38326-h/38326-h.html)).
- Rights posture: English body marked public domain in the United States. Latin
  edition likely public domain but digital provenance remains unverified.
- Coverage ceiling: source `principal-work`; English body `complete-work` after
  inspection. Projected maturity ceiling Level 4 initially, Level 5 with Latin.
- Admission rationale: connects institutional Christianity, documentary method, and
  political memory without treating Latin Europe as the shelf's default center.
- Unresolved risk: no independently located clean Latin file.

### 9. Sima Guang

- Proposed ID: `LIB-MEDIEVAL-AUTHORITY-009-SIMA-GUANG`
- Registry title: `Zizhi Tongjian / Comprehensive Mirror in Aid of Governance`
- Authority label: `Sima Guang and the Northern Song compilation team`
- Dates: `1065` to `1084`; label `completed 1084 AD`
- Era basis: `composition_period`; tags: `song-china`, `classical-chinese`, `east-asia`
- Permitted type: `chronicle`
- Corridor / function: court-sponsored historical compilation designed to instruct
  rulers through chronologically ordered precedent.
- Boundary: the principal text has 294 juan; later commentaries, abridgments, tables,
  and critical apparatus are separate bodies. Model the compilation team in notes
  rather than presenting Sima Guang as the sole mechanical author.
- Preferred original candidate: Chinese Text Project transcription aligned to a
  *Sibu Congkan* base scan, explicitly marked as OCR requiring comparison with images
  ([S19](https://ctext.org/wiki.pl?if=en&res=593436)).
- Preferred English candidate: none. Existing English translations are partial or
  modern; AI translations announced by CTP are not admission candidates.
- Fallback: an institutional public-domain scan of the 1816 Hu Kejia edition
  catalogued by Open Library ([S20](https://openlibrary.org/books/OL17918355M/Zi_zhi_tong_jian)).
- Rights posture: the premodern work and 1816 print are public-domain candidates, but
  CTP transcription reuse and OCR accuracy require separate confirmation.
- Coverage ceiling: `principal-work` only after all 294 juan are present and checked;
  otherwise `partial-work`. Projected maturity ceiling Level 4 without English.
- Admission rationale: a direct non-European case of history built as a technology
  of governance.
- Unresolved risk: scale, OCR errors, commentary mixing, and no reusable complete English.

### 10. Kalhana

- Proposed ID: `LIB-MEDIEVAL-AUTHORITY-010-KALHANA`
- Registry title: `Rajatarangini / River of Kings`
- Authority label: `Kalhana`
- Dates: `1148` to `1150`; label `c. 1148-1150 AD`
- Era basis: `composition_period`; tags: `kashmir`, `sanskrit`, `south-asia`
- Permitted type: `chronicle`
- Corridor / function: Sanskrit dynastic history combining documentary inquiry,
  inherited narrative, political judgment, and regional memory.
- Boundary: Kalhana's eight books are the authority. Later continuations of Kashmir's
  chronicle tradition require separate records or bodies.
- Preferred original candidate: Sanskrit text printed with M. A. Stein's edition;
  confirm whether the Wikisource/scan sequence includes the full Sanskrit apparatus.
- Preferred English candidate: M. A. Stein, *Kalhana's Rajatarangini*, 1900, volumes
  I-II. The Wikisource index exposes volume I and its page status
  ([S21](https://en.wikisource.org/wiki/Index:Kalhana%27s_Rajatarangini_Vol_1.djvu)).
- Fallback: the linked Internet Archive scan surfaced through the work-level catalogue
  ([S22](https://dhwani.ink/works/rajatarangini-kalhana)); recover the upstream item
  rather than treating the aggregator as evidence.
- Rights posture: 1900 edition and translation are public-domain candidates in the
  United States; Wikisource transcription provenance and both volumes require inspection.
- Coverage ceiling: source `principal-work`; each volume `partial-work` until the pair
  is verified. Projected maturity ceiling Level 5.
- Admission rationale: preserves South Asian historical method as more than a
  religious or literary supplement.
- Unresolved risk: determining whether the candidate contains a clean separable
  Sanskrit body, English body, or parallel edition.

### 11. *Azuma Kagami* editorial tradition

- Proposed ID: `LIB-MEDIEVAL-AUTHORITY-011-AZUMA-KAGAMI-TRADITION`
- Registry title: `Azuma Kagami / Mirror of the East`
- Authority label: `Kamakura bakufu chronicle editorial tradition`
- Dates: `1266` to `1300`; label `compiled late 13th c. AD; events 1180-1266`
- Era basis: `multi_period`; tags: `kamakura-japan`, `classical-japanese`, `warrior-government`
- Permitted type: `chronicle`
- Corridor / function: documentary memory of the emergence, institutions, disputes,
  and legitimating practices of warrior government.
- Boundary: anonymous/composite editorial tradition. The Berkeley JHTI presentation
  contains only volumes 1-5 of the Japanese original aligned to selected English
  translation; it is not the complete chronicle.
- Preferred original candidate: JHTI's Kanei-ban text derived from the National
  Institute of Japanese Literature database, volumes 1-5
  ([S23](https://jhti.studentorg.berkeley.edu/texthon17.htm)). Use for review only
  until NIJL and JHTI reuse terms are independently confirmed.
- Preferred English candidate: none admissible. JHTI states that Minoru Shinoda's
  selected 1960 translation is published by permission, all rights reserved, and may
  not be republished beyond fair use.
- Fallback: metadata-only record anchored by the National Diet Library work authority
  record ([S24](https://id.ndl.go.jp/auth/ndlna/00633641)); later locate a rights-clear
  Japanese scan.
- Rights posture: English restricted; Japanese digital text `unknown` pending source
  database terms.
- Coverage ceiling: source `partial-work`; projected maturity ceiling Level 4 if a
  lawful Japanese body is found, with English gap explicit.
- Admission rationale: the pilot's clearest institutional record of a non-imperial
  warrior government.
- Unresolved risk: source-body rights and absence of reusable English.

### 12. *Secret History of the Mongols* textual tradition

- Proposed ID: `LIB-MEDIEVAL-AUTHORITY-012-SECRET-HISTORY-MONGOLS-TRADITION`
- Registry title: `Secret History of the Mongols / Monggol-un niuca tobca'an`
- Authority label: `Anonymous Mongol court textual tradition preserved in Chinese transcription`
- Dates: `1228` to `1264`; label `13th c. AD; date disputed`
- Era basis: `multi_period`; tags: `mongol-empire`, `inner-asia`, `middle-mongol`, `china`
- Permitted type: `chronicle`
- Corridor / function: Mongol imperial origin, lineage, conquest, political norms,
  and memory transmitted through a Chinese-character phonetic transcription and gloss.
- Boundary: no original Mongolian-script witness survives. The received text combines
  Chinese-character transcription of Mongolian with Chinese gloss/translation; modern
  reconstructed Mongolian and English translations are derivative scholarly bodies.
- Preferred original candidate: locate and inspect a public-domain scan of the 1908
  Ye Dehui edition of the *Yuan chao bi shi*. Do not treat a modern Unicode
  transliteration as the lost original.
- Preferred English candidate: none admissible. Cleaves (1982) and de Rachewiltz
  (2004) are modern copyrighted translations.
- Fallback: metadata-only record. A scholarly account confirms that the earliest full
  witness survives only in Chinese transcription with Chinese translation and that
  its circumstances remain uncertain
  ([S25](https://www.cambridge.org/core/journals/bulletin-of-the-school-of-oriental-and-african-studies/article/abs/secret-history-of-the-mongols-some-fresh-revelations/0EF9D9817213E16E60A227DF9C2E1B31)).
- Rights posture: modern English restricted; 1908 print is a public-domain candidate,
  but no institutional downloadable body was verified in this pass.
- Coverage ceiling: source `fragmentary` because the original witness and script are
  lost even if the transmitted text is complete within its derivative tradition.
  Projected maturity ceiling Level 6 precisely by documenting that limit, not by
  claiming original-language completeness.
- Admission rationale: the pilot's most demanding survival, transcription, and
  reconstruction case.
- Unresolved risk: disputed date, derivative witness, and lack of a verified reusable body.

## Corridor Matrix

| Corridor | Authorities | Primary mechanism | What the pilot can compare |
| --- | --- | --- | --- |
| Roman-Byzantine-Mediterranean | Justinianic tradition; Procopius | codification, imperial administration, war narrative | law as institutional continuity versus history as contested court memory |
| Arabic-Persianate | Qur'anic tradition; al-Tabari; Nizam al-Mulk; Ibn Khaldun | canon, transmitted report, advice literature, causal historiography | four different ways authority organizes memory and rule |
| Arabic-Sanskritic contact | al-Biruni | translation, comparison, scientific and religious description | knowledge movement without assuming cultural equivalence |
| Latin ecclesiastical | Bede | correspondence, chronology, conversion, institutional narrative | church networks as documentary and political infrastructure |
| Chinese court historiography | Sima Guang | state-sponsored compilation and precedent | historical record designed explicitly for governance |
| Sanskrit regional historiography | Kalhana | dynastic narrative and source criticism | regional memory outside both court annal and sacred canon |
| Japanese warrior government | *Azuma Kagami* | documentary chronicle and retrospective legitimation | institutional memory of a new governing class |
| Mongol-Chinese textual survival | *Secret History* | phonetic transcription, gloss, reconstruction | what survives when original script and witness are lost |

This is intentionally asymmetric. Four Arabic/Persianate records remain because they
exercise four distinct mechanisms, not because that corridor receives a quota.

## Ranked Implementation Order

1. **Qur'anic textual tradition — difficult exemplar.** Exercise canonical text,
   manuscript non-equivalence, printed reference edition, translation separation,
   and variable digital rights before any body admission.
2. **Secret History of the Mongols — difficult exemplar.** Establish whether Level 6
   can describe derivative survival honestly without claiming a lost original.
3. **Justinianic legal tradition — difficult exemplar.** Model a composite,
   multilingual, multi-edition legal corpus with component-level coverage.
4. **Procopius.** Admit *Wars* volume by volume from established public-domain routes;
   do not imply the other works.
5. **Kalhana.** Verify the two-volume Stein edition and separate Sanskrit from English.
6. **Bede.** Admit the English body, then locate and verify a Latin counterpart.
7. **al-Biruni.** Verify both Sachau volumes; retain the Arabic gap until resolved.
8. **Nizam al-Mulk.** Inspect the Persian scan and locate the full 1916 English body.
9. **Ibn Khaldun.** Verify Quatremere Arabic volumes; keep English metadata-only.
10. **Sima Guang.** Resolve reuse and OCR quality before attempting a 294-juan body.
11. **Azuma Kagami tradition.** Do not copy JHTI text until Japanese-body rights are clear.
12. **al-Tabari.** Keep metadata-only until a specific Arabic edition and full volume
    sequence are verified; do not use circulating SUNY PDFs.

## Rejected-Candidate Ledger

No primary candidate was rejected. The ordered reserves remain outside the pilot:

| Reserve | Disposition | Reason |
| --- | --- | --- |
| Anna Komnene | Deferred | Valuable Byzantine/Crusader countervoice, but Procopius plus the Justinianic tradition already test the initial Byzantine corridor. |
| Zhu Xi | Deferred | Institutionally important, but Sima Guang offers a more direct first record of history as governance. |
| Ibn Battuta | Deferred | Travel and network observation are underrepresented, but al-Biruni supplies the pilot's first cross-civilizational observer with stronger public-domain prospects. |
| *Tale of the Heike* | Deferred | Important memory and literary transmission; *Azuma Kagami* has the stronger institutional-government function for this pilot. |
| Magna Carta tradition | Deferred | Legally consequential, but the Justinianic composite is the harder and more portable first legal exemplar. |
| Thomas Aquinas | Deferred | High intellectual importance but weaker fit with the pilot's primary transmission and institutional-memory comparison. |

Deferred means excluded from this twelve-record pilot, not rejected from the Medieval shelf.

## Contradictions and Evidence Limits

- **Online access is not reuse permission.** JHTI permits on-screen comparison while
  expressly restricting its English translation. CTP is open access, but its OCR and
  reuse posture are not equivalent to a rights-cleared portable body.
- **Public-domain work is not verified file provenance.** A nineteenth-century edition
  may be public domain while a modern transcription, normalization, or scan package
  carries separate terms or unclear lineage.
- **Original language is not always an original witness.** The *Secret History* is the
  decisive case: Chinese-character transcription of Mongolian is a transmitted witness,
  not the lost Mongolian-script original.
- **Complete work is not complete authority.** A complete *Wars*, *Muqaddimah*, or
  *Ecclesiastical History* remains only one principal work within its author's corpus.
- **Publication date does not settle global copyright.** The packet records US
  public-domain statements where repositories supply them. Admission must retain any
  jurisdictional qualification relevant to the operator's intended use.

## Implementation Acceptance Conditions

Before any registry mutation, review must settle each proposed ID, authority label,
date range, and coverage ceiling. Before any body admission, Library Import must:

1. inspect the actual file header and ending;
2. match author/work/editor/translator/edition to the provenance record;
3. verify the complete-work or partial-work claim;
4. record the host's license statement and jurisdictional limit;
5. assign one body ID per physical or logical provenance body;
6. hash and count the admitted file through `admit-text`;
7. run `verify-texts`, `library validate`, and the library test suite.

No record in this packet is `reviewed`, Level 6, or approved for body admission. The
three exemplars are tests of Level-6 reasoning, not pre-awarded Level-6 records.

## Source Ledger

Twenty-four substantive sources were reviewed, below the ceiling of thirty-six. One
additional discovery-only aggregator (S22) is retained transparently to preserve the
route to an upstream scan, but it is excluded from the substantive count. Other
discovery-only search results and mirrors rejected for weak provenance are not counted.

| ID | Source | Evidence role | Status |
| --- | --- | --- | --- |
| S01 | Grenoble, *Corpus Iuris Civilis* | component identity, languages, edition routes | confirmed institutional surface |
| S02 | Grenoble, *Libraria Numerica* | digitized Mommsen/Krueger editions | candidate provenance |
| S03 | Perseus Catalog, Procopius *De Bellis* | author, work, Dewing edition, Greek/English | confirmed catalogue metadata |
| S04 | Project Gutenberg, Dewing author page | available English *Wars* volumes | confirmed US-PD candidates |
| S05 | LacusCurtius, Procopius *Wars* | fallback structured transcription | rights unresolved |
| S06 | Corpus Coranicum, Cairo 1924 reference display | reference-text identity and witness distinction | confirmed project statement |
| S07 | Project Gutenberg `#16955` | English translations, formats, US-PD statement | confirmed candidate with provenance caveat |
| S08 | Corpus Coranicum manuscript overview | manuscript scale and variable image rights | confirmed project statement |
| S09 | SUNY Press, complete al-Tabari set | complete English series identity and dates | confirmed restricted publication |
| S10 | BnF catalogue, al-Tabari volume XXXVI | bibliographic cross-check | confirmed catalogue metadata |
| S11 | Open Library, *Siyasatnamah* | Persian edition/item route | candidate; file uninspected |
| S12 | Encyclopaedia Iranica, Dinshah Irani | 1916 English translation bibliography | confirmed bibliographic claim |
| S13 | Encyclopaedia Iranica, *Siar al-moluk* | edition and recension history | scholarly reference |
| S14 | Open Library, *Alberuni's India* | 1910 two-volume English edition route | candidate; files uninspected |
| S15 | UC digitization catalogue for *Alberuni's India* | fallback edition identity | catalogue metadata |
| S16 | Open Library, Quatremere *Muqaddimah* | 1858 Arabic edition route | candidate; files uninspected |
| S17 | Project Gutenberg `#38326` | Bede English body and US-PD status | confirmed candidate |
| S18 | Gutenberg HTML front matter | translation and Latin-edition lineage | source assertion in edition |
| S19 | Chinese Text Project, *Zizhi Tongjian* | base edition, 294-juan text route, OCR warning | confirmed project statement |
| S20 | Open Library, 1816 *Zizhi Tongjian* | public-domain print fallback | catalogue metadata |
| S21 | Wikisource, Stein *Rajatarangini* vol. I | scan and transcription route | candidate; coverage unverified |
| S22 | Dhwani work page | upstream scan discovery only | excluded from substantive count; aggregator; not admission evidence |
| S23 | Berkeley JHTI, *Azuma Kagami* | Japanese edition, five-volume scope, explicit English restriction | confirmed rights/scope statement |
| S24 | National Diet Library authority record | work identity and variants | confirmed authority metadata |
| S25 | Cambridge/Bulletin of SOAS article abstract | derivative witness and uncertainty | scholarly reference; article restricted |

## Persistence and Authority

This packet is repository-local metadata research under `archive/library/medieval/`
and is intended for later Git review. It contains no private source body. Creating it did not admit records to
`library-registry.json`, alter an era index, ingest the private Archive catalog, stage,
commit, push, or publish anything.
