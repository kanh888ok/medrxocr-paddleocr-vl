param(
  [string]$Python = "C:\pocrgpu312\Scripts\python.exe",
  [string]$CudaBin = "C:\pocrgpu312\Lib\site-packages\nvidia\cu13\bin\x86_64",
  [string]$RunName = ""
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$WorkspaceRoot = Split-Path $RepoRoot -Parent
$ErnieRoot = Join-Path $WorkspaceRoot "work\ERNIE-release-v1.5"
$BaseConfig = Join-Path $RepoRoot "configs\erniekit_paddleocr_vl_lora_smoke_win4070.yaml"

if (-not (Test-Path $Python)) {
  throw "Python not found: $Python"
}
if (-not (Test-Path $CudaBin)) {
  throw "CUDA bin not found: $CudaBin"
}
if (-not (Test-Path $ErnieRoot)) {
  throw "ERNIE source not found: $ErnieRoot"
}
if (-not (Test-Path $BaseConfig)) {
  throw "Config not found: $BaseConfig"
}

if ([string]::IsNullOrWhiteSpace($RunName)) {
  $RunName = "checkpoint_run_" + (Get-Date -Format "yyyyMMdd_HHmmss")
}

$OutputDir = "./outputs/medrxocr_lora_smoke_win4070/$RunName"
$LogDir = "$OutputDir/visualdl_logs"
$DistLog = "outputs/medrxocr_lora_smoke_win4070/dist_$RunName"
$TempConfig = "outputs/medrxocr_lora_smoke_win4070/$RunName.yaml"

New-Item -ItemType Directory -Force -Path (Join-Path $RepoRoot "outputs\medrxocr_lora_smoke_win4070") | Out-Null

$configText = Get-Content -LiteralPath $BaseConfig -Raw -Encoding UTF8
$configText = $configText -replace '(?m)^logging_dir: .+$', "logging_dir: $LogDir"
$configText = $configText -replace '(?m)^output_dir: .+$', "output_dir: $OutputDir"
Set-Content -LiteralPath (Join-Path $RepoRoot $TempConfig) -Value $configText -Encoding UTF8

$env:PYTHONPATH = "$ErnieRoot;$env:PYTHONPATH"
$env:PATH = "$CudaBin;$env:PATH"
$env:CUDA_VISIBLE_DEVICES = "0"
$env:FLAGS_allocator_strategy = "auto_growth"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

Push-Location $RepoRoot
try {
  & $Python -u -m paddle.distributed.launch `
    --log_dir $DistLog `
    --gpus 0 `
    --master "127.0.0.1:8110" `
    (Join-Path $ErnieRoot "erniekit\launcher.py") `
    train `
    $TempConfig
}
finally {
  Pop-Location
}
