@echo off
setlocal
set ROOT=%~dp0..
"D:\Anaconda\envs\py312\python.exe" -m connect_lab.cli doctor --config "%ROOT%\configs\testbed.example.yaml"
