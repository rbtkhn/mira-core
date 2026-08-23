# Industrial Library Batch 004 Project Gutenberg Original-Language Admission Receipt

Date: 2026-08-23

Status: admitted to Mira Library private text store.

## Scope

This admission covers the Batch 004 clean Project Gutenberg original-language companions for Flaubert, Balzac, and Hugo.

Private text root used for admission: `C:\private\mira-library-texts`

Private inspection root: `C:\private\mira-library-inspection\industrial-batch004-original-language`

## Admitted Bodies

| Authority | Body ID | Work | License | Bytes | SHA-256 |
| --- | --- | --- | --- | ---: | --- |
| Gustave Flaubert | `LIB-INDUSTRIAL-AUTHORITY-010-FLAUBERT-MADAME-BOVARY-FRENCH-PG14155` | `Madame Bovary` | `public-domain` | 751987 | `93f0a2259dbaf5fde6e7b96adc22346d52f80eb1e9319336c8381a045efe40cd` |
| Honore de Balzac | `LIB-INDUSTRIAL-AUTHORITY-004-BALZAC-COMEDIE-HUMAINE-VOL09-PG55860` | `La Comedie humaine - Volume 09. Scenes de la vie parisienne - Tome 01` | `public-domain` | 1340207 | `df295f9b869683c98b2a87b8cf32c261cb97acdb1b102ccdd0ab741894d643a9` |
| Victor Hugo | `LIB-INDUSTRIAL-AUTHORITY-005-HUGO-LES-MISERABLES-FRENCH-TOME1-PG17489` | `Les miserables Tome I: Fantine` | `public-domain` | 710496 | `a5de514ba7b9f2e1790e7e259c4e8b7a35ae1d29e4bf9a5f8767039c58b80503` |
| Victor Hugo | `LIB-INDUSTRIAL-AUTHORITY-005-HUGO-LES-MISERABLES-FRENCH-TOME2-PG17493` | `Les miserables Tome II: Cosette` | `public-domain` | 629938 | `ffddbcee83e3c537b5586bfbbaf97ea6fab2b04250b9efaa63c027ab20aaffd0` |
| Victor Hugo | `LIB-INDUSTRIAL-AUTHORITY-005-HUGO-LES-MISERABLES-FRENCH-TOME3-PG17494` | `Les miserables Tome III: Marius` | `public-domain` | 556738 | `79894e327a20044dad5b93dd7d1fae0a8c06b74b86cd9f19d37bb54ffbacd44f` |
| Victor Hugo | `LIB-INDUSTRIAL-AUTHORITY-005-HUGO-LES-MISERABLES-FRENCH-TOME4-PG17518` | `Les miserables Tome IV: L'idylle rue Plumet et l'epopee rue Saint-Denis` | `public-domain` | 786691 | `5ceb65a2be245776a61aaa15f311b9b31964c1826121a3ba65ddd3bfae7fa4af` |
| Victor Hugo | `LIB-INDUSTRIAL-AUTHORITY-005-HUGO-LES-MISERABLES-FRENCH-TOME5-PG17519` | `Les miserables Tome V: Jean Valjean` | `public-domain` | 675293 | `d78e6ddc87cc5971b1a0107ae06f19b4cc63030553fcdfd94929c7472f0d470d` |

## Verification

- `library admit-text` succeeded for all seven bodies.
- `library render-index --json` regenerated `archive/library/text-sources-index.md` and `archive/library/industrial/index.md`; indexed body count increased from 512 to 519.
- `library validate --json` passed.
- Manual private-payload byte/hash verification passed for all seven admitted files.
- Full `library verify-texts --json` was not rerun for this receipt because the same private store is already known to be missing many pre-existing Ancient and Colonial payloads unrelated to this admission.

## Boundary

No private Archive ingestion, staging, commit, push, or publication occurred.
