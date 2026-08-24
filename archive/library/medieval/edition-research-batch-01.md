# Medieval Edition Research — Batch 01

Date: 2026-08-19
Status: `review-only`
Authority effect: `none`
Records: 10
Substantive sources: 20 of 30 maximum

## Decision Result

This batch resolves the first feasibility layer for ten difficult Medieval authorities. It identifies preferred witnesses or editions where defensible, but authorizes no registry mutation, download, private-body admission, completeness claim, or maturity advancement.

The result is deliberately asymmetrical:

- The Tanzil Qur'anic reference text is the only original-language route with an explicit reusable text license, and its verbatim/no-change condition must be preserved.
- Marco Polo's Yule–Cordier English route is promising but not equivalent to BnF français 1116.
- The Rus' Primary Chronicle has strong institutional witness access but separately governed transcription and translation layers.
- The remaining records are partial, restricted, metadata-only, or lack a complete English route.
- Viewability never counts as portability, and public-domain age never substitutes for file provenance or repository terms.

## Triage Matrix

| Authority | Original rights | English rights | Body coverage ceiling | Current / ceiling |
| --- | --- | --- | --- | --- |
| Justinian I / Tribonianic legal commission | `unknown` | `unknown` | `principal-works` | L2 / L6 |
| Qur'anic textual tradition | `plausible-open` | `unknown` | `Hafs-reference-text-only` | L3 / L6 |
| Alf Layla wa-Layla medieval textual tradition | `unknown` | `restricted` | `selected-works-281-nights` | L2 / L6 |
| Marco Polo and Rustichello of Pisa textual tradition | `unknown` | `plausible-open` | `one-witness-plus-non-equivalent-english` | L3 / L6 |
| Rus' Primary Chronicle textual tradition | `restricted` | `unknown` | `laurentian-recension-only` | L2 / L6 |
| Anonymous Mongol court textual tradition | `unknown` | `restricted` | `received-chinese-transcription-witness` | L2 / L6 |
| Kamakura bakufu chronicle editorial tradition | `unknown` | `restricted` | `partial-work-volumes-1-5` | L3 / L5 |
| Michael the Syrian | `unknown` | `not-located` | `french-plus-imperfect-syriac-no-english` | L2 / L5 |
| Song Shi Yuan editorial tradition | `restricted` | `not-located` | `original-only-if-complete-lawful-body-found` | L2 / L5 |
| Goryeosa Joseon court editorial tradition | `restricted` | `restricted` | `metadata-only-english-partial` | L2 / L5 |

## Record Findings

### 1. Justinian I / Tribonianic legal commission — *Corpus Iuris Civilis*

- **Candidate:** `MED-CAND-001`.
- **Boundary:** Four separately transmitted components: Institutes, Digest, Codex, and Novels.
- **Original route:** University of Grenoble component texts; Mommsen–Krueger/Krueger, with Schoell–Kroll lineage still required for Novels.
- **English route:** Component public-domain translations only; no complete aligned English corpus confirmed.
- **Rights:** original `unknown`; English `unknown`.
- **Coverage:** `principal-works`.
- **Maturity estimate:** Level 2; ceiling Level 6. No advancement is authorized.
- **Disposition:** `research-incomplete`.
- **Next action:** Create a four-component edition and rights ledger.
- **Evidence:**
  - **confirmed-metadata:** Grenoble identifies Mommsen–Krueger and all fifty Digest books. [Source](https://droitromain.univ-grenoble-alpes.fr/Corpus/digest.htm) — lineage root: droitromain.univ-grenoble-alpes.fr.
  - **confirmed-metadata:** Grenoble distinguishes component editions. [Source](https://droitromain.univ-grenoble-alpes.fr/bibliographi.htm) — lineage root: droitromain.univ-grenoble-alpes.fr.
- **Unresolved:** No file has been inspected or admitted. Viewability does not establish portability. Edition alignment and reuse terms remain body-specific.

### 2. Qur'anic textual tradition — *Qur'an*

- **Candidate:** `MED-CAND-024`.
- **Boundary:** Reference text, readings, manuscripts, translations, and annotations are separate bodies; initial candidate is Tanzil Hafs only.
- **Original route:** Tanzil Uthmani Quran Text, preserved verbatim with required notice and link.
- **English route:** Separately inspected public-domain translation; no English file yet verified.
- **Rights:** original `plausible-open`; English `unknown`.
- **Coverage:** `Hafs-reference-text-only`.
- **Maturity estimate:** Level 3; ceiling Level 6. No advancement is authorized.
- **Disposition:** `original-candidate-strong-english-unresolved`.
- **Next action:** Inspect a Tanzil release byte-for-byte, then verify one English edition.
- **Evidence:**
  - **confirmed-metadata:** Tanzil states CC BY 3.0, verbatim distribution, no changes, attribution, linking, and notice preservation. [Source](https://tanzil.net/docs/Text_License) — lineage root: tanzil.net.
  - **confirmed-metadata:** The Quranic Arabic Corpus uses a GNU license for its distinct annotated corpus. [Source](https://corpus.quran.com/license.jsp) — lineage root: corpus.quran.com.
- **Unresolved:** No file has been inspected or admitted. Viewability does not establish portability. Edition alignment and reuse terms remain body-specific.

### 3. Alf Layla wa-Layla medieval textual tradition — *One Thousand and One Nights*

- **Candidate:** `MED-CAND-075`.
- **Boundary:** BnF arabe 3609–3611 only: 281 medieval nights; exclude later Galland additions and Bulaq accretions.
- **Original route:** BnF manuscript images; diplomatic Arabic transcription not located.
- **English route:** Haddawy/Mahdi is aligned but modern and restricted; not proposed for admission.
- **Rights:** original `unknown`; English `restricted`.
- **Coverage:** `selected-works-281-nights`.
- **Maturity estimate:** Level 2; ceiling Level 6. No advancement is authorized.
- **Disposition:** `metadata-only`.
- **Next action:** Locate an admissible diplomatic Arabic transcription.
- **Evidence:**
  - **confirmed-metadata:** BnF calls the Galland witness the oldest known substantial manuscript and dates the copy to the fourteenth century. [Source](https://essentiels.bnf.fr/fr/article/7cbf6b6d-8f7c-428c-ae42-9a58a7374522-transmission-mille-et-une-nuits) — lineage root: essentiels.bnf.fr.
  - **confirmed-metadata:** Presses de l'Ifpo states the three surviving volumes contain 281 nights. [Source](https://books.openedition.org/ifpo/24378) — lineage root: books.openedition.org.
- **Unresolved:** No file has been inspected or admitted. Viewability does not establish portability. Edition alignment and reuse terms remain body-specific.

### 4. Marco Polo and Rustichello of Pisa textual tradition — *Devisement du monde*

- **Candidate:** `MED-CAND-074`.
- **Boundary:** Collaborative multilingual tradition, not a single recoverable authorial text; BnF français 1116 is the preferred witness.
- **Original route:** BnF français 1116 images, followed by a verified Franco-Italian transcription.
- **English route:** Yule–Cordier 1903/1920 complete edition at Project Gutenberg; not equivalent to français 1116.
- **Rights:** original `unknown`; English `plausible-open`.
- **Coverage:** `one-witness-plus-non-equivalent-english`.
- **Maturity estimate:** Level 3; ceiling Level 6. No advancement is authorized.
- **Disposition:** `paired-candidates-located-not-equivalent`.
- **Next action:** Inspect both Gutenberg volumes and BnF terms; encode recension mismatch.
- **Evidence:**
  - **confirmed-metadata:** BnF dates the work to 1299, names Rustichello, identifies français 1116, and records 143 manuscripts. [Source](https://catalogue.bnf.fr/ark:/12148/cb13592024s) — lineage root: catalogue.bnf.fr.
  - **confirmed-metadata:** Project Gutenberg identifies the complete Yule–Cordier 1903/1920 lineage. [Source](https://www.gutenberg.org/files/10636/10636-h/10636-h.htm) — lineage root: www.gutenberg.org.
- **Unresolved:** No file has been inspected or admitted. Viewability does not establish portability. Edition alignment and reuse terms remain body-specific.

### 5. Rus' Primary Chronicle textual tradition — *Povest' vremennykh let*

- **Candidate:** `MED-CAND-076`.
- **Boundary:** Primary Chronicle in named recensions; first witness is its portion of the 1377 Laurentian Codex, excluding later continuations.
- **Original route:** NLR Laurentian Codex F.p.IV.2 images and modern-alphabet transliteration.
- **English route:** Cross/Sherbowitz-Wetzor Laurentian translation, pending publication-rights verification.
- **Rights:** original `restricted`; English `unknown`.
- **Coverage:** `laurentian-recension-only`.
- **Maturity estimate:** Level 2; ceiling Level 6. No advancement is authorized.
- **Disposition:** `witness-strong-portability-unresolved`.
- **Next action:** Separate manuscript, NLR transliteration, and English translation rights.
- **Evidence:**
  - **confirmed-metadata:** NLR identifies F.p.IV.2 and the oldest surviving Primary Chronicle version. [Source](https://expositions.nlr.ru/LaurentianCodex/eng/manuscript1.html) — lineage root: expositions.nlr.ru.
  - **confirmed-metadata:** NLR documents editorial modernization and permission for its modern translation. [Source](https://expositions.nlr.ru/LaurentianCodex/eng/project2.html) — lineage root: expositions.nlr.ru.
- **Unresolved:** No file has been inspected or admitted. Viewability does not establish portability. Edition alignment and reuse terms remain body-specific.

### 6. Anonymous Mongol court textual tradition — *Secret History of the Mongols*

- **Candidate:** `MED-CAND-043`.
- **Boundary:** Lost Middle Mongol composition surviving in Chinese phonetic transcription, gloss, and paraphrase; reconstructions are derivative.
- **Original route:** Institutional scan of the Ye Dehui witness still to be located.
- **English route:** Cleaves and de Rachewiltz complete translations are modern and restricted.
- **Rights:** original `unknown`; English `restricted`.
- **Coverage:** `received-chinese-transcription-witness`.
- **Maturity estimate:** Level 2; ceiling Level 6. No advancement is authorized.
- **Disposition:** `metadata-only`.
- **Next action:** Locate an institutional Ye Dehui scan preserving all textual layers.
- **Evidence:**
  - **confirmed-metadata:** SOAS scholarship treats the received witness and reconstructions as distinct layers. [Source](https://www.cambridge.org/core/journals/bulletin-of-the-school-of-oriental-and-african-studies/article/abs/secret-history-of-the-mongols-some-fresh-revelations/0EF9D9817213E16E60A227DF9C2E1B31) — lineage root: www.cambridge.org.
  - **confirmed-metadata:** UQAM's Pelliot route covers only chapters I–VI. [Source](https://classiques.uqam.ca/classiques/pelliot_paul/histoire_secrete_mongols/histoire_secrete_mongols.html) — lineage root: classiques.uqam.ca.
- **Unresolved:** No file has been inspected or admitted. Viewability does not establish portability. Edition alignment and reuse terms remain body-specific.

### 7. Kamakura bakufu chronicle editorial tradition — *Azuma Kagami*

- **Candidate:** `MED-CAND-067`.
- **Boundary:** Anonymous composite chronicle; JHTI exposes only Kan'ei-ban volumes 1–5 aligned to 1180–1185 translation.
- **Original route:** JHTI/NIJL Kan'ei-ban paragraphs for volumes 1–5, pending NIJL reuse verification.
- **English route:** Shinoda 1960 selected translation; JHTI explicitly prohibits republication.
- **Rights:** original `unknown`; English `restricted`.
- **Coverage:** `partial-work-volumes-1-5`.
- **Maturity estimate:** Level 3; ceiling Level 5. No advancement is authorized.
- **Disposition:** `partial-and-restricted`.
- **Next action:** Investigate an openly licensed complete NIJL original text.
- **Evidence:**
  - **confirmed-metadata:** JHTI names the Kan'ei-ban/NIJL lineage and volumes 1–5 limit. [Source](https://jhti.studentorg.berkeley.edu/texthon17.htm) — lineage root: jhti.studentorg.berkeley.edu.
  - **confirmed-metadata:** NIJL states item rights vary and permission is needed absent PD/CC marking. [Source](https://kokusho.nijl.ac.jp/page/en/usage.html?ln=en) — lineage root: kokusho.nijl.ac.jp.
- **Unresolved:** No file has been inspected or admitted. Viewability does not establish portability. Edition alignment and reuse terms remain body-specific.

### 8. Michael the Syrian — *Chronicle*

- **Candidate:** `MED-CAND-006`.
- **Boundary:** Chabot four-volume edition: three French translation volumes and a Syriac text volume; omissions remain explicit.
- **Original route:** Chabot volume IV Syriac, preferably the 1910 printing rather than an uninspected 1963 reprint.
- **English route:** No complete English located; Chabot French volumes are verification bodies only.
- **Rights:** original `unknown`; English `not-located`.
- **Coverage:** `french-plus-imperfect-syriac-no-english`.
- **Maturity estimate:** Level 2; ceiling Level 5. No advancement is authorized.
- **Disposition:** `original-partial-no-english`.
- **Next action:** Inspect all four Chabot volumes and enumerate Syriac omissions.
- **Evidence:**
  - **confirmed-metadata:** Penn identifies four volumes, French/Syriac division, and a 1963 volume-IV reprint route. [Source](https://onlinebooks.library.upenn.edu/webbin/book/lookupid?key=olbp65151) — lineage root: onlinebooks.library.upenn.edu.
  - **confirmed-metadata:** Syri.ac identifies chapters missing from Chabot volume IV and substitutions from Bar Hebraeus. [Source](https://syri.ac/michaelsyrian) — lineage root: syri.ac.
- **Unresolved:** No file has been inspected or admitted. Viewability does not establish portability. Edition alignment and reuse terms remain body-specific.

### 9. Song Shi Yuan editorial tradition — *Song Shi*

- **Candidate:** `MED-CAND-062`.
- **Boundary:** The 496-juan Yuan official history; Siku scan, Zhonghua edition, and web transcription are separate bodies.
- **Original route:** CText Siku Quanshu scan for inspection only; a reusable complete body remains unlocated.
- **English route:** No complete English translation located.
- **Rights:** original `restricted`; English `not-located`.
- **Coverage:** `original-only-if-complete-lawful-body-found`.
- **Maturity estimate:** Level 2; ceiling Level 5. No advancement is authorized.
- **Disposition:** `metadata-only`.
- **Next action:** Locate a lawful complete 496-juan scan outside CText's no-bulk surface.
- **Evidence:**
  - **confirmed-metadata:** CText identifies 496 juan and the Yuan editorial team. [Source](https://ctext.org/datawiki.pl?if=en&res=545989) — lineage root: ctext.org.
  - **confirmed-metadata:** CText denies blanket republication and forbids automated bulk download. [Source](https://ctext.org/faq) — lineage root: ctext.org.
- **Unresolved:** No file has been inspected or admitted. Viewability does not establish portability. Edition alignment and reuse terms remain body-specific.

### 10. Goryeosa Joseon court editorial tradition — *Goryeosa*

- **Candidate:** `MED-CAND-070`.
- **Boundary:** The 139-volume official history; Classical Chinese, modern Korean, and English translation are separate bodies.
- **Original route:** NIKH Goryeo source database; site displays all rights reserved.
- **English route:** UH Press 2024 covers introduction and first ten annals volumes only; restricted.
- **Rights:** original `restricted`; English `restricted`.
- **Coverage:** `metadata-only-english-partial`.
- **Maturity estimate:** Level 2; ceiling Level 5. No advancement is authorized.
- **Disposition:** `metadata-only`.
- **Next action:** Request NIKH reuse terms and map the partial English subset.
- **Evidence:**
  - **confirmed-metadata:** NIKH lists Goryeosa as a dedicated source collection and displays all rights reserved. [Source](https://db.history.go.kr/) — lineage root: db.history.go.kr.
  - **confirmed-metadata:** UH Press states its translation covers the introduction and first ten annals volumes, 918–1095. [Source](https://uhpress.hawaii.edu/title/koryosa-the-history-of-koryo-the-annals-of-the-kings-918-1095/) — lineage root: uhpress.hawaii.edu.
- **Unresolved:** No file has been inspected or admitted. Viewability does not establish portability. Edition alignment and reuse terms remain body-specific.


## Ranked Next Inspection Order

1. Qur'anic textual tradition — inspect the Tanzil file and required notice.
2. Marco Polo–Rustichello — inspect both Yule–Cordier volumes and document recension mismatch.
3. Rus' Primary Chronicle — separate manuscript, NLR transliteration, and English translation.
4. Justinianic legal tradition — build the four-component edition ledger.
5. Michael the Syrian — inspect Chabot's sequence and enumerate Syriac omissions.
6. Azuma Kagami — preserve the English prohibition and investigate NIJL rights.
7. Goryeosa — request original-text terms and map the restricted English subset.
8. Song Shi — locate a lawful complete 496-juan body outside CText's no-bulk surface.
9. One Thousand and One Nights — define the 281-night witness inventory and find a diplomatic Arabic transcription.
10. Secret History of the Mongols — recover an institutional Ye Dehui witness without collapsing textual layers.

## Evidence Classification

- `confirmed-metadata` means directly stated by the linked repository, publisher, or institutional project.
- Boundaries, ceilings, dispositions, and next actions are **researcher inference**.
- Missing licenses, edition alignment, translation, or witness relationships remain **unresolved uncertainty**.
- No proposition was resolved by source counting.

## Validation Receipt

- Ten records correspond to selected candidates in the accepted 60-authority manifest.
- Twenty substantive sources are used: two per authority and below the ceiling of thirty.
- Every record has a boundary, original and English route, lineage, rights posture, body ceiling, maturity estimate, disposition, gap, and next action.
- Restricted, unknown, and not-located bodies produce no `available`, `verified`, reviewed, admission-ready, complete, or equivalence claim.
- No text was downloaded or admitted.
- No registry, era index, private text store, Archive catalog, staging, commit, push, or publication action occurred.

## Persistence

This packet and its JSON companion are repository-local, untracked review artifacts. They are research guidance, not Library Import approval.
