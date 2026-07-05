# Windows 快速开始

这里分三种情况：只看 Demo、只复查已有结果、重新处理数据。没有 GPU 也可以先跑 Demo 和单元测试；完整 PaddleOCR-VL 推理需要本地模型和 CUDA 环境。

## 0. 只看 Demo 和已有结果

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-demo.txt
streamlit run demo\app.py
```

Demo 自带脱敏样例，不需要下载原始数据。已有指标可直接查看：

```text
outputs/lora_eval1115_realshot_summary.json
outputs/lora_strategy_experiment_summary.json
docs/technical_report.md
docs/lora_strategy_experiments.md
```

轻量代码检查：

```powershell
python -m pip install -r requirements.txt
python -m unittest discover -s tests
```

## 1. 准备环境

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 2. 下载数据

按 `docs/data_acquisition_plan.md` 中的数据源下载文件，放到：

```text
data/raw/mendeley_bilingual/
data/raw/bd200/
data/raw/rxhandbd/
```

大文件也可以从 AI Studio 数据包下载：

```text
https://aistudio.baidu.com/dataset/detail/384020/intro
```

## 3. 转换数据

```powershell
python scripts\prepare_mendeley_bilingual.py --csv data\raw\mendeley_bilingual\annotations.csv --image-root data\raw\mendeley_bilingual\images --output data\interim\mendeley_bilingual.jsonl

python scripts\prepare_rxhandbd.py --labels data\raw\rxhandbd\train_labels.csv --image-root data\raw\rxhandbd\train --split train --output data\interim\rxhandbd_train.jsonl

python scripts\prepare_rxhandbd.py --labels data\raw\rxhandbd\test_labels.csv --image-root data\raw\rxhandbd\test --split eval --output data\interim\rxhandbd_eval.jsonl

python scripts\prepare_bangladesh_yolo.py --image-root data\raw\bd200\images --label-root data\raw\bd200\labels --output data\interim\bd200_regions.jsonl
```

## 4. 生成划分

```powershell
python scripts\create_submission_splits.py --mendeley data\interim\mendeley_bilingual.jsonl --rxhandbd-train data\interim\rxhandbd_train.jsonl --rxhandbd-eval data\interim\rxhandbd_eval.jsonl --bd200 data\interim\bd200_regions.jsonl --output-dir data\processed
```

## 5. 质量检查

```powershell
python scripts\quality_audit.py --annotations data\processed\medrxocr_train.jsonl --root . --output outputs\quality_train.json
python scripts\dataset_stats.py --annotations data\processed\medrxocr_train.jsonl --output outputs\stats_train.json
```

## 6. 生成训练清单

```powershell
python scripts\build_sft_manifest.py --input data\processed\medrxocr_train.jsonl --output data\processed\train_rx_sft.jsonl
python scripts\build_sft_manifest.py --input data\processed\medrxocr_val.jsonl --output data\processed\val_rx_sft.jsonl
```

## 7. 运行 demo

```powershell
pip install -r requirements-demo.txt
streamlit run demo\app.py
```

## 8. 复查已有评估

已有评估结果保存在 `outputs/` 和 `docs/`。如果本地已经准备好 PaddleOCR-VL 环境和模型目录，可以用下面脚本重新跑实拍子集：

```powershell
scripts\run_realshot_eval.ps1
```

公开词图评估脚本见：

```text
scripts/run_paddleocrvl_word_eval.py
scripts/run_paddleocrvl_worker_timeout_eval.py
```

这些脚本会读取本地数据和模型，不会从 GitHub 自动下载大文件。
