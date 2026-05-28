$ErrorActionPreference = "Continue"

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Port = 8765
$PidFile = Join-Path $ProjectRoot "data\catbaby.pid"

function Get-CatBabyProcessIds {
  $all = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue
  if (!$all) {
    return @()
  }
  return @(
    $all |
      Where-Object {
        $_.CommandLine -and
        $_.CommandLine.Contains($ProjectRoot) -and
        $_.CommandLine -match "server\.py"
      } |
      Select-Object -ExpandProperty ProcessId
  )
}

function Test-CatBabyProcessId($ProcessId) {
  $process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
  if (!$process) {
    return $false
  }
  $listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
    Where-Object { $_.OwningProcess -eq $ProcessId } |
    Select-Object -First 1
  if ($listener) {
    return $true
  }
  $details = Get-CimInstance Win32_Process -Filter "ProcessId=$ProcessId" -ErrorAction SilentlyContinue
  return [bool]($details -and $details.CommandLine -and $details.CommandLine.Contains($ProjectRoot) -and $details.CommandLine -match "server\.py")
}

$targets = @()
if (Test-Path $PidFile) {
  $pidText = (Get-Content $PidFile -Raw).Trim()
  if ($pidText -match "^\d+$" -and (Test-CatBabyProcessId -ProcessId ([int]$pidText))) {
    $targets += [int]$pidText
  }
}

$targets += @(Get-CatBabyProcessIds)
$targets = @($targets | Where-Object { $_ -and $_ -ne $PID } | Select-Object -Unique)

if ($targets.Count -eq 0) {
  Write-Host "[CatBaby] No running CatBaby process found."
  if (Test-Path $PidFile) {
    Remove-Item $PidFile -Force
  }
  exit 0
}

foreach ($id in $targets) {
  $process = Get-Process -Id $id -ErrorAction SilentlyContinue
  if ($process) {
    Write-Host "[CatBaby] Stopping PID: $id"
    Stop-Process -Id $id -Force -ErrorAction SilentlyContinue
  }
}

Start-Sleep -Milliseconds 500

if (Test-Path $PidFile) {
  Remove-Item $PidFile -Force
}

$left = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
  Where-Object { $targets -contains $_.OwningProcess } |
  Select-Object -First 1

if ($left) {
  Write-Host "[CatBaby] Port $Port is still used by PID $($left.OwningProcess)."
  exit 2
}

Write-Host "[CatBaby] Stopped."
