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
    max_yaml_depth: int = 32
    max_yaml_nodes: int = 10_000
    max_assertions: int = 100
    max_facts: int = 200
    scalar_chars: int = 2_000
    metadata_chars: int = 500


@dataclass(frozen=True)
class DomainPolicy:
    allowed_roles: frozenset[str]
    controlling_roles: frozenset[str]


@dataclass(frozen=True)
class HostPolicy:
    consequence_levels: frozenset[str]
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
    consequence_levels=frozenset({"low", "medium", "high"}),
    domains={
        "repository-contract": DomainPolicy(
            allowed_roles=frozenset(
                {
                    "canonical-operating-contract",
                    "canonical-domain-contract",
                    "advisory-guidance",
                }
            ),
            controlling_roles=frozenset(
                {"canonical-operating-contract", "canonical-domain-contract"}
            ),
        ),
        "archive-membership": DomainPolicy(
            allowed_roles=frozenset(
                {
                    "source-manifest",
                    "archive-source",
                    "derived-index",
                    "advisory-guidance",
                }
            ),
            controlling_roles=frozenset({"source-manifest"}),
        ),
        "workflow-state": DomainPolicy(
            allowed_roles=frozenset(
                {
                    "canonical-workflow-record",
                    "generated-view",
                    "cadence-handoff",
                    "advisory-guidance",
                }
            ),
            controlling_roles=frozenset({"canonical-workflow-record"}),
        ),
    },
    bounds=Bounds(),
)
