$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

function Test-Command {
    param([string]$Name)
    return Get-Command $Name -ErrorAction SilentlyContinue
}

$env:PYTHONUTF8 = "1"
$env:PIP_DISABLE_PIP_VERSION_CHECK = "1"

$UseUv = $false
if (Test-Command "uv") {
    $UseUv = $true
}

if ($UseUv) {
    uv venv .venv
    uv pip install -r requirements.txt

    if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
    if (Test-Path "build") { Remove-Item -Recurse -Force "build" }

    uv run pyinstaller --onefile --name "cpu_info" main.py
    Write-Host "Build complete. See dist\cpu_info.exe"
    exit 0
}

$VenvPath = Join-Path $ProjectRoot ".venv"
$PythonCmd = "python"
$PythonArgs = @()
if (Test-Command "py") {
    $PythonCmd = "py"
    $PythonArgs = @("-3")
} elseif (-not (Test-Command $PythonCmd)) {
    throw "Python not found. Install Python 3 or ensure python.exe is on PATH."
}

if (-not (Test-Path $VenvPath)) {
    & $PythonCmd @PythonArgs -m venv $VenvPath
}

if (Test-Path (Join-Path $VenvPath "Scripts")) {
    $VenvScripts = Join-Path $VenvPath "Scripts"
} elseif (Test-Path (Join-Path $VenvPath "bin")) {
    $VenvScripts = Join-Path $VenvPath "bin"
} else {
    throw "Virtual environment not created correctly at $VenvPath."
}

$PythonExe = Join-Path $VenvScripts "python.exe"
$PipExe = Join-Path $VenvScripts "pip.exe"

if (-not (Test-Path $PythonExe)) {
    throw "Virtual environment not created correctly at $VenvPath."
}

& $PythonExe -m pip install --upgrade pip
& $PythonExe -m pip install -r requirements.txt

if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }

& $PythonExe -m PyInstaller --onefile --name "cpu_info" main.py

Write-Host "Build complete. See dist\cpu_info.exe"
