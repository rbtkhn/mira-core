if ($null -eq $script:MiraCoreLegacyWarnings) {
    $script:MiraCoreLegacyWarnings = @{}
}

function Resolve-MiraCoreEnvironment {
    param(
        [Parameter(Mandatory = $true)][string] $Canonical,
        [Parameter(Mandatory = $true)][string] $Legacy
    )

    $current = [Environment]::GetEnvironmentVariable($Canonical, 'Process')
    $old = [Environment]::GetEnvironmentVariable($Legacy, 'Process')
    if ([string]::IsNullOrEmpty($current)) { $current = $null }
    if ([string]::IsNullOrEmpty($old)) { $old = $null }
    if ($null -ne $current -and $null -ne $old -and $current -ne $old) {
        throw "Conflicting environment variables: $Canonical and $Legacy"
    }
    if ($null -ne $current) {
        return $current
    }
    if ($null -ne $old) {
        if (-not $script:MiraCoreLegacyWarnings.ContainsKey($Legacy)) {
            Write-Warning "$Legacy is deprecated; use $Canonical"
            $script:MiraCoreLegacyWarnings[$Legacy] = $true
        }
        return $old
    }
    return $null
}
