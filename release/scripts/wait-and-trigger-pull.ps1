param(
    [string]$Branch = "main",
    [int]$TimeoutMinutes = 20,
    [int]$PollSeconds = 15,
    [string]$RequireCiSuccess = "true",
    [string]$SkipPublish = "false",
    [string]$TriggerCommand = "Write-Host 'No trigger command configured. Nothing to run.'",
    [string]$NotifyMode = "ntfy",
    [string]$WebhookUrl = "",
    [string]$NtfyTopic = "data-solution-2026-deploy",
    [string]$NtfyBaseUrl = "https://ntfy.sh"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Test-CommandExists {
    param([string]$Name)
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Get-RepoRoot {
    return (git rev-parse --show-toplevel).Trim()
}

function Get-ReleaseVersion {
    param([string]$RepoRoot)
    $versionFile = Join-Path $RepoRoot "release\VERSION"
    if (-not (Test-Path $versionFile)) {
        return $null
    }
    $version = (Get-Content -Path $versionFile -Raw).Trim()
    if ([string]::IsNullOrWhiteSpace($version)) {
        return $null
    }
    if ($version -notmatch '^v') {
        $version = "v$version"
    }
    return $version
}

function Get-GitHubRepoSlug {
    $remoteUrl = (git remote get-url origin 2>$null)
    if ([string]::IsNullOrWhiteSpace($remoteUrl)) {
        return $null
    }
    if ($remoteUrl -match 'github\.com[:/]([^/]+/[^/.]+)') {
        return $Matches[1]
    }
    return $null
}

function Get-ReleaseNotesUrl {
    param(
        [string]$Version,
        [string]$TargetBranch
    )
    if ([string]::IsNullOrWhiteSpace($Version)) {
        return $null
    }
    $repoSlug = Get-GitHubRepoSlug
    if ([string]::IsNullOrWhiteSpace($repoSlug)) {
        return $null
    }
    return "https://github.com/$repoSlug/blob/$TargetBranch/release/notes/$Version.md"
}

function Get-DeployNotificationContext {
    param(
        [string]$CommitSha,
        [string]$TargetBranch
    )
    $repoRoot = Get-RepoRoot
    $version = Get-ReleaseVersion -RepoRoot $repoRoot
    $notesUrl = Get-ReleaseNotesUrl -Version $version -TargetBranch $TargetBranch
    $shortSha = if ($CommitSha.Length -ge 7) { $CommitSha.Substring(0, 7) } else { $CommitSha }
    return @{
        Version = $version
        NotesUrl = $notesUrl
        ShortSha = $shortSha
        FullSha = $CommitSha
    }
}

function Format-DeployNotificationMessage {
    param(
        [hashtable]$Context,
        [string]$OutcomeLine,
        [string]$ErrorDetail = ""
    )
    $versionLabel = if ($Context.Version) { $Context.Version } else { "(no release/VERSION)" }
    $lines = @(
        $OutcomeLine
        "Release: $versionLabel"
        "Commit: $($Context.ShortSha)"
    )
    if (-not [string]::IsNullOrWhiteSpace($ErrorDetail)) {
        $lines += "Error: $ErrorDetail"
    }
    if ($Context.NotesUrl) {
        $lines += "Release notes: $($Context.NotesUrl)"
    }
    return ($lines -join [Environment]::NewLine)
}

function Send-Notification {
    param(
        [string]$Title,
        [string]$Message,
        [string]$Level,
        [string]$ClickUrl = ""
    )
    Write-Host "[$Level] $Title - $Message"

    if ($NotifyMode -in @("toast", "both")) {
        if (Test-CommandExists "New-BurntToastNotification") {
            New-BurntToastNotification -Text $Title, $Message | Out-Null
        } elseif (Get-Module -ListAvailable -Name BurntToast) {
            Import-Module BurntToast -ErrorAction SilentlyContinue
            if (Test-CommandExists "New-BurntToastNotification") {
                New-BurntToastNotification -Text $Title, $Message | Out-Null
            }
        }
    }

    if ($NotifyMode -in @("ntfy", "both")) {
        try {
            $ntfyUrl = "$($NtfyBaseUrl.TrimEnd('/'))/$NtfyTopic"
            $ntfyTitle = "$Title"
            $ntfyPriority = if ($Level -eq "ERROR") { "high" } else { "default" }
            $headers = @{
                "Title" = $ntfyTitle
                "Priority" = $ntfyPriority
                "Tags" = if ($Level -eq "ERROR") { "x,warning" } else { "white_check_mark,rocket" }
            }
            if (-not [string]::IsNullOrWhiteSpace($ClickUrl)) {
                $headers["Click"] = $ClickUrl
            }
            Invoke-RestMethod -Method Post -Uri $ntfyUrl -Headers $headers -Body $Message | Out-Null
        } catch {
            Write-Host "[WARN] Failed to send ntfy notification: $($_.Exception.Message)"
        }
    }

    if ($NotifyMode -in @("webhook", "both")) {
        if ([string]::IsNullOrWhiteSpace($WebhookUrl)) {
            Write-Host "[WARN] Webhook mode enabled but no WebhookUrl configured."
        } else {
            try {
                $body = @{
                    title = $Title
                    message = $Message
                    level = $Level
                    timestamp = (Get-Date).ToString("o")
                } | ConvertTo-Json -Depth 4
                Invoke-RestMethod -Method Post -Uri $WebhookUrl -ContentType "application/json" -Body $body | Out-Null
            } catch {
                Write-Host "[WARN] Failed to send webhook notification: $($_.Exception.Message)"
            }
        }
    }
}

function Get-HeadCommit {
    (git rev-parse HEAD).Trim()
}

function Update-RemoteBranch {
    param([string]$TargetBranch)
    git fetch origin $TargetBranch --quiet | Out-Null
}

function Test-CommitOnRemoteBranch {
    param(
        [string]$CommitSha,
        [string]$TargetBranch
    )
    $remoteRef = "origin/$TargetBranch"
    $mergeBaseExitCode = 0
    git merge-base --is-ancestor $CommitSha $remoteRef 2>$null
    $mergeBaseExitCode = $LASTEXITCODE
    return $mergeBaseExitCode -eq 0
}

function Get-CiState {
    param(
        [string]$CommitSha,
        [string]$TargetBranch
    )
    $json = gh run list --branch $TargetBranch --commit $CommitSha --json databaseId,status,conclusion,name --limit 20
    if (-not $json) {
        return @{ State = "none"; Message = "No workflow runs found yet." }
    }

    $runs = $json | ConvertFrom-Json
    if (-not $runs -or $runs.Count -eq 0) {
        return @{ State = "none"; Message = "No workflow runs found yet." }
    }

    $inProgress = @($runs | Where-Object { $_.status -ne "completed" })
    if ($inProgress.Count -gt 0) {
        return @{
            State = "running"
            Message = "CI still running: $($inProgress.Count) workflow(s) in progress."
        }
    }

    $failed = @($runs | Where-Object { $_.conclusion -ne "success" })
    if ($failed.Count -gt 0) {
        $names = ($failed | ForEach-Object { "$($_.name):$($_.conclusion)" }) -join ", "
        return @{
            State = "failed"
            Message = "CI completed with non-success conclusion(s): $names"
        }
    }

    return @{ State = "success"; Message = "All CI workflows for commit succeeded." }
}

if (-not (Test-CommandExists "git")) {
    throw "git is required but was not found."
}

$requireCi = @("1", "true", "yes", "y", "on") -contains $RequireCiSuccess.ToLowerInvariant()
$skipPublish = @("1", "true", "yes", "y", "on") -contains $SkipPublish.ToLowerInvariant()

if ($requireCi -and -not (Test-CommandExists "gh")) {
    throw "gh CLI is required when -RequireCiSuccess is enabled."
}

try {
    $commitSha = Get-HeadCommit
    $deployContext = Get-DeployNotificationContext -CommitSha $commitSha -TargetBranch $Branch
    $deadline = (Get-Date).AddMinutes($TimeoutMinutes)

    Write-Host "Monitoring commit $commitSha on branch '$Branch'..."
    Send-Notification -Title "CI/CD watcher started" -Message "Waiting for commit $commitSha on origin/$Branch (CI required: $requireCi)." -Level "INFO"

    # Step 1: wait until commit is visible on origin/main
    while ((Get-Date) -lt $deadline) {
        Update-RemoteBranch -TargetBranch $Branch
        if (Test-CommitOnRemoteBranch -CommitSha $commitSha -TargetBranch $Branch) {
            Write-Host "Commit is now visible on origin/$Branch."
            break
        }
        Write-Host "Commit not yet on origin/$Branch. Waiting $PollSeconds second(s)..."
        Start-Sleep -Seconds $PollSeconds
    }

    if (-not (Test-CommitOnRemoteBranch -CommitSha $commitSha -TargetBranch $Branch)) {
        throw "Timed out waiting for commit to appear on origin/$Branch."
    }

    # Step 2: wait for CI success (optional)
    if ($requireCi) {
        while ((Get-Date) -lt $deadline) {
            $ci = Get-CiState -CommitSha $commitSha -TargetBranch $Branch
            Write-Host $ci.Message

            if ($ci.State -eq "success") {
                break
            }
            if ($ci.State -eq "failed") {
                throw "CI failed; deploy trigger aborted."
            }
            Start-Sleep -Seconds $PollSeconds
        }

        $finalCi = Get-CiState -CommitSha $commitSha -TargetBranch $Branch
        if ($finalCi.State -ne "success") {
            throw "Timed out waiting for CI success."
        }
    }

    # Step 3: tag and publish GitHub release (skipped when GitHub Actions already published)
    if (-not $skipPublish) {
        $publishScript = Join-Path (Get-RepoRoot) "release\scripts\publish-release.ps1"
        if (Test-Path $publishScript) {
            Write-Host "Publishing release for commit $commitSha..."
            & powershell -NoProfile -ExecutionPolicy Bypass -File $publishScript -CommitSha $commitSha
            if ($LASTEXITCODE -ne 0) {
                throw "publish-release.ps1 failed with exit code $LASTEXITCODE."
            }
        }
    } else {
        Write-Host "Skipping local publish (GitHub Actions publishes release on main)."
    }

    # Step 4: trigger NAS pull/deploy action
    Write-Host "Running trigger command..."
    Invoke-Expression $TriggerCommand
    if ($LASTEXITCODE -ne 0) {
        throw "Deploy trigger command failed with exit code $LASTEXITCODE."
    }
    Write-Host "Trigger command completed."
    $versionLabel = if ($deployContext.Version) { $deployContext.Version } else { "unknown" }
    $successTitle = "Deploy succeeded: $versionLabel"
    $successMessage = Format-DeployNotificationMessage -Context $deployContext -OutcomeLine "NAS deployment completed."
    Send-Notification -Title $successTitle -Message $successMessage -Level "SUCCESS" -ClickUrl $deployContext.NotesUrl
} catch {
    $errorMessage = $_.Exception.Message
    if (-not $deployContext) {
        $deployContext = Get-DeployNotificationContext -CommitSha (Get-HeadCommit) -TargetBranch $Branch
    }
    $versionLabel = if ($deployContext.Version) { $deployContext.Version } else { "unknown" }
    $failureTitle = "Deploy failed: $versionLabel"
    $failureMessage = Format-DeployNotificationMessage -Context $deployContext -OutcomeLine "NAS deployment did not complete." -ErrorDetail $errorMessage
    Send-Notification -Title $failureTitle -Message $failureMessage -Level "ERROR" -ClickUrl $deployContext.NotesUrl
    throw
}
