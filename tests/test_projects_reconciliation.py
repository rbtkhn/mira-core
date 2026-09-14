from pathlib import Path
import re
import subprocess
import stat

import pytest
import publication_validation as routing


def test_four_active_homes_and_no_competing_gems_home():
    root = Path(__file__).resolve().parents[1] / 'projects'
    assert {p.name for p in root.iterdir() if p.is_dir()} == {
        'grace-mar', 'hannah-vlog', 'learning-core',
    }
    assert (root / 'grace-mar/grace-gems/admission-matrix.md').is_file()
    assert (root / 'grace-mar/ottoman-rugs/README.md').is_file()


@pytest.mark.parametrize('relative', sorted(routing.RETIRED_PROJECT_PATHS))
def test_retired_path_allows_tracked_deletion_only(tmp_path, relative):
    def git(*args):
        subprocess.run(['git', *args], cwd=tmp_path, check=True, capture_output=True)
    git('init', '-q')
    path = tmp_path / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('Synthetic old orientation\n')
    (tmp_path / 'projects/README.md').write_text('Synthetic current index\n')
    git('add', '--', relative, 'projects/README.md')
    git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
        '-c', 'core.hooksPath=/dev/null', 'commit', '-qm', 'Fixture baseline')
    # Git objects are read-only on Windows; allow the canonical temp cleanup.
    for artifact in (tmp_path / '.git/objects').rglob('*'):
        if artifact.is_file():
            artifact.chmod(artifact.stat().st_mode | stat.S_IWRITE)
    assert routing.build_report([relative], repo_root=tmp_path)['status'] == 'blocked'
    path.unlink()
    report = routing.build_report([relative], repo_root=tmp_path)
    assert report['status'] == 'manual-required'
    assert report['owners'] == ['projects/reconciliation']
    assert report['manual_checks'] == [routing.MANUAL_PROJECT_RECONCILIATION_CHECK]


def test_absent_untracked_retirement_is_not_admitted(tmp_path):
    (tmp_path / 'projects').mkdir()
    (tmp_path / 'projects/README.md').write_text('Synthetic\n')
    assert routing.build_report(['projects/lab/README.md'], repo_root=tmp_path)['status'] == 'blocked'


def test_all_active_project_links_resolve():
    root = Path(__file__).resolve().parents[1]
    for path in (root / 'projects').rglob('*.md'):
        for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
            if target.startswith(('https:', 'http:', '#')):
                continue
            resolved = (path.parent / target.split('#')[0]).resolve()
            assert resolved.is_relative_to(root)
            assert resolved.is_file(), (path, target)


def test_transfer_contract_links_reach_shared_section():
    root = Path(__file__).resolve().parents[1]
    sources = [root / 'projects' / name / 'README.md' for name in (
        'grace-mar', 'grace-mar/ottoman-rugs', 'grace-mar/mountain-villa', 'learning-core', 'grace-mar/grace-gems',
    )] + [root / 'docs/skill-drafts' / name / 'SKILL.md' for name in ('mira-work', 'mira-treasury')]
    for source in sources:
        targets = re.findall(r'\[[^\]]+\]\(([^)]+#cross-project-method-transfer)\)', source.read_text(encoding='utf-8'))
        assert len(targets) == 1
        path, fragment = targets[0].split('#')
        target = (source.parent / path).resolve()
        assert target == (root / 'projects/README.md').resolve()
        headings = [re.sub(r'[^a-z0-9 -]', '', x.lower()).replace(' ', '-')
                    for x in re.findall(r'^#+ (.+)$', target.read_text(encoding='utf-8'), re.M)]
        assert fragment in headings
