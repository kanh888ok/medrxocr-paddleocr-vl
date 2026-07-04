# 标注说明

## 目标

把处方图片转成统一 JSON 标注。看不清的内容写 `[UNK]`，不存在或无法判断的字段写 `null`。不要凭经验补内容。

当前公开标注主要覆盖：

- 整页 OCR 文本。
- 药品区域框。
- 手写药品词。

药品名、剂量、频次、疗程等结构化字段需要后续人工补充。

## 核心字段

```text
document_type
patient
visit
medications
doctor
full_ocr_text
regions
```

样本元数据：

```text
source_id
license
split
pii_redacted
language
visual_tags
difficulty
```

## 药品行字段

```json
{
  "drug_name_raw": "",
  "drug_name_normalized": "",
  "strength": "",
  "dose": "",
  "frequency": "",
  "route": "",
  "duration": "",
  "instruction": ""
}
```

## 标注规则

- `*_raw` 字段按图片原文填写，不自动纠错。
- 规范化字段只在证据明确时填写。
- 看不清的字不要猜。
- 缩写不要随意展开。
- 同一张图多人复核时，以图片证据为准。

## 隐私处理

以下信息需要脱敏或标记为不可用：

- 患者姓名。
- 电话。
- 身份证号或就诊号。
- 地址。
- 二维码或条形码。
- 可识别个人的医生签名或编号。

## 难度标签

`easy`：

- 图片清楚。
- 多数是印刷体。
- 没有明显遮挡。

`medium`：

- 有部分手写。
- 有轻微倾斜、印章、模糊。

`hard`：

- 手写很重。
- 印章或签名遮挡正文。
- 透视变形明显。
- 光线差或阴影重。
- 有折痕、遮挡、涂改。
- 药名罕见或缩写多。

## 视觉标签

可多选：

```text
handwritten
printed
mixed_printed_handwritten
bangla
english
mixed_language
blur
skew
perspective
shadow
stamp_overlap
signature_overlap
fold
wrinkle
occlusion
crossed_out
low_resolution
table_like_layout
```
