$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
& "D:\Anaconda\envs\py312\python.exe" -m connect_lab.cli doctor --config "$Root\configs\testbed.example.yaml"
