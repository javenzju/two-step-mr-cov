# -*- coding: utf-8 -*-
"""Analyze Chen Yan's blind re-code (FILLED csv) vs sealed key.
Mirrors compute_kappa_2nd.py normalization, then prints confusion matrices + disagreements.
This is a READ-ONLY diagnostic (no fabrication): it only reports what Chen Yan actually filled."""
import csv, io, os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
SECOND = os.path.join(HERE, "kappa_second_coder_chenyan_FILLED.csv")
KEY = os.path.join(HERE, "..", "kappa", "kappa_answer_key_20260903.csv")
MVMR_KEY_STUDIES = {"S168", "S235", "S236", "S230", "S351", "S406"}

def norm_key_iv(val, sid):
    if sid in MVMR_KEY_STUDIES:
        return "MVMR联合估计"
    v = (val or "").strip()
    if v == "无法判断":
        return "无法判断"
    if v == "":
        return ""
    return "分开选IV"

def norm_key_reports(val):
    v = (val or "").strip()
    if v.startswith("是"):
        return "是"
    if v.startswith("部分"):
        return "部分"
    if v.startswith("否"):
        return "否"
    return v

def load(path):
    with io.open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

second = load(SECOND)
key = {r["study_id"]: r for r in load(KEY)}

def confusion(field, norm_key=None):
    cats = []
    cm = defaultdict(lambda: defaultdict(int))
    pairs = []
    for r in second:
        sid = r["study_id"]
        if sid not in key:
            continue
        b = (r.get(field) or "").strip()
        kraw = key[sid].get(field, "")
        k = norm_key(kraw, sid) if norm_key else (kraw or "").strip()
        if b == "" or k == "":
            continue
        for c in (b, k):
            if c not in cats:
                cats.append(c)
        cm[b][k] += 1
        pairs.append((sid, b, k))
    cats.sort()
    print(f"\n=== {field} (n={len(pairs)}) ===")
    header = "blind \\ key".ljust(16) + "".join(c.ljust(14) for c in cats) + "rowTot"
    print(header)
    for b in cats:
        row = b.ljust(16) + "".join(str(cm[b][k]).ljust(14) for k in cats) + str(sum(cm[b].values()))
        print(row)
    coltot = "colTot".ljust(16) + "".join(str(sum(cm[b][k] for b in cats)).ljust(14) for k in cats)
    print(coltot)
    print("Disagreements:")
    nd = 0
    for sid, b, k in pairs:
        if b != k:
            nd += 1
            print(f"  {sid}: blind={b}  key={k}")
    print(f"  total disagreements = {nd}")

confusion("design_type")
confusion("IV_selection_strategy", norm_key_iv)
confusion("reports_overlap_risk", lambda v, s: norm_key_reports(v))
