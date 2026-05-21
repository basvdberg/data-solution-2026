# Enable repository Git hooks that refresh Markdown TOCs and project structure on each commit.
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

git config core.hooksPath .githooks
Write-Host "Configured core.hooksPath=.githooks for $(git rev-parse --show-toplevel)"
