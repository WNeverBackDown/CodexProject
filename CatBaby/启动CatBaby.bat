@echo off
set "ROOT=%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%ROOT%scripts\start.ps1"
if errorlevel 1 pause
