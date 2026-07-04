# 实拍评估基线

## 评估口径

本次评估使用 `realshot_eval_18` 子集。该子集来自固定 eval 集中的 18 张处方图片，实拍后不重新标注，沿用原图标注，仅替换图像输入。

评估模型为 PaddleOCR-VL-1.5，属于零样本基线，不是微调后结果。

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

超时样本：

```text
0012, 0026, 0033, 0269, 0272, 0281, 0312
```

结果文件：

```text
outputs/paddleocrvl_v15_realshot_eval18_gpu_timeout/metrics.json
outputs/paddleocrvl_v15_realshot_eval18_gpu_timeout/predictions.jsonl
```

## 结论

PaddleOCR-VL-1.5 可以在实拍子集上运行，但零样本效果较弱，且部分样本在 120 秒内没有返回结果。该结果说明真实拍摄场景对模型有明显挑战，后续需要继续做图像预处理、LoRA/SFT 微调和错误分析。

## 复现命令

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_realshot_eval_timeout.ps1
```

如需单张无超时测试，可使用：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_realshot_eval.ps1 -Limit 1
```
