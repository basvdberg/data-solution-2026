Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function New-MinimalReleaseNotes {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Version,
        [string]$Date = "",
        [string]$PreviousTag = "<previous-tag>"
    )

    if ([string]::IsNullOrWhiteSpace($Date)) {
        $Date = (Get-Date).ToString("yyyy-MM-dd")
    }

    return @"
# Release $Version

Operator-facing release notes. Published to GitHub Releases via ``publish-release.ps1``. Format follows [Keep a Changelog](https://keepachangelog.com/).

## Metadata

- Version: ``$Version``
- Date: ``$Date``
- Branch: ``main``
- Commit: ``<fill-after-commit>``

## Scope

Brief description of what is included in this release.

## Changes

### Added

-

### Changed

-

### Fixed

-

## Deployment

- Push to ``main`` after filling scope and changes above.

## Related artifacts

- Release details: [``readme.md``](readme.md)
"@
}
