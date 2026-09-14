import io
import json
import os
from pathlib import Path
import subprocess
import tarfile
import zipfile

import pytest
import artifact_delivery as subject


def deck(path, *, broken=False, font="Arial"):
    p = "http://schemas.openxmlformats.org/presentationml/2006/main"
    a = "http://schemas.openxmlformats.org/drawingml/2006/main"
    r = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    ns = "http://schemas.openxmlformats.org/package/2006/relationships"
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("ppt/presentation.xml", f'<p:presentation xmlns:p="{p}" xmlns:r="{r}"><p:sldIdLst><p:sldId id="256" r:id="r1"/></p:sldIdLst></p:presentation>')
        z.writestr("ppt/_rels/presentation.xml.rels", f'<Relationships xmlns="{ns}"><Relationship Id="r1" Type="{r}/slide" Target="slides/slide1.xml"/></Relationships>')
        z.writestr("ppt/slides/slide1.xml", f'<p:sld xmlns:p="{p}" xmlns:a="{a}" xmlns:r="{r}"><a:latin typeface="{font}"/><a:hlinkClick r:id="h1"/></p:sld>')
        if not broken:
            z.writestr("ppt/slides/_rels/slide1.xml.rels", f'<Relationships xmlns="{ns}"><Relationship Id="h1" Type="{r}/hyperlink" Target="https://example.org/" TargetMode="External"/></Relationships>')


def archive(path, extra=None):
    with tarfile.open(path, "w:gz") as tar:
        entries = {"dist/index.html": b"hello", "dist/.openai/hosting.json": b"{}"}
        if extra:
            entries.update(extra)
        for name, data in entries.items():
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))


def test_linked_deck_count_fonts_relationships_and_hash(tmp_path):
    path = tmp_path / "linked.pptx"
    deck(path)
    report = subject.verify_deck(path, 1, ["Arial"])
    assert report["sha256"] == subject.digest(path)
    assert report["hyperlink_relationships"] == 1
    for slides, fonts in [(2, ["Arial"]), (1, ["Calibri"]), (1, [])]:
        with pytest.raises(subject.DeliveryError):
            subject.verify_deck(path, slides, fonts)
    deck(path, broken=True)
    with pytest.raises(subject.DeliveryError, match="hyperlink"):
        subject.verify_deck(path, 1, ["Arial"])


def test_archive_validation_rejects_paths_and_invalid_packages(tmp_path):
    path = tmp_path / "site.tar.gz"
    archive(path)
    assert subject.verify_archive(path)["status"] == "passed"
    archive(path, {"dist/../../escape": b"bad"})
    with pytest.raises(subject.DeliveryError):
        subject.verify_archive(path)
    path.write_bytes(b"invalid")
    with pytest.raises(tarfile.TarError):
        subject.verify_archive(path)


def test_windows_space_path_and_unc():
    assert subject.bash_path(r"C:\private\space folder\site.tar.gz") == "/c/private/space folder/site.tar.gz"
    with pytest.raises(subject.DeliveryError):
        subject.bash_path(r"\\server\share\file")


def setup_delivery(tmp_path):
    project, plugin, temp, runtime = [tmp_path / name for name in ("space project", "plugin", "temporary", "runtime")]
    for path in (project, plugin, temp, runtime):
        path.mkdir()
    for name in ("node/bin/node.exe" if os.name == "nt" else "node/bin/node", "python/python.exe" if os.name == "nt" else "python/bin/python", "node/node_modules/@oai/artifact-tool/package.json"):
        path = runtime / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("fixture")
    (plugin / "container_tools").mkdir()
    for resource in ("artifact_tool_utils.mjs", "mark_artifact_operation_started.mjs",
                     "inspect_presentation_package_integrity.py", "inspect_presentation_layout_geometry.py"):
        (plugin / "container_tools" / resource).write_text("fixture")
    script = project / "author.mjs"
    script.write_text("fixture")
    return subject.parser().parse_args(["--operation", "presentation", "--project", str(project), "--plugin-root", str(plugin),
        "--temp-root", str(temp), "--runtime-root", str(runtime), "--script", str(script), "--output", str(temp / "final.pptx"), "--font", "Arial", "--slides", "1"])


@pytest.mark.parametrize("exit_code,valid", [(0, True), (7, True), (9, False), (0, False)])
def test_process_and_artifact_results_are_independent(tmp_path, monkeypatch, exit_code, valid):
    args = setup_delivery(tmp_path)
    original = os.environ.copy()
    def run(command, *, cwd, env, capture_output):
        if command[-1] == "--version":
            return subprocess.CompletedProcess(command, 0, b"version", b"")
        assert env["RUNTIME_NODE_MODULES"] == str(args.runtime_root / "node/node_modules")
        assert env["TMP"] == env["TEMP"] == env["MIRA_CORE_SESSION_TEMP_ROOT"] == str(args.temp_root)
        assert json.loads(env["DELIVERY_FONT_FAMILIES"]) == ["Arial"]
        if valid:
            deck(args.output)
        return subprocess.CompletedProcess(command, exit_code, b"secret-token", b"secret-token")
    monkeypatch.setattr(subject.subprocess, "run", run)
    code, report = subject.execute(args)
    assert code == (exit_code or (0 if valid else 1))
    assert report["recoverable_artifact"] == (exit_code != 0 and valid)
    assert "secret-token" not in json.dumps(report)
    assert os.environ == original


def test_dependencies_fonts_and_bash_fail_before_authoring(tmp_path, monkeypatch):
    args = setup_delivery(tmp_path)
    monkeypatch.setattr(subject.subprocess, "run", lambda *a, **k: pytest.fail("must fail before execution"))
    args.font = []
    with pytest.raises(subject.DeliveryError):
        subject.execute(args)
    args.operation = "sites-package"
    with pytest.raises(subject.DeliveryError, match="Bash"):
        subject.execute(args)
    args.runtime_root = tmp_path / "missing"
    with pytest.raises(OSError):
        subject.execute(args)


def test_existing_artifact_is_not_recovered_as_new_success(tmp_path):
    args = setup_delivery(tmp_path)
    deck(args.output)
    with pytest.raises(subject.DeliveryError, match="new file"):
        subject.execute(args)


def test_failed_runtime_probe_prevents_authoring(tmp_path, monkeypatch):
    args = setup_delivery(tmp_path)
    calls = []
    def fail(command, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 12, b"", b"")
    monkeypatch.setattr(subject.subprocess, "run", fail)
    with pytest.raises(subject.DeliveryError, match="runtime executable probe"):
        subject.execute(args)
    assert len(calls) == 1 and calls[0][-1] == "--version"
    assert not args.output.exists()


def test_absent_modules_prevents_authoring(tmp_path, monkeypatch):
    args = setup_delivery(tmp_path)
    (args.runtime_root / "node/node_modules/@oai/artifact-tool/package.json").unlink()
    monkeypatch.setattr(subject.subprocess, "run", lambda *a, **k: pytest.fail("authoring must not start"))
    with pytest.raises(OSError):
        subject.execute(args)


def test_changed_reference_invalidates_otherwise_valid_output(tmp_path, monkeypatch):
    args = setup_delivery(tmp_path)
    args.reference = tmp_path / "reference.pptx"
    deck(args.reference)
    before = subject.digest(args.reference)
    def author(command, **kwargs):
        if command[-1] != "--version":
            assert kwargs["env"]["DELIVERY_REFERENCE_SHA256"] == before
            assert kwargs["env"]["DELIVERY_REFERENCE"] == str(args.reference)
            deck(args.output)
            args.reference.write_bytes(b"changed")
        return subprocess.CompletedProcess(command, 0, b"", b"")
    monkeypatch.setattr(subject.subprocess, "run", author)
    code, report = subject.execute(args)
    assert code == 1
    assert report["command_status"] == "passed"
    assert report["artifact_validation"]["status"] == "failed"


def test_failed_runtime_probe_prevents_authoring(tmp_path, monkeypatch):
    args = setup_delivery(tmp_path)
    calls = []
    def fail(command, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 12, b"", b"")
    monkeypatch.setattr(subject.subprocess, "run", fail)
    with pytest.raises(subject.DeliveryError, match="runtime executable probe"):
        subject.execute(args)
    assert len(calls) == 1 and calls[0][-1] == "--version"
    assert not args.output.exists()


def test_absent_modules_prevents_authoring(tmp_path, monkeypatch):
    args = setup_delivery(tmp_path)
    (args.runtime_root / "node/node_modules/@oai/artifact-tool/package.json").unlink()
    monkeypatch.setattr(subject.subprocess, "run", lambda *a, **k: pytest.fail("authoring must not start"))
    with pytest.raises(OSError):
        subject.execute(args)
