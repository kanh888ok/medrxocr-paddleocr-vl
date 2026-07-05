param(
  [string]$Python = "C:\pocrgpu312\Scripts\python.exe",
  [string]$CudaBin = "C:\pocrgpu312\Lib\site-packages\nvidia\cu13\bin\x86_64",
  [string]$Config = "configs\erniekit_paddleocr_vl_lora_public_small_win4070.yaml",
  [string]$OutputRoot = "outputs\medrxocr_lora_public_small_win4070",
  [string]$RunName = "",
  [int]$MasterPort = 8110,
  [int]$MaxSteps = 0,
  [int]$SaveSteps = 0,
  [int]$EvalSteps = 0,
  [int]$LoggingSteps = 0
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$WorkspaceRoot = Split-Path $RepoRoot -Parent
$ErnieRoot = Join-Path $WorkspaceRoot "work\ERNIE-release-v1.5"
$BaseConfig = Join-Path $RepoRoot $Config

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

$OutputRootRel = ($OutputRoot -replace "\\", "/").TrimEnd("/")
$OutputDir = "./$OutputRootRel/$RunName"
$LogDir = "./$OutputRootRel/logs_$RunName"
$DistLog = "$OutputRootRel/dist_$RunName"
$TempConfig = "$OutputRootRel/$RunName.yaml"

New-Item -ItemType Directory -Force -Path (Join-Path $RepoRoot $OutputRoot) | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $RepoRoot ($LogDir -replace "^\\./", "")) | Out-Null

$configText = Get-Content -LiteralPath $BaseConfig -Raw -Encoding UTF8
$configText = $configText -replace '(?m)^logging_dir: .+$', "logging_dir: $LogDir"
$configText = $configText -replace '(?m)^output_dir: .+$', "output_dir: $OutputDir"
if ($MaxSteps -gt 0) {
  $configText = $configText -replace '(?m)^max_steps: .+$', "max_steps: $MaxSteps"
}
if ($SaveSteps -gt 0) {
  $configText = $configText -replace '(?m)^save_steps: .+$', "save_steps: $SaveSteps"
}
if ($EvalSteps -gt 0) {
  $configText = $configText -replace '(?m)^eval_steps: .+$', "eval_steps: $EvalSteps"
}
if ($LoggingSteps -gt 0) {
  $configText = $configText -replace '(?m)^logging_steps: .+$', "logging_steps: $LoggingSteps"
}
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
    --master "127.0.0.1:$MasterPort" `
    (Join-Path $ErnieRoot "erniekit\launcher.py") `
    train `
    $TempConfig
}
finally {
  Pop-Location
}
