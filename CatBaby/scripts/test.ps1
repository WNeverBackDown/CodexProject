$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Python = "D:\Anaconda\envs\py312\python.exe"
$LocalDeps = Join-Path $ProjectRoot ".deps"

if (!(Test-Path $Python)) {
  throw "Python interpreter not found: $Python"
}

if (Test-Path $LocalDeps) {
  $env:PYTHONPATH = "$LocalDeps;$env:PYTHONPATH"
}

& $Python -m unittest discover -s (Join-Path $ProjectRoot "tests")
