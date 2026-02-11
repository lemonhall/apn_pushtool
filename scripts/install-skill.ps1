param(
  [string]$Target = "$HOME\\.agents\\skills"
)

$ErrorActionPreference = "Stop"

$src = Join-Path $PSScriptRoot "..\\skills\\apn-pushtool"
$dstRoot = $Target
$dst = Join-Path $dstRoot "apn-pushtool"
$dstSecrets = Join-Path $dst "secrets"

if (!(Test-Path $src)) {
  throw "Skill source not found: $src"
}

New-Item -ItemType Directory -Force -Path $dstRoot | Out-Null

$secretsBackup = $null
if (Test-Path $dstSecrets) {
  $ts = Get-Date -Format "yyyyMMdd-HHmmss"
  $secretsBackup = Join-Path $dstRoot "apn-pushtool.secrets.bak.$ts"
  Copy-Item -Recurse -Force $dstSecrets $secretsBackup
  Write-Host "Existing secrets backed up to: $secretsBackup" -ForegroundColor Yellow
}

if (Test-Path $dst) {
  $ts = Get-Date -Format "yyyyMMdd-HHmmss"
  $bak = Join-Path $dstRoot "apn-pushtool.bak.$ts"
  Move-Item -Force $dst $bak
  Write-Host "Existing skill backed up to: $bak" -ForegroundColor Yellow
}

Copy-Item -Recurse -Force $src $dst

if ($secretsBackup) {
  New-Item -ItemType Directory -Force -Path $dstSecrets | Out-Null
  Copy-Item -Recurse -Force (Join-Path $secretsBackup "*") $dstSecrets
  Write-Host "Secrets restored to: $dstSecrets" -ForegroundColor Green
}

Write-Host "Installed skill to: $dst" -ForegroundColor Green
