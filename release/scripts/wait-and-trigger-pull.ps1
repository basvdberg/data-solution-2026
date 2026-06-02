param(
    [string]$Branch = "main",
    [int]$TimeoutMinutes = 20,
    [int]$PollSeconds = 15,
    [bool]$RequireCiSuccess = $true,
    [string]$TriggerCommand = "Write-Host 'No trigger command configured. Nothing to run.'",
    [string]$NotifyMode = "ntfy",
    [string]$WebhookUrl = "",
    [string]$NtfyTopic = "bas-data-solution-deploy",
    [string]$NtfyBaseUrl = "https://ntfy.sh"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Test-CommandExists {
    param([string]$Name)
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Send-Notification {
    param(
        [string]$Title,
        [string]$Message,
        [string]$Level
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

if ($RequireCiSuccess -and -not (Test-CommandExists "gh")) {
    throw "gh CLI is required when -RequireCiSuccess is enabled."
}

try {
    $commitSha = Get-HeadCommit
    $deadline = (Get-Date).AddMinutes($TimeoutMinutes)

    Write-Host "Monitoring commit $commitSha on branch '$Branch'..."

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
    if ($RequireCiSuccess) {
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

    # Step 3: trigger NAS pull/deploy action
    Write-Host "Running trigger command..."
    Invoke-Expression $TriggerCommand
    Write-Host "Trigger command completed."
    Send-Notification -Title "NAS deploy trigger succeeded" -Message "Commit $commitSha passed checks and trigger command completed." -Level "SUCCESS"
} catch {
    $errorMessage = $_.Exception.Message
    Send-Notification -Title "NAS deploy trigger failed" -Message $errorMessage -Level "ERROR"
    throw
}
