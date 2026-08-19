# Ancient Library Maturity Audit

Status: `working-audit`

This audit applies the Mira Library maturity ladder from
[`../README.md`](../README.md) to the current Ancient source-authority records.
It is a human curatorial surface, not the machine authority. The registry
remains [`../library-registry.json`](../library-registry.json), and private text
bodies remain outside Git in the portable text store.

Generated from the registry state after the Level 3 improvement pass for
Vedic, Avestan/Gathic, Arrian, and Ptolemy records. It is a snapshot for
prioritization, not a claim that every source has been philologically reviewed.

## Summary

| Level | Count | Meaning |
| --- | ---: | --- |
| 0 | 0 | Stub only / no admitted local text body. |
| 1 | 0 | Located candidate, not yet admitted. |
| 2 | 0 | Admitted text exists, but coverage metadata is unset. |
| 3 | 6 | Selected or partial coverage remains intentionally visible. |
| 4 | 36 | Principal or complete coverage is available, usually translation-only or original-only. |
| 5 | 14 | English plus original-language coverage exists. |
| 6 | 0 | No authority is yet marked fully mature by this audit. |

## Priority Read

The Ancient shelf has at least one admitted local text body for every one of
its 56 authority records. The most important maturity gaps are:

- replace or supplement Ptolemy's partial Stevenson/LacusCurtius coverage with
  a clean full Geography body if one can be lawfully admitted;
- add a clean full Rig Veda or broader Vedic corpus body if a lawful stable
  candidate can be admitted without brittle scraping;
- continue broader Avesta coverage beyond Vendidad and anthology selections;
- clean web-extracted bodies where navigation or wrapper residue remains; and
- add original-language or English counterpart coverage for one-sided records
  when lawful and clean.

## Level 3 Sufficiency Decisions

Selected-work coverage is intentionally preserved for records where a complete
or principal-works claim would be too strong. Current disposition:

- Sufficient seed coverage for offline use, but not complete corpus coverage:
  Cicero, Plato, Aristotle.
- Still visibly incomplete against the source-authority title: Vedic seer
  tradition, Avestan/Gathic Zoroastrian tradition, Ptolemy.
- Arrian moved out of Level 3 after `Indica` was admitted in Greek.

## Source Status

| Source ID | Authority | Principal Title | Level | Text Status | Coverage | Bodies | Languages | Next Curatorial Move |
| --- | --- | --- | ---: | --- | --- | ---: | --- | --- |
| LIB-ANCIENT-AUTHOR-001-ASHOKA | Ashoka | Rock and Pillar Edicts | 4 | available | principal-works | 1 | english | Add original-language or English counterpart where lawful and useful. |
| LIB-ANCIENT-AUTHOR-002-KAUTILYA | Kautilya / Chanakya | Arthashastra | 4 | available | principal-work | 1 | english | Add original-language or English counterpart where lawful and useful. |
| LIB-ANCIENT-AUTHOR-003-HERODOTUS | Herodotus | Histories | 5 | available | complete-surviving-corpus | 3 | english, ancient greek | Curate toward complete/fragmentary authority modeling. |
| LIB-ANCIENT-AUTHOR-004-STRABO | Strabo | Geographica | 5 | available | complete-surviving-corpus | 4 | english, ancient greek | Curate toward complete/fragmentary authority modeling. |
| LIB-ANCIENT-AUTHOR-005-DARIUS-I | Darius I | Behistun Inscription | 4 | available | principal-work | 1 | english | Add original-language or English counterpart where lawful and useful. |
| LIB-ANCIENT-AUTHOR-006-JULIUS-CAESAR | Julius Caesar | Commentarii, especially Commentarii de Bello Gallico | 5 | available | principal-works | 4 | english, latin | Curate toward complete/fragmentary authority modeling. |
| LIB-ANCIENT-AUTHOR-007-TACITUS | Tacitus | Annals; Histories; Germania | 5 | available | principal-works | 9 | english, latin | Curate toward complete/fragmentary authority modeling. |
| LIB-ANCIENT-AUTHOR-008-CONFUCIUS-KONGZI | Confucius / Kongzi | Analects; Spring and Autumn Annals attribution | 4 | available | principal-work | 1 | english | Add original-language or English counterpart where lawful and useful. |
| LIB-ANCIENT-AUTHOR-009-LAOZI | Laozi | Dao De Jing | 4 | available | principal-work | 1 | english | Add original-language or English counterpart where lawful and useful. |
| LIB-ANCIENT-AUTHOR-010-SUNZI | Sunzi | The Art of War | 4 | available | principal-work | 1 | english | Add original-language or English counterpart where lawful and useful. |
| LIB-ANCIENT-AUTHOR-011-VEDIC-SEER-TRADITION | Vedic seer tradition | Vedas | 3 | available | selected-works | 1 | english | Add missing principal bodies or keep visibly incomplete selected coverage. |
| LIB-ANCIENT-AUTHOR-012-UPANISHADIC-TRADITION | Upanishadic tradition | Principal Upanishads | 4 | available | principal-work | 1 | English | Add original-language or English counterpart where lawful and useful. |
| LIB-ANCIENT-AUTHOR-013-VYASA-MAHABHARATA-TRADITION | Vyasa / Mahabharata tradition | Mahabharata; Bhagavad Gita | 4 | available | principal-work | 1 | English | Add original-language or English counterpart where lawful and useful. |
| LIB-ANCIENT-AUTHOR-014-VALMIKI | Valmiki | Ramayana | 4 | available | complete-surviving-corpus | 1 | English | Add original-language or English counterpart where lawful and useful. |
| LIB-ANCIENT-AUTHOR-015-AVESTAN-GATHIC-TRADITION | Avestan / Gathic Zoroastrian tradition | Avesta; Gathas | 3 | available | selected-works | 2 | english | Add missing principal bodies or keep visibly incomplete selected coverage. |
| LIB-ANCIENT-AUTHOR-016-CYRUS-II-ACHAEMENID-CHANCERY | Cyrus II / Achaemenid imperial chancery | Cyrus Cylinder | 4 | available | principal-work | 1 | english | Add original-language or English counterpart where lawful and useful. |
| LIB-ANCIENT-AUTHOR-017-MENCIUS-MENGZI | Mencius / Mengzi | Mencius | 4 | available | principal-work | 1 | chinese | Add original-language or English counterpart where lawful and useful. |
| LIB-ANCIENT-AUTHOR-018-ZHUANGZI | Zhuangzi | Zhuangzi | 4 | available | principal-work | 1 | english | Add original-language or English counterpart where lawful and useful. |
| LIB-ANCIENT-AUTHOR-019-HAN-FEIZI | Han Feizi | Han Feizi | 4 | available | principal-work | 1 | chinese | Add original-language or English counterpart where lawful and useful. |
| LIB-ANCIENT-AUTHOR-020-SIMA-QIAN | Sima Qian | Shiji / Records of the Grand Historian | 4 | available | complete-surviving-corpus | 1 | Chinese | Add original-language or English counterpart where lawful and useful. |
| LIB-ANCIENT-AUTHOR-021-BAN-GU | Ban Gu | Hanshu / Book of Han | 4 | available | complete-surviving-corpus | 1 | Chinese | Add original-language or English counterpart where lawful and useful. |
| LIB-ANCIENT-AUTHOR-022-FAN-YE | Fan Ye | Hou Hanshu / Book of the Later Han | 4 | available | principal-work | 1 | chinese | Add original-language or English counterpart where lawful and useful. |
| LIB-ANCIENT-AUTHOR-023-CHEN-SHOU | Chen Shou | Sanguozhi / Records of the Three Kingdoms | 4 | available | complete-surviving-corpus | 1 | Chinese | Add original-language or English counterpart where lawful and useful. |
| LIB-ANCIENT-AUTHOR-024-YIJING-TRADITION | Yijing tradition | Yijing / Book of Changes | 4 | available | principal-work | 1 | Chinese | Add original-language or English counterpart where lawful and useful. |
| LIB-ANCIENT-AUTHOR-025-SHUJING-TRADITION | Shujing tradition | Shujing / Book of Documents | 4 | available | principal-work | 1 | chinese | Add original-language or English counterpart where lawful and useful. |
| LIB-ANCIENT-AUTHOR-026-SHIJING-TRADITION | Shijing tradition | Shijing / Book of Odes | 4 | available | principal-work | 1 | English | Add original-language or English counterpart where lawful and useful. |
| LIB-ANCIENT-AUTHOR-027-THUCYDIDES | Thucydides | History of the Peloponnesian War | 5 | available | complete-surviving-corpus | 2 | english, ancient greek | Curate toward complete/fragmentary authority modeling. |
| LIB-ANCIENT-AUTHOR-028-XENOPHON | Xenophon | Anabasis; Cyropaedia; Hellenica | 5 | available | principal-works | 6 | english, ancient greek | Curate toward complete/fragmentary authority modeling. |
| LIB-ANCIENT-AUTHOR-029-POLYBIUS | Polybius | Histories | 4 | available | principal-work | 2 | english | Add original-language or English counterpart where lawful and useful. |
| LIB-ANCIENT-AUTHOR-030-DIODORUS-SICULUS | Diodorus Siculus | Bibliotheca Historica | 4 | available | principal-work | 3 | ancient greek | Add original-language or English counterpart where lawful and useful. |
| LIB-ANCIENT-AUTHOR-031-DIONYSIUS-OF-HALICARNASSUS | Dionysius of Halicarnassus | Roman Antiquities | 4 | available | principal-work | 1 | ancient greek | Add original-language or English counterpart where lawful and useful. |
| LIB-ANCIENT-AUTHOR-032-PLUTARCH | Plutarch | Parallel Lives; Life of Artaxerxes; Life of Alexander | 4 | available | principal-work | 1 | English | Add original-language or English counterpart where lawful and useful. |
| LIB-ANCIENT-AUTHOR-033-ARRIAN | Arrian | Anabasis of Alexander; Indica | 5 | available | principal-works | 2 | English, ancient greek | Curate toward complete/fragmentary authority modeling. |
| LIB-ANCIENT-AUTHOR-034-CICERO | Cicero | Orations; Letters; Philosophical Works | 3 | available | selected-works | 13 | Latin, English, English; Latin | Keep selected-work claim; improve only when completing corpus or adding major omitted works. |
| LIB-ANCIENT-AUTHOR-035-LIVY | Livy | Ab Urbe Condita | 5 | available | complete-surviving-corpus | 5 | English, latin | Curate toward complete/fragmentary authority modeling. |
| LIB-ANCIENT-AUTHOR-036-SALLUST | Sallust | Bellum Catilinae; Bellum Jugurthinum | 5 | available | principal-works | 2 | english, latin | Curate toward complete/fragmentary authority modeling. |
| LIB-ANCIENT-AUTHOR-037-PLINY-THE-ELDER | Pliny the Elder | Naturalis Historia / Natural History | 4 | available | complete-surviving-corpus | 6 | English | Add original-language or English counterpart where lawful and useful. |
| LIB-ANCIENT-AUTHOR-038-SUETONIUS | Suetonius | De Vita Caesarum / Lives of the Caesars | 4 | available | principal-work | 1 | english | Add original-language or English counterpart where lawful and useful. |
| LIB-ANCIENT-AUTHOR-039-HOMER | Homer | Iliad; Odyssey | 5 | available | complete-surviving-corpus | 4 | english, ancient greek | Curate toward complete/fragmentary authority modeling. |
| LIB-ANCIENT-AUTHOR-040-PLATO | Plato | Republic; dialogues | 3 | available | selected-works | 57 | english, ancient greek | Keep selected-work claim; improve only when completing corpus or adding major omitted works. |
| LIB-ANCIENT-AUTHOR-041-ARISTOTLE | Aristotle | Politics; Nicomachean Ethics | 3 | available | selected-works | 10 | english, ancient greek | Keep selected-work claim; improve only when completing corpus or adding major omitted works. |
| LIB-ANCIENT-AUTHOR-042-SOPHOCLES | Sophocles | Antigone; Oedipus Rex | 5 | available | complete-surviving-corpus | 9 | english, ancient greek | Curate toward complete/fragmentary authority modeling. |
| LIB-ANCIENT-AUTHOR-043-VIRGIL | Virgil | Aeneid | 5 | available | principal-works | 7 | english, latin | Curate toward complete/fragmentary authority modeling. |
| LIB-ANCIENT-AUTHOR-044-LUCRETIUS | Lucretius | De Rerum Natura / On the Nature of Things | 5 | available | complete-surviving-corpus | 2 | english, latin | Curate toward complete/fragmentary authority modeling. |
| LIB-ANCIENT-AUTHOR-045-PTOLEMY | Ptolemy | Geography | 3 | available | selected-works | 1 | english | Add missing principal bodies or keep visibly incomplete selected coverage. |
| LIB-ANCIENT-AUTHOR-046-AMMIANUS-MARCELLINUS | Ammianus Marcellinus | Res Gestae | 4 | available | principal-work | 1 | English | Add original-language or English counterpart where lawful and useful. |
| LIB-ANCIENT-AUTHOR-047-JOSEPHUS | Josephus | Jewish War; Antiquities | 4 | available | principal-works | 2 | English | Add original-language or English counterpart where lawful and useful. |
| LIB-ANCIENT-AUTHOR-048-EUSEBIUS-OF-CAESAREA | Eusebius of Caesarea | Ecclesiastical History | 4 | available | principal-work | 1 | ancient greek | Add original-language or English counterpart where lawful and useful. |
| LIB-ANCIENT-AUTHOR-049-AURELIUS-VICTOR | Aurelius Victor | De Caesaribus | 4 | available | principal-work | 1 | latin | Add original-language or English counterpart where lawful and useful. |
| LIB-ANCIENT-AUTHOR-050-EUTROPIUS | Eutropius | Breviarium | 4 | available | principal-work | 1 | english | Add original-language or English counterpart where lawful and useful. |
| LIB-ANCIENT-AUTHOR-051-BIBLICAL-TRADITION | Biblical textual tradition | Hebrew Bible / Old Testament; New Testament | 5 | available | principal-works | 5 | english, hebrew; biblical aramaic, koine greek, latin, ancient greek; koine greek | Curate toward complete/fragmentary authority modeling. |
| LIB-ANCIENT-AUTHOR-052-BUDDHIST-DHAMMAPADA-TRADITION | Buddhist textual tradition | Dhammapada | 4 | available | principal-work | 1 | english | Add original-language or English counterpart where lawful and useful. |
| LIB-ANCIENT-AUTHOR-053-JAIN-ACARANGA-TRADITION | Jain textual tradition | Acaranga Sutra | 4 | available | principal-work | 1 | english | Add original-language or English counterpart where lawful and useful. |
| LIB-ANCIENT-AUTHOR-054-EGYPTIAN-MORTUARY-TRADITION | Egyptian mortuary textual tradition | Book of the Dead; Pyramid Texts | 4 | available | principal-work | 1 | english | Add original-language or English counterpart where lawful and useful. |
| LIB-ANCIENT-AUTHOR-055-MESOPOTAMIAN-COSMOLOGICAL-TRADITION | Mesopotamian sacred and cosmological textual tradition | Enuma Elish; hymns and laments | 4 | available | principal-work | 1 | english | Add original-language or English counterpart where lawful and useful. |
| LIB-ANCIENT-AUTHOR-056-ZARATHUSTRA-GATHAS | Zarathustra / Zoroaster | Gathas | 4 | available | principal-work | 1 | english | Add original-language or English counterpart where lawful and useful. |
