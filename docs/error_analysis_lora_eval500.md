# LoRA step512 500张词图错误分析

## 总览

- 样本数：500
- 可计分样本：500
- 错误/超时记录：0
- Exact Match：0.2960
- Mean CER：0.4059
- Micro CER：0.3954

## 推理耗时

- 平均耗时：1.31s
- P50：1.41s
- P95：1.97s
- P99：2.14s
- 最慢样本：2.24s
- 超过 10.0s 的样本数：0

## 字符错误

- matches: 2318
- substitutions: 844
- insertions: 274
- deletions: 219
- edit_distance: 1337

## 最差样本

- rxhandbd_eval_P0424：CER=7.75
- rxhandbd_eval_P0173：CER=3.6666666666666665
- rxhandbd_eval_P0231：CER=3.0
- rxhandbd_eval_P0021：CER=2.75
- rxhandbd_eval_P0267：CER=2.6
