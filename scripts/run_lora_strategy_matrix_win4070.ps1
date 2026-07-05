param(
  [string]$Python = "C:\pocrgpu312\Scripts\python.exe",
  [ValidateSet("rank4", "rank16", "aug_rank8", "hard_focus_rank8")]
  [string]$Experiment = "rank4",
  [string]$RunName = ""
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

Push-Location $RepoRoot
try {
  & $Python scripts\make_lora_experiment_configs.py

  if ($Experiment -eq "aug_rank8") {
    & $Python scripts\build_augmented_word_sft_manifest.py --include-original
  }
  if ($Experiment -eq "hard_focus_rank8") {
    & $Python scripts\build_hard_word_sft_manifest.py --limit 512
  }

  $Config = "configs\experiments\erniekit_paddleocr_vl_lora_word_${Experiment}_win4070.yaml"
  $OutputRoot = "outputs\medrxocr_lora_strategy_${Experiment}_win4070"
  & powershell -ExecutionPolicy Bypass -File scripts\run_lora_sft_win4070.ps1 `
    -Python $Python `
    -Config $Config `
    -OutputRoot $OutputRoot `
    -RunName $RunName `
    -MaxSteps 0 `
    -SaveSteps 0 `
    -EvalSteps 0 `
    -LoggingSteps 0
}
finally {
  Pop-Location
}
