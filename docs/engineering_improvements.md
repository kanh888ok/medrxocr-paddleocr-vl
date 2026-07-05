# 工程化改进记录

## 已采纳

本轮优先处理不依赖真实线下处方的数据和工程问题：

- 将 CER、Exact Match、字符错误统计等公共逻辑放入 `src/medrxocr/evaluation/`。
- 将 JSONL 读取、过滤和 JSON 写出放入 `src/medrxocr/data/`。
- 增加文本和图片工具函数，放入 `src/medrxocr/utils/`。
- 新增 `scripts/analyze_word_eval.py`，可从预测文件生成错误分析和耗时报告。
- 更新 `scripts/run_paddleocrvl_word_eval.py`，增加慢样本标记、渐进式 `max_new_tokens` 配置和断点续跑记录。
- 新增 `tests/`，使用 Python 自带 `unittest`，不引入额外测试依赖。
- 新增轻量 GitHub Actions，只跑单元测试，不下载模型和数据。

## 当前分析结果

LoRA step512 在固定 500 张公开 RxHandBD 词图上：

- Exact Match：0.2960
- Mean CER：0.4059
- Micro CER：0.3954
- 平均推理耗时：1.31s
- P95 推理耗时：1.97s
- 超过 10s 的慢样本：0

realshot_eval_18 上：

- 18 张中 11 张返回结果，7 张超时。
- Mean CER：0.9542
- Micro CER：0.9124
- 平均推理耗时：63.77s
- P95 推理耗时：120.03s

这说明公开词图任务已经有稳定微调收益，但实拍整页处方仍是主要难点。

## 可复现命令

```powershell
python -m unittest discover -s tests

python scripts\summarize_word_eval.py `
  --baseline outputs\paddleocrvl_v1_local_rxhandbd_word_eval500_max32\predictions.jsonl `
  --lora outputs\paddleocrvl_lora_word_full_lr2e5_step512_rxhandbd_eval500_max32\predictions.jsonl `
  --output outputs\lora_word_eval500_comparison.json `
  --cutoffs 100 300 400 500

python scripts\analyze_word_eval.py `
  --predictions outputs\paddleocrvl_lora_word_full_lr2e5_step512_rxhandbd_eval500_max32\predictions.jsonl `
  --output-json outputs\error_analysis_lora_eval500.json `
  --output-md docs\error_analysis_lora_eval500.md
```

## 暂缓项

- W&B/MLflow 暂不接入，避免增加账号、网络和依赖成本。
- Docker 镜像暂不补，PaddleOCR-VL 和 ERNIEKit 的 GPU 环境较重，后续可单独做。
- 数据增强先保留为实验方向，避免在没有完整对比前影响当前稳定结论。
