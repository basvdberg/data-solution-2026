param(
    [string]$PublishedVersion = "",
    [switch]$WhatIf,
    [switch]$SkipStage
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "release-paths.ps1")
. (Join-Path $PSScriptRoot "release-notes-stub.ps1")

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

$repoRoot = (git rev-parse --show-toplevel).Trim()
$versionFile = Join-Path $repoRoot "release\VERSION"

if (-not (Test-Path $versionFile)) {
    throw "Missing version file: $versionFile"
}

$current = Normalize-ReleaseVersion ((Get-Content -Path $versionFile -Raw).Trim())
if (-not [string]::IsNullOrWhiteSpace($PublishedVersion)) {
    $published = Normalize-ReleaseVersion $PublishedVersion
    if ($published -ne $current) {
        Write-Host "close-release: VERSION is $current; published was $published (continuing)."
    }
}

$next = Get-NextVersion -Current $current
$notesPath = Get-ReleaseNotesPath -Version $next -RepoRoot $repoRoot

if (Test-Path $notesPath) {
    Write-Host "close-release: $next already exists; skipping bump."
    exit 0
}

Write-Host "close-release: opening next release $current -> $next"

if ($WhatIf) {
    exit 0
}

$releaseDir = Get-ReleaseVersionDir -Version $next -RepoRoot $repoRoot
New-Item -ItemType Directory -Path $releaseDir -Force | Out-Null
Set-Content -Path $versionFile -Value "$next`n" -Encoding UTF8

$stub = New-MinimalReleaseNotes -Version $next -PreviousTag $current
Set-Content -Path $notesPath -Value $stub.TrimEnd() -Encoding UTF8

if (-not $SkipStage) {
    $relVersion = "release/VERSION"
    $relNotes = $notesPath.Substring($repoRoot.Length + 1) -replace '\\', '/'
    git -C $repoRoot add $relVersion $relNotes 2>$null | Out-Null
}

Write-Host "close-release: prepared $next (edit notes.md before next publish)."
