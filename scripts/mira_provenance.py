"""Private, explicit provenance and review store for the Mira-work pilot.

This module deliberately has no default database path and no conversation
capture hook. Callers must provide a path and explicit records. The store is
an evidence aid, not an authority or memory daemon.
"""

from __future__ import annotations

import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


PROVENANCE_STATUSES = {"observed", "supplied", "inferred", "generated", "confirmed"}
REVIEW_STATUSES = {"review_required", "reviewed", "rejected"}
PRIVACY_CLASSES = {"private", "project", "shareable"}


class ProvenanceError(ValueError):
    """Raised when a record would violate the pilot contract."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class MemoryRecord:
    id: str
    content: str
    source_ref: str
    source_date: str
    project: str
    lane: str
    provenance_status: str
    confidence: float
    review_status: str
    freshness_until: str | None
    privacy_class: str
    decision_ref: str | None
    created_at: str


class ProvenanceStore:
    """SQLite-backed store with explicit project/lane isolation."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self._create_schema()

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> "ProvenanceStore":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _create_schema(self) -> None:
        self.connection.executescript(
            """
            PRAGMA foreign_keys = ON;
            CREATE TABLE IF NOT EXISTS records (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                source_ref TEXT NOT NULL,
                source_date TEXT NOT NULL,
                project TEXT NOT NULL,
                lane TEXT NOT NULL,
                provenance_status TEXT NOT NULL,
                confidence REAL NOT NULL,
                review_status TEXT NOT NULL,
                freshness_until TEXT,
                privacy_class TEXT NOT NULL,
                decision_ref TEXT,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS records_scope
                ON records(project, lane, created_at);
            CREATE TABLE IF NOT EXISTS recall_traces (
                id TEXT PRIMARY KEY,
                record_id TEXT NOT NULL REFERENCES records(id),
                query TEXT NOT NULL,
                reason TEXT NOT NULL,
                selected_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS measurements (
                id TEXT PRIMARY KEY,
                phase TEXT NOT NULL CHECK (phase IN ('baseline', 'pilot')),
                task TEXT NOT NULL,
                preparation_minutes REAL NOT NULL,
                reconstruction_minutes REAL NOT NULL,
                source_checks INTEGER NOT NULL,
                corrections INTEGER NOT NULL,
                evidence_gaps INTEGER NOT NULL,
                repeated_work INTEGER NOT NULL,
                confidence REAL NOT NULL,
                recorded_at TEXT NOT NULL
            );
            """
        )
        self.connection.commit()

    @staticmethod
    def _validate(
        *,
        content: str,
        source_ref: str,
        source_date: str,
        project: str,
        lane: str,
        provenance_status: str,
        confidence: float,
        review_status: str | None,
        privacy_class: str,
    ) -> str:
        if not content.strip() or not source_ref.strip() or not source_date.strip():
            raise ProvenanceError("content, source_ref, and source_date are required")
        if not project.strip() or not lane.strip():
            raise ProvenanceError("project and lane are required for isolation")
        if provenance_status not in PROVENANCE_STATUSES:
            raise ProvenanceError(f"invalid provenance_status: {provenance_status}")
        if not 0 <= confidence <= 1:
            raise ProvenanceError("confidence must be between 0 and 1")
        if privacy_class not in PRIVACY_CLASSES:
            raise ProvenanceError(f"invalid privacy_class: {privacy_class}")
        effective_review = review_status or (
            "review_required" if provenance_status in {"inferred", "generated"} else "reviewed"
        )
        if effective_review not in REVIEW_STATUSES:
            raise ProvenanceError(f"invalid review_status: {effective_review}")
        return effective_review

    def write_record(
        self,
        *,
        content: str,
        source_ref: str,
        source_date: str,
        project: str,
        lane: str,
        provenance_status: str,
        confidence: float,
        privacy_class: str = "private",
        freshness_until: str | None = None,
        decision_ref: str | None = None,
        review_status: str | None = None,
    ) -> MemoryRecord:
        effective_review = self._validate(
            content=content,
            source_ref=source_ref,
            source_date=source_date,
            project=project,
            lane=lane,
            provenance_status=provenance_status,
            confidence=confidence,
            review_status=review_status,
            privacy_class=privacy_class,
        )
        record = MemoryRecord(
            id=str(uuid.uuid4()),
            content=content,
            source_ref=source_ref,
            source_date=source_date,
            project=project,
            lane=lane,
            provenance_status=provenance_status,
            confidence=confidence,
            review_status=effective_review,
            freshness_until=freshness_until,
            privacy_class=privacy_class,
            decision_ref=decision_ref,
            created_at=utc_now(),
        )
        self.connection.execute(
            """INSERT INTO records VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            tuple(record.__dict__.values()),
        )
        self.connection.commit()
        return record

    def review(self, record_id: str, status: str) -> None:
        if status not in REVIEW_STATUSES:
            raise ProvenanceError(f"invalid review_status: {status}")
        cursor = self.connection.execute("UPDATE records SET review_status = ? WHERE id = ?", (status, record_id))
        if cursor.rowcount == 0:
            raise ProvenanceError(f"record not found: {record_id}")
        self.connection.commit()

    def recall(
        self,
        *,
        query: str,
        project: str,
        lane: str,
        include_unreviewed: bool = False,
        include_stale: bool = False,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        if not query.strip() or not project.strip() or not lane.strip():
            raise ProvenanceError("query, project, and lane are required")
        if limit < 1 or limit > 100:
            raise ProvenanceError("limit must be between 1 and 100")
        review_clause = "" if include_unreviewed else "AND review_status = 'reviewed'"
        freshness_clause = "" if include_stale else "AND (freshness_until IS NULL OR freshness_until >= ?)"
        params: tuple[Any, ...] = (project, lane)
        if not include_stale:
            params += (utc_now(),)
        params += (f"%{query}%", limit)
        rows = self.connection.execute(
            f"""SELECT * FROM records WHERE project = ? AND lane = ? {review_clause}
                {freshness_clause} AND content LIKE ? ORDER BY created_at DESC LIMIT ?""",
            params,
        ).fetchall()
        results: list[dict[str, Any]] = []
        for row in rows:
            reason = f"scope={project}/{lane}; text_match; review={row['review_status']}"
            trace_id = str(uuid.uuid4())
            self.connection.execute(
                "INSERT INTO recall_traces VALUES (?, ?, ?, ?, ?)",
                (trace_id, row["id"], query, reason, utc_now()),
            )
            item = dict(row)
            item["recall_trace"] = {"id": trace_id, "reason": reason}
            results.append(item)
        self.connection.commit()
        return results

    def record_measurement(
        self,
        *,
        phase: str,
        task: str,
        preparation_minutes: float,
        reconstruction_minutes: float,
        source_checks: int,
        corrections: int,
        evidence_gaps: int,
        repeated_work: int,
        confidence: float,
    ) -> None:
        if phase not in {"baseline", "pilot"}:
            raise ProvenanceError("phase must be baseline or pilot")
        if min(preparation_minutes, reconstruction_minutes, source_checks, corrections, evidence_gaps, repeated_work) < 0:
            raise ProvenanceError("measurement values cannot be negative")
        if not 0 <= confidence <= 1:
            raise ProvenanceError("confidence must be between 0 and 1")
        self.connection.execute(
            "INSERT INTO measurements VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), phase, task, preparation_minutes, reconstruction_minutes, source_checks,
             corrections, evidence_gaps, repeated_work, confidence, utc_now()),
        )
        self.connection.commit()

    def measurements(self, phase: str | None = None) -> list[dict[str, Any]]:
        if phase is None:
            rows = self.connection.execute("SELECT * FROM measurements ORDER BY recorded_at").fetchall()
        else:
            rows = self.connection.execute("SELECT * FROM measurements WHERE phase = ? ORDER BY recorded_at", (phase,)).fetchall()
        return [dict(row) for row in rows]


def summarize_measurements(rows: Iterable[dict[str, Any]]) -> dict[str, float | int | None]:
    data = list(rows)
    if not data:
        return {"count": 0, "preparation_minutes": None, "reconstruction_minutes": None, "confidence": None}
    return {
        "count": len(data),
        "preparation_minutes": sum(float(r["preparation_minutes"]) for r in data) / len(data),
        "reconstruction_minutes": sum(float(r["reconstruction_minutes"]) for r in data) / len(data),
        "confidence": sum(float(r["confidence"]) for r in data) / len(data),
    }
