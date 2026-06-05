Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (git rev-parse --show-toplevel).Trim()
$deployHook = Join-Path $repoRoot "release\scripts\post-push-hook.ps1"
if (-not (Test-Path $deployHook)) {
    throw "Deploy hook script not found: $deployHook"
}

$hooksPath = (git config --get core.hooksPath 2>$null)
if ([string]::IsNullOrWhiteSpace($hooksPath)) {
    $hooksPath = Join-Path $repoRoot ".git\hooks"
} elseif (-not [System.IO.Path]::IsPathRooted($hooksPath)) {
    $hooksPath = Join-Path $repoRoot $hooksPath
}

$prePushHook = Join-Path $hooksPath "pre-push"
$sharedPrePush = Join-Path $repoRoot "..\cursor-config\githooks\pre-push"
$sharedPrePushResolved = (Resolve-Path $sharedPrePush -ErrorAction SilentlyContinue)

Write-Host "Repo: $repoRoot"
Write-Host "Git hooks path: $hooksPath"
Write-Host "NAS deploy hook: $deployHook"

if ($sharedPrePushResolved -and (Test-Path $sharedPrePushResolved)) {
    $expected = $sharedPrePushResolved.Path
    if ((Test-Path $prePushHook) -and ((Get-Item $prePushHook).FullName -eq $expected)) {
        Write-Host "Shared pre-push hook already active at $prePushHook"
    } elseif (Test-Path $prePushHook) {
        Write-Host "[OK] pre-push hook present at $prePushHook"
        Write-Host "     (should invoke post-push-hook.ps1 for this repo)"
    } else {
        Write-Host "[WARN] pre-push missing at $hooksPath"
        Write-Host "       Expected shared hook: $expected"
        Write-Host "       Commit cursor-config/githooks/pre-push or copy it into your hooksPath."
    }
} else {
    Write-Host "[WARN] cursor-config/githooks/pre-push not found beside repo."
    Write-Host "       Clone cursor-config as a sibling or add a pre-push hook that calls:"
    Write-Host "       $deployHook"
}

# Legacy .git/hooks/post-push is not used by Git; remove confusion if present.
$legacyPostPush = Join-Path $repoRoot ".git\hooks\post-push"
if (Test-Path $legacyPostPush) {
    Write-Host ""
    Write-Host "Note: Git does not run a post-push hook. Deploy uses pre-push at hooksPath above."
    Write-Host "      You may delete legacy file: $legacyPostPush"
}

Write-Host ""
Write-Host "Prerequisites: gh auth login, ssh bas@basnas, ntfy topic data-solution-2026-deploy"
Write-Host "After push to main: GitHub Actions (tests + release) then NAS deploy via deploy-on-nas.sh"
