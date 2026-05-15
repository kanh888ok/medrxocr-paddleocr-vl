# MedRxOCR Annotation Guideline

## 1. 标注目标

把处方图像转为结构化 JSON。不要凭空推断；看不清就标 `[UNK]`；缺失字段标 `null`。

## 2. 输出 schema

核心字段：

- document_type
- patient
- visit
- medications
- doctor
- full_ocr_text
- regions
- visual_tags
- difficulty

## 3. 药品行字段

每个药品行：

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

## 4. 规则

### 原始字段

- `*_raw`：保持图像原文。
- 不扩写，不纠错。

### 规范字段

- `*_normalized`：小写、标准拼写、统一单位。
- 药品名可用 RxNorm/NMPA 词典辅助。

### 隐私字段

以下一律脱敏：

- 患者姓名
- 电话
- 身份证/病人 ID
- 地址
- 二维码/条形码
- 医生注册号
- 医生签名如构成可识别身份

## 5. 难度标签

### easy

- 清晰扫描/拍照
- 主要为印刷体
- 无明显遮挡

### medium

- 有少量手写、印章、轻微倾斜、轻微模糊

### hard

满足任一：

- 大量医生手写
- 印章/签名遮挡
- 明显透视畸变
- 强阴影或低光
- 折痕/遮挡/涂改
- 药品名罕见或缩写严重

## 6. visual_tags

可多选：

- handwritten
- printed
- mixed_printed_handwritten
- bangla
- english
- mixed_language
- blur
- skew
- perspective
- shadow
- stamp_overlap
- signature_overlap
- fold
- wrinkle
- occlusion
- crossed_out
- low_resolution
- table_like_layout
