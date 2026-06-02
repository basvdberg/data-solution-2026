Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (git rev-parse --show-toplevel).Trim()
$scriptPath = Join-Path $repoRoot "release\scripts\wait-and-trigger-pull.ps1"

# Example NAS trigger command (replace host/user/script to your environment)
$trigger = "ssh nas-user@nas-host '~/apps/data-solution-2026/release/scripts/deploy-on-nas.sh'"

Start-Process powershell -ArgumentList @(
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-File", "`"$scriptPath`"",
    "-Branch", "main",
    "-TimeoutMinutes", "20",
    "-PollSeconds", "15",
    "-RequireCiSuccess", "true",
    "-TriggerCommand", "`"$trigger`""
) | Out-Null
