# -*- coding: utf-8 -*-
"""
D61_fill_kappa_template.py
Load the REAL second-coder blind re-code (kappa_recode_wb_20260904.csv) into the
public instrument code/kappa_second_coder_template.csv.

The second coder assessed THREE fields (per codebook S1 / S7):
    design_type, IV_selection_strategy, reports_overlap_risk
This script copies those labels verbatim (no fabrication) and keeps the blind
context columns (study_id / pmid / first_author_year / journal / title) so the
file remains a self-contained, inspectable record.

Run BEFORE compute_kappa_2nd.py.
"""
import csv, io, os

HERE = os.path.dirname(os.path.abspath(__file__))
RECODE = os.path.join("..", "③ 真实数据应用", "temp", "kappa_recode_wb_20260904.csv")
# fallback absolute path in case the relative path fails
RECODE_ABS = r"D:\WorkBuddy\两步法MR中介\③ 真实数据应用\temp\kappa_recode_wb_20260904.csv"
TEMPLATE = os.path.join(HERE, "kappa_second_coder_template.csv")

FIELDS = ["design_type", "IV_selection_strategy", "reports_overlap_risk"]
BLIND = ["study_id", "pmid", "first_author_year", "journal", "title"]


def load(path):
    with io.open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main():
    rec = load(RECODE if os.path.exists(RECODE) else RECODE_ABS)
    recmap = {r["study_id"]: r for r in rec}
    # preserve the template's blind context, overwrite the 3 coding columns
    with io.open(TEMPLATE, encoding="utf-8-sig", newline="") as f:
        tpl = list(csv.DictReader(f))
    out = []
    for row in tpl:
        sid = row["study_id"]
        r = recmap.get(sid, {})
        o = {c: row.get(c, "") for c in BLIND}
        for fld in FIELDS:
            o[fld] = (r.get(fld, "") or "").strip()
        out.append(o)
    cols = BLIND + FIELDS
    with io.open(TEMPLATE, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(out)
    filled = sum(1 for o in out if any(o[f] for f in FIELDS))
    print(f"Wrote {TEMPLATE}")
    print(f"  rows={len(out)}  rows_with_coding_labels={filled}")
    print(f"  fields={FIELDS}")
    # sanity: show the 3 disagreements on design_type (independence evidence)
    dis = [o["study_id"] for o in out if o["design_type"] == "不属于两步法MR中介-排除"]
    print(f"  design_type 'exclude' coded by 2nd coder: {dis}")


if __name__ == "__main__":
    main()
