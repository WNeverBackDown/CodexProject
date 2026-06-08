param(
  [string]$Serial = ""
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$ArgsList = @("-m", "pytest", "-m", "android", "--html", "reports\html\android.html", "--self-contained-html")
if ($Serial) {
  $ArgsList += @("--serial", $Serial)
}

& "D:\Anaconda\envs\py312\python.exe" @ArgsList
