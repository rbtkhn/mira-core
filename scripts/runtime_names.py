from __future__ import annotations

import os
import sys
from collections.abc import MutableMapping
from typing import Callable, Mapping


ENVIRONMENT_ALIASES = {
    "MIRA_CORE_SESSION_TEMP_ROOT": "NARRATIVE_SESSION_TEMP_ROOT",
    "MIRA_CORE_PYTHON": "NARRATIVE_PYTHON",
    "MIRA_CORE_VALIDATION_CACHE": "NARRATIVE_VALIDATION_CACHE",
    "MIRA_CORE_CHOICE_DB": "NARRATIVE_CHOICE_DB",
    "MIRA_CORE_RUN_ARGUMENTS_JSON": "NARRATIVE_RUN_ARGUMENTS_JSON",
    "MIRA_CORE_SYSTEM_ARCHIVE_ROOT": "NARRATIVE_SYSTEM_ARCHIVE_ROOT",
    "MIRA_CORE_SYSTEM_ARCHIVE_REPLICA_ROOT": "NARRATIVE_SYSTEM_ARCHIVE_REPLICA_ROOT",
    "MIRA_CORE_SYSTEM_ARCHIVE_CONFIG": "NARRATIVE_SYSTEM_ARCHIVE_CONFIG",
    "MIRA_CORE_JOURNAL_DRAFT_ROOT": "NARRATIVE_MIRA_JOURNAL_DRAFT_ROOT",
}


class EnvironmentNameConflict(ValueError):
    """Raised when canonical and compatibility names disagree."""


_WARNED_LEGACY_NAMES: set[str] = set()


def _default_warning(message: str) -> None:
    print(message, file=sys.stderr)


def resolve_environment(
    canonical: str,
    environment: Mapping[str, str] = os.environ,
    *,
    warn: Callable[[str], None] = _default_warning,
) -> str | None:
    legacy = ENVIRONMENT_ALIASES[canonical]
    current = environment.get(canonical) or None
    old = environment.get(legacy) or None
    if current is not None and old is not None and current != old:
        raise EnvironmentNameConflict(
            f"conflicting environment variables: {canonical} and {legacy}"
        )
    if current is not None:
        return current
    if old is not None:
        if legacy not in _WARNED_LEGACY_NAMES:
            warn(f"{legacy} is deprecated; use {canonical}")
            _WARNED_LEGACY_NAMES.add(legacy)
        return old
    return None


def pop_environment(
    canonical: str,
    environment: MutableMapping[str, str],
    *,
    warn: Callable[[str], None] = _default_warning,
) -> str | None:
    value = resolve_environment(canonical, environment, warn=warn)
    environment.pop(canonical, None)
    environment.pop(ENVIRONMENT_ALIASES[canonical], None)
    return value


def remove_environment_pair(
    canonical: str, environment: MutableMapping[str, str]
) -> None:
    environment.pop(canonical, None)
    environment.pop(ENVIRONMENT_ALIASES[canonical], None)
