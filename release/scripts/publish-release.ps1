param(
    [string]$CommitSha = "",
    [switch]$SkipTagPush,
    [switch]$WhatIf
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "release-paths.ps1")

function Test-CommandExists {
    param([string]$Name)
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Get-VersionAtCommit {
    param(
        [string]$Sha,
        [string]$RepoRoot
    )
    $spec = "${Sha}:release/VERSION"
    $version = (git -C $RepoRoot show $spec 2>$null)
    if (-not $version) {
        return $null
    }
    $version = $version.Trim()
    if ([string]::IsNullOrWhiteSpace($version)) {
        return $null
    }
    return (Normalize-ReleaseVersion $version)
}

function Test-TagExists {
    param(
        [string]$Version,
        [string]$RepoRoot
    )
    git -C $RepoRoot rev-parse --verify "refs/tags/$Version" 2>$null | Out-Null
    return $LASTEXITCODE -eq 0
}

function Test-GitHubReleaseExists {
    param([string]$Version)
    if (-not (Test-CommandExists "gh")) {
        return $false
    }
    gh release view $Version 2>$null | Out-Null
    return $LASTEXITCODE -eq 0
}

$repoRoot = (git rev-parse --show-toplevel).Trim()
if ([string]::IsNullOrWhiteSpace($CommitSha)) {
    $CommitSha = (git -C $repoRoot rev-parse HEAD).Trim()
}

$version = Get-VersionAtCommit -Sha $CommitSha -RepoRoot $repoRoot
if (-not $version) {
    Write-Host "publish-release: no release/VERSION at $CommitSha; skipping."
    exit 0
}

$notesPath = Get-ReleaseNotesPath -Version $version -RepoRoot $repoRoot
if (-not (Test-Path $notesPath)) {
    Write-Host "publish-release: missing $notesPath; skipping GitHub release."
    exit 0
}

Write-Host "publish-release: version $version at $CommitSha"

if ($WhatIf) {
    exit 0
}

if (-not (Test-TagExists -Version $version -RepoRoot $repoRoot)) {
    git -C $repoRoot tag -a $version $CommitSha -m "Release $version"
    Write-Host "publish-release: created tag $version"
} else {
    Write-Host "publish-release: tag $version already exists"
}

if (-not $SkipTagPush) {
    git -C $repoRoot push origin "refs/tags/$version" 2>&1 | Out-Host
    if ($LASTEXITCODE -ne 0) {
        Write-Host "publish-release: tag push failed (tag may already exist on remote)."
    } else {
        Write-Host "publish-release: pushed tag $version"
    }
}

if (-not (Test-CommandExists "gh")) {
    Write-Host "publish-release: gh CLI not found; skipping GitHub release."
    exit 0
}

if (Test-GitHubReleaseExists -Version $version) {
    Write-Host "publish-release: GitHub release $version already exists"
    exit 0
}

gh release create $version `
    --target $CommitSha `
    --title "Release $version" `
    --notes-file $notesPath

Write-Host "publish-release: created GitHub release $version"
