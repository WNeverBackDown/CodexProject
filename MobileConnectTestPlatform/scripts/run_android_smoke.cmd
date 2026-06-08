@echo off
setlocal
set ROOT=%~dp0..
cd /d "%ROOT%"
if "%~1"=="" (
  "D:\Anaconda\envs\py312\python.exe" -m pytest -m android --html "reports\html\android.html" --self-contained-html
) else (
  "D:\Anaconda\envs\py312\python.exe" -m pytest -m android --serial "%~1" --html "reports\html\android.html" --self-contained-html
)
