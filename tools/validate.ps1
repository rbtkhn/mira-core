[CmdletBinding()]
param(
    [ValidateSet('Full', 'Fast')]
    [string] $Mode = 'Full',
    [switch] $Force
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$validator = Join-Path $repoRoot 'tools\validate_repo.py'
$validatorArguments = @('--mode', $Mode.ToLowerInvariant())
if ($Force) {
    $validatorArguments += '--force'
}
$pyLauncher = @(
    Get-Command py.exe `
        -CommandType Application `
        -ErrorAction SilentlyContinue
)[0]

if ($env:NARRATIVE_PYTHON) {
    & $env:NARRATIVE_PYTHON $validator @validatorArguments
} elseif ($pyLauncher) {
    & $pyLauncher.Source -3 $validator @validatorArguments
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    & python3 $validator @validatorArguments
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python $validator @validatorArguments
} else {
    Write-Error 'Python 3.11+ was not found. Install Python or set NARRATIVE_PYTHON.'
    exit 1
}
exit $LASTEXITCODE
