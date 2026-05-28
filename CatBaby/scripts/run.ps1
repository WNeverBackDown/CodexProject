$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Python = "D:\Anaconda\envs\py312\python.exe"

if (!(Test-Path $Python)) {
  throw "Python interpreter not found: $Python"
}

& $Python (Join-Path $ProjectRoot "server.py") --host 127.0.0.1 --port 8765
