param(
  [string]$ErnieRoot = "",
  [string]$Python = "C:\pocrgpu312\Scripts\python.exe"
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
if ([string]::IsNullOrWhiteSpace($ErnieRoot)) {
  $WorkspaceRoot = Split-Path $RepoRoot -Parent
  $ErnieRoot = Join-Path $WorkspaceRoot "work\ERNIE-release-v1.5"
}

if (-not (Test-Path $ErnieRoot)) {
  throw "ERNIE source not found: $ErnieRoot"
}
if (-not (Test-Path $Python)) {
  throw "Python not found: $Python"
}

$patcher = @'
from pathlib import Path
import site
import sys

ernie_root = Path(sys.argv[1])

def patch_file(path, replacements):
    text = path.read_text(encoding="utf-8")
    original = text
    for old, new in replacements:
        if new in text:
            continue
        if old not in text:
            raise RuntimeError(f"pattern not found in {path}: {old[:80]!r}")
        text = text.replace(old, new)
    if text != original:
        path.write_text(text, encoding="utf-8")
        print(f"patched {path}")
    else:
        print(f"already patched {path}")

model_utils = None
for site_dir in site.getsitepackages():
    candidate = Path(site_dir) / "paddleformers" / "transformers" / "model_utils.py"
    if candidate.exists():
        model_utils = candidate
        break
if model_utils is None:
    raise RuntimeError("paddleformers model_utils.py not found")

patch_file(
    model_utils,
    [
        (
            "    part_state_dict = {}\n",
            "    def _safe_slice_shape(py_safe_slice):\n"
            "        if hasattr(py_safe_slice, \"shape\"):\n"
            "            return py_safe_slice.shape\n"
            "        if hasattr(py_safe_slice, \"get_shape\"):\n"
            "            return py_safe_slice.get_shape()\n"
            "        raise AttributeError(\"safe tensor slice has neither shape nor get_shape\")\n\n"
            "    part_state_dict = {}\n",
        ),
        ("len(py_safe_slice_.shape)", "len(_safe_slice_shape(py_safe_slice_))"),
    ],
)

ernie_model = ernie_root / "ernie" / "modeling_paddleocr_vl_ernie.py"
patch_file(
    ernie_model,
    [
        (
            "        cache_position = paddle.arange(\n"
            "            past_seen_tokens, past_seen_tokens + sequence_length\n"
            "        )\n",
            "        if past_seen_tokens == 0 and target_length == sequence_length + 1:\n"
            "            target_length = sequence_length\n"
            "        cache_position = paddle.arange(\n"
            "            past_seen_tokens, past_seen_tokens + sequence_length\n"
            "        )\n",
        )
    ],
)

trainer = ernie_root / "erniekit" / "train" / "ocr_vl_sft" / "pretraining_trainer.py"
patch_file(
    trainer,
    [
        ("    def save_model(self, output_dir=None):", "    def save_model(self, output_dir=None, *args, **kwargs):"),
        (
            "        super().save_model(output_dir)\n",
            "        output_dir = output_dir or self.args.output_dir\n"
            "        super().save_model(output_dir)\n",
        ),
    ],
)
'@

$tmp = Join-Path $env:TEMP "medrxocr_patch_erniekit_windows.py"
Set-Content -LiteralPath $tmp -Value $patcher -Encoding UTF8
& $Python $tmp $ErnieRoot
