param(
    [string]$RemoteName,
    [string]$RemoteUrl,
    [string]$StdinFile
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Send-ImmediateNtfy {
    param(
        [string]$Title,
        [string]$Message,
        [string]$Topic,
        [string]$ClickUrl = ""
    )
    try {
        $ntfyUrl = "https://ntfy.sh/$Topic"
        $headers = @{
            "Title" = $Title
            "Priority" = "default"
            "Tags" = "rocket"
        }
        if (-not [string]::IsNullOrWhiteSpace($ClickUrl)) {
            $headers["Click"] = $ClickUrl
        }
        Invoke-RestMethod -Method Post -Uri $ntfyUrl -Headers $headers -Body $Message | Out-Null
    } catch {
        Write-Host "[WARN] Immediate ntfy failed: $($_.Exception.Message)"
    }
}

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
    Write-Host "post-push: no update for refs/heads/main; skipping CI/CD trigger."
    exit 0
}

$repoRoot = (git rev-parse --show-toplevel).Trim()
$scriptPath = Join-Path $repoRoot "release\scripts\wait-and-trigger-pull.ps1"
$versionFile = Join-Path $repoRoot "release\VERSION"
$version = if (Test-Path $versionFile) { (Get-Content -Path $versionFile -Raw).Trim() } else { "unknown" }
if ($version -and $version -notmatch '^v') {
    $version = "v$version"
}
$shortSha = (git rev-parse --short HEAD).Trim()
$ntfyTopic = "data-solution-2026-deploy"

Send-ImmediateNtfy `
    -Title "Push to main: $version" `
    -Message "CI/CD cycle started ($shortSha). GitHub Actions runs tests and release; this machine deploys to NAS after CI is green." `
    -Topic $ntfyTopic

# bash -lc required: non-interactive ssh does not load ~/.profile (git wrapper PATH).
$trigger = "ssh bas@basnas 'bash -lc ''bash ~/apps/data-solution-2026/release/scripts/deploy-on-nas.sh'''"

Start-Process powershell -ArgumentList @(
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-File", "`"$scriptPath`"",
    "-Branch", "main",
    "-TimeoutMinutes", "20",
    "-PollSeconds", "15",
    "-RequireCiSuccess", "1",
    "-SkipPublish", "1",
    "-NotifyMode", "ntfy",
    "-NtfyTopic", $ntfyTopic,
    "-TriggerCommand", "`"$trigger`""
) | Out-Null

Write-Host "post-push: background deploy watcher started for main (publish via GitHub Actions)."
