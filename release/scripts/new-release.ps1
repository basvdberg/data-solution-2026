param(
    [switch]$WhatIf
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

$current = (Get-Content -Path $versionFile -Raw).Trim()
if ([string]::IsNullOrWhiteSpace($current)) {
    throw "release/VERSION is empty."
}
$current = Normalize-ReleaseVersion $current

$next = Get-NextVersion -Current $current
$date = (Get-Date).ToString("yyyy-MM-dd")

$releaseDir = Get-ReleaseVersionDir -Version $next -RepoRoot $repoRoot
$notesPath = Get-ReleaseNotesPath -Version $next -RepoRoot $repoRoot

if (Test-Path $notesPath) {
    Write-Host "new-release: $next already has release notes; skipping bump."
    exit 0
}

Write-Host "new-release: bumping $current -> $next"

if ($WhatIf) {
    exit 0
}

New-Item -ItemType Directory -Path $releaseDir -Force | Out-Null
Set-Content -Path $versionFile -Value "$next`n" -Encoding UTF8

$stub = New-MinimalReleaseNotes -Version $next -Date $date -PreviousTag $current
Set-Content -Path $notesPath -Value $stub.TrimEnd() -Encoding UTF8

function Get-RepoRelativePath {
    param([string]$AbsolutePath, [string]$Root)
    return $AbsolutePath.Substring($Root.Length + 1) -replace '\\', '/'
}

$gitAddPaths = @(
    "release/VERSION",
    (Get-RepoRelativePath $notesPath $repoRoot)
)
foreach ($path in $gitAddPaths) {
    git -C $repoRoot add $path 2>$null | Out-Null
}

Write-Host "new-release: prepared $next (edit notes.md under $releaseDir before push)."
