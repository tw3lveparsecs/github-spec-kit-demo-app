[CmdletBinding()]
param(
  [switch]$Docker,
  [switch]$NoInstall,
  [int]$Port = 5000
)

$ErrorActionPreference = 'Stop'

function Write-Info($msg) { Write-Host "[start] $msg" }

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$backendDir = Join-Path $repoRoot 'backend'
$venvDir = Join-Path $backendDir '.venv'
$pythonExe = Join-Path $venvDir 'Scripts\python.exe'

if ($Docker) {
  Write-Info "Starting via Docker Compose..."
  Push-Location $repoRoot
  try {
    # Works with both Docker Compose v2 (docker compose) and v1 (docker-compose)
    if (Get-Command docker -ErrorAction SilentlyContinue) {
      try {
        docker compose up --build
      } catch {
        docker-compose up --build
      }
    } else {
      throw "Docker is not installed or not on PATH."
    }
  } finally {
    Pop-Location
  }
  exit 0
}

Write-Info "Repo root: $repoRoot"
Write-Info "Backend dir: $backendDir"

if (-not (Test-Path $venvDir)) {
  Write-Info "Creating virtual environment in backend/.venv..."
  Push-Location $backendDir
  try {
    python -m venv .venv
  } finally {
    Pop-Location
  }
}

if (-not (Test-Path $pythonExe)) {
  throw "Expected venv python at $pythonExe but it was not found."
}

if (-not $NoInstall) {
  Write-Info "Installing backend dependencies..."
  Push-Location $backendDir
  try {
    & $pythonExe -m pip install --upgrade pip
    & $pythonExe -m pip install -r requirements.txt
    if (Test-Path (Join-Path $backendDir 'requirements-dev.txt')) {
      & $pythonExe -m pip install -r requirements-dev.txt
    }
  } finally {
    Pop-Location
  }
}

Write-Info "Starting backend on port $Port..."
$env:PYTHONPATH = (Join-Path $backendDir 'src')
$env:PORT = "$Port"

Push-Location $backendDir
try {
  # run_dev.py binds to 0.0.0.0:5000 by default; PORT is provided for future use.
  & $pythonExe run_dev.py
} finally {
  Pop-Location
}
