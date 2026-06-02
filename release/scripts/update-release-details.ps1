Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (git rev-parse --show-toplevel).Trim()
$versionFile = Join-Path $repoRoot "release\VERSION"
$detailsRoot = Join-Path $repoRoot "release\details"

if (-not (Test-Path $versionFile)) {
    throw "Missing version file: $versionFile"
}

$version = (Get-Content -Path $versionFile -Raw).Trim()
if ([string]::IsNullOrWhiteSpace($version)) {
    throw "release/VERSION is empty."
}

$releaseDir = Join-Path $detailsRoot $version
New-Item -ItemType Directory -Path $releaseDir -Force | Out-Null

$readmePath = Join-Path $releaseDir "README.md"
$promptsPath = Join-Path $releaseDir "prompts.md"

if (-not (Test-Path $readmePath)) {
    $commitSha = (git rev-parse HEAD).Trim()
    $now = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssK")
    $readme = @"
# Release $version - Details

## Release metadata

- Version: $version
- Development start: $now
- Development end: $now
- Release branch: main
- Release commit: $commitSha

## Sequential summary of applied changes

1. Update this section with the ordered change list for this release.

## Linked files

- Prompts for this release: [`prompts.md`](prompts.md)
"@
    Set-Content -Path $readmePath -Value $readme -Encoding UTF8
}

if (-not (Test-Path $promptsPath)) {
    $prompts = @"
# Prompts used in $version

1. Add release prompts here.
"@
    Set-Content -Path $promptsPath -Value $prompts -Encoding UTF8
}

$rootReadme = Join-Path $detailsRoot "README.md"
if (Test-Path $rootReadme) {
    $content = Get-Content -Path $rootReadme -Raw
    $link = "- [`$version`]($version/README.md)"
    if (-not $content.Contains($link)) {
        Add-Content -Path $rootReadme -Value "`r`n$link"
    }
}

Write-Host "Release details synced for $version"
