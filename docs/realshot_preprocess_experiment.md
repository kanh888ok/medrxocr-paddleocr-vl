# 实拍预处理对比记录

## 目的

本次实验尝试在 `realshot_eval_18` 上做简单图像预处理，观察是否能减少 PaddleOCR-VL-1.5 的超时或降低 CER。

该实验是探索记录，不作为模型微调结果。

## 预处理版本

| 版本 | 处理方式 |
|---|---|
| `resize_long_1280` | RGB 转换，长边缩放到 1280 |
| `contrast_sharp_1280` | 自动对比度、轻微增强对比度和锐化，长边缩放到 1280 |
| `gray_autocontrast_sharp_1280` | 灰度化、自动对比度、轻微增强对比度和锐化，长边缩放到 1280 |

生成脚本：

```powershell
python scripts\build_realshot_preprocess_variants.py
```

批量评估脚本：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_realshot_preprocess_compare.ps1
```

## 小试结果

先选取两个样本做小试，避免直接跑完整 18 张造成长时间等待：

- `0003`：原始图可以返回结果。
- `0012`：原始图在 120 秒阈值下超时。

| 图像 ID | 输入版本 | 结果 | CER | 耗时 |
|---|---|---|---:|---:|
| `0003` | 原始实拍图 | 成功 | 0.9008 | 24.76 秒 |
| `0003` | `resize_long_1280` | 超时 | - | 90.02 秒 |
| `0003` | `gray_autocontrast_sharp_1280` | 超时 | - | 90.02 秒 |
| `0012` | 原始实拍图 | 超时 | - | 120.05 秒 |
| `0012` | `resize_long_1280` | 超时 | - | 90.03 秒 |
| `0012` | `gray_autocontrast_sharp_1280` | 超时 | - | 90.02 秒 |

## 结论

这轮简单预处理没有带来收益。缩放和灰度增强不但没有解决 `0012` 的超时，还让原本能返回的 `0003` 出现超时。

因此这类简单预处理不作为当前优化结果。真实拍摄场景中，简单缩放、对比度增强和灰度化没有稳定改善 PaddleOCR-VL-1.5 的推理表现。后续实验可以继续检查文档区域裁剪、透视校正、版面区域分块识别和 LoRA/SFT 微调。

## 复查文件

```text
scripts/build_realshot_preprocess_variants.py
scripts/run_realshot_preprocess_compare.ps1
outputs/realshot_preprocess_pilot_summary.json
```
