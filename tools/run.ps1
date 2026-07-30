[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $RunArguments
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$runner = Join-Path $repoRoot 'tools\run_repo.py'
$argumentsEnvironment = 'NARRATIVE_RUN_ARGUMENTS_JSON'
$hadPreviousArguments = Test-Path "Env:$argumentsEnvironment"
$previousArguments = [Environment]::GetEnvironmentVariable(
    $argumentsEnvironment,
    [EnvironmentVariableTarget]::Process
)
$serializedArguments = ConvertTo-Json -Compress -InputObject @($RunArguments)
[Environment]::SetEnvironmentVariable(
    $argumentsEnvironment,
    $serializedArguments,
    [EnvironmentVariableTarget]::Process
)

try {
    if ($env:NARRATIVE_PYTHON) {
        & $env:NARRATIVE_PYTHON $runner --arguments-env
    } elseif (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3 $runner --arguments-env
    } elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
        & python3 $runner --arguments-env
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        & python $runner --arguments-env
    } else {
        Write-Error 'Python 3.11+ was not found. Install Python or set NARRATIVE_PYTHON.'
        exit 1
    }
    $runExitCode = $LASTEXITCODE
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
