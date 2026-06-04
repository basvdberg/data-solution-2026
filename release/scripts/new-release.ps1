param(
    [switch]$WhatIf
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

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
if ($current -notmatch '^v') {
    $current = "v$current"
}

$next = Get-NextVersion -Current $current
$previous = Get-PreviousVersionLabel -Current $current
$date = (Get-Date).ToString("yyyy-MM-dd")

$notesPath = Join-Path $repoRoot "release\notes\$next.md"
$detailsDir = Join-Path $repoRoot "release\details\$next"
$detailsReadme = Join-Path $detailsDir "README.md"
$detailsPrompts = Join-Path $detailsDir "prompts.md"

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

New-Item -ItemType Directory -Path $detailsDir -Force | Out-Null
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

- Update scope and changes in ``release/notes/$next.md``.

## Linked files

- Release note: [``release/notes/$next.md``](../../notes/$next.md)

"@
    Set-Content -Path $detailsReadme -Value $readme.TrimEnd() -Encoding UTF8
}

if (-not (Test-Path $detailsPrompts)) {
    Set-Content -Path $detailsPrompts -Value "# Prompts for $next`r`n" -Encoding UTF8
}

git -C $repoRoot add "release/VERSION" "release/notes/$next.md" "release/details/$next/README.md" "release/details/$next/prompts.md" 2>$null | Out-Null

$detailsIndex = Join-Path $repoRoot "release\details\README.md"
if (Test-Path $detailsIndex) {
    $link = "- [`$next`]($next/README.md)"
    $indexContent = Get-Content -Path $detailsIndex -Raw
    if (-not $indexContent.Contains($link)) {
        Add-Content -Path $detailsIndex -Value "`r`n$link"
        git -C $repoRoot add "release/details/README.md" 2>$null | Out-Null
    }
}

Write-Host "new-release: prepared $next (edit release/notes/$next.md before push)."
