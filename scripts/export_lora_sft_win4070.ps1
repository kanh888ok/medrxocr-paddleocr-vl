param(
  [string]$Python = "C:\pocrgpu312\Scripts\python.exe",
  [string]$CudaBin = "C:\pocrgpu312\Lib\site-packages\nvidia\cu13\bin\x86_64",
  [string]$Config = "configs\erniekit_paddleocr_vl_lora_word_export_win4070.yaml",
  [int]$MasterPort = 8116
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$WorkspaceRoot = Split-Path $RepoRoot -Parent
$ErnieRoot = Join-Path $WorkspaceRoot "work\ERNIE-release-v1.5"
$ConfigPath = Join-Path $RepoRoot $Config

if (-not (Test-Path $Python)) {
  throw "Python not found: $Python"
}
if (-not (Test-Path $CudaBin)) {
  throw "CUDA bin not found: $CudaBin"
}
if (-not (Test-Path $ErnieRoot)) {
  throw "ERNIE source not found: $ErnieRoot"
}
if (-not (Test-Path $ConfigPath)) {
  throw "Config not found: $ConfigPath"
}

$RunName = [IO.Path]::GetFileNameWithoutExtension($Config)
$DistLog = "outputs/medrxocr_lora_word_win4070/dist_export_$RunName"

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
    export `
    $Config
}
finally {
  Pop-Location
}
