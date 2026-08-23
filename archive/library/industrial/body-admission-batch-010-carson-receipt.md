# Industrial Library Body Admission Batch 010: Carson Receipt

Date: 2026-08-23

## Authority Boundary

This batch admitted one Carson private-reading text body. It did not push,
publish, ingest source bodies into the private Archive, or admit source bodies
to Git. Staging and commit were separately authorized after admission.

Active private text root:

`C:\private\mira-library-texts`

## Admitted Body

- Source ID: `LIB-INDUSTRIAL-AUTHORITY-078-CARSON`
- Authority: Rachel Carson
- Body ID: `LIB-INDUSTRIAL-AUTHORITY-078-CARSON-SILENT-SPRING-TEDK-MUSE`
- Work title: `Silent Spring`
- Edition: The Ted K Archive plain text source (`.muse`) for `Silent Spring`,
  copied to `.txt` for library admission; Fortieth Anniversary Edition /
  Mariner Books edition metadata; private-reading derivative, accessed
  2026-08-23
- License status: `permissioned`
- License notes: private-reading-online-source; no redistribution; source text
  preserves copyright and renewal notices for Rachel Carson, Linda Lear
  introduction, and Edward O. Wilson afterword.
- Coverage status: `complete-work`
- Coverage notes: Full online text includes front matter, chapters 1-17, list
  of principal sources, afterword, and back matter; source-authority coverage
  remains principal-work.
- Language: `english`
- Text bytes: 647862
- Text SHA256:
  `d004b864177187274b0f1d72bbfa3821bda8e8e85f4ef8591caa32a0e6bf745a`
- Text location:
  `library-text://LIB-INDUSTRIAL-AUTHORITY-078-CARSON-SILENT-SPRING-TEDK-MUSE.txt`
- Body imported to Archive: false

## Source-Route Provenance

This admission follows the Batch 010 Carson body-research receipt. The upstream
plain text source was The Ted K Archive `.muse` export. The `.muse` file was
copied byte-for-byte to a `.txt` candidate because `admit-text` accepts text
extensions but rejected `.muse`; the SHA256 remained identical.

Private research receipt:

- `archive/library/industrial/body-research-batch-010-carson-receipt.md`
- `archive/library/industrial/body-research-batch-010-carson-receipt.json`

## Validation

- `library validate --json`: passed
- `library render-index --check --json`: passed
- `tests/test_archive_library.py`: passed, 26 tests
- Direct private-store hash readback for the admitted Carson body: passed

## Industrial State After Batch

- Industrial authorities: 68
- Registry-represented Industrial authorities: 68
- Industrial authorities still missing bodies: 0
- Industrial registry bodies: 116

## Re-entry Point

Industrial is now ready for a final seal-readiness receipt and explicit
version-seal decision, subject to the required scoped validation and the known
library-wide private-payload caveat outside Industrial.
