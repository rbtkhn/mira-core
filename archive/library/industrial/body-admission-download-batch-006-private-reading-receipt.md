# Industrial Library Batch 006 Private Reading Admission And Download Receipt

Status: `admitted-and-downloaded-private-reading`
Era: `industrial`
Date: 2026-08-23
Gate: `operator-review-before-next-admission`
Private text root: `C:\private\mira-library-texts`
Private inspection root: `C:\private\mira-library-texts\inspection\industrial-batch-006-online`

## Authority Boundary

The operator selected both prior options: admit the four already downloaded
Churchill Project Gutenberg bodies and download/inspect the next online-
available Batch 006 bodies. This receipt records that work only. It does not
stage, commit, push, publish, redistribute, or ingest any body into the private
Archive.

## Batch Result

Authorities touched: 9
Churchill bodies admitted: 4
Additional online candidate files downloaded: 9
Additional Lenin component files downloaded: 12
Failed download routes: 1
Registry mutated: yes, Churchill only
Indexes regenerated: yes
Archive ingestion: no
Staged: no
Committed: no
Pushed: no

## Churchill Registry Admissions

| Body ID | Work | Source | Bytes | SHA-256 | Status |
| --- | --- | --- | ---: | --- | --- |
| `LIB-INDUSTRIAL-AUTHORITY-057-CHURCHILL-MALAKAND-PG9404` | `The Story of the Malakand Field Force: An Episode of Frontier War` | Project Gutenberg #9404 | 545609 | `f8edd77a202898e910fd2ebe530e3aed19f877d5b8b1959600471e280a53a612` | admitted; hash matched |
| `LIB-INDUSTRIAL-AUTHORITY-057-CHURCHILL-RIVER-WAR-PG4943` | `The River War: An Account of the Reconquest of the Sudan` | Project Gutenberg #4943 | 784351 | `0176d9305dfc29b7b92adfeaf223ba21d17e2803e5c5259f79a4ba74ee17cf46` | admitted; hash matched |
| `LIB-INDUSTRIAL-AUTHORITY-057-CHURCHILL-WORLD-CRISIS-VOL-1-PG59794` | `The World Crisis, Volume 1 (of 6)` | Project Gutenberg #59794 | 1317310 | `ca4451a818c18cdcb7135c7c66d7566bb914b85a1043539112e0a0a592ff3f75` | admitted; hash matched |
| `LIB-INDUSTRIAL-AUTHORITY-057-CHURCHILL-LIBERALISM-SOCIAL-PROBLEM-PG18419` | `Liberalism and the Social Problem` | Project Gutenberg #18419 | 517570 | `0894fc8499b424287e8aa120dc02ddf236d004b46f3d8443d295c20a562226fc` | admitted; hash matched |

The Churchill source-level record was also corrected from a metadata-only
`wartime speeches` stub to a located `selected works` authority with an
1898-1945 selected-works lane. Wartime speeches and broadcasts remain future
exact-route candidates.

## Additional Downloaded Inspection Candidates

| Candidate | Local file | Bytes | SHA-256 | Inspection disposition |
| --- | --- | ---: | --- | --- |
| Durkheim, `Le Suicide`, PG #40489 | `durkheim-le-suicide-pg40489.txt` | 1122589 | `7B170FE725C164EBBFC6BB83B758B0302C3504003D5E1ADF0EE5582FE4B538D3` | full PG text; header matched |
| Freud, `Civilization and its discontents`, PG #78221 | `freud-civilization-discontents-pg78221.txt` | 208244 | `5BD503CFF493B952E487DF18AAAFB578BAAFE277BDB8D63735803B8314536665` | full PG text; header matched |
| Einstein, `Relativity`, PG #30155 | `einstein-relativity-pg30155.txt` | 210653 | `86ED8156239455CBB6ED33E06097707D3AB7C40D46E9AA5FF32D3C3F94EF68FD` | full PG text; header matched |
| Einstein, `Über die spezielle und die allgemeine Relativitätstheorie`, PG #77850 | `einstein-ueber-relativitaet-pg77850.txt` | 165241 | `39F90EE5619FB88C563A731EDF1E666DFC26B7CD0E0DAAE90E7973879D4F643B` | full PG text; header matched |
| Lenin, `Imperialism`, MIA index | `lenin-imperialism-mia-index.html` | 11985 | `93324AE0EAC9567C4E5308F14418D2A6B756C8B077FE71EB23D5D2704225D73C` | index page; component pages downloaded separately |
| Lenin, `Imperialism`, MIA prefaces and chapters | `lenin-imperialism-mia\pref01.htm` through `ch10.htm` | 373252 total | component hashes recorded in JSON receipt | multi-file HTML body candidate; not yet admitted |
| Carson, `Silent Spring`, Faded Page route | `carson-silent-spring-fadedpage.html` | 21567 | `A4D8BDA10F68C39F631671A135601C66754B7F3D15F200EC3C6ECEF034701B62` | landing/details page observed; not a confirmed full body |
| UDHR, UN page | `udhr-un-page.html` | 105813 | `2015ACD3FFD39A8750307EE5C0E19A8FD315EC6057D57FE844B5CB13478E6A2D` | official page downloaded; HTML source candidate |
| UN Charter, UN page | `un-charter-un-page.html` | 150983 | `D16948227E71190640856DC908808E44313833AE7397F1EC576C97573B6DFAE2` | official page downloaded; HTML source candidate |
| Mandela, NMF page | `mandela-i-am-prepared-to-die-nmf.html` | 32884 | `56870E05547A1FF42874943B6CF1080E84B5F84FB57C9563F0E150BCC6F569FF` | online article downloaded; contains speech excerpt/provenance |

Failed route: SAHO Mandela URL returned HTTP 404 and was not downloaded.

## Validation

- `tools\run.ps1 library validate --json`: passed.
- `tools\run.ps1 library render-index --check --json`: passed.
- `tools\run.ps1 test --path tests/test_archive_library.py`: passed, 26 tests.
- Direct Churchill registry/file SHA-256 comparison: 4 of 4 matched.

Full `library verify-texts` was not run because the verifier is global-only in
this tooling and prior work established unrelated older private-store gaps.
The newly admitted Churchill bodies were checked directly instead.

## Re-Entry Point

The next bounded action is admission review for the downloaded PG-ready bodies:
Durkheim, Freud, Einstein English, and Einstein German. Lenin needs a
multi-file admission decision. Carson needs a fuller text route if the current
Faded Page file remains only a detail page. UDHR, UN Charter, and Mandela need
HTML-body or extracted-text admission policy under the private-reading model.
