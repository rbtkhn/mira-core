function Resolve-MiraCoreEnvironment {
    param(
        [Parameter(Mandatory = $true)][string] $Canonical,
        [string] $Legacy
    )

    $current = [Environment]::GetEnvironmentVariable($Canonical, 'Process')
    if ([string]::IsNullOrEmpty($current)) { $current = $null }
    if ($null -ne $current) {
        return $current
    }
    return $null
}
