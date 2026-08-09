from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


EMAIL_RE = re.compile(r"(?<![\w.+-])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
CREDENTIAL_RE = re.compile(
    r"(?i)(?:api[_-]?key|access[_-]?token|password|secret)\s*[:=]\s*\S+"
)
PRIVATE_KEY_RE = re.compile(
    r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----"
)


@dataclass(frozen=True)
class Bounds:
    max_packet_bytes: int = 256 * 1024
    max_comparands: int = 50
    scalar_chars: int = 2_000
    metadata_chars: int = 500
    max_anchors: int = 25


@dataclass(frozen=True)
class DomainPolicy:
    near_tolerance_seconds: int


@dataclass(frozen=True)
class HostPolicy:
    domains: dict[str, DomainPolicy]
    bounds: Bounds

    def privacy_rule_ids(self, value: Any) -> tuple[str, ...]:
        rules: set[str] = set()

        def inspect(item: Any) -> None:
            if isinstance(item, str):
                if EMAIL_RE.search(item):
                    rules.add("privacy.email")
                if CREDENTIAL_RE.search(item):
                    rules.add("privacy.credential_assignment")
                if PRIVATE_KEY_RE.search(item):
                    rules.add("privacy.private_key")
            elif isinstance(item, dict):
                for key, nested in item.items():
                    inspect(key)
                    inspect(nested)
            elif isinstance(item, (list, tuple)):
                for nested in item:
                    inspect(nested)

        inspect(value)
        return tuple(sorted(rules))


HOST_POLICY = HostPolicy(
    domains={
        "military-activity": DomainPolicy(near_tolerance_seconds=6 * 60 * 60),
        "maritime-incident": DomainPolicy(near_tolerance_seconds=24 * 60 * 60),
        "diplomatic-position": DomainPolicy(near_tolerance_seconds=24 * 60 * 60),
    },
    bounds=Bounds(),
)
