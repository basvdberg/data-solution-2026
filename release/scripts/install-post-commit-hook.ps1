Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (git rev-parse --show-toplevel).Trim()
$hooksDir = Join-Path $repoRoot ".git\hooks"
$hookPath = Join-Path $hooksDir "post-commit"

if (-not (Test-Path $hooksDir)) {
    throw "Hooks directory not found: $hooksDir"
}

$hookContent = @"
#!/usr/bin/env pwsh
`$ErrorActionPreference = 'Stop'
pwsh -NoProfile -ExecutionPolicy Bypass -File "$repoRoot/release/scripts/post-commit-hook.ps1"
"@

Set-Content -Path $hookPath -Value $hookContent -Encoding UTF8

Write-Host "Installed post-commit hook at $hookPath"
Write-Host "Note: update NAS host/user in release/scripts/post-commit-hook.ps1"
