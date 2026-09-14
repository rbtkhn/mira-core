"""Local artifact execution adapter. Never installs, publishes, or edits plugin caches."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import posixpath
import subprocess
import tarfile
import zipfile
import xml.etree.ElementTree as ET

from session_preflight import probe_temp_root, is_within

REPO_ROOT = Path(__file__).resolve().parent.parent


class DeliveryError(ValueError):
    pass


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def required_path(path: Path, *, directory: bool = False) -> Path:
    if not path.is_absolute():
        raise DeliveryError("paths must be absolute")
    resolved = path.resolve(strict=True)
    if not (resolved.is_dir() if directory else resolved.is_file()):
        raise DeliveryError("required executable or resource has the wrong type")
    return resolved


def bash_path(path: str | Path) -> str:
    """Convert drive paths for Git Bash utilities (not for Windows Node)."""
    raw = str(path)
    windows = PureWindowsPath(raw)
    if windows.drive:
        if len(windows.drive) != 2 or not windows.root:
            raise DeliveryError("Git Bash packaging requires an absolute local drive path")
        return "/" + windows.drive[0].lower() + "/" + "/".join(windows.parts[1:])
    return raw


def runtime(root: Path) -> dict[str, Path]:
    root = required_path(root, directory=True)
    win = os.name == "nt"
    return {
        "node": required_path(root / "node/bin" / ("node.exe" if win else "node")),
        "modules": required_path(root / "node/node_modules", directory=True),
        "python": required_path(root / "python" / ("python.exe" if win else "bin/python")),
    }


def verify_archive(path: Path) -> dict:
    names = set()
    metadata = None
    with tarfile.open(path, "r:gz") as archive:
        for count, member in enumerate(archive, 1):
            name = member.name.rstrip("/")
            if count > 100000 or member.size > 512 * 1024 * 1024:
                raise DeliveryError("archive exceeds validation limits")
            parts = PurePosixPath(name).parts
            if not parts or parts[0] != "dist" or ".." in parts or "\\" in name or ":" in name:
                raise DeliveryError("unsafe archive path")
            if not (member.isfile() or member.isdir()) or name in names:
                raise DeliveryError("archive contains links, special files or duplicate entries")
            names.add(name)
            if name == "dist/.openai/hosting.json":
                if member.size > 1024 * 1024:
                    raise DeliveryError("hosting metadata too large")
                metadata = json.load(archive.extractfile(member))
    if not isinstance(metadata, dict) or not ({"dist/index.html", "dist/server/index.js"} & names):
        raise DeliveryError("archive requires hosting metadata and a static or worker entrypoint")
    return {"status": "passed", "entry_count": len(names), "sha256": digest(path)}


def verify_deck(path: Path, slides: int, fonts: list[str]) -> dict:
    """Independent package checks; does not claim visual layout or font availability."""
    p = "http://schemas.openxmlformats.org/presentationml/2006/main"
    a = "http://schemas.openxmlformats.org/drawingml/2006/main"
    r = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    declared = set(fonts)
    found_fonts = set()
    links = 0
    with zipfile.ZipFile(path) as package:
        names = set(package.namelist())
        if len(names) != len(package.namelist()):
            raise DeliveryError("duplicate deck package entries")
        if any(i.file_size > 64 * 1024 * 1024 for i in package.infolist()):
            raise DeliveryError("deck member exceeds validation limit")
        presentation = ET.fromstring(package.read("ppt/presentation.xml"))
        ids = presentation.findall(f"{{{p}}}sldIdLst/{{{p}}}sldId")
        if len(ids) != slides:
            raise DeliveryError("slide count does not match declaration")
        relationships = {}
        for name in names:
            if not name.endswith(".rels"):
                continue
            tree = ET.fromstring(package.read(name))
            base = posixpath.dirname(posixpath.dirname(name))
            relationships[name] = {item.get("Id"): item for item in tree}
            if len(relationships[name]) != len(tree):
                raise DeliveryError("duplicate relationship IDs")
            for item in tree:
                target = item.get("Target", "")
                if item.get("TargetMode") == "External":
                    if item.get("Type", "").endswith("/hyperlink"):
                        from urllib.parse import urlsplit
                        parsed = urlsplit(target)
                        if parsed.scheme not in ("https", "http", "mailto") or not parsed.path and not parsed.netloc or parsed.username or parsed.password:
                            raise DeliveryError("invalid external hyperlink")
                        links += 1
                elif posixpath.normpath(posixpath.join(base, target.lstrip("/")) if not target.startswith("/") else target[1:]) not in names:
                    raise DeliveryError("broken internal package relationship")
        slide_rels = relationships.get("ppt/_rels/presentation.xml.rels", {})
        for item in ids:
            rel = slide_rels.get(item.get(f"{{{r}}}id"))
            if rel is None or not rel.get("Type", "").endswith("/slide"):
                raise DeliveryError("slide relationship is missing")
        for name in names:
            if not name.startswith("ppt/slides/slide") or not name.endswith(".xml"):
                continue
            tree = ET.fromstring(package.read(name))
            rels = relationships.get(posixpath.dirname(name) + "/_rels/" + posixpath.basename(name) + ".rels", {})
            for item in tree.iter():
                if item.tag in (f"{{{a}}}latin", f"{{{a}}}ea", f"{{{a}}}cs") and item.get("typeface"):
                    found_fonts.add(item.get("typeface"))
                if item.tag in (f"{{{a}}}hlinkClick", f"{{{a}}}hlinkMouseOver"):
                    rel = rels.get(item.get(f"{{{r}}}id"))
                    if rel is None or not rel.get("Type", "").endswith("/hyperlink"):
                        raise DeliveryError("broken hyperlink relationship")
        if not declared or not found_fonts or not found_fonts <= declared:
            raise DeliveryError("explicit slide fonts do not match declared reference fonts")
    return {"status": "passed", "slide_count": slides, "fonts": sorted(found_fonts),
            "hyperlink_relationships": links, "sha256": digest(path),
            "coverage": "package-count-font-declarations-relationships-hash; visual QA separate"}


def execute(args: argparse.Namespace) -> tuple[int, dict]:
    project = required_path(args.project, directory=True)
    plugin = required_path(args.plugin_root, directory=True)
    for boundary in (REPO_ROOT, project, plugin):
        preflight = probe_temp_root(args.temp_root, repo_root=boundary)
        if not preflight["writable"] or not preflight["probe_removed"]:
            raise DeliveryError("external temporary-root preflight failed")
    temporary = args.temp_root.resolve(strict=True)
    output = args.output.resolve()
    if not args.output.is_absolute() or not is_within(output, temporary) or output.exists():
        raise DeliveryError("output must be a new file under the preflighted temporary root")
    deps = runtime(args.runtime_root)
    env = os.environ.copy()
    env.update(RUNTIME_NODE_MODULES=str(deps["modules"]), TMP=str(temporary), TEMP=str(temporary),
               TMPDIR=str(temporary), MIRA_CORE_SESSION_TEMP_ROOT=str(temporary),
               DELIVERY_OUTPUT=str(output), DELIVERY_PYTHON=str(deps["python"]))
    env["PATH"] = str(deps["node"].parent) + os.pathsep + env.get("PATH", "")
    reference_hash = None
    if args.operation == "presentation":
        if args.script is None or not args.font or not args.slides or args.slides < 1:
            raise DeliveryError("presentation requires script, positive slide count and declared fonts")
        script = required_path(args.script)
        if not is_within(script, project):
            raise DeliveryError("authoring script must be inside the specified project")
        required_path(deps["modules"] / "@oai/artifact-tool/package.json")
        for resource in ("artifact_tool_utils.mjs", "mark_artifact_operation_started.mjs",
                         "inspect_presentation_package_integrity.py", "inspect_presentation_layout_geometry.py"):
            required_path(plugin / "container_tools" / resource)
        if args.reference:
            reference_hash = digest(required_path(args.reference))
        env.update(DELIVERY_FONT_FAMILIES=json.dumps(args.font), DELIVERY_REFERENCE_SHA256=reference_hash or "",
                   DELIVERY_REFERENCE=str(args.reference.resolve()) if args.reference else "",
                   DELIVERY_PLUGIN_ROOT=str(plugin), DELIVERY_EXPECTED_SLIDES=str(args.slides))
        command = [str(deps["node"]), str(script)]
    else:
        if args.bash is None:
            raise DeliveryError("Sites packaging requires an explicit Git Bash executable")
        bash = required_path(args.bash)
        # Git for Windows bin/bash.exe uses usr/bin for dirname, tar, mktemp, etc.
        utilities = required_path(bash.parent.parent / "usr/bin", directory=True) if os.name == "nt" else bash.parent
        for utility in ("dirname", "mktemp", "tar", "grep"):
            required_path(utilities / (utility + (".exe" if os.name == "nt" else "")))
        env["PATH"] = os.pathsep.join((str(bash.parent), str(utilities), env["PATH"]))
        env["TMPDIR"] = bash_path(temporary)
        wrapper = required_path(plugin / "scripts/package-site.mjs")
        required_path(project / ".openai/hosting.json")
        command = [str(deps["node"]), str(wrapper), str(project), bash_path(output)]
    receipt = output.with_name(output.name + ".delivery.json")
    if receipt.exists():
        raise DeliveryError("receipt already exists")
    # Execute only bounded runtime probes before the authoring/packaging step.
    for executable in (deps["node"], deps["python"], *([bash] if args.operation == "sites-package" else [])):
        probe = subprocess.run([str(executable), "--version"], cwd=project, env=env, capture_output=True)
        if probe.returncode != 0:
            raise DeliveryError("bundled runtime executable probe failed")
    output.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(command, cwd=project, env=env, capture_output=True)
    report = {"schema_version": "artifact-delivery.v1", "operation": args.operation,
              "process_exit_code": result.returncode, "command_status": "passed" if result.returncode == 0 else "failed",
              "reference_sha256": reference_hash, "authority_effect": "none",
              "captured_output": "not retained; may contain credentials", "artifact_validation": {"status": "failed"}}
    try:
        validation = verify_deck(output, args.slides, args.font) if args.operation == "presentation" else verify_archive(output)
        if reference_hash and digest(args.reference) != reference_hash:
            raise DeliveryError("reference deck changed during authoring")
        report["artifact_validation"] = validation
    except (OSError, ValueError, KeyError, zipfile.BadZipFile, tarfile.TarError, ET.ParseError):
        report["artifact_validation"] = {"status": "failed", "reason": "output missing or independent package checks failed"}
    report["status"] = "passed" if result.returncode == 0 and report["artifact_validation"]["status"] == "passed" else "failed"
    report["recoverable_artifact"] = result.returncode != 0 and report["artifact_validation"]["status"] == "passed"
    receipt.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return result.returncode if result.returncode else (0 if report["status"] == "passed" else 1), report


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--operation", required=True, choices=("presentation", "sites-package"))
    for name in ("project", "plugin-root", "runtime-root", "temp-root", "output"):
        value.add_argument("--" + name, required=True, type=Path)
    for name in ("script", "reference", "bash"):
        value.add_argument("--" + name, type=Path)
    value.add_argument("--font", action="append", default=[])
    value.add_argument("--slides", type=int)
    return value


def main(arguments: list[str] | None = None) -> int:
    try:
        code, report = execute(parser().parse_args(arguments))
    except DeliveryError as error:
        code, report = 1, {"status": "blocked", "reason": str(error), "authority_effect": "none"}
    except (OSError, ValueError, subprocess.SubprocessError):
        code, report = 1, {"status": "blocked", "reason": "dependency, input or execution preflight failed", "authority_effect": "none"}
    print(json.dumps(report, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
