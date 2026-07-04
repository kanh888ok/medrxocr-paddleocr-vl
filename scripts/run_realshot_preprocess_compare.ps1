param(
  [string]$PythonExe = "C:\pocrgpu312\Scripts\python.exe",
  [int]$TimeoutSec = 120,
  [string[]]$Variants = @("resize_long_1280", "contrast_sharp_1280", "gray_autocontrast_sharp_1280")
)

$ErrorActionPreference = "Stop"

if (!(Test-Path $PythonExe)) {
  throw "Python environment not found: $PythonExe"
}

& $PythonExe scripts\build_realshot_preprocess_variants.py `
  --input data\eval\realshot_eval_18.jsonl `
  --output-root data\eval\realshot_preprocessed `
  --manifest-dir data\eval `
  --variants ($Variants -join ",")

foreach ($Variant in $Variants) {
  $InputFile = "data\eval\realshot_eval_18_$Variant.jsonl"
  $OutputDir = "outputs\paddleocrvl_v15_realshot_eval18_${Variant}_timeout"
  Write-Host "Running $Variant -> $OutputDir"
  & $PythonExe scripts\run_paddleocrvl_timeout_batch.py `
    --python-exe $PythonExe `
    --root . `
    --input $InputFile `
    --output-dir $OutputDir `
    --source-id realshot_mendeley_bilingual_1000 `
    --pipeline-version v1.5 `
    --cache-root C:\pocr_cache_ms `
    --model-source modelscope `
    --timeout-sec $TimeoutSec
}
