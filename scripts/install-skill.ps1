param(
  [string]$Target = "$HOME\\.agents\\skills"
)

$ErrorActionPreference = "Stop"

$src = Join-Path $PSScriptRoot "..\\skills\\apn-pushtool"
$dstRoot = $Target
$dst = Join-Path $dstRoot "apn-pushtool"

if (!(Test-Path $src)) {
  throw "Skill source not found: $src"
}

New-Item -ItemType Directory -Force -Path $dstRoot | Out-Null

if (Test-Path $dst) {
  $ts = Get-Date -Format "yyyyMMdd-HHmmss"
  $bak = Join-Path $dstRoot "apn-pushtool.bak.$ts"
  Move-Item -Force $dst $bak
  Write-Host "Existing skill backed up to: $bak" -ForegroundColor Yellow
}

Copy-Item -Recurse -Force $src $dst

Write-Host "Installed skill to: $dst" -ForegroundColor Green
