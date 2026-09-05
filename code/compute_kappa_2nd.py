# -*- coding: utf-8 -*-
"""
compute_kappa_2nd.py
=====================
Compute inter-coder reliability for the SECOND (independent) coder against the
SEALED answer key.

This script NEVER fabricates the second coder's labels: it only runs when a real
second-coder CSV (filled from kappa_second_coder_template.csv) is provided. With
no such file it prints instructions and exits.

The second coder assessed THREE fields (codebook S1 / S7):
    design_type, IV_selection_strategy, reports_overlap_risk
These are the fields used throughout S7.2-S7.5.

Key normalisation
------------------
The sealed answer key stores IV_selection_strategy for a handful of studies as
long free-text notes rather than the canonical {MVMR联合估计, 分开选IV, 无法判断}
labels. To reproduce the published confusion matrix (S7.4) and kappa values, we
reconcile the key to the canonical labels using the paper's OWN published
per-study mapping:
  * IV_selection_strategy: studies S168, S235, S236, S230, S351, S406 are the
    six "MVMR joint estimation" keys (S7.4); studies whose key value is literally
    "无法判断" stay 无法判断; every other non-blank key value maps to 分开选IV.
  * reports_overlap_risk: the single key value "是(...)" collapses to "是".
Blank key entries are excluded per field (they are "not assessed"), exactly as in
S7.2 ("n (valid pairs)", "Blank excluded").

What it computes, per field and overall
--------------------------------------
  * n (valid pairs, blanks excluded)
  * observed agreement Po (%)
  * expected agreement Pe (chance)
  * Cohen's kappa = (Po - Pe) / (1 - Pe)
  * PABAK = 2*Po - 1  (prevalence-and-bias-adjusted kappa)
  * Pe -> 1 artifact flag (kappa collapses to ~0 because one category is absent
    from one coder -> chance agreement near-certain; MATHEMATICAL artifact, not
    disagreement; report observed agreement / PABAK instead)
  * bootstrap 95% CI for kappa and Po (1000 resamples, seed 2026)
  * macro-averaged kappa across non-artifact fields

IMPORTANT: the first coder is the AI (Claude); the second coder MUST be an
independent human. Do not paste the answer-key values back in.
"""
import argparse, csv, io, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

KEY_FIELDS = ["design_type", "IV_selection_strategy", "reports_overlap_risk"]

# Canonical label sets (for reporting only)
IV_CANON = ["MVMR联合估计", "分开选IV", "无法判断"]
REP_CANON = ["是", "部分", "否"]

# Per-study key normalisation derived from the published S7.4 confusion matrix.
MVMR_KEY_STUDIES = {"S168", "S235", "S236", "S230", "S351", "S406"}


def norm_key_iv(val, sid):
    """Reconcile the sealed key's IV_selection_strategy to canonical labels."""
    if sid in MVMR_KEY_STUDIES:
        return "MVMR联合估计"
    v = (val or "").strip()
    if v == "无法判断":
        return "无法判断"
    if v == "":
        return ""  # blank -> excluded as "not assessed"
    return "分开选IV"


def norm_key_reports(val):
    v = (val or "").strip()
    if v.startswith("是"):
        return "是"
    if v.startswith("部分"):
        return "部分"
    if v.startswith("否"):
        return "否"
    return v  # blank -> excluded


def load_csv(path):
    with io.open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def cohen_kappa(a, b):
    """Cohen's kappa for two aligned label vectors (nominal). Blanks excluded by caller."""
    a = [str(x).strip() for x in a]
    b = [str(x).strip() for x in b]
    n = len(a)
    agree = sum(1 for x, y in zip(a, b) if x == y and x != "")
    Po = agree / n if n else float("nan")
    cats = sorted(set(a) | set(b))
    cnt_a = {c: a.count(c) for c in cats}
    cnt_b = {c: b.count(c) for c in cats}
    Pe = sum((cnt_a[c] / n) * (cnt_b[c] / n) for c in cats) if n else float("nan")
    if Pe >= 1.0 - 1e-12:
        return Po, Pe, float("nan"), True   # Pe->1 artifact
    k = (Po - Pe) / (1 - Pe)
    return Po, Pe, k, False


def bootstrap(a, b, n_boot=1000, seed=2026):
    rng = np.random.default_rng(seed)
    n = len(a)
    kas, pos = [], []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        aa = [a[i] for i in idx]; bb = [b[i] for i in idx]
        if len(set(aa)) < 2 or len(set(bb)) < 2:
            continue
        Po, Pe, k, art = cohen_kappa(aa, bb)
        if not art and k == k:
            kas.append(k); pos.append(Po)
    kas = np.array(kas); pos = np.array(pos)
    def ci(v):
        return (float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))) if len(v) else (float("nan"), float("nan"))
    return ci(kas), ci(pos)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--second", default=os.path.join(HERE, "kappa_second_coder_template.csv"))
    ap.add_argument("--key", default=os.path.join(HERE, "kappa", "kappa_answer_key_20260903.csv"))
    ap.add_argument("--out", default=os.path.join(HERE, "kappa_2nd_report.csv"))
    ap.add_argument("--log", default=os.path.join(HERE, "compute_kappa_2nd.log"))
    args = ap.parse_args()

    log_lines = []
    def log(s=""):
        log_lines.append(str(s))
        print(s)

    second = load_csv(args.second)
    filled = [r for r in second if any((r.get(f) or "").strip() for f in KEY_FIELDS)]
    if len(filled) == 0:
        log("=" * 70)
        log("NO SECOND-CODER LABELS FOUND in: " + args.second)
        log("")
        log("This script does NOT fabricate the second coder's answers.")
        log("To compute kappa:")
        log("  1. Open kappa_second_coder_template.csv (blind context only).")
        log("  2. Fill design_type, IV_selection_strategy, reports_overlap_risk")
        log("     from the study full texts using the codebook (kappa_instructions.md).")
        log("  3. Re-run:  python compute_kappa_2nd.py")
        log("=" * 70)
        return

    log("=" * 70)
    log("Second-coder reliability  |  second=%s" % os.path.basename(args.second))
    log("                          |  key    =%s" % os.path.basename(args.key))
    log("")

    key = load_csv(args.key)
    keymap = {r["study_id"]: r for r in key}
    rows = []
    for r in filled:
        sid = r["study_id"]
        if sid in keymap:
            rows.append((sid, r, keymap[sid]))
    if not rows:
        log("ERROR: no study_id overlap between second coder file and answer key.")
        return

    report = [["field", "n_valid", "n_blank_excluded", "Po", "Pe", "kappa",
               "kappa_95CI_low", "kappa_95CI_high", "Po_95CI_low", "Po_95CI_high",
               "PABAK", "Pe_to_1_artifact"]]
    overall = []
    for fld in KEY_FIELDS:
        if fld == "design_type":
            a = [r2.get(fld, "").strip() for _, r2, _ in rows]
            b = [keymap[sid].get(fld, "").strip() for sid, _, _ in rows]
        elif fld == "IV_selection_strategy":
            a = [r2.get(fld, "").strip() for _, r2, _ in rows]
            b = [norm_key_iv(keymap[sid].get(fld, ""), sid) for sid, _, _ in rows]
        else:  # reports_overlap_risk
            a = [r2.get(fld, "").strip() for _, r2, _ in rows]
            b = [norm_key_reports(keymap[sid].get(fld, "")) for sid, _, _ in rows]
        # exclude blank pairs (either side)
        pa, pb, nblank = [], [], 0
        for x, y in zip(a, b):
            if x == "" or y == "":
                nblank += 1
                continue
            pa.append(x); pb.append(y)
        Po, Pe, k, art = cohen_kappa(pa, pb)
        kci, pci = bootstrap(pa, pb)
        pabak = (2 * Po - 1) if (Po == Po) else float("nan")
        flag = "YES (kappa=0 is artifact; report Po/PABAK)" if art else "no"
        log(f"  {fld:22s} n={len(pa):2d} (blank excl {nblank:2d})  "
            f"Po={Po:6.1%}  Pe={Pe:6.1%}  kappa={('%.2f'%k) if k==k else 'NaN':>5}  "
            f"PABAK={('%.2f'%pabak) if pabak==pabak else 'NaN':>5}  "
            f"{'[Pe->1 ARTIFACT]' if art else ''}")
        report.append([fld, len(pa), nblank, round(Po, 4), round(Pe, 4),
                       (round(k, 4) if k == k else ""),
                       round(kci[0], 4), round(kci[1], 4),
                       round(pci[0], 4), round(pci[1], 4),
                       (round(pabak, 4) if pabak == pabak else ""), flag])
        if not art and k == k:
            overall.append(k)

    if overall:
        macro = float(np.mean(overall))
        log(f"\n  Macro-averaged kappa (excl. Pe->1 fields) = {macro:.2f}")
        report.append(["OVERALL_macro", "", "", "", "", round(macro, 4), "", "", "", "", "", "avg of non-artifact fields"])
    else:
        log("\n  All fields hit the Pe->1 artifact; report observed agreement per field.")

    with io.open(args.out, "w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f).writerows(report)
    log(f"\n  Report written: {args.out}")
    log("=" * 70)

    with io.open(args.log, "w", encoding="utf-8-sig") as f:
        f.write("\n".join(log_lines) + "\n")


if __name__ == "__main__":
    main()
