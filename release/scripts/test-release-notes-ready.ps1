Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$PlaceholderScope = "Brief description of what is included in this release."
$PlaceholderCommit = "<fill-after-commit>"
$ChangeSectionNames = @("Added", "Changed", "Deprecated", "Removed", "Fixed", "Security")

function Test-ReleaseNotesReady {
    param(
        [Parameter(Mandatory = $true)]
        [string]$NotesPath
    )

    if (-not (Test-Path $NotesPath)) {
        return $false
    }

    $content = Get-Content -Path $NotesPath -Raw
    if ([string]::IsNullOrWhiteSpace($content)) {
        return $false
    }

    if ($content -match [regex]::Escape($PlaceholderCommit)) {
        return $false
    }

    if (-not (Test-ReleaseNotesScopeReady -Content $content)) {
        return $false
    }

    if (-not (Test-ReleaseNotesHasChangeBullet -Content $content)) {
        return $false
    }

    return $true
}

function Test-ReleaseNotesScopeReady {
    param([string]$Content)

    if ($Content -notmatch '(?ms)^## Scope\s*\r?\n+(.*?)(?=^## |\z)') {
        return $false
    }

    $scopeBody = $Matches[1].Trim()
    if ([string]::IsNullOrWhiteSpace($scopeBody)) {
        return $false
    }

    $scopeLines = @(
        $scopeBody -split '\r?\n' |
            ForEach-Object { $_.Trim() } |
            Where-Object { $_ -ne "" -and $_ -ne "-" }
    )

    if ($scopeLines.Count -eq 0) {
        return $false
    }

    foreach ($line in $scopeLines) {
        if ($line -eq $PlaceholderScope) {
            return $false
        }
    }

    return $true
}

function Test-ReleaseNotesHasChangeBullet {
    param([string]$Content)

    if ($Content -match '(?ms)^## Changes\s*\r?\n+(.*?)(?=^## |\z)') {
        foreach ($line in ($Matches[1] -split '\r?\n')) {
            $trimmed = $line.Trim()
            if ($trimmed -match '^-\s+\S') {
                return $true
            }
        }
    }

    foreach ($section in $ChangeSectionNames) {
        $pattern = "(?ms)^### $section\s*\r?\n+(.*?)(?=^### |^## |\z)"
        if ($Content -notmatch $pattern) {
            continue
        }

        $body = $Matches[1]
        foreach ($line in ($body -split '\r?\n')) {
            $trimmed = $line.Trim()
            if ($trimmed -match '^-\s+\S') {
                return $true
            }
        }
    }

    return $false
}

function Test-ReleaseRetrospectiveScaffold {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RetrospectivePath
    )

    if (-not (Test-Path $RetrospectivePath)) {
        return $false
    }

    $content = Get-Content -Path $RetrospectivePath -Raw
    return $content -match 'pass / fail / partial'
}

function Test-ReleaseNotesScaffold {
    param(
        [Parameter(Mandatory = $true)]
        [string]$NotesPath
    )

    if (-not (Test-Path $NotesPath)) {
        return $true
    }

    $content = Get-Content -Path $NotesPath -Raw
    if ([string]::IsNullOrWhiteSpace($content)) {
        return $true
    }

    if (-not (Test-ReleaseNotesScopeReady -Content $content)) {
        return $true
    }

    return -not (Test-ReleaseNotesHasChangeBullet -Content $content)
}

function Test-ReleaseFolderScaffold {
    param(
        [Parameter(Mandatory = $true)]
        [string]$VersionDir,
        [string]$RepoRoot
    )

    $versionName = Split-Path $VersionDir -Leaf
    $notesPath = Join-Path $VersionDir "notes.md"
    $retroPath = Join-Path $VersionDir "retrospective.md"

    $notesScaffold = Test-ReleaseNotesScaffold -NotesPath $notesPath
    $retroScaffold = $false
    if (Test-Path $retroPath) {
        $retroScaffold = Test-ReleaseRetrospectiveScaffold -RetrospectivePath $retroPath
    }

    return @{
        Version = $versionName
        NotesScaffold = $notesScaffold
        RetroScaffold = $retroScaffold
        IsScaffold = $notesScaffold -and (-not (Test-Path $retroPath) -or $retroScaffold)
    }
}
