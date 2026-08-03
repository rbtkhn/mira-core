[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $PythonArguments
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$bootstrap = Join-Path $PSScriptRoot 'runtime_bootstrap.py'
$pyLauncher = @(
    Get-Command py.exe `
        -CommandType Application `
        -ErrorAction SilentlyContinue
)[0]
[Console]::Error.WriteLine(
    'DEPRECATED: scripts/python.ps1 is a compatibility shim; use tools/run.ps1 or tools/validate.ps1.'
)

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
    exit 1
}
if ($LASTEXITCODE -ne 0 -or -not $python) {
    exit 1
}

& ($python.Trim()) @PythonArguments
exit $LASTEXITCODE
