$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Python = "D:\Anaconda\envs\py312\python.exe"
$Requirements = Join-Path $ProjectRoot "requirements.txt"
$LocalDeps = Join-Path $ProjectRoot ".deps"

if (!(Test-Path $Python)) {
  throw "Python interpreter not found: $Python"
}

New-Item -ItemType Directory -Force -Path $LocalDeps | Out-Null
& $Python -m pip install --target $LocalDeps -r $Requirements
