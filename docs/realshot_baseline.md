# 实拍评估基线

## 评估口径

本次评估使用 `realshot_eval_18` 子集。该子集来自固定 eval 集中的 18 张处方图片，实拍后不重新标注，沿用原图标注，仅替换图像输入。

早期评估模型为 PaddleOCR-VL-1.5，属于零样本基线，不是微调后结果。之后补充了 PaddleOCR-VL v1 本地模型与 LoRA step512 的同口径对比。

运行环境：

- GPU：NVIDIA GeForce RTX 4070 Laptop GPU
- PaddlePaddle GPU：3.3.1
- PaddleOCR：3.5.0
- 模型源：ModelScope
- 单张超时阈值：120 秒

## 结果

| 模型 | 图像数 | 成功返回 | 超时 | Mean CER（成功样本） | Micro CER（成功样本） | 平均耗时（成功样本） |
|---|---:|---:|---:|---:|---:|---:|
| PaddleOCR-VL-1.5 | 18 | 11 | 7 | 0.9542 | 0.9124 | 27.97 秒 |
| PaddleOCR-VL v1 本地模型 | 18 | 18 | 0 | 0.9297 | 0.8792 | 22.52 秒 |
| LoRA step512 | 18 | 18 | 0 | 0.8729 | 0.8679 | 27.07 秒 |

超时样本：

```text
0012, 0026, 0033, 0269, 0272, 0281, 0312
```

结果文件：

```text
outputs/paddleocrvl_v15_realshot_eval18_gpu_timeout/metrics.json
outputs/paddleocrvl_v15_realshot_eval18_gpu_timeout/predictions.jsonl
outputs/paddleocrvl_v1_local_realshot_eval18_layout_max128_worker_retry/metrics.json
outputs/paddleocrvl_lora_step512_realshot_eval18_max128/metrics.json
```

## 结论

PaddleOCR-VL-1.5 可以在实拍子集上运行，但零样本效果较弱，且部分样本在 120 秒内没有返回结果。

后续改用 warm-worker 评估方式后，PaddleOCR-VL v1 本地模型和 LoRA step512 均完成 18/18。LoRA 的 Micro CER 从 0.8792 降到 0.8679，提升幅度不大，但方向为正。该结果说明真实拍摄场景仍然困难，后续更需要扩大实拍样本、多拍摄条件和版面级切分。

## 复现命令

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_realshot_eval_timeout.ps1
```

同口径微调前后对比使用 warm-worker 脚本：

```powershell
python scripts\run_paddleocrvl_worker_timeout_eval.py --root . --input data\eval\realshot_eval_18.jsonl --output-dir outputs\paddleocrvl_v1_local_realshot_eval18_layout_max128_worker_retry --source-id realshot_mendeley_bilingual_1000 --pipeline-version v1 --vl-rec-model-dir ..\work\PaddlePaddle\PaddleOCR-VL --model-label PaddleOCR-VL-v1-local-realshot-layout-max128-worker-retry --max-new-tokens 128 --timeout-sec 90 --load-timeout-sec 180 --retries 2
```

如需单张无超时测试，可使用：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_realshot_eval.ps1 -Limit 1
```
