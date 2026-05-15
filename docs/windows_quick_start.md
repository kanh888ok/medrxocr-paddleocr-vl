# Windows Quick Start

## 1. 解压项目

```powershell
Expand-Archive .\MedRxOCR_competition_execution_pack.zip -DestinationPath .\MedRxOCR
cd .\MedRxOCR\MedRxOCR_competition_execution_pack
```

## 2. 建环境

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3. 下载数据

按 `docs/data_acquisition_plan.md` 打开 P0 数据源链接，下载到：

```text
data/raw/mendeley_bilingual/
data/raw/bd200/
data/raw/rxhandbd/
```

## 4. 转换数据

```powershell
python scripts\prepare_mendeley_bilingual.py --csv data\raw\mendeley_bilingual\annotations.csv --image-root data\raw\mendeley_bilingual\images --output data\interim\mendeley_bilingual.jsonl
```

## 5. 质控

```powershell
python scripts\quality_audit.py --annotations data\interim\mendeley_bilingual.jsonl --root . --output outputs\quality_report.json
python scripts\dataset_stats.py --annotations data\interim\mendeley_bilingual.jsonl --output outputs\dataset_stats.json
```

## 6. 构建 SFT

```powershell
python scripts\create_submission_splits.py --mendeley data\interim\mendeley_bilingual.jsonl --rxhandbd-train data\interim\rxhandbd_train.jsonl --rxhandbd-eval data\interim\rxhandbd_eval.jsonl --bd200 data\interim\bd200_regions.jsonl --output-dir data\processed

python scripts\build_sft_manifest.py --input data\processed\medrxocr_train.jsonl --output data\processed\train_rx_sft.jsonl
python scripts\build_sft_manifest.py --input data\processed\medrxocr_val.jsonl --output data\processed\val_rx_sft.jsonl
python scripts\build_sft_manifest.py --input data\processed\medrxocr_eval.jsonl --output data\processed\eval_rx_sft.jsonl
```

## 7. Demo

```powershell
streamlit run demo\app.py
```
