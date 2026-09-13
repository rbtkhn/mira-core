from types import SimpleNamespace

import pytest
import publication_validation as routing


@pytest.mark.parametrize('path', sorted(routing.RETIRED_WORKTREE_POINTERS))
def test_exact_absent_gitlink_routes_for_deletion(tmp_path, monkeypatch, path):
    def tree(args, **kwargs):
        assert args == ['git', 'ls-tree', 'HEAD', '--', path]
        return SimpleNamespace(returncode=0, stdout='160000 commit ' + 'a' * 40 + '\t' + path + '\n')
    monkeypatch.setattr(routing.subprocess, 'run', tree)
    report = routing.build_report([path], repo_root=tmp_path)
    assert report['status'] == 'manual-required'
    assert report['owners'] == ['repo-structural']
    target = tmp_path / path
    target.mkdir(parents=True)
    assert routing.build_report([path], repo_root=tmp_path)['status'] == 'blocked'


@pytest.mark.parametrize('mode,code', [('100644 blob', 0), ('', 0), ('160000 commit', 1)])
def test_missing_blob_or_failed_inspection_is_not_deletion_authority(tmp_path, monkeypatch, mode, code):
    path = sorted(routing.RETIRED_WORKTREE_POINTERS)[0]
    monkeypatch.setattr(routing.subprocess, 'run', lambda *a, **k: SimpleNamespace(
        returncode=code, stdout=mode + ' ' + 'a' * 40 + '\t' + path + '\n'))
    assert routing.build_report([path], repo_root=tmp_path)['status'] == 'blocked'


def test_neighbor_is_not_admitted(tmp_path):
    path = tmp_path / '.codex-tmp/private-neighbor.txt'
    path.parent.mkdir()
    path.write_text('fictional')
    assert routing.build_report([path.relative_to(tmp_path).as_posix()], repo_root=tmp_path)['status'] == 'blocked'
