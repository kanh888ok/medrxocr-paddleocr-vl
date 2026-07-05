# Demo 说明

这个 Demo 是演示原型，不是默认加载模型的在线 OCR 服务。它自带一个脱敏样例，别人 clone 仓库后可以直接运行，查看图片预览、OCR 文本、结构化 JSON 和当前评估结果。

运行方式：

```powershell
pip install -r requirements-demo.txt
streamlit run demo\app.py
```

页面包含三部分：

- 查看 PaddleOCR-VL baseline 与 LoRA 的评估对比。
- 查看内置脱敏样例，或上传图片预览。
- 粘贴 OCR 文本，并生成统一 JSON 结构。
- 可选启用本地 OCR 推理。

默认情况下 Demo 不会加载 PaddleOCR-VL，也不会调用 LoRA 模型。这样没有 GPU 的机器也能打开查看。

如需在页面内对上传图片做真实 OCR，需要：

- 本机已安装 PaddleOCR-VL 推理环境。
- 已准备 PaddleOCR-VL 或 LoRA 合并后的模型目录。
- 在页面里勾选“启用本地 OCR”，填写模型目录后再运行。

批量评估和正式指标仍建议使用 `scripts/run_paddleocrvl_*.py`。
