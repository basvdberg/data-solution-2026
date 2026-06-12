param(
    [switch]$WhatIf
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "release-paths.ps1")
. (Join-Path $PSScriptRoot "release-notes-stub.ps1")

$repoRoot = (git rev-parse --show-toplevel).Trim()
$versionFile = Join-Path $repoRoot "release\VERSION"

if (-not (Test-Path $versionFile)) {
    Write-Host "ensure-open-release: missing release/VERSION; skipping."
    exit 0
}

$version = Normalize-ReleaseVersion ((Get-Content -Path $versionFile -Raw).Trim())
$notesPath = Get-ReleaseNotesPath -Version $version -RepoRoot $repoRoot

if (Test-Path $notesPath) {
    Write-Host "ensure-open-release: $version already has notes.md."
    exit 0
}

$releaseDir = Get-ReleaseVersionDir -Version $version -RepoRoot $repoRoot
Write-Host "ensure-open-release: creating minimal notes for $version"

if ($WhatIf) {
    exit 0
}

New-Item -ItemType Directory -Path $releaseDir -Force | Out-Null
$stub = New-MinimalReleaseNotes -Version $version
Set-Content -Path $notesPath -Value $stub.TrimEnd() -Encoding UTF8

$relNotes = $notesPath.Substring($repoRoot.Length + 1) -replace '\\', '/'
git -C $repoRoot add $relNotes 2>$null | Out-Null

Write-Host "ensure-open-release: prepared $notesPath"
