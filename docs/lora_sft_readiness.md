# LoRA/SFT 启动检查

## 当前结论

当前本机环境可以运行 PaddleOCR-VL 推理评估，但还不能直接启动 LoRA/SFT 训练。

主要原因：

- `erniekit`、`paddlenlp`、`paddlemix`、`visualdl` 等训练依赖未安装。
- `data/processed` 中缺少训练集、验证集和 ERNIEKit SFT 清单。

因此现在不能把项目写成“已经完成微调训练”。比较稳妥的说法是：项目已提供训练清单生成脚本和 LoRA/SFT 配置，当前仍需补充正式训练环境、训练日志和微调后指标。

## 检查命令

```powershell
python scripts\check_training_env.py --output outputs\lora_sft_readiness.json
```

## 需要补齐

| 项目 | 当前状态 |
|---|---|
| PaddlePaddle GPU 推理环境 | 已具备 |
| PaddleOCR 推理环境 | 已具备 |
| ERNIEKit / PaddleNLP / PaddleMIX | 未安装 |
| `medrxocr_train.jsonl` | 本地未恢复 |
| `medrxocr_val.jsonl` | 本地未恢复 |
| ERNIEKit SFT train/val 清单 | 本地未生成 |
| LoRA/SFT 配置 | 已提供 |

## 下一步

如果要继续做微调，需要先恢复 AI Studio 数据包中的 `data/processed`，再安装训练依赖，随后先跑 20-100 条样本的小规模 smoke training。只有训练能正常保存 checkpoint 后，才适合跑完整小规模 LoRA/SFT 并报告微调后指标。
