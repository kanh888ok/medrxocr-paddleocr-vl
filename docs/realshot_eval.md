# 实拍评估子集

## 目的

为补充真实拍摄场景，项目从已匹配的处方图片中制作了一个小规模实拍子集。做法参考 Real5-OmniDocBench 的思路：不重新标注文字内容，只替换图像输入，用来观察模型在手机拍摄、倾斜、阴影、模糊和纸张边缘干扰下的表现。

## 当前结果

- 已读取 20 张手机实拍图片。
- 20 张均已匹配到 Mendeley bilingual prescription 原图。
- 其中 18 张对应固定 eval 集，可以作为严格实拍评估子集。
- 其中 2 张对应固定 train 集，只作为采集示例，不计入严格 eval 指标。

映射表见：

```text
docs/realshot_20_mapping.csv
```

本地生成文件：

```text
data/eval/realshot_images/
data/eval/realshot_20.jsonl
data/eval/realshot_eval_18.jsonl
data/eval/realshot_20_mapping.csv
```

`data/eval` 默认不提交到 GitHub。实拍图片如需公开，建议放到 AI Studio 数据包，并保留本文件和映射表作为说明。

## 可写入报告的口径

参考 Real5-OmniDocBench 的真实拍摄评估思路，从固定评估集中匹配出 18 张处方图片进行手机实拍。实拍后不重新标注，沿用原评估集标注，仅替换图像输入，用于补充测试模型在真实拍摄、倾斜、阴影、模糊和纸张边缘干扰条件下的识别能力。另有 2 张实拍样本匹配到训练集原图，仅作为采集示例，不计入严格评估结果。

## 不足

- 严格 eval 数量目前是 18 张，不是 20 张。
- 每张原图目前只有 1 个实拍版本，还没有覆盖 5 类固定拍摄场景。
- 还没有跑 PaddleOCR-VL 在该实拍子集上的指标。
- 实拍图片本体尚未发布到 AI Studio 数据包。

## 下一步

- 再补拍 2 张固定 eval 原图，使严格 eval 子集达到 20 张。
- 如时间允许，按正常拍摄、倾斜、弱光/阴影、纸张弯曲、屏幕/打印翻拍 5 类场景扩展。
- 跑一次 `realshot_eval_18.jsonl` 的 OCR 评测，并与原图 eval 结果对比。
