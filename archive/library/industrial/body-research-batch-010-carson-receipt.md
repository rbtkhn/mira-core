# Industrial Library Body Research Batch 010: Carson Receipt

Date: 2026-08-23

## Authority Boundary

This batch performed Carson source-route inspection and private download only.
It did not mutate the registry, admit a body, stage, commit, push, publish,
ingest source bodies into the private Archive, or create a version seal.

Private inspection root:

`C:\private\mira-library-texts\inspection\industrial-batch-010-carson`

## Registry Target

- Source ID: `LIB-INDUSTRIAL-AUTHORITY-078-CARSON`
- Authority: Rachel Carson
- Registry title: `Silent Spring`
- Current registry status before this batch: `stub`
- Current text status before this batch: `missing`
- Intended gate reached here: `admission-ready candidate`

## Source Route Inspected

The Ted K Archive hosts a full online `Silent Spring` text surface with export
links for standalone HTML and plain text source.

- Source page:
  `https://www.thetedkarchive.com/library/rachel-carson-silent-spring`
- Plain text source:
  `https://www.thetedkarchive.com/library/rachel-carson-silent-spring.muse`
- Standalone HTML:
  `https://www.thetedkarchive.com/library/rachel-carson-silent-spring.html`
- Download manifest:
  `carson-tedk-download-manifest.json`
- Download manifest SHA256:
  `8c5ad958c8b9817b77aa702a1f551a4812e9fe95362593b541d60a1750bca46c`

Downloaded private files:

| File | Bytes | SHA256 |
| --- | ---: | --- |
| `tedk-rachel-carson-silent-spring-page.html` | 713745 | `7acafe2088f5e37a148c629095cbc1234d92e48d583873d2fc476efce2fcb507` |
| `tedk-rachel-carson-silent-spring-standalone.html` | 687979 | `04c2362dc571e5117880695f9bea96156b2fceefa20d434fd9e9099dc31bf10d` |
| `tedk-rachel-carson-silent-spring.muse` | 647862 | `d004b864177187274b0f1d72bbfa3821bda8e8e85f4ef8591caa32a0e6bf745a` |

## Inspection

The `.muse` source is the preferred private-reading candidate. It includes:

- title, author, date, source, publisher, topic, and language metadata;
- copyright/front-matter page for the Fortieth Anniversary / Mariner edition;
- Carson's author's note and acknowledgments;
- introduction by Linda Lear;
- chapters 1-17;
- list of principal sources;
- afterword by Edward O. Wilson;
- about-the-author and also-available back matter.

Inspection found the original copyright and renewal notice preserved in the
body. For the personal-reading library, this is not a block if the text is
available online; preserve `private-reading-online-source; no redistribution`
at any admission or outward-boundary review.

## Proposed Admission Candidate

If the next gate is authorized, admit the `.muse` source as:

- Body ID:
  `LIB-INDUSTRIAL-AUTHORITY-078-CARSON-SILENT-SPRING-TEDK-MUSE`
- Work title:
  `Silent Spring`
- Edition label:
  `The Ted K Archive plain text source (.muse) for Silent Spring, Fortieth Anniversary Edition / Mariner Books edition metadata; private-reading derivative, accessed 2026-08-23`
- License status:
  `permissioned`
- License notes:
  `private-reading-online-source; no redistribution; source text preserves copyright and renewal notices for Rachel Carson, Linda Lear introduction, and Edward O. Wilson afterword.`
- Coverage status:
  `complete-work`
- Coverage notes:
  `Full online text includes front matter, chapters 1-17, list of principal sources, afterword, and back matter; source-authority coverage remains principal-work.`
- Language:
  `english`

## Re-entry Point

The next bounded action is body admission of the `.muse` candidate using the
metadata above. If authorized and validated, Industrial would reach 68 of 68
authorities represented.
