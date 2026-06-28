# Installs the script-breakdown skill into Claude Code's user skills folder.
# Run after cloning this repo on a new machine (or after reinstalling Windows):
#   powershell -ExecutionPolicy Bypass -File .\install-skill.ps1

$src  = Join-Path $PSScriptRoot "skills\script-breakdown\SKILL.md"
$dest = Join-Path $env:USERPROFILE ".claude\skills\script-breakdown"

if (-not (Test-Path $src)) { Write-Error "SKILL.md not found at $src"; exit 1 }
New-Item -ItemType Directory -Force -Path $dest | Out-Null
Copy-Item $src (Join-Path $dest "SKILL.md") -Force
Write-Host "Installed script-breakdown skill -> $dest"
Write-Host "Open Claude Code and run:  /script-breakdown ""your topic"""
