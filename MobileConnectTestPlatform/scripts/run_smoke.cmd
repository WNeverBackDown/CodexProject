@echo off
setlocal
set ROOT=%~dp0..
cd /d "%ROOT%"
"D:\Anaconda\envs\py312\python.exe" -m pytest -m "smoke and not android" --html "reports\html\smoke.html" --self-contained-html
