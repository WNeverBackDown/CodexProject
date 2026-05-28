$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Python = "D:\Anaconda\envs\py312\python.exe"
$Port = 8765
$DataDir = Join-Path $ProjectRoot "data"
$PidFile = Join-Path $DataDir "catbaby.pid"
$OutLog = Join-Path $DataDir "catbaby.out.log"
$ErrLog = Join-Path $DataDir "catbaby.err.log"
$Url = "http://127.0.0.1:$Port"

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

if (!(Test-Path $Python)) {
  Write-Host "[CatBaby] Python not found: $Python"
  exit 1
}

New-Item -ItemType Directory -Force -Path $DataDir | Out-Null

$known = @()
if (Test-Path $PidFile) {
  $pidText = (Get-Content $PidFile -Raw).Trim()
  if ($pidText -match "^\d+$") {
    if (Test-CatBabyProcessId -ProcessId ([int]$pidText)) {
      $known += [int]$pidText
    }
  }
}

$known += @(Get-CatBabyProcessIds)
$known = @($known | Where-Object { $_ } | Select-Object -Unique)
if ($known.Count -gt 0) {
  Set-Content -Path $PidFile -Value $known[0]
  Write-Host "[CatBaby] Already running. PID: $($known[0])"
  Write-Host "[CatBaby] Opening: $Url"
  Start-Process $Url
  exit 0
}

$listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if ($listener) {
  Write-Host "[CatBaby] Port $Port is already in use by PID $($listener.OwningProcess)."
  Write-Host "[CatBaby] Close that process or change CatBaby's port."
  exit 2
}

$server = Join-Path $ProjectRoot "server.py"
$command = "cd /d `"$ProjectRoot`" && `"$Python`" `"$server`" --host 127.0.0.1 --port $Port > `"$OutLog`" 2> `"$ErrLog`""
$process = Start-Process `
  -FilePath "cmd.exe" `
  -ArgumentList "/c", $command `
  -WorkingDirectory $ProjectRoot `
  -WindowStyle Hidden `
  -PassThru
$processId = [int]$process.Id
Set-Content -Path $PidFile -Value $processId

$started = $null
for ($i = 0; $i -lt 20; $i++) {
  Start-Sleep -Milliseconds 300
  $started = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($started) {
    break
  }
}

if ($started) {
  Set-Content -Path $PidFile -Value $started.OwningProcess
  Write-Host "[CatBaby] Started. PID: $($started.OwningProcess)"
  Write-Host "[CatBaby] Opening: $Url"
  Start-Process $Url
  exit 0
}

Write-Host "[CatBaby] Failed to confirm startup."
Write-Host "[CatBaby] Logs:"
Write-Host "[CatBaby] $OutLog"
Write-Host "[CatBaby] $ErrLog"
if (Test-Path $ErrLog) {
  Get-Content $ErrLog -Tail 20
}
exit 3
