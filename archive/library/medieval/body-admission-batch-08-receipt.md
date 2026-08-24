# Medieval Body Admission Batch 08

Status: partial success.

This failure-isolated batch may inspect and admit no more than 24
public-domain bodies across six named authorities: the Justinianic legal
tradition, Anna Komnene, Gregory of Tours, Murasaki Shikibu, Geoffrey Chaucer,
and the Rus' Primary Chronicle tradition. Existing bodies and alternate
mirrors do not count as growth.

Three Project Gutenberg candidates passed inspection and dry-run and were
admitted for Chaucer:

| Body | Language | Coverage | Bytes |
| --- | --- | --- | ---: |
| Purves *Canterbury Tales* section | English | complete contents of the named editorial presentation | 1,126,070 |
| *Cjantaclar e Partelote* | Friulian | Nun's Priest's Tale only | 50,776 |
| *Dalle Novelle di Canterbury* | Italian | prologue and six named tales | 420,437 |

The Purves body is a mechanically bounded derivative of Project Gutenberg
2383. It preserves the Gutenberg header and full license, adds an explicit
extraction note, leaves the *Canterbury Tales* section unchanged, and removes
only separately titled works outside the registry boundary.

The other five authorities produced no defensible additions. Justinian's
additional components lack a resolved file-level public-domain transcription;
Anna's Greek routes are open-license rather than public-domain; Gregory's only
clean Gutenberg route is already admitted; Waley's Genji parts 5-6 are absent
from Gutenberg and the located Japanese routes are open-license or scans; and
the Rus' witness still lacks a clean recension-bound public-domain file. These
are isolated failures, not admissions.

Post-batch shelf state: 60 Medieval authorities, 70 Medieval bodies, and
66,814,262 bytes. Ancient remains 56 authorities, 193 bodies, and 159,939,301
bytes; the body-count gap is now 123.

Validation passes: library schema and invariants, generated-index drift, all
249 clean `available` bodies with zero hash failures, and all 24 focused
archive-library tests. Fourteen `needs-review` bodies remain deliberately
outside clean-body hash verification.
Registry-to-store reconciliation is exact: 263 registered bodies, 263 private
files, zero missing files, and zero unregistered files.

Persistence: the registry, private text store, and both local receipt files
have changed. Nothing has been staged, committed, pushed, or published.
