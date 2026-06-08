$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root
& "D:\Anaconda\envs\py312\python.exe" -m pytest -m "smoke and not android" --html "reports\html\smoke.html" --self-contained-html
