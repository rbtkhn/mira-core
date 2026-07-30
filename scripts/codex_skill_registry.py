from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_DRAFT_ROOT = REPO_ROOT / "docs" / "skill-drafts"
CODEX_SKILLS_ROOT = Path.home() / ".codex" / "skills"
DEPLOYABLE_SKILL_NAMES = (
    "best-intake",
    "elicitation",
    "learn-from-choices",
    "smart-intake",
    "voice-comparison",
    "geopolitical-synthesis",
    "reality-check",
    "voice-accountability",
)


@dataclass(frozen=True)
class SkillEntry:
    name: str
    source: Path
    dest: Path

    @property
    def source_dir(self) -> Path:
        return self.source.parent

    @property
    def dest_dir(self) -> Path:
        return self.dest.parent


@dataclass(frozen=True)
class SkillMirrorState:
    name: str
    status: str
    source_path: str
    installed: bool


def discover_repo_skill_names() -> list[str]:
    if not SKILL_DRAFT_ROOT.exists():
        return []
    names: list[str] = []
    for path in SKILL_DRAFT_ROOT.glob("*/SKILL.md"):
        if path.parent.name not in names:
            names.append(path.parent.name)
    return sorted(names)


def discover_codex_skill_names() -> list[str]:
    if not CODEX_SKILLS_ROOT.exists():
        return []
    names: list[str] = []
    for path in CODEX_SKILLS_ROOT.iterdir():
        if not path.is_dir():
            continue
        if path.name == ".system":
            continue
        names.append(path.name)
    return sorted(names)


def build_registry(names: list[str] | None = None) -> dict[str, SkillEntry]:
    chosen = list(DEPLOYABLE_SKILL_NAMES) if names is None else names
    return {
        name: SkillEntry(
            name=name,
            source=SKILL_DRAFT_ROOT / name / "SKILL.md",
            dest=CODEX_SKILLS_ROOT / name / "SKILL.md",
        )
        for name in chosen
    }


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_skill_frontmatter(path: Path) -> dict[str, str]:
    """Read the small scalar frontmatter contract used by repository skills."""
    text = read_text(path)
    if not text.startswith("---\n"):
        return {}
    _, separator, _ = text.partition("\n---\n")
    if not separator:
        return {}
    metadata: dict[str, str] = {}
    frontmatter = text[4 : text.index("\n---\n", 4)]
    for raw_line in frontmatter.splitlines():
        if (
            not raw_line.strip()
            or raw_line.lstrip().startswith("#")
            or ":" not in raw_line
        ):
            continue
        key, value = raw_line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"').strip("'")
    return metadata


def skill_files(directory: Path) -> dict[Path, Path]:
    if not directory.exists():
        return {}
    return {
        path.relative_to(directory): path
        for path in sorted(directory.rglob("*"))
        if path.is_file() and "__pycache__" not in path.parts
    }


def skill_mirror_state(entry: SkillEntry) -> SkillMirrorState:
    try:
        source_path = entry.source.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        source_path = f"{entry.source.parent.name}/{entry.source.name}"
    if not entry.source.exists():
        return SkillMirrorState(
            entry.name, "MISSING_SOURCE", source_path, entry.dest.exists()
        )
    if not entry.dest.exists():
        return SkillMirrorState(entry.name, "MISSING_DEST", source_path, False)
    source_files = skill_files(entry.source_dir)
    dest_files = skill_files(entry.dest_dir)
    if set(source_files) != set(dest_files):
        return SkillMirrorState(entry.name, "DRIFT", source_path, True)
    if any(
        source_files[path].read_bytes() != dest_files[path].read_bytes()
        for path in source_files
    ):
        return SkillMirrorState(entry.name, "DRIFT", source_path, True)
    return SkillMirrorState(entry.name, "IN_SYNC", source_path, True)
