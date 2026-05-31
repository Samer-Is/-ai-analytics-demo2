<#
.SYNOPSIS
    Refresh the offline Parquet snapshot used by the deployed Renty AI Analytics app.

.DESCRIPTION
    Re-extracts the data warehouse tables from the live SQL Server into local
    Parquet files, copies them to the deployment server, and restarts the
    container so DuckDB reloads the views.

    Run this from a machine that:
      * is on the internal network / VPN (so it can reach the live DB), and
      * has the project Python virtual environment with pyodbc, pyarrow, duckdb.

    The app keeps serving the previous snapshot until the new files are copied
    and the container restarts, so downtime is only a few seconds.

.PARAMETER Server
    SSH target for the deployment server. Default: qoad@172.86.86.16

.PARAMETER RemoteDir
    App directory on the server. Default: ~/renty

.PARAMETER Years
    How many years of history to keep in the large fact tables. Default: 3

.PARAMETER SkipExtract
    Reuse the existing local data/renty/*.parquet files instead of re-extracting.

.PARAMETER SkipRestart
    Copy the files but do not restart the remote container.

.EXAMPLE
    pwsh ./scripts/refresh_snapshot.ps1

.EXAMPLE
    pwsh ./scripts/refresh_snapshot.ps1 -Years 5 -Server qoad@172.86.86.16
#>
[CmdletBinding()]
param(
    [string]$Server    = "qoad@172.86.86.16",
    [string]$RemoteDir = "~/renty",
    [int]$Years        = 3,
    [switch]$SkipExtract,
    [switch]$SkipRestart
)

$ErrorActionPreference = "Stop"

# Resolve paths relative to this script: scripts/ -> app root -> repo root.
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$AppRoot   = Split-Path -Parent $ScriptDir
$RepoRoot  = Split-Path -Parent $AppRoot
$DataDir   = Join-Path $AppRoot "data\renty"
$Python    = Join-Path $RepoRoot ".venv\Scripts\python.exe"

Write-Host "App root : $AppRoot"
Write-Host "Data dir : $DataDir"
Write-Host "Server   : $Server  ($RemoteDir)"
Write-Host ""

# 1) Extract a fresh snapshot from the live database.
if (-not $SkipExtract) {
    if (-not (Test-Path $Python)) {
        throw "Python venv not found at $Python. Activate/create the venv first."
    }
    Write-Host "==> Extracting snapshot from the live database ($Years years)..." -ForegroundColor Cyan
    & $Python (Join-Path $AppRoot "scripts\extract_snapshot.py") --out $DataDir --years $Years
    if ($LASTEXITCODE -ne 0) { throw "Snapshot extraction failed (exit $LASTEXITCODE)." }
} else {
    Write-Host "==> Skipping extraction; using existing files in $DataDir" -ForegroundColor Yellow
}

$parquet = Get-ChildItem -Path $DataDir -Filter *.parquet -ErrorAction SilentlyContinue
if (-not $parquet) { throw "No .parquet files found in $DataDir." }
$totalMb = [math]::Round(($parquet | Measure-Object Length -Sum).Sum / 1MB, 1)
Write-Host ("    {0} files, {1} MB" -f $parquet.Count, $totalMb)

# 2) Copy the snapshot to the server.
Write-Host "==> Copying snapshot to $Server`:$RemoteDir/data/renty ..." -ForegroundColor Cyan
ssh $Server "mkdir -p $RemoteDir/data/renty"
if ($LASTEXITCODE -ne 0) { throw "Could not create remote data directory." }
scp ($DataDir + "\*.parquet") "$Server`:$RemoteDir/data/renty/"
if ($LASTEXITCODE -ne 0) { throw "scp of snapshot failed." }

# 3) Restart the container so DuckDB rebuilds its views over the new Parquet files.
if (-not $SkipRestart) {
    Write-Host "==> Restarting the remote container ..." -ForegroundColor Cyan
    ssh $Server "cd $RemoteDir && docker compose -f docker-compose.deploy.yml restart"
    if ($LASTEXITCODE -ne 0) { throw "Container restart failed." }
    Write-Host "==> Verifying offline snapshot ..." -ForegroundColor Cyan
    ssh $Server "sleep 4; docker exec renty-analytics python db.py"
} else {
    Write-Host "==> Skipping container restart (use 'docker compose ... restart' to apply)." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Snapshot refresh complete." -ForegroundColor Green
