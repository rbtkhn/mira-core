[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string] $Repository,
    [switch] $RemoveStale
)

# Functions are separated for isolated PowerShell tests; no public bypass flags.
function Resolve-LockTarget([string] $Root) {
    if (-not [IO.Path]::IsPathRooted($Root)) { throw 'Repository must be absolute' }
    $resolvedGitDir = & git -C $Root rev-parse --path-format=absolute --git-dir
    $gitExit = $LASTEXITCODE
    if ($gitExit -ne 0) { throw 'Cannot resolve Git directory' }
    $gitDir = [IO.Path]::GetFullPath(($resolvedGitDir -join '').Trim())
    return [IO.Path]::GetFullPath((Join-Path $gitDir 'index.lock'))
}
function Get-LockOwners {
    @(Get-CimInstance Win32_Process -ErrorAction Stop | Where-Object {
        $_.Name -in @('git.exe', 'git-lfs.exe')
    })
}
function Read-LockMetadata([string] $Path) {
    $item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
    if ($item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
        throw 'Lock must be a regular file'
    }
    return "$($item.Length):$($item.LastWriteTimeUtc.Ticks)"
}
function Wait-LockStability { Start-Sleep -Seconds 2 }
function Assert-ExclusiveLock([string] $Path) {
    $handle = [IO.File]::Open($Path, [IO.FileMode]::Open,
        [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
    $handle.Dispose()
}
function Invoke-IndexLock([string] $Root, [bool] $Remove) {
    $target = Resolve-LockTarget $Root
    if (-not (Test-Path -LiteralPath $target)) {
        return @{status='absent'; path=$target; removed=$false}
    }
    if (@(Get-LockOwners).Count -ne 0) { throw 'Git or Git LFS process is active' }
    $before = Read-LockMetadata $target
    Wait-LockStability
    if ((Read-LockMetadata $target) -ne $before) { throw 'Lock changed during observation' }
    Assert-ExclusiveLock $target
    if ((Resolve-LockTarget $Root) -cne $target) { throw 'Resolved Git lock path changed' }
    if (@(Get-LockOwners).Count -ne 0) { throw 'Git or Git LFS process became active' }
    if ((Read-LockMetadata $target) -ne $before) { throw 'Lock changed before removal' }
    if ($Remove) { Remove-Item -LiteralPath $target -ErrorAction Stop }
    return @{status=$(if ($Remove) {'removed'} else {'stale-candidate'}); path=$target; removed=$Remove}
}

if ($MyInvocation.InvocationName -ne '.') {
    try {
        Invoke-IndexLock $Repository ([bool]$RemoveStale) | ConvertTo-Json -Compress
        exit 0
    } catch {
        @{status='blocked'; removed=$false; error=$_.Exception.Message} | ConvertTo-Json -Compress
        exit 1
    }
}
