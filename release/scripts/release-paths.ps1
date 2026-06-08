Set-StrictMode -Version Latest

function Normalize-ReleaseVersion {
    param([string]$Version)
    $v = $Version.Trim()
    if ([string]::IsNullOrWhiteSpace($v)) {
        throw "Release version is empty."
    }
    if ($v -notmatch '^v') {
        $v = "v$v"
    }
    if ($v -notmatch '^v(\d{4})\.(\d{2})\.(\d{2})\.(\d+)$') {
        throw "Invalid release version (expected vYYYY.MM.DD.N): $Version"
    }
    return $v
}

function Get-ReleaseVersionDir {
    param(
        [string]$Version,
        [string]$RepoRoot
    )
    $v = Normalize-ReleaseVersion $Version
    if ($v -match '^v(\d{4})\.(\d{2})\.(\d{2})\.(\d+)$') {
        return Join-Path $RepoRoot "release\$($Matches[1])\$($Matches[2])\$($Matches[3])\$v"
    }
    throw "Invalid release version: $Version"
}

function Get-ReleaseNotesPath {
    param([string]$Version, [string]$RepoRoot)
    return Join-Path (Get-ReleaseVersionDir -Version $Version -RepoRoot $RepoRoot) "notes.md"
}

function Get-ReleaseDetailsReadmePath {
    param([string]$Version, [string]$RepoRoot)
    return Join-Path (Get-ReleaseVersionDir -Version $Version -RepoRoot $RepoRoot) "readme.md"
}

function Get-ReleasePromptsPath {
    param([string]$Version, [string]$RepoRoot)
    return Join-Path (Get-ReleaseVersionDir -Version $Version -RepoRoot $RepoRoot) "prompts.md"
}

function Get-ReleaseRetrospectivePath {
    param([string]$Version, [string]$RepoRoot)
    return Join-Path (Get-ReleaseVersionDir -Version $Version -RepoRoot $RepoRoot) "retrospective.md"
}

function Get-AllReleaseVersionDirs {
    param([string]$RepoRoot)
    $releaseRoot = Join-Path $RepoRoot "release"
    if (-not (Test-Path $releaseRoot)) {
        return @()
    }
    return Get-ChildItem -Path $releaseRoot -Recurse -Directory |
        Where-Object { $_.Name -match '^v\d{4}\.\d{2}\.\d{2}\.\d+$' } |
        Sort-Object FullName
}
