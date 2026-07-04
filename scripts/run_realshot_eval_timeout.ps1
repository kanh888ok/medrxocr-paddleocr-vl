param(
  [string]$PythonExe = "",
  [string]$OutputDir = "outputs\paddleocrvl_v15_realshot_eval18_gpu_timeout",
  [string]$InputFile = "data\eval\realshot_eval_18.jsonl",
  [string]$PipelineVersion = "v1.5",
  [string]$CacheRoot = "C:\pocr_cache_ms",
  [string]$ModelSource = "modelscope",
  [int]$TimeoutSec = 120
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $InputFile)) {
  throw "Missing $InputFile. Download or prepare the real-shot eval package first."
}

if (-not $PythonExe) {
  if (Test-Path "C:\pocrgpu312\Scripts\python.exe") {
    $PythonExe = "C:\pocrgpu312\Scripts\python.exe"
  } elseif (Test-Path "C:\pocr312\Scripts\python.exe") {
    $PythonExe = "C:\pocr312\Scripts\python.exe"
  } else {
    $PythonExe = "python"
  }
}

& $PythonExe scripts\check_realshot_qc.py --output outputs\realshot_qc_check.json

& $PythonExe scripts\run_paddleocrvl_timeout_batch.py `
  --python-exe $PythonExe `
  --root . `
  --input $InputFile `
  --output-dir $OutputDir `
  --source-id realshot_mendeley_bilingual_1000 `
  --pipeline-version $PipelineVersion `
  --cache-root $CacheRoot `
  --model-source $ModelSource `
  --timeout-sec $TimeoutSec
