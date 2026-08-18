from __future__ import annotations

import os
import sys
from collections.abc import MutableMapping
from typing import Callable, Mapping


DEPRECATED_ENVIRONMENT_ALIASES = {
    "MIRA_CORE_SESSION_TEMP_ROOT": "NARRATIVE_SESSION_TEMP_ROOT",
    "MIRA_CORE_PYTHON": "NARRATIVE_PYTHON",
    "MIRA_CORE_VALIDATION_CACHE": "NARRATIVE_VALIDATION_CACHE",
    "MIRA_CORE_CHOICE_DB": "NARRATIVE_CHOICE_DB",
    "MIRA_CORE_CADENCE_DB": "NARRATIVE_CADENCE_DB",
    "MIRA_CORE_RUN_ARGUMENTS_JSON": "NARRATIVE_RUN_ARGUMENTS_JSON",
    "MIRA_CORE_JOURNAL_DRAFT_ROOT": "NARRATIVE_MIRA_JOURNAL_DRAFT_ROOT",
}

DEPRECATED_ENVIRONMENT_ALIAS_CHAINS = {
    "MIRA_CORE_ARCHIVE_ROOT": (
        "MIRA_CORE_SYSTEM_ARCHIVE_ROOT",
        "NARRATIVE_SYSTEM_ARCHIVE_ROOT",
    ),
    "MIRA_CORE_ARCHIVE_REPLICA_ROOT": (
        "MIRA_CORE_SYSTEM_ARCHIVE_REPLICA_ROOT",
        "NARRATIVE_SYSTEM_ARCHIVE_REPLICA_ROOT",
    ),
    "MIRA_CORE_ARCHIVE_CONFIG": (
        "MIRA_CORE_SYSTEM_ARCHIVE_CONFIG",
        "NARRATIVE_SYSTEM_ARCHIVE_CONFIG",
    ),
}
ENVIRONMENT_ALIASES: dict[str, str] = {}
ENVIRONMENT_ALIAS_CHAINS: dict[str, tuple[str, ...]] = {}


class EnvironmentNameConflict(ValueError):
    """Raised when canonical and compatibility names disagree."""


_WARNED_LEGACY_NAMES: set[str] = set()


def environment_aliases(canonical: str) -> tuple[str, ...]:
    if canonical in DEPRECATED_ENVIRONMENT_ALIAS_CHAINS:
        return DEPRECATED_ENVIRONMENT_ALIAS_CHAINS[canonical]
    if canonical in DEPRECATED_ENVIRONMENT_ALIASES:
        return (DEPRECATED_ENVIRONMENT_ALIASES[canonical],)
    return ()


def _default_warning(message: str) -> None:
    print(message, file=sys.stderr)


def resolve_environment(
    canonical: str,
    environment: Mapping[str, str] = os.environ,
    *,
    warn: Callable[[str], None] = _default_warning,
) -> str | None:
    current = environment.get(canonical) or None
    if current is None:
        for alias in environment_aliases(canonical):
            if environment.get(alias) and alias not in _WARNED_LEGACY_NAMES:
                warn(f"{alias} is no longer supported; use {canonical}")
                _WARNED_LEGACY_NAMES.add(alias)
    return current


def pop_environment(
    canonical: str,
    environment: MutableMapping[str, str],
    *,
    warn: Callable[[str], None] = _default_warning,
) -> str | None:
    value = resolve_environment(canonical, environment, warn=warn)
    environment.pop(canonical, None)
    aliases = environment_aliases(canonical)
    for alias in aliases:
        environment.pop(alias, None)
    return value


def remove_environment_pair(
    canonical: str, environment: MutableMapping[str, str]
) -> None:
    environment.pop(canonical, None)
    aliases = environment_aliases(canonical)
    for alias in aliases:
        environment.pop(alias, None)
