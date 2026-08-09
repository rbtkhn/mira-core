from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
NG = ROOT / "narrative-geopolitics"
MANIFEST = NG / "archive" / "source-manifest.json"
PUBLICATIONS = NG / "publications"
ALLOWED_ROLES = {"author", "guest", "host", "co-host", "panelist"}
ALLOWED_STATUS = {"confirmed", "provisional", "inferred"}
AUTHORED_MODALITIES = {"newsletter", "substack-post", "x-post-text", "essay", "article"}
ALLOWED_HOST_KINDS = {"channel", "show", "host-person"}
KNOWN_PUBLICATIONS = {
    "escalationtrap": ("escalation-trap", "Escalation Trap"),
    "tritaparsi": ("trita-parsi", "Trita Parsi"),
}
DOMAIN_PUBLICATIONS = {
    "responsiblestatecraft.org": ("responsible-statecraft", "Responsible Statecraft"),
    "jeffsachs.org": ("jeffrey-sachs", "Jeffrey Sachs"),
    "thjodolfur.is": ("thjodolfur-is", "Thjodolfur"),
    "mondevudailleurs.com": ("monde-vu-dailleurs", "Monde Vu d'Ailleurs"),
}


def canonical_slug(value: str) -> str:
    aliases = {
        "larry-johnson": "johnson",
        "ted-postol": "postol",
        "scott-ritter": "ritter",
        "trita-parsi": "parsi",
        "alexander-mercouris": "mercouris",
        "alex-christoforou": "cristoforou",
        "christoforou": "cristoforou",
        "jiang-xueqin": "jiang",
    }
    return aliases.get(value, value)


def load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST.read_text(encoding="utf-8-sig"))


def source_frontmatter_url(row: dict[str, Any]) -> str:
    """Recover explicit URL provenance when an older manifest row omitted it."""
    path = ROOT / str(row.get("local_path") or "")
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    match = re.search(r"(?m)^source_url:\s*[\"']?([^\"'\r\n]+)", text)
    return match.group(1).strip() if match else ""


def in_scope(row: dict[str, Any], start: str | None, end: str | None) -> bool:
    date = str(row.get("date") or "")
    return (not start or date >= start) and (not end or date <= end)


def publication_from_row(row: dict[str, Any]) -> dict[str, str] | None:
    modality = str(row.get("modality") or "").casefold()
    source_class = str(row.get("source_class") or "").casefold()
    if modality not in AUTHORED_MODALITIES and not source_class.startswith("authored"):
        return None
    url = str(row.get("source_url") or "") or source_frontmatter_url(row)
    host = re.search(r"https?://(?:www\.)?([^/]+)", url)
    domain = host.group(1).casefold() if host else ""
    if not domain:
        return None
    if domain.endswith(".substack.com"):
        stem = domain.removesuffix(".substack.com")
        slug = re.sub(r"[^a-z0-9]+", "-", stem).strip("-")
        known = KNOWN_PUBLICATIONS.get(stem)
        if known:
            slug, name = known
        else:
            slug = re.sub(r"[^a-z0-9]+", "-", stem).strip("-")
            name = stem.replace("-", " ").title()
        return {"publication_slug": slug, "publication_name": name, "publication_url": f"https://{domain}/"}
    if domain == "substack.com" and "/@tritaparsi/" in url.casefold():
        return {"publication_slug": "trita-parsi", "publication_name": "Trita Parsi", "publication_url": "https://tritaparsi.substack.com/"}
    known = DOMAIN_PUBLICATIONS.get(domain)
    if known:
        slug, name = known
        return {"publication_slug": slug, "publication_name": name, "publication_url": f"https://{domain}/"}
    return None


def authored_candidate(row: dict[str, Any]) -> bool:
    return str(row.get("source_class", "")).casefold().startswith("authored") or str(row.get("modality", "")).casefold() in AUTHORED_MODALITIES


def publication_absence_reason(row: dict[str, Any]) -> str:
    url = str(row.get("source_url") or "") or source_frontmatter_url(row)
    if "youtube.com" in url.casefold() or "youtu.be" in url.casefold():
        return "youtube_container_not_publication"
    if "x.com" in url.casefold() or "twitter.com" in url.casefold():
        return "social_platform_not_publication"
    if "msn.com" in url.casefold():
        return "syndicated_access_url_not_authorial_publication"
    if not url:
        return "no_publication_url_or_identity"
    return "publication_identity_not_resolved"


def host_kind(row: dict[str, Any]) -> str | None:
    host = canonical_slug(str(row.get("host_slug") or ""))
    if not host:
        return None
    if (NG / "channels" / host).is_dir():
        return "channel"
    if (NG / "voices" / host).is_dir():
        return "host-person"
    return "show"


def infer_roles(row: dict[str, Any]) -> tuple[dict[str, list[str]], dict[str, str], dict[str, str]]:
    voices = [canonical_slug(str(v)) for v in row.get("voice_slugs") or [] if str(v)]
    source_class = str(row.get("source_class") or "").casefold()
    modality = str(row.get("modality") or "").casefold()
    host = canonical_slug(str(row.get("host_slug") or ""))
    authored = modality in AUTHORED_MODALITIES or source_class.startswith("authored")
    panel = "panel" in source_class or modality in {"panel", "live-panel"}
    roles: dict[str, list[str]] = {}
    status: dict[str, str] = {}
    basis: dict[str, str] = {}
    explicit_roles = row.get("voice_roles") or {}
    explicit_status = row.get("role_status") or {}
    explicit_basis = row.get("role_basis") or {}
    for voice in voices:
        prior_roles = explicit_roles.get(voice) or explicit_roles.get(canonical_slug(voice))
        if prior_roles:
            roles[voice] = list(prior_roles)
            status[voice] = explicit_status.get(voice) or explicit_status.get(canonical_slug(voice)) or "provisional"
            basis[voice] = explicit_basis.get(voice) or explicit_basis.get(canonical_slug(voice)) or "explicit_manifest_role"
            continue
        if authored:
            role, why, state = "author", "authored_source_class", "confirmed"
        elif panel:
            role, why, state = "panelist", "panel_source_class", "inferred"
        elif host and canonical_slug(host) == voice:
            role, why, state = "host", "host_voice_match", "inferred"
        elif host:
            role, why, state = "guest", "host_route_with_person_voice", "inferred"
        else:
            role, why, state = "guest", "voice_route_without_host", "provisional"
        roles[voice] = [role]
        status[voice] = state
        basis[voice] = why
    return roles, status, basis


def validate_row(row: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    voices = {canonical_slug(str(v)) for v in row.get("voice_slugs") or []}
    roles = row.get("voice_roles") or {}
    statuses = row.get("role_status") or {}
    bases = row.get("role_basis") or {}
    if set(roles) - voices:
        failures.append("voice_roles contains a person absent from voice_slugs")
    for voice, values in roles.items():
        if not isinstance(values, list) or not values or not set(values).issubset(ALLOWED_ROLES):
            failures.append(f"invalid role values for {voice}")
        if statuses.get(voice) not in ALLOWED_STATUS:
            failures.append(f"invalid role status for {voice}")
        if not bases.get(voice):
            failures.append(f"missing role basis for {voice}")
    host = str(row.get("host_slug") or "")
    if host and host in voices and host not in {canonical_slug(str(v)) for v in row.get("voice_slugs") or []}:
        failures.append("host route is not canonicalized")
    publication = row.get("publication_slug")
    if publication and publication in voices:
        failures.append("publication slug appears as a person voice")
    if row.get("host_kind") not in (None, *ALLOWED_HOST_KINDS):
        failures.append("invalid host_kind")
    if row.get("publication_slug") and not row.get("publication_name"):
        failures.append("publication_name is required with publication_slug")
    if authored_candidate(row) and not row.get("publication_slug") and not row.get("publication_absence_reason"):
        failures.append("authored source needs publication provenance or explicit absence reason")
    return failures


def migrate(manifest: dict[str, Any], start: str | None, end: str | None, write: bool) -> dict[str, Any]:
    changed: list[str] = []
    failures: list[str] = []
    for row in manifest.get("sources", []):
        if not in_scope(row, start, end):
            continue
        roles, status, basis = infer_roles(row)
        updates: dict[str, Any] = {
            "voice_roles": roles,
            "role_status": status,
            "role_basis": basis,
            "host_kind": host_kind(row),
        }
        publication = publication_from_row(row)
        if publication:
            updates.update(publication)
            updates["publication_absence_reason"] = None
        elif authored_candidate(row):
            updates["publication_absence_reason"] = publication_absence_reason(row)
        for key, value in updates.items():
            if row.get(key) != value:
                row[key] = value
                if row.get("local_path") not in changed:
                    changed.append(row["local_path"])
        failures.extend(f"{row.get('local_path')}: {item}" for item in validate_row(row))
    if write and not failures:
        MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return {"changed": sorted(changed), "failures": sorted(set(failures)), "write": write and not failures}


def render_publication(slug: str, name: str, rows: list[dict[str, Any]]) -> str:
    lines = [f"# Publication Shelf: {name}", "", "Status: `manifest-derived`", "", f"Publication slug: `{slug}`", "", "This shelf is provenance and publication continuity, not a person voice record.", "", "## Authored Sources", "", "| Date | Title | Voice | Source |", "| --- | --- | --- | --- |"]
    for row in sorted(rows, key=lambda item: (item.get("date", ""), item.get("local_path", ""))):
        voices = ", ".join(f"`{v}`" for v in row.get("voice_slugs") or [])
        link = "../../" + row["local_path"].split("narrative-geopolitics/", 1)[-1]
        lines.append(f"| `{row.get('date', '')}` | {row.get('title', '')} | {voices} | [source]({link}) |")
    lines += ["", "## Boundary", "", "Publication membership does not make the publication an independent analytical voice or corroborating source.", ""]
    return "\n".join(lines)


def write_publications(manifest: dict[str, Any], start: str | None, end: str | None) -> list[str]:
    grouped: dict[str, tuple[str, list[dict[str, Any]]]] = {}
    for row in manifest.get("sources", []):
        if not in_scope(row, start, end) or not row.get("publication_slug"):
            continue
        slug = row["publication_slug"]
        grouped.setdefault(slug, (row.get("publication_name", slug), []))[1].append(row)
    written: list[str] = []
    for slug, (name, rows) in grouped.items():
        target = PUBLICATIONS / slug / "README.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_publication(slug, name, rows), encoding="utf-8", newline="\n")
        written.append(target.relative_to(ROOT).as_posix())
    return sorted(written)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-date")
    parser.add_argument("--end-date")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--write-publications", action="store_true")
    parser.add_argument("--validate", action="store_true", help="validate all manifest rows without changing them")
    args = parser.parse_args()
    manifest = load_manifest()
    if args.validate:
        failures = []
        for row in manifest.get("sources", []):
            failures.extend(f"{row.get('local_path')}: {item}" for item in validate_row(row))
        print(json.dumps({"rows": len(manifest.get("sources", [])), "failures": sorted(set(failures)), "valid": not failures}, indent=2, ensure_ascii=False))
        return 1 if failures else 0
    report = migrate(manifest, args.start_date, args.end_date, args.write)
    if args.write_publications and args.write:
        report["publications"] = write_publications(manifest, args.start_date, args.end_date)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if report["failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
