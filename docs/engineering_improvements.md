# 工程化改进记录

## 已采纳

- 将 CER、Exact Match、字符错误统计等公共逻辑放入 `src/medrxocr/evaluation/`。
- 将 JSONL 读取、过滤和 JSON 写出放入 `src/medrxocr/data/`。
- 增加文本和图片工具函数，放入 `src/medrxocr/utils/`。
- 新增 `scripts/analyze_word_eval.py`，可从预测文件生成错误分析和耗时报告。
- 更新 `scripts/run_paddleocrvl_word_eval.py`，增加慢样本标记、渐进式 `max_new_tokens` 配置和断点续跑记录。
- 新增 `tests/`，使用 Python 自带 `unittest`，不引入额外测试依赖。
- 新增轻量 GitHub Actions，只跑单元测试，不下载模型和数据。
- Demo 增加内置脱敏样例；本地 OCR 推理改为可选开关。

## 当前结果

公开 RxHandBD 词图 1115 张：

| 模型 | Exact Match | Mean CER | Micro CER |
|---|---:|---:|---:|
| PaddleOCR-VL 基线 | 0.2386 | 0.4327 | 0.4255 |
| LoRA step512 | 0.2682 | 0.3831 | 0.3783 |
| LoRA aug-light step512 | 0.2825 | 0.3754 | 0.3702 |

`realshot_eval_18`：

| 模型 | 成功返回 | 超时 | Mean CER | Micro CER |
|---|---:|---:|---:|---:|
| PaddleOCR-VL v1 本地模型 | 18 | 0 | 0.9297 | 0.8792 |
| LoRA step512 | 18 | 0 | 0.8729 | 0.8679 |

## 可复查命令

```powershell
python -m unittest discover -s tests

python scripts\analyze_word_eval.py `
  --predictions outputs\paddleocrvl_lora_word_full_lr2e5_step512_rxhandbd_eval500_max32\predictions.jsonl `
  --output-json outputs\error_analysis_lora_eval500.json `
  --output-md docs\error_analysis_lora_eval500.md
```

## 暂缓项

- W&B/MLflow 暂不接入，避免增加账号、网络和依赖成本。
- Docker 镜像暂不补，PaddleOCR-VL 和 ERNIEKit 的 GPU 环境较重，后续可单独做。
- 药品词典后处理还没系统做。
