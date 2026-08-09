"""Reversible, conservative transcript sectioning proposal.

This module deliberately does not write archive files. It creates a proposed
section layout for QA before any retrofit is applied.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ProposedSection:
    heading: str
    body: str
    start_paragraph: int
    end_paragraph: int


def complete_boundary(paragraph: str) -> bool:
    """Only allow a boundary after a paragraph that ends like a full thought."""
    text = paragraph.strip()
    return bool(text) and bool(re.search(r"[.!?…\"’)]$", text))


TRANSITION_CUES = (
    "turning to ", "let's turn", "let us turn", "another issue", "another point",
    "the other issue", "the other point", "now let me", "now,", "what about ",
    "let's discuss", "let us discuss", "first of all", "secondly", "finally",
)


def explicit_transition(paragraph: str) -> bool:
    lowered = paragraph.strip().casefold()
    return (
        lowered.startswith(TRANSITION_CUES)
        or bool(re.match(r"^(what|how|why|where|when)\s+", lowered))
        or structural_cue(paragraph)
    )


def structural_cue(paragraph: str) -> bool:
    text = paragraph.strip()
    return bool(
        re.match(r"^(?:#{2,4}\s+|\[?\d{1,2}:\d{2}(?::\d{2})?\]?\s+)", text)
        or re.match(r"^(?:\*\*)?[A-Z][A-Za-z .'-]{1,60}(?:\*\*)?:\s+", text)
    )


def meaningful_label(label: str) -> bool:
    normalized = re.sub(r"\s+", " ", label).strip()
    return bool(normalized) and not re.fullmatch(r"(?:segment|section)\s*\d*", normalized, re.I)


LABEL_STOPWORDS = {"the", "and", "that", "this", "with", "from", "have", "will", "about", "what", "they", "their", "there", "today", "also", "very", "just", "into"}
LABEL_BOILERPLATE = {"source", "ingest", "date", "kind", "transcript", "title", "slug", "archive", "narrative", "geopolitics", "youtube", "md", "file"}
CURATED_LABELS = (
    (re.compile(r"drone.*(?:attack|offensive)|(?:attack|offensive).*drone", re.I), "Drone Offensive"),
    (re.compile(r"(?:iran|iranian).*(?:ceasefire|talks|negotiat)|(?:ceasefire|talks|negotiat).*(?:iran|iranian)", re.I), "Iran Ceasefire Negotiations"),
    (re.compile(r"(?:china|beijing).*(?:taiwan|energy|oil)|(?:taiwan|energy|oil).*china", re.I), "China and Energy Pressure"),
    (re.compile(r"nato.*russia|russia.*nato", re.I), "NATO–Russia Escalation"),
    (re.compile(r"strait of hormuz|hormuz.*(?:oil|energy)|(?:oil|energy).*hormuz", re.I), "Strait of Hormuz and Oil Markets"),
)


def derive_label(block: str, title: str = "") -> str:
    """Derive a compact topic label without using transcript boilerplate."""
    title_tokens = set(re.findall(r"[A-Za-z]+", title.casefold()))
    safe_title = "" if title_tokens.intersection(LABEL_BOILERPLATE) else title
    text = re.sub(r"[_-]+", " ", f"{safe_title} {block}")
    text = re.sub(r"\s+", " ", text).strip()
    for pattern, label in CURATED_LABELS:
        if pattern.search(text):
            return label
    phrases = re.findall(r"\b(?:Iran|Israel|Ukraine|Russia|China|NATO|Trump|energy|drones?|sanctions?|ceasefire|negotiations?|Hormuz|Taiwan|Europe)\b", text, re.I)
    words = re.findall(r"[A-Za-z][A-Za-z'-]{3,}", text)
    chosen: list[str] = []
    for value in phrases + words:
        value = value.title() if value.lower() not in {"nato", "iran", "israel", "ukraine", "russia", "china"} else value.upper() if value.lower() == "nato" else value.title()
        if value.casefold() in LABEL_STOPWORDS or value.casefold() in LABEL_BOILERPLATE or value.casefold() in {x.casefold() for x in chosen}:
            continue
        if chosen and value.casefold() == chosen[-1].casefold():
            continue
        chosen.append(value)
        if len(chosen) >= 5:
            break
    label = " ".join(chosen)
    if any(word.casefold() in LABEL_BOILERPLATE for word in label.split()):
        return ""
    return label if meaningful_label(label) and len(label.split()) >= 2 else ""


def propose(paragraphs: list[str], labels: list[str]) -> list[ProposedSection]:
    """Build sections from explicit paragraph boundaries and supplied topic labels.

    `labels` must contain one label per proposed block. A proposal is rejected
    if any block is empty, begins mid-sentence, or has a generic label.
    """
    if len(paragraphs) < 2 or len(labels) < 2:
        return []
    points = [0]
    for index, paragraph in enumerate(paragraphs[:-1], 1):
        if complete_boundary(paragraph) and explicit_transition(paragraphs[index]):
            points.append(index)
    points.append(len(paragraphs))
    points = sorted(set(points))
    if len(points) < 3:
        return []
    sections: list[ProposedSection] = []
    for index, (start, end) in enumerate(zip(points, points[1:])):
        block = "\n\n".join(p.strip() for p in paragraphs[start:end] if p.strip()).strip()
        label = labels[index].strip() if index < len(labels) else ""
        if not block or not meaningful_label(label):
            return []
        if start > 0 and not paragraphs[start].lstrip()[:1].isupper() and not structural_cue(paragraphs[start]):
            return []
        sections.append(ProposedSection(f"{label}", block, start, end))
    return sections


def render(sections: list[ProposedSection]) -> str:
    return "\n\n".join(f"### {section.heading}\n\n{section.body}" for section in sections) + "\n"


if __name__ == "__main__":
    raise SystemExit("Import sectioning_v2.propose for dry-run QA; no archive writes are performed.")
