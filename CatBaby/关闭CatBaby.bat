@echo off
set "ROOT=%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%ROOT%scripts\stop.ps1"
if errorlevel 1 pause
