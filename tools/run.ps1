[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $RunArguments
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$runner = Join-Path $repoRoot 'tools\run_repo.py'
$bootstrap = Join-Path $repoRoot 'scripts\runtime_bootstrap.py'
$argumentsEnvironment = 'NARRATIVE_RUN_ARGUMENTS_JSON'
$hadPreviousArguments = Test-Path "Env:$argumentsEnvironment"
$previousArguments = [Environment]::GetEnvironmentVariable(
    $argumentsEnvironment,
    [EnvironmentVariableTarget]::Process
)
$serializedArguments = ConvertTo-Json -Compress -InputObject @($RunArguments)
$pyLauncher = @(
    Get-Command py.exe `
        -CommandType Application `
        -ErrorAction SilentlyContinue
)[0]
[Environment]::SetEnvironmentVariable(
    $argumentsEnvironment,
    $serializedArguments,
    [EnvironmentVariableTarget]::Process
)

try {
    if ($env:NARRATIVE_PYTHON) {
        $python = & $env:NARRATIVE_PYTHON $bootstrap --print-python
    } elseif ($pyLauncher) {
        $python = & $pyLauncher.Source -3 $bootstrap --print-python
    } elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
        $python = & python3 $bootstrap --print-python
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        $python = & python $bootstrap --print-python
    } else {
        Write-Error 'Python 3.11+ was not found. Install Python or set NARRATIVE_PYTHON.'
        $python = $null
        $LASTEXITCODE = 1
    }
    $bootstrapExitCode = $LASTEXITCODE
    if ($bootstrapExitCode -ne 0 -or -not $python) {
        $runExitCode = if ($bootstrapExitCode) { $bootstrapExitCode } else { 1 }
    } else {
        & ($python.Trim()) $runner --arguments-env
        $runExitCode = $LASTEXITCODE
    }
} finally {
    if ($hadPreviousArguments) {
        [Environment]::SetEnvironmentVariable(
            $argumentsEnvironment,
            $previousArguments,
            [EnvironmentVariableTarget]::Process
        )
    } else {
        [Environment]::SetEnvironmentVariable(
            $argumentsEnvironment,
            $null,
            [EnvironmentVariableTarget]::Process
        )
    }
}
exit $runExitCode
