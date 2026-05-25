#!/usr/bin/env python3
"""Evaluate MedRxOCR predictions against gold JSONL."""

import argparse, json, re
from pathlib import Path
from collections import Counter

FIELD_PATHS = [
    ("document_type",),
    ("patient", "age"),
    ("patient", "sex"),
    ("visit", "date"),
    ("visit", "department"),
    ("visit", "diagnosis"),
    ("doctor", "signature_present"),
    ("doctor", "stamp_present"),
]
MED_SLOTS = ["drug_name_normalized", "strength", "dose", "frequency", "route", "duration", "instruction"]

def norm(x):
    if x is None: return ""
    x = str(x).lower().strip()
    x = re.sub(r"\s+", " ", x)
    return x

def get(obj, path):
    cur = obj
    for p in path:
        if not isinstance(cur, dict): return None
        cur = cur.get(p)
    return cur

def load(path):
    rows = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip(): continue
        row = json.loads(line)
        rows[row["image_id"]] = row
    return rows

def ann(row):
    return row.get("annotation") or row.get("prediction") or row

def f1(gold_items, pred_items):
    g, p = Counter(gold_items), Counter(pred_items)
    tp = sum((g & p).values())
    fp = sum((p - g).values())
    fn = sum((g - p).values())
    if tp == fp == fn == 0: return 1.0, tp, fp, fn
    if tp == 0: return 0.0, tp, fp, fn
    return 2 * tp / (2 * tp + fp + fn), tp, fp, fn

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--gold", required=True)
    p.add_argument("--pred", required=True)
    p.add_argument("--output", default=None)
    args = p.parse_args()

    gold = load(args.gold)
    pred = load(args.pred)
    ids = sorted(set(gold) & set(pred))
    if not ids:
        raise SystemExit("No overlapping image_id.")

    correct = total = 0
    g_items, p_items = [], []
    json_valid = 0

    for image_id in ids:
        g = ann(gold[image_id])
        pr = ann(pred[image_id])
        if isinstance(pr, dict): json_valid += 1

        for path in FIELD_PATHS:
            total += 1
            correct += int(norm(get(g, path)) == norm(get(pr, path)))

        for m in g.get("medications", []) if isinstance(g.get("medications", []), list) else []:
            for slot in MED_SLOTS:
                g_items.append(f"{slot}={norm(m.get(slot))}")
        for m in pr.get("medications", []) if isinstance(pr.get("medications", []), list) else []:
            for slot in MED_SLOTS:
                p_items.append(f"{slot}={norm(m.get(slot))}")

    med_f1, tp, fp, fn = f1(g_items, p_items)
    res = {
        "n_images": len(ids),
        "json_valid_rate": json_valid / len(ids),
        "field_exact_accuracy": correct / total if total else 0,
        "metric_scope": "Lightweight slot-level baseline metric; medication slots are pooled as a multiset and are not strictly aligned by image row or clinical field instance.",
        "medication_slot_f1": med_f1,
        "medication_slot_tp": tp,
        "medication_slot_fp": fp,
        "medication_slot_fn": fn
    }
    text = json.dumps(res, ensure_ascii=False, indent=2)
    print(text)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")

if __name__ == "__main__":
    main()
