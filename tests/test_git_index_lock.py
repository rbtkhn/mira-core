"""Execute the PowerShell decision path with isolated process/access fixtures."""
from pathlib import Path
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
SHELL = shutil.which('pwsh') or shutil.which('powershell')
pytestmark = pytest.mark.skipif(not SHELL, reason='PowerShell unavailable')


@pytest.mark.parametrize('case', ['git', 'lfs', 'enumeration', 'changed', 'disappeared', 'exclusive', 'resolved', 'stale', 'inspect'])
def test_lock_decision_preserves_unproven_locks(tmp_path, case):
    lock = tmp_path / 'index.lock'; lock.write_text('')
    script = tmp_path / 'check.ps1'
    helper = (ROOT / 'tools/git-index-lock.ps1').as_posix().replace("'", "''")
    target = lock.as_posix().replace("'", "''")
    mocks = {
        'git': "function Get-LockOwners { [pscustomobject]@{Name='git.exe'} }",
        'lfs': "function Get-LockOwners { [pscustomobject]@{Name='git-lfs.exe'} }",
        'enumeration': "function Get-LockOwners { throw 'enumeration unavailable' }",
        'changed': "function Wait-LockStability { Add-Content -LiteralPath $script:target 'changed' }",
        'disappeared': "function Wait-LockStability { Remove-Item -LiteralPath $script:target }",
        'exclusive': "function Assert-ExclusiveLock { throw 'exclusive denied' }",
        'resolved': "function Resolve-LockTarget { $script:calls++; if ($script:calls -gt 1) { return ($script:target + '.other') }; return $script:target }",
    }
    script.write_text(f"""
. '{helper}' -Repository '{tmp_path.as_posix()}'
$script:target = '{target}'
$script:calls = 0
function Resolve-LockTarget {{ return $script:target }}
function Get-LockOwners {{ @() }}
function Wait-LockStability {{ }}
{mocks.get(case, '')}
try {{ Invoke-IndexLock '{tmp_path.as_posix()}' ${'false' if case == 'inspect' else 'true'} | ConvertTo-Json -Compress; exit 0 }}
catch {{ Write-Output $_.Exception.Message; exit 1 }}
""", encoding='utf-8')
    result = subprocess.run([SHELL, '-NoProfile', '-File', str(script)], capture_output=True, text=True)
    assert result.returncode == (0 if case in {'stale', 'inspect'} else 1), result.stdout + result.stderr
    assert lock.exists() == (case not in {'stale', 'disappeared'})


def test_native_failure_survives_successful_diagnostic(tmp_path):
    script = tmp_path / 'exit.ps1'
    script.write_text("& $PSHOME/pwsh -NoProfile -Command 'exit 7'\n$taskExit = $LASTEXITCODE\nWrite-Output 'diagnostic succeeded'\nexit $taskExit\n")
    if Path(SHELL).name.lower() != 'pwsh.exe' and Path(SHELL).name.lower() != 'pwsh':
        pytest.skip('pwsh fixture')
    result = subprocess.run([SHELL, '-NoProfile', '-File', str(script)], capture_output=True)
    assert result.returncode == 7
