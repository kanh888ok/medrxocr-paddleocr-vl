# LoRA/SFT 说明

## 初始检查点

已发布一个初始检查点：

`https://aistudio.baidu.com/dataset/detail/384021/intro`

它用于继续训练和复现实验，不作为正式微调结果报告。正式指标需要在固定评估集上重新评测后再写入文档。

## 生成训练清单

普通 SFT 清单：

```bash
python scripts/build_sft_manifest.py \
  --input data/processed/medrxocr_train.jsonl \
  --output data/processed/train_rx_sft.jsonl
```

ERNIEKit 格式：

```bash
python scripts/build_erniekit_vl_sft_manifest.py \
  --input data/processed/medrxocr_train.jsonl \
  --output data/processed/train_rx_erniekit_sft.jsonl
```

验证集同理，将输入换成 `data/processed/medrxocr_val.jsonl`。

## 训练配置

配置文件：

```text
configs/erniekit_paddleocr_vl_lora_medrxocr.yaml
```

## 结果口径

当前表格中的指标是 PaddleOCR-VL / PaddleOCR-VL-1.5 的 zero-shot 词图识别基线。

初始检查点需要单独说明，不能写成“微调后指标已完成”。
