param(
    [switch]$Force,
    [switch]$WhatIf
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "release-paths.ps1")
. (Join-Path $PSScriptRoot "test-release-notes-ready.ps1")

$repoRoot = (git rev-parse --show-toplevel).Trim()
$taggedVersions = @{}
foreach ($tag in (git -C $repoRoot tag -l "v*" 2>$null)) {
    $taggedVersions[$tag.Trim()] = $true
}

$toRemove = @()
foreach ($dir in (Get-AllReleaseVersionDirs -RepoRoot $repoRoot)) {
    $version = $dir.Name
    if ($taggedVersions.ContainsKey($version)) {
        continue
    }

    $status = Test-ReleaseFolderScaffold -VersionDir $dir.FullName -RepoRoot $repoRoot
    if ($status.IsScaffold) {
        $toRemove += $dir
    }
}

if ($toRemove.Count -eq 0) {
    Write-Host "prune-scaffold-releases: no scaffold folders to remove."
    exit 0
}

Write-Host "prune-scaffold-releases: found $($toRemove.Count) scaffold folder(s):"
foreach ($dir in $toRemove) {
    Write-Host "  $($dir.FullName.Substring($repoRoot.Length + 1))"
}

if (-not $Force) {
    Write-Host "prune-scaffold-releases: dry run (pass -Force to delete)."
    exit 0
}

if ($WhatIf) {
    exit 0
}

foreach ($dir in $toRemove) {
    Remove-Item -Path $dir.FullName -Recurse -Force
    Write-Host "prune-scaffold-releases: removed $($dir.Name)"
}

Write-Host "prune-scaffold-releases: done."
