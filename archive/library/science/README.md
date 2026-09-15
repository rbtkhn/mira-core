# Science

A curated collection of scientific papers worth returning to. Science uses
publication dates and subjects, without an era structure. History keeps its
existing era shelves. Both sections share the Library registry and private
text store; neither is a second catalog or an automatic acquisition queue.

## Browse and retrieve

- [Papers by publication date](index.md)
- [Shared registry](../library-registry.json)
- [Searchable text index](../text-sources-index.md)
- [History](../history/README.md)

```powershell
tools/run.ps1 library list --section science --json
tools/run.ps1 library search --section science --query citation --json
tools/run.ps1 library locate LIB-SCIENCE-QIAN-2025-VERICITE --json
```

Original PDFs live privately under the resolved Library text root at
`science/originals/`. The registry records their source URLs, hashes, byte
counts, and page counts. Searchable text copies use the existing `text_bodies`
model. They are reading aids: consult the PDF for tables, figures and equations.
Neither PDFs nor text bodies belong in Git.

## Curation

Study discovers and evaluates through its
[research practice](../../../docs/skill-drafts/mira-study/references/research-practice.md).
Library preserves selected originals through
[Library Import](../../../docs/skill-drafts/library-import/SKILL.md).
Mind revisits implications; saving creates no operational or learning authority.

Select a paper when it materially changes a judgment, supplies a central
experiment or useful method, or merits repeated study. Retain contrary results
and limitations. A service's generated report is discovery material, not an
original paper. Avoid automatic bibliography downloads and duplicate versions.

Use one registry record per paper, with authors, publication date at known
precision, DOI/source link, exact version, subjects, selection rationale,
limitations, and local original provenance. Label preprints as such; do not
silently replace an admitted version when an upstream file changes.

`reading_state` distinguishes **saved**, **read**, and **assessed**. File inspection
and hashing establish saved, not full reading or scientific validation. Advance
read or assessed only with an actual reading or bounded assessment account.

## Initial pilot

Four papers from the September 15, 2026 research-practice trial are saved.
They concern evidence selection, citation quality, verification, and planning.
The collection is intentionally narrow; it claims no representative coverage
of science, no independent replication, and no Library historical seal.
