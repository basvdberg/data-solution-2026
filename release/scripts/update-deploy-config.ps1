param(
    [switch]$WhatIf
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Meaningful infra = files that deploy-infra-on-nas.sh syncs to legacy NAS paths.
# Docs (readme.md) and local-server.env.example do not affect runtime stacks.
$meaningfulPatterns = @(
    '^infra/airflow/.*\.(yaml|yml)$'
    '^infra/airflow/\.env\.example$'
    '^infra/kafka/.*\.(yaml|yml)$'
    '^infra/kafka/\.env\.example$'
    '^infra/postgres/.*\.(yaml|yml|sql|sh)$'
    '^infra/postgres/\.env\.example$'
    '^infra/scripts/(deploy-infra-on-nas|nas-remote-env)\.sh$'
)

function Test-MeaningfulInfraPath {
    param([string]$Path)
    $normalized = ($Path -replace '\\', '/').Trim()
    if ([string]::IsNullOrWhiteSpace($normalized)) {
        return $false
    }
    foreach ($pattern in $meaningfulPatterns) {
        if ($normalized -match $pattern) {
            return $true
        }
    }
    return $false
}

function Get-LatestVersionTag {
    $tags = git tag -l "v*" --sort=-version:refname 2>$null
    if (-not $tags) {
        return $null
    }
    return ($tags | Select-Object -First 1).Trim()
}

function Get-ChangedPathsSinceTag {
    param([string]$Tag)
    if ([string]::IsNullOrWhiteSpace($Tag)) {
        return @()
    }
    $output = git diff --name-only "${Tag}..HEAD" 2>$null
    if (-not $output) {
        return @()
    }
    return @($output | ForEach-Object { $_.Trim() } | Where-Object { $_ })
}

function Get-StagedPaths {
    $output = git diff --cached --name-only 2>$null
    if (-not $output) {
        return @()
    }
    return @($output | ForEach-Object { $_.Trim() } | Where-Object { $_ })
}

$repoRoot = (git rev-parse --show-toplevel).Trim()
$configPath = Join-Path $repoRoot "release\deploy-config.json"
$versionFile = Join-Path $repoRoot "release\VERSION"

if (-not (Test-Path $versionFile)) {
    Write-Host "update-deploy-config: release/VERSION not found; skipping."
    exit 0
}

$version = (Get-Content -Path $versionFile -Raw).Trim()
if ($version -notmatch '^v') {
    $version = "v$version"
}

$sinceTag = Get-LatestVersionTag
$pathsSinceTag = Get-ChangedPathsSinceTag -Tag $sinceTag
$stagedPaths = Get-StagedPaths
$allPaths = @($pathsSinceTag + $stagedPaths | Sort-Object -Unique)

$meaningfulPaths = @($allPaths | Where-Object { Test-MeaningfulInfraPath $_ } | Sort-Object -Unique)
$syncInfra = $meaningfulPaths.Count -gt 0

if ($syncInfra) {
    $tagLabel = if ($sinceTag) { $sinceTag } else { "none" }
    $reason = "Meaningful infra runtime file(s) changed since tag ${tagLabel}: $($meaningfulPaths -join ', ')"
} else {
    $reason = if ($sinceTag) {
        "No meaningful infra runtime changes since tag $sinceTag."
    } else {
        "No meaningful infra runtime changes in this commit window."
    }
}

$config = [ordered]@{
    sync_infra = $syncInfra
    paths      = $meaningfulPaths
    reason     = $reason
    version    = $version
    since_tag  = $sinceTag
    updated_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
}

$json = ($config | ConvertTo-Json -Depth 4)

if ($WhatIf) {
    Write-Host $json
    exit 0
}

Set-Content -Path $configPath -Value $json -Encoding UTF8 -NoNewline
Add-Content -Path $configPath -Value "" -Encoding UTF8

git -C $repoRoot add "release/deploy-config.json" 2>$null | Out-Null

Write-Host "update-deploy-config: sync_infra=$syncInfra ($($meaningfulPaths.Count) path(s))"
