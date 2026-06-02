Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (git rev-parse --show-toplevel).Trim()
$hooksDir = Join-Path $repoRoot ".git\hooks"
$hookPath = Join-Path $hooksDir "post-push"

if (-not (Test-Path $hooksDir)) {
    throw "Hooks directory not found: $hooksDir"
}

$hookContent = @'
#!/usr/bin/env bash
set -euo pipefail
remote_name="$1"
remote_url="$2"
stdin_file=$(mktemp)
cat > "$stdin_file"
powershell -NoProfile -ExecutionPolicy Bypass -File "__REPO_ROOT__/release/scripts/post-push-hook.ps1" -RemoteName "$remote_name" -RemoteUrl "$remote_url" -StdinFile "$stdin_file"
rm -f "$stdin_file"
'@

$hookContent = $hookContent.Replace("__REPO_ROOT__", $repoRoot.Replace('\', '/'))

Set-Content -Path $hookPath -Value $hookContent -Encoding UTF8

Write-Host "Installed post-push hook at $hookPath"
Write-Host "Next: update NAS host/user in release/scripts/post-push-hook.ps1"
