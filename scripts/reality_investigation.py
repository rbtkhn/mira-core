"""Read-only helpers for bounded reality-check investigations.

The Codex web connector performs retrieval. This module keeps classification,
lineage, and observable disposition deterministic and repository-local.
"""

from __future__ import annotations

from datetime import date
from urllib.parse import urlparse


DISCOVERY_ONLY_DOMAINS = {"reddit.com", "www.reddit.com", "wikipedia.org", "www.wikipedia.org"}
PRIMARY_HINTS = {"imo.org", "ukmto.org", "eia.gov", "iea.org", "centcom.mil", "spa.gov.sa", "qna.org.qa"}
PROFESSIONAL_HINTS = {"apnews.com", "reuters.com", "spglobal.com", "kpler.com", "lloydslist.com", "icis.com"}


def source_tier(url: str, *, role: str | None = None) -> str:
    domain = (urlparse(url).hostname or "").lower()
    if domain in DISCOVERY_ONLY_DOMAINS:
        return "discovery-only"
    if any(domain == item or domain.endswith("." + item) for item in PRIMARY_HINTS):
        return "primary"
    if any(domain == item or domain.endswith("." + item) for item in PROFESSIONAL_HINTS):
        return "professional"
    if role in {"commentary", "analysis", "social"}:
        return "discovery-only"
    return "unclassified"


def lineage_root(*, canonical_url: str, syndication_root: str | None = None) -> str:
    return syndication_root or canonical_url


def window_status(event_date: str, start: str, end: str) -> str:
    event = date.fromisoformat(event_date)
    return "inside" if date.fromisoformat(start) <= event <= date.fromisoformat(end) else "outside"


def independence_eligible(*, tier: str, interested_source: bool, lineage: str, seen_lineages: set[str]) -> bool:
    if tier in {"discovery-only", "unclassified"} or interested_source:
        return False
    return lineage not in seen_lineages


def observable_disposition(*, supports: int, challenges: int, unresolved_reason: str | None = None) -> str:
    if supports and challenges:
        return "contested"
    if supports:
        return "supported"
    if challenges:
        return "challenged"
    return "unresolved" if unresolved_reason else "unresolved"
