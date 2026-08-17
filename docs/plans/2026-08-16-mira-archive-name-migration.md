# Mira Archive name migration contract

## Decision

Rename the active `System Archive` interface to **Mira Archive** and its
repository path from `system-archive/` to `archive/`.

The rename changes how the capability is named and reached. It does not change
the archive's authority: Mira Archive preserves and retrieves records, while
collection-native systems retain authority over membership, routing,
interpretation, adjudication, continuity, and identity.

This document is a migration contract, not implementation authority. Saving it
does not authorize the directory rename, code changes, staging, commit, push,
deployment, publication, private-config mutation, or movement of external
archive roots.

## Canonical names

| Surface | New canonical name |
| --- | --- |
| Capability | `Mira Archive` |
| Repository directory | `archive/` |
| Operator command | `tools/run.ps1 archive` |
| Python entry point | `scripts/archive.py` |
| Storage root | `MIRA_CORE_ARCHIVE_ROOT` |
| Replica root | `MIRA_CORE_ARCHIVE_REPLICA_ROOT` |
| Configuration variable | `MIRA_CORE_ARCHIVE_CONFIG` |
| Default private configuration | `C:\private\mira-core-archive-config.json` |

## Compatibility cycle

The compatibility cycle begins with the implementation of this contract on
2026-08-16. It has no automatic expiry: removal requires the separately
authorized evidence gate below.

For one explicit compatibility cycle:

- `system-archive` remains a deprecated command alias;
- `scripts/system_archive.py` becomes a thin compatibility wrapper;
- `MIRA_CORE_SYSTEM_ARCHIVE_*` remains accepted with one warning per variable
  and process;
- existing `NARRATIVE_SYSTEM_ARCHIVE_*` aliases remain accepted at the
  outermost legacy layer;
- equal values are accepted and conflicting non-empty values fail closed;
- former private configuration paths remain readable fallbacks; and
- writers emit only the new canonical names.

Alias precedence is:

```text
MIRA_CORE_ARCHIVE_*
-> MIRA_CORE_SYSTEM_ARCHIVE_*
-> NARRATIVE_SYSTEM_ARCHIVE_*
```

Removing any compatibility alias requires a later, separately authorized
migration.

## Immutable historical identifiers

Do not rewrite existing:

- `urn:narrative-systems:system-archive:*:v1` schema identifiers;
- context-pack compiler identifiers already present in artifacts;
- replay-plan contract identifiers already present in artifacts;
- catalog fingerprints;
- object hashes;
- record IDs such as `SAR-*`;
- immutable manifests, receipts, audits, or historical prose; or
- Git history.

These values identify the format and provenance under which records were
created. Renaming them in place would damage historical intelligibility.

When a new schema or contract version is independently justified, new writers
should use the `mira-core:archive` namespace. Candidate v2 forms are:

```text
urn:mira-core:archive:context-pack:v2
mira-archive-context-compiler-v2
mira-archive-replay-plan-v2
```

Readers must accept both generations. Writers should emit only the new
generation after v2 becomes canonical. The rename alone does not require a
schema-version increase.

## Repository-path migration

The active path moves from `system-archive/` to `archive/`. Active references
in code, tests, current documentation, local skills, command routing, and
validation rules move with it.

Registry values require classification before editing:

1. A mutable current path may move to `archive/`.
2. A digest-bound or historically asserted path remains unchanged.
3. When an active registry must change a historically meaningful path, create
   a versioned successor rather than rewriting the prior record.
4. During compatibility, readers may resolve a former `system-archive/` prefix
   to `archive/`, but path translation must remain distinct from record
   mutation.

No private configuration or external canonical or replica root moves
automatically. Those roots store archive content rather than the repository
interface and should remain byte-for-byte stable.

## Dependent concepts

The current name also appears as:

- a Mira memory-carrier ID;
- a command-router key;
- a public-interface forbidden token;
- a validation owner;
- a skill-routing target;
- an error-message prefix; and
- part of registry and policy IDs.

Active carrier and routing IDs should become `archive`, with `system-archive`
accepted as an input alias during compatibility. Historical carrier receipts
and versioned registry or policy IDs remain unchanged. Public interfaces should
continue preventing leakage of internal implementation terminology, updated to
cover both the former and current internal tokens where necessary.

## Implementation sequence

1. Add canonical environment names and ordered alias resolution, with conflict
   tests and one-warning behavior.
2. Add the canonical `archive` command while retaining the deprecated command
   alias.
3. Move implementation names and the repository directory with compatibility
   wrappers where external callers may depend on them.
4. Classify registry paths as mutable, versioned, or immutable before changing
   any registry bytes.
5. Update active documentation, skills, validation routing, carrier routing,
   tests, and error messages.
6. Verify old artifacts and catalogs before considering cleanup.
7. Record the beginning and intended duration of the compatibility cycle.

Each step should be reviewable independently. A mechanical repository-wide
replacement is forbidden because it would conflate active interface names with
historical identifiers.

## Verification requirements

The migration is complete only when:

1. `archive status` and deprecated `system-archive status` return equivalent
   substantive results.
2. The former command and environment variables warn exactly once.
3. Conflicting aliases fail closed.
4. Existing catalogs open without object migration or rehashing.
5. Existing context packs and replay plans remain readable.
6. Object counts, hashes, provenance, and catalog contents are unchanged.
7. A fresh configuration works using only `MIRA_CORE_ARCHIVE_*`.
8. Repository validation and archive-specific tests pass.
9. Administrative searches find `system-archive` only in compatibility code,
   immutable identifiers, and clearly marked history.
10. No private configuration or external archive root has moved automatically.

The terminal validation receipt must distinguish:

- repository-path and interface changes;
- compatibility behavior;
- old-artifact readability;
- catalog and object-store invariance; and
- intentionally retained historical names.

## Compatibility-removal boundary

Compatibility removal is not part of the rename implementation. It requires
separate authority and evidence that:

- no active repository writer emits former names;
- no configured private environment relies on them;
- old artifacts remain readable without the deprecated command;
- supported external callers have completed migration; and
- the documented compatibility period has ended.

Even after compatibility removal, immutable identifiers and historical prose
remain intact.

## Initial impact receipt

A bounded pre-implementation search on 2026-08-16 found 64 tracked files
containing at least one form of `system-archive`, `System Archive`,
`SYSTEM_ARCHIVE`, `system_archive`, or `narrative-system-archive`. This count is
an orientation aid, not a replacement list. At the time of inspection, the
working tree was clean.
