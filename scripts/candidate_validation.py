"""Focused checks of immutable Git bytes; no checkout or working-tree overlay."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import uuid
from collections import deque


def git_environment() -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if k not in {
        'GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY',
        'GIT_ALTERNATE_OBJECT_DIRECTORIES'}}
    env['GIT_NO_REPLACE_OBJECTS'] = '1'
    return env


def git(repo: Path, *args: str) -> bytes:
    return subprocess.check_output(['git', '-C', str(repo), *args], stderr=subprocess.PIPE,
                                   env=git_environment())


def safe_path(raw: str) -> str:
    parts = PurePosixPath(raw).parts
    reserved = {'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(1, 10)),
                *(f'LPT{i}' for i in range(1, 10))}
    if (not raw or raw.startswith('/') or '\\' in raw or ':' in raw
            or raw != '/'.join(parts) or any(
                p in {'.', '..'} or p.lower() == '.git' or p.endswith((' ', '.'))
                or p.split('.')[0].upper() in reserved
                or any(ord(c) < 32 or c in '<>"|?*' for c in p) for p in parts)):
        raise ValueError(f'unsafe candidate path: {raw!r}')
    return raw


def export_commit(repo: Path, commit: str, destination: Path) -> str:
    if not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise ValueError('--candidate-ref requires a full lowercase commit SHA')
    if git(repo, 'cat-file', '-t', commit).strip() != b'commit':
        raise ValueError('candidate must identify a commit, not a tree or tag')
    tree = git(repo, 'rev-parse', commit + '^{tree}').decode().strip()
    entries = []
    seen: dict[str, str] = {}
    for row in git(repo, 'ls-tree', '-rz', '--full-tree', commit).split(b'\0'):
        if not row:
            continue
        metadata, raw = row.split(b'\t', 1)
        mode, kind, blob = metadata.decode().split()
        name = safe_path(raw.decode('utf-8'))
        if mode not in {'100644', '100755'} or kind != 'blob':
            raise ValueError(f'unsupported candidate entry: {name} ({mode})')
        # Reject directory as well as filename aliases on case-insensitive hosts.
        for length in range(1, len(PurePosixPath(name).parts) + 1):
            prefix = '/'.join(PurePosixPath(name).parts[:length])
            previous = seen.setdefault(prefix.casefold(), prefix)
            if previous != prefix:
                raise ValueError(f'case-colliding candidate path: {name}')
        entries.append((name, mode, blob))
    destination.mkdir()  # Never reuse a populated fixture.
    process = subprocess.Popen(['git', '-C', str(repo), 'cat-file', '--batch'],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.DEVNULL, env=git_environment())
    try:
        for name, mode, blob in entries:
            process.stdin.write((blob + '\n').encode()); process.stdin.flush()
            header = process.stdout.readline().decode().split()
            if len(header) != 3 or header[:2] != [blob, 'blob']:
                raise ValueError(f'cannot export blob: {name}')
            size = int(header[2])
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as output:
                remaining = size
                while remaining:
                    chunk = process.stdout.read(min(remaining, 1024 * 1024))
                    if not chunk:
                        raise ValueError(f'incomplete blob: {name}')
                    output.write(chunk); remaining -= len(chunk)
            if process.stdout.read(1) != b'\n':
                raise ValueError(f'invalid blob delimiter: {name}')
            if mode == '100755':
                target.chmod(0o755)
        process.stdin.close()
        if process.wait() != 0:
            raise ValueError('candidate export failed')
    finally:
        if process.poll() is None:
            process.kill(); process.wait()
    return tree


def inventory(root: Path) -> dict[str, str]:
    result = {}
    if root.exists():
        for folder, dirs, files in os.walk(root, followlinks=False):
            for name in dirs + files:
                path = Path(folder) / name
                rel = path.relative_to(root).as_posix()
                if path.is_symlink():
                    result[rel] = 'unsupported-link'
                elif path.is_file():
                    result[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def run_candidate(repo: Path, commit: str, paths: list[str], python: Path,
                  temp_root: Path, environment: dict[str, str], timeout: int = 600) -> int:
    attempt = temp_root / ('candidate-' + uuid.uuid4().hex)
    attempt.mkdir()
    snapshot = attempt / 'tree'
    log = attempt / 'pytest.log'
    report = {'validation_scope': 'immutable-candidate', 'commit': commit, 'tree': None,
              'tests': paths, 'runtime': str(python), 'attempt': str(attempt),
              'supplemental_files': [], 'missing_dependencies': [], 'exit_code': 2,
              'dependency_coverage': 'selected test paths and test-reported missing imports/files; not a complete dependency graph'}
    before = {}
    try:
        if not paths:
            raise ValueError('candidate validation requires explicit test selections')
        report['tree'] = export_commit(repo, commit, snapshot)
        before = inventory(snapshot)
        for raw in paths:
            safe_path(raw)
            path = snapshot / raw
            if not raw.startswith('tests/') or not path.exists():
                report['missing_dependencies'].append(raw)
                raise ValueError(f'focused test path missing from candidate: {raw}')
        env = {k: v for k, v in environment.items()
               if not k.startswith(('MIRA_CORE_', 'NARRATIVE_'))
               and k not in {'PYTHONPATH', 'PYTHONHOME', 'PYTEST_ADDOPTS', 'PYTEST_PLUGINS'}}
        env['PYTHONPATH'] = os.pathsep.join([str(snapshot / 'scripts'), str(snapshot)])
        env['PYTEST_DISABLE_PLUGIN_AUTOLOAD'] = '1'
        env['PYTHONIOENCODING'] = 'utf-8'
        command = [str(python), '-m', 'pytest', '-q', '--tb=short', '-p', 'no:cacheprovider',
                   '-m', 'not repository_integrity', '--basetemp', str(attempt / 'pytest'), *paths]
        with log.open('xb') as output:
            try:
                result = subprocess.run(command, cwd=snapshot, env=env, stdout=output,
                                        stderr=subprocess.STDOUT, timeout=timeout)
                report['exit_code'] = result.returncode
            except subprocess.TimeoutExpired:
                report['exit_code'] = 124
        # Retain full output on disk; bound the displayed failure excerpt.
        tail = deque(maxlen=40)
        count = 0
        missing = []
        with log.open(encoding='utf-8', errors='replace') as saved:
            for line in saved:
                count += 1
                tail.append(line[:1000])
                if len(missing) < 100 and any(term in line for term in
                        ('FileNotFoundError', 'ModuleNotFoundError', 'No such file', 'cannot import name')):
                    missing.append(line[:500].rstrip())
        report['missing_dependencies'] = list(dict.fromkeys(missing))
        encoding = getattr(sys.stdout, 'encoding', None) or 'utf-8'
        print(''.join(tail)[-4000:].encode(encoding, errors='backslashreplace').decode(encoding))
        report['log_lines'] = count
        report['display_limit'] = 'last 40 lines, at most 4000 characters; full log retained'
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        report['error'] = str(error)
    finally:
        after = inventory(snapshot)
        report['inventory_before'] = before
        report['inventory_after'] = after
        changed = [p for p, digest in before.items() if after.get(p) != digest]
        report['changed_candidate_files'] = changed
        if changed:
            report['exit_code'] = 1
        report['status'] = 'passed' if report['exit_code'] == 0 else 'failed'
        report['log'] = str(log) if log.exists() else None
        receipt = attempt / 'result.json'
        with receipt.open('x', encoding='utf-8') as output:
            json.dump(report, output, indent=2)
        print(json.dumps({k: report[k] for k in ('validation_scope', 'commit', 'tree',
                         'status', 'exit_code')} | {'result': str(receipt)}))
    return report['exit_code']
