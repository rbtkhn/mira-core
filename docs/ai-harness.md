# Repository-Native AI Harness Contract

The harness audit explains the repository controls that can shape Codex without
changing those controls. Run it with:

```powershell
.\tools\run.ps1 harness
```

## Control map

The audit groups controls into five stations: what is already present, how
Codex chooses help, what specialist context joins a job, what actions are
available, and what proves completion. Repository-relative paths and the
evidence labels `VERIFIED`, `INFERRED`, and `INACCESSIBLE` keep the result
portable and honest.

`AGENTS.md` owns repository-local phrase routing. Skill frontmatter owns
discovery descriptions. Full skill procedures remain behind selection. Domain
scripts own executable behavior, and `scripts/validate_repository.py` plus the
test suite own deterministic completion checks.

## Skill ownership

Files under `docs/skill-drafts/` are canonical. The deployable allowlist in
`scripts/codex_skill_registry.py` names the skills that may be mirrored into the
user-level Codex skill root. Installed copies are mirrors, never a second source
of truth. `coffee` and `dream` remain repository-local and route only through
`AGENTS.md`.

The audit compares complete deployable skill directories. Drift receives
`ONE_HOME`; the audit reports it but never synchronizes either side.

## Safety and evidence boundary

The default audit is read-only. It does not run intake, synthesis, publication,
skill synchronization, or any other mutating command. It does not edit, retire,
or prepare patches for controls.

Repository files can verify declared instructions, routes, skills, commands,
and checks. They cannot prove the exact selected model, active sandbox and tool
set, or which available control shaped a particular run. Those remain explicit
coverage gaps rather than inferred facts.

Before changing a model behind an existing workflow, use the
[Model Substitution Readiness](model-substitution-readiness.md) gate. Its
runtime evidence fills these coverage gaps for one proposed substitution
without treating the harness audit as model, security, privacy, rights, or
production approval.

## Outputs

The default is a human console report. `--json` emits the same structured audit
to standard output. `--write-receipt` atomically writes the ignored
`tmp/ai-harness/latest.json`. `--strict` exits nonzero for invalid repository
contracts or drift in a repo-owned installed skill mirror; it still performs no
repair.
