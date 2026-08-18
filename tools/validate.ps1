[CmdletBinding()]
param(
    [ValidateSet('Full', 'Fast')]
    [string] $Mode = 'Full',
    [switch] $Force,
    [string] $TempRoot
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$runtimeEnvironment = Join-Path $PSScriptRoot 'runtime-env.ps1'
. $runtimeEnvironment
if (-not $TempRoot) {
    $TempRoot = Resolve-MiraCoreEnvironment -Canonical 'MIRA_CORE_SESSION_TEMP_ROOT'
}
$validator = Join-Path $repoRoot 'tools\validate_repo.py'
$validatorArguments = @('--mode', $Mode.ToLowerInvariant())
if ($Force) {
    $validatorArguments += '--force'
}
if ($TempRoot) {
    $validatorArguments += @('--temp-root', $TempRoot)
}
$pyLauncher = @(
    Get-Command py.exe `
        -CommandType Application `
        -ErrorAction SilentlyContinue
)[0]

$pythonOverride = Resolve-MiraCoreEnvironment -Canonical 'MIRA_CORE_PYTHON'
if ($pythonOverride) {
    & $pythonOverride $validator @validatorArguments
} elseif ($pyLauncher) {
    & $pyLauncher.Source -3 $validator @validatorArguments
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    & python3 $validator @validatorArguments
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python $validator @validatorArguments
} else {
    Write-Error 'Python 3.11+ was not found. Install Python or set MIRA_CORE_PYTHON.'
    exit 1
}
exit $LASTEXITCODE
