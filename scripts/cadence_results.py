"""Lane-neutral verification results for cadence reporting."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


Status = Literal["passed", "failed", "unavailable", "skipped"]
Scope = Literal["experiment", "contract", "repository"]


@dataclass(frozen=True)
class VerificationResult:
    check_id: str
    status: Status
    failure_class: str | None
    scope: Scope
    affected_paths: tuple[str, ...] = ()
    references: tuple[str, ...] = ()
    evidence: str = ""
    owner: str = ""
    next_action: str = ""
    command: tuple[str, ...] | None = None
    output_tail: str = ""
    details: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.status != "passed" and (not self.owner or not self.next_action):
            raise ValueError("non-passing verification results require owner and next_action")
        if any(path.startswith(("/", "\\")) or ".." in path.replace("\\", "/").split("/") for path in self.affected_paths):
            raise ValueError("affected paths must be repository-relative")

    @property
    def passed(self) -> bool:
        return self.status == "passed"

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["affected_paths"] = list(self.affected_paths)
        payload["references"] = list(self.references)
        payload["command"] = list(self.command) if self.command else None
        return payload


def command_result(
    *,
    check_id: str,
    status: Status,
    scope: Scope,
    command: list[str] | tuple[str, ...],
    output_tail: str = "",
    failure_class: str | None = None,
    owner: str = "cadence",
    next_action: str = "Rerun the command and inspect its output.",
    evidence: str = "",
    affected_paths: tuple[str, ...] = (),
    references: tuple[str, ...] = (),
    details: dict[str, Any] | None = None,
) -> VerificationResult:
    return VerificationResult(
        check_id=check_id,
        status=status,
        failure_class=failure_class,
        scope=scope,
        affected_paths=affected_paths,
        references=references,
        evidence=evidence or output_tail[-2000:],
        owner=owner if status != "passed" else "",
        next_action=next_action if status != "passed" else "",
        command=tuple(command),
        output_tail=output_tail[-2000:],
        details=details or {},
    )


def aggregate(results: list[VerificationResult]) -> dict[str, Any]:
    rank = {"passed": 0, "skipped": 1, "unavailable": 2, "failed": 3}
    ordered = sorted(results, key=lambda result: rank[result.status], reverse=True)
    blocking = [result for result in ordered if result.status in {"failed", "unavailable"}]
    return {
        "status": ordered[0].status if ordered else "skipped",
        "passed": not blocking,
        "results": [result.to_dict() for result in results],
        "blockers": [result.to_dict() for result in blocking],
        "next_action": blocking[0].next_action if blocking else "No verification repair is required.",
    }
