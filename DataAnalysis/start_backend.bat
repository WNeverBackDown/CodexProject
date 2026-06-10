@echo off
setlocal
cd /d %~dp0
set DATAPULSE_ENV=development
"D:\Anaconda\envs\py312\python.exe" -m pip install -r requirements.txt
"D:\Anaconda\envs\py312\python.exe" main.py
