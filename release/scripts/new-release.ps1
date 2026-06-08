param(
    [switch]$WhatIf
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "release-paths.ps1")

function Get-NextVersion {
    param([string]$Current)
    if ($Current -notmatch '^v?(\d{4})\.(\d{2})\.(\d{2})\.(\d+)$') {
        throw "release/VERSION has invalid format (expected vYYYY.MM.DD.N): $Current"
    }
    $year = [int]$Matches[1]
    $month = [int]$Matches[2]
    $day = [int]$Matches[3]
    $increment = [int]$Matches[4]
    $today = Get-Date
    if ($year -eq $today.Year -and $month -eq $today.Month -and $day -eq $today.Day) {
        return "v{0:D4}.{1:D2}.{2:D2}.{3}" -f $year, $month, $day, ($increment + 1)
    }
    return "v{0:D4}.{1:D2}.{2:D2}.1" -f $today.Year, $today.Month, $today.Day
}

function Get-PreviousVersionLabel {
    param([string]$Current)
    if ($Current -match '^v?(\d{4})\.(\d{2})\.(\d{2})\.(\d+)$') {
        $increment = [int]$Matches[4]
        if ($increment -gt 1) {
            return "v$($Matches[1]).$($Matches[2]).$($Matches[3]).$($increment - 1)"
        }
    }
    $tags = git tag -l "v*" --sort=-version:refname 2>$null
    if ($tags -and $tags.Count -gt 0) {
        $latest = $tags | Select-Object -First 1
        if ($latest -ne $Current) {
            return $latest
        }
        if ($tags.Count -gt 1) {
            return $tags[1]
        }
    }
    return "<previous-tag>"
}

$repoRoot = (git rev-parse --show-toplevel).Trim()
$versionFile = Join-Path $repoRoot "release\VERSION"
$templateFile = Join-Path $repoRoot "release\release-notes-template.md"

if (-not (Test-Path $versionFile)) {
    throw "Missing version file: $versionFile"
}
if (-not (Test-Path $templateFile)) {
    throw "Missing template: $templateFile"
}

$current = (Get-Content -Path $versionFile -Raw).Trim()
if ([string]::IsNullOrWhiteSpace($current)) {
    throw "release/VERSION is empty."
}
$current = Normalize-ReleaseVersion $current

$next = Get-NextVersion -Current $current
$previous = Get-PreviousVersionLabel -Current $current
$date = (Get-Date).ToString("yyyy-MM-dd")

$releaseDir = Get-ReleaseVersionDir -Version $next -RepoRoot $repoRoot
$notesPath = Get-ReleaseNotesPath -Version $next -RepoRoot $repoRoot
$detailsReadme = Get-ReleaseDetailsReadmePath -Version $next -RepoRoot $repoRoot
$detailsPrompts = Get-ReleasePromptsPath -Version $next -RepoRoot $repoRoot
$retroTemplate = Join-Path $repoRoot "release\retrospective-template.md"
$retroPath = Get-ReleaseRetrospectivePath -Version $next -RepoRoot $repoRoot

if (Test-Path $notesPath) {
    Write-Host "new-release: $next already has release notes; skipping bump."
    exit 0
}

Write-Host "new-release: bumping $current -> $next"

if ($WhatIf) {
    exit 0
}

$template = Get-Content -Path $templateFile -Raw
$notes = $template `
    -replace '<version>', $next `
    -replace '<YYYY-MM-DD>', $date `
    -replace '<sha>', '<fill-after-commit>' `
    -replace '<tag>', $previous

New-Item -ItemType Directory -Path $releaseDir -Force | Out-Null
Set-Content -Path $versionFile -Value "$next`n" -Encoding UTF8
Set-Content -Path $notesPath -Value $notes.TrimEnd() -Encoding UTF8

if (-not (Test-Path $detailsReadme)) {
    $readme = @"
# Release $next - Details

## Release metadata

- Version: ``$next``
- Development start: ``$((Get-Date).ToString("yyyy-MM-ddTHH:mm:ssK"))``
- Development end: ``$((Get-Date).ToString("yyyy-MM-ddTHH:mm:ssK"))``
- Release branch: ``main``
- Release commit: ``<fill-after-commit>``

## Summary

- Update scope and changes in ``notes.md`` in this folder.

## Linked files

- Release note: [``notes.md``](notes.md)
- Retrospective: [``retrospective.md``](retrospective.md)
- Incident register: [``doc/operation/incident/``](../../../doc/operation/incident/readme.md)

"@
    Set-Content -Path $detailsReadme -Value $readme.TrimEnd() -Encoding UTF8
}

if (-not (Test-Path $detailsPrompts)) {
    Set-Content -Path $detailsPrompts -Value "# Prompts for $next`r`n" -Encoding UTF8
}

if (-not (Test-Path $retroPath)) {
    if (Test-Path $retroTemplate) {
        $retro = (Get-Content -Path $retroTemplate -Raw) `
            -replace '<version>', $next `
            -replace '<YYYY-MM-DD>', $date `
            -replace '<sha>', '<fill-after-commit>'
        Set-Content -Path $retroPath -Value $retro.TrimEnd() -Encoding UTF8
    } else {
        Set-Content -Path $retroPath -Value "# Retrospective — $next`r`n" -Encoding UTF8
    }
}

function Get-RepoRelativePath {
    param([string]$AbsolutePath, [string]$Root)
    return $AbsolutePath.Substring($Root.Length + 1) -replace '\\', '/'
}

$gitAddPaths = @(
    "release/VERSION",
    (Get-RepoRelativePath (Get-ReleaseNotesPath -Version $next -RepoRoot $repoRoot) $repoRoot),
    (Get-RepoRelativePath (Get-ReleaseDetailsReadmePath -Version $next -RepoRoot $repoRoot) $repoRoot),
    (Get-RepoRelativePath (Get-ReleasePromptsPath -Version $next -RepoRoot $repoRoot) $repoRoot),
    (Get-RepoRelativePath (Get-ReleaseRetrospectivePath -Version $next -RepoRoot $repoRoot) $repoRoot)
)
foreach ($path in $gitAddPaths) {
    git -C $repoRoot add $path 2>$null | Out-Null
}

Write-Host "new-release: prepared $next (edit notes.md under $releaseDir before push)."
