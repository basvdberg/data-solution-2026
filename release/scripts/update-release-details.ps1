param(
    [switch]$Refresh
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "release-paths.ps1")

function Format-MetadataValue {
    param([string]$Value)
    if ($Value -match '^`.*`$') {
        return $Value
    }
    return "``$Value``"
}

function Set-MetadataLine {
    param(
        [string]$Content,
        [string]$Key,
        [string]$Value
    )
    $formatted = Format-MetadataValue $Value
    $pattern = "(?m)^- ${Key}:.*$"
    $line = "- ${Key}: $formatted"
    if ($Content -match $pattern) {
        return [regex]::Replace($Content, $pattern, $line, 1)
    }

    $metadataHeader = "## Release metadata"
    if ($Content -match "(?m)^## Release metadata\s*$") {
        return [regex]::Replace(
            $Content,
            "(?m)^(## Release metadata\s*)$",
            "`$1`r`n$line",
            1
        )
    }
    return $Content + "`r`n$line`r`n"
}

function Update-ReleaseReadmeMetadata {
    param(
        [string]$ReadmePath,
        [string]$Version
    )

    $commitSha = (git rev-parse HEAD).Trim()
    $branch = (git rev-parse --abbrev-ref HEAD).Trim()
    $now = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssK")

    if (-not (Test-Path $ReadmePath)) {
        $readme = @"
# Release $Version - Details

## Release metadata

- Version: $(Format-MetadataValue $Version)
- Development start: $(Format-MetadataValue $now)
- Development end: $(Format-MetadataValue $now)
- Release branch: $(Format-MetadataValue $branch)
- Release commit: $(Format-MetadataValue $commitSha)

## Sequential summary of applied changes

1. Update this section with the ordered change list for this release.

"@
        Set-Content -Path $ReadmePath -Value $readme -Encoding UTF8
        return
    }

    $content = Get-Content -Path $ReadmePath -Raw

    if ($content -notmatch '(?m)^- Version:') {
        $content = Set-MetadataLine $content "Version" $Version
    }
    if ($content -notmatch '(?m)^- Development start:') {
        $content = Set-MetadataLine $content "Development start" $now
    }

    $content = Set-MetadataLine $content "Development end" $now
    $content = Set-MetadataLine $content "Release branch" $branch
    $content = Set-MetadataLine $content "Release commit" $commitSha

    Set-Content -Path $ReadmePath -Value $content.TrimEnd() -Encoding UTF8
}

$repoRoot = (git rev-parse --show-toplevel).Trim()
$versionFile = Join-Path $repoRoot "release\VERSION"

if (-not (Test-Path $versionFile)) {
    throw "Missing version file: $versionFile"
}

$version = Normalize-ReleaseVersion (Get-Content -Path $versionFile -Raw).Trim()

$releaseDir = Get-ReleaseVersionDir -Version $version -RepoRoot $repoRoot
New-Item -ItemType Directory -Path $releaseDir -Force | Out-Null

$readmePath = Get-ReleaseDetailsReadmePath -Version $version -RepoRoot $repoRoot

if ($Refresh) {
    Update-ReleaseReadmeMetadata -ReadmePath $readmePath -Version $version
} elseif (-not (Test-Path $readmePath)) {
    Update-ReleaseReadmeMetadata -ReadmePath $readmePath -Version $version
}

if ($Refresh) {
    Write-Host "Release details refreshed for $version"
} else {
    Write-Host "Release details synced for $version"
}
