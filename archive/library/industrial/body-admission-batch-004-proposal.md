# Industrial Body Admission Batch 004 Proposal

Status: `operator-review-before-body-admission`
Era: `industrial`
Batch: `industrial-body-admission-batch-004`
Inspection receipt: `archive/library/industrial/body-research-batch-004-inspection-receipt.md`
Private inspection root: `C:\private\mira-library-inspection\industrial-batch004`
Proposed private text root: `C:\private\mira-library-texts`

## Boundary

This proposal requests operator review before admitting Batch 004 bodies into the private Mira Library text store and adding body metadata to `archive/library/library-registry.json`. It does not itself admit bodies, ingest into the private Archive, stage, commit, push, or publish.

## Proposed Admission Set

Admit 16 Project Gutenberg candidate text bodies across 12 Industrial Batch 004 authorities.

| Authority | Candidate ID | Work | Bytes | SHA-256 |
| --- | --- | --- | ---: | --- |
| Alexander Pushkin | `PUSHKIN-EUGENE-ONEGIN-PG23997` | Eugene Onegin | 282067 | `3c5769f513be4317ea8d0f80ba9e8e7ad807877d55249c99489f68ade5e3e3cc` |
| Honore de Balzac | `BALZAC-FATHER-GORIOT-PG1237` | Father Goriot | 612225 | `c4c1001259654f71aaa23585b04dbb8ca9a1b0c1ad87a49520bbc465fab3ae42` |
| Victor Hugo | `HUGO-LES-MISERABLES-PG135` | Les Miserables | 3369207 | `6cf3b9d6fc5e6f733737425267d3af296d7f99f9b9fd1d255a3ab7689a6346ab` |
| Charlotte Bronte | `CHARLOTTE-BRONTE-JANE-EYRE-PG1260` | Jane Eyre | 1084803 | `13414dee2951c3ee731d76d2ffd822016b2479c892162760c5d0eb2aa5fa7631` |
| Emily Bronte | `EMILY-BRONTE-WUTHERING-HEIGHTS-PG768` | Wuthering Heights | 693819 | `e533fe750589f0421d5d744576315f5c2b9b0d69e981179ea0551bbf134c5e02` |
| Gustave Flaubert | `FLAUBERT-MADAME-BOVARY-PG2413` | Madame Bovary | 694920 | `c5847f1c60fed60559d9396245a9196b33fed6a4ab58de9b5c7fe5fc4b2f83f8` |
| Fyodor Dostoevsky | `DOSTOEVSKY-NOTES-UNDERGROUND-PG600` | Notes from Underground | 266972 | `6ce7d6ff7288263f1fd07d7ecfc07e419735cbbb4dff5107964af1afd8b2079e` |
| Fyodor Dostoevsky | `DOSTOEVSKY-BROTHERS-KARAMAZOV-PG28054` | The Brothers Karamazov | 2039159 | `a8bda7296fbdcab50c97e3ccd6dde2c10c3bf9d5725fdfeb2b4dc78b62823ce5` |
| Leo Tolstoy | `TOLSTOY-WAR-AND-PEACE-PG2600` | War and Peace | 3359610 | `2d5bb2ad5f422765e714617e21fa31bbaf8958aa79682c86fca6660fcc5d1b2b` |
| Leo Tolstoy | `TOLSTOY-ANNA-KARENINA-PG1399` | Anna Karenina | 2067952 | `a3e29e08c15c63bb22069f4256316c2ebebd422ecb5c33462ddc00ae00b27571` |
| Henrik Ibsen | `IBSEN-DOLLS-HOUSE-PG2542` | A Doll's House | 169080 | `d72a481b08ca7ace73e8ca2087b2baec29fc00e0d6e493f5e877b12116bccf4f` |
| Henrik Ibsen | `IBSEN-ENEMY-PEOPLE-PG2446` | An Enemy of the People | 204047 | `a38988e897a473218fec4eb96f7d551e03ad68fba12a24be9299b562a980fa92` |
| Anton Chekhov | `CHEKHOV-LADY-DOG-PG13415` | The Lady with the Dog and Other Stories | 423298 | `79eb6eeed77023b08bea36499bd1ac60ec6d84852b59714bb0b88cee21992a27` |
| Anton Chekhov | `CHEKHOV-PLAYS-SECOND-SERIES-PG7986` | Plays by Anton Chekhov, Second Series | 419036 | `4c08d7117dcd946cdcfd42c3d56ac79a114f4b55d2e186b19978ede25947351a` |
| Walt Whitman | `WHITMAN-LEAVES-GRASS-PG1322` | Leaves of Grass | 780492 | `77c066a8774e2b04d8bfbc570d9aa5131410355cd6062ab5962ac773240f3140` |
| Emily Dickinson | `DICKINSON-POEMS-FIRST-PG2678` | Poems by Emily Dickinson, First Series | 72664 | `824ab5c5f8269702697a36cfa21b0b530720d9d39444bb2438db09f484a1d488` |

## Admission Rules

- Preserve each candidate as a separate provenance body record.
- Preserve translator and edition notes at admission time.
- Do not claim complete-surviving-corpus coverage for any Batch 004 authority.
- Keep Whitman and Dickinson edition-history cautions visible.

## Acceptance Tests

- library validate passes.
- render-index check passes.
- focused library tests pass.
- 16/16 Industrial Batch 004 private payloads present with matching hashes and byte counts after admission.
