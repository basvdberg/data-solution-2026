param(
    [string]$RemoteName,
    [string]$RemoteUrl,
    [string]$StdinFile
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not (Test-Path $StdinFile)) {
    throw "post-push stdin file not found: $StdinFile"
}

# Only trigger for pushes that include refs/heads/main.
$lines = Get-Content -Path $StdinFile
$pushedMain = $false
foreach ($line in $lines) {
    if ([string]::IsNullOrWhiteSpace($line)) {
        continue
    }
    $parts = $line -split "\s+"
    if ($parts.Count -lt 4) {
        continue
    }
    $remoteRef = $parts[2]
    if ($remoteRef -eq "refs/heads/main") {
        $pushedMain = $true
        break
    }
}

if (-not $pushedMain) {
    Write-Host "post-push: no update for refs/heads/main; skipping deploy trigger."
    exit 0
}

$repoRoot = (git rev-parse --show-toplevel).Trim()
$scriptPath = Join-Path $repoRoot "release\scripts\wait-and-trigger-pull.ps1"

# Replace these values for your environment.
$trigger = "ssh bas@basnas '~/apps/data-solution-2026/release/scripts/deploy-on-nas.sh'"
$ntfyTopic = "data-solution-2026-deploy"

Start-Process powershell -ArgumentList @(
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-File", "`"$scriptPath`"",
    "-Branch", "main",
    "-TimeoutMinutes", "20",
    "-PollSeconds", "15",
    "-RequireCiSuccess", "1",
    "-NotifyMode", "ntfy",
    "-NtfyTopic", $ntfyTopic,
    "-TriggerCommand", "`"$trigger`""
) | Out-Null

Write-Host "post-push: background deploy watcher started for main."
