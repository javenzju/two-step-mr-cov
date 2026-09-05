# -*- coding: utf-8 -*-
"""
M4b ρ_MY 实证估计 (纯 Python, 绕开段错误 R 包)
=================================================================================
用户核心批评: 论文的卖点 "ρ_MY>0 会导致 CI 变宽/翻转" 一直停留在理论模拟网格,
8 个真实重叠案例的 ρ_MY 全被设成 0, 从未从真实数据估计。

本脚本: 对 6 个干净的非零重叠真实案例, 从中介 GWAS 与结局 GWAS 的 harmonized
per-SNP 效应量直接估计中介-结局的"方向一致性/遗传相关" ρ_MY^emp, 并:
  (1) 报告经验分布 (多少例为正, 均值/范围/95%CI);
  (2) 把经验 ρ 代入 S10 校正, 复算经验 widen_pct, 与 rho=0 基线对照;
  (3) 区分 S10 字面参数(样本重叠) 与本脚本估计量(遗传相关/方向一致性), 透明处理。

数据来源:
  - X = tophits(exp_id)               -> β_ZX (暴露效应, 缓存)
  - M = tophits(med_id)               -> β_ZM@M (中介效应, 缓存)
  - a_med = get_associations(X, mid)  -> β_ZM@X (缓存, stage2 已拉)
  - a_out = get_associations(M, oid)  -> β_ZY@M (缓存, stage2 已拉)
  - [新拉] a_outX = get_associations(X, oid) -> β_ZY@X
  - [新拉] a_XM   = get_associations(M, exp_id)-> β_ZX@M
所有 β 经 OpenGWAS 对齐到同一参考等位, 本脚本再按参考方向统一翻转, 保证可比。

估算量:
  ρ_M  : Pearson(β_ZM@M, β_ZY@M)  over M SNPs        (仅缓存, 无新拉)
  ρ_X  : Pearson(β_ZM@X, β_ZY@X)  over X SNPs        (需 a_outX 新拉)
  ρ_res: 对 X 路径残差化后 Pearson(resid_M, resid_Y)  (需 a_XM + a_outX)
Fisher-z 给 95%CI。主指标取 n 较大者 (ρ_M 或 ρ_X)。
输出: temp/M4b_rhoMY_empirical_20260904.csv + 同名 .log
"""
import os, sys, json, time, csv, math, importlib.util
sys.path.insert(0, r"D:/WorkBuddy/两步法MR中介/③ 真实数据应用")
PROJ = r"D:/WorkBuddy/两步法MR中介"
TEMP = os.path.join(PROJ, "③ 真实数据应用", "temp")
LOGD = os.path.join(PROJ, "③ 真实数据应用", "log")
os.makedirs(TEMP, exist_ok=True); os.makedirs(LOGD, exist_ok=True)
LOG = os.path.join(LOGD, "M4b_rhoMY_empirical_20260904.log"); LOG_L = []
def L(m):
    s = f"[{time.strftime('%H:%M:%S')}] {m}"; print(s); LOG_L.append(s)

pb = importlib.import_module("M4b_phaseB_pipeline")
get_tophits = pb.get_tophits; get_associations = pb.get_associations; harmonize_ivw = pb.harmonize_ivw
import importlib
s10 = importlib.import_module("M4b_s10_cov")
estimate_cov_prod_mr = s10.estimate_cov_prod_mr; corrected_se = s10.corrected_se

import numpy as np

def align(beta_ref_ea, beta_ref_nea, rec):
    """把 rec(ea/nea/beta) 对齐到参考方向(ref_ea/ref_nea), 返回带符号 beta 或 None"""
    if rec is None: return None
    if rec["ea"] == beta_ref_ea: return rec["beta"]
    if rec["nea"] and rec["ea"] == beta_ref_nea: return -rec["beta"]
    return None  # 模糊, 丢弃

def pearson_ci(xs, ys):
    xs = np.asarray(xs, float); ys = np.asarray(ys, float)
    n = len(xs)
    if n < 4: return (float("nan"), float("nan"), float("nan"), n)
    r = float(np.corrcoef(xs, ys)[0, 1])
    if abs(r) >= 1: r = math.copysign(0.999999, r)
    z = 0.5 * math.log((1 + r) / (1 - r))
    se = 1.0 / math.sqrt(n - 3)
    lo = math.tanh(z - 1.96 * se); hi = math.tanh(z + 1.96 * se)
    return (r, lo, hi, n)

# ---- 载入 6 候选 + 基线(stage2 rho=0) ----
BASE = os.path.join(TEMP, "M4b_stage2_recompute_20260904.csv")
base_rows = {r["study_id"]: r for r in csv.DictReader(open(BASE, encoding="utf-8-sig"))}
CLEAN = ["S014", "S273", "S255", "S137", "S217", "S267"]   # 干净非零重叠 (S320/S293 exp==med 退化, 排除)
CASE_META = {
    "S014": ("ebi-a-GCST90018925", "ieu-b-5144", "ukb-d-I9_CORATHER"),
    "S273": ("ebi-a-GCST90029003", "ebi-a-GCST90029016", "ebi-a-GCST90018866"),
    "S255": ("ebi-a-GCST90002406", "ebi-a-GCST90025992", "finn-b-CD2_LYMPHOID_LEUKAEMIA_EXALLC"),
    "S137": ("ieu-b-4812", "ebi-a-GCST90025990", "ebi-a-GCST90038646"),
    "S217": ("ebi-a-GCST90038685", "ebi-a-GCST90018991", "ebi-a-GCST90018801"),
    "S267": ("ebi-a-GCST90025967", "ebi-a-GCST90092943", "finn-b-H7_OCUMUSCLE"),
}

out_fields = ["study_id", "exposure", "mediator", "outcome",
              "n_X", "n_M", "n_shared", "pi_shared",
              "rho_M", "rho_M_lo", "rho_M_hi", "n_rho_M",
              "rho_X", "rho_X_lo", "rho_X_hi", "n_rho_X",
              "rho_resid", "rho_resid_lo", "rho_resid_hi", "n_rho_resid",
              "primary_rho", "primary_source", "primary_n",
              "widen_pct_rho0", "widen_pct_empirical", "flip_empirical",
              "ci_corr_lo_emp", "ci_corr_hi_emp", "naive_sig", "corr_sig_emp",
              "notes"]
res = []
for sid in CLEAN:
    eid, mid, oid = CASE_META[sid]
    b = base_rows[sid]
    L(f"\n=== {sid}: {b['exposure'][:18]} -> {b['mediator'][:18]} -> {b['outcome'][:18]} ===")
    X = get_tophits(eid); M = get_tophits(mid)
    a_med = get_associations(list(X.keys()), mid)     # β_ZM@X (缓存)
    a_out = get_associations(list(M.keys()), oid)     # β_ZY@M (缓存)
    a_outX = get_associations(list(X.keys()), oid)    # β_ZY@X (新拉)
    a_XM = get_associations(list(M.keys()), eid)  # β_ZX@M (新拉)
    # ---- ρ_M : 在 M SNPs 上, 以 M(tophits) 方向为参考, 对齐 β_ZY ----
    bm, by = [], []
    for rs, ex in M.items():
        bzm = ex["beta"]                      # β_ZM@M (参考方向)
        bzy = align(ex["ea"], ex["nea"], a_out.get(rs))
        if bzy is None: continue
        bm.append(bzm); by.append(bzy)
    rho_M, lo_M, hi_M, n_Mr = pearson_ci(bm, by)
    # ---- ρ_X : 在 X SNPs 上, 以 X(tophits) 方向为参考, 对齐 β_ZM, β_ZY ----
    bxm, bxy = [], []
    for rs, ex in X.items():
        bzm = align(ex["ea"], ex["nea"], a_med.get(rs))   # β_ZM@X
        bzy = align(ex["ea"], ex["nea"], a_outX.get(rs))   # β_ZY@X
        if bzm is None or bzy is None: continue
        bxm.append(bzm); bxy.append(bzy)
    rho_X, lo_X, hi_X, n_Xr = pearson_ci(bxm, bxy)
    # ---- ρ_resid : 在 M SNPs 上残差化 X 路径 ----
    a_hat = float(b["alpha_hat"]); beta_hat = float(b["beta_hat"])
    # β_XY = IVW(X -> Y), 固定效应, 直接算
    bx_y, by_y, se_y = [], [], []
    for rs, ex in X.items():
        bxy_ = align(ex["ea"], ex["nea"], a_outX.get(rs))
        sy = a_outX.get(rs)
        if bxy_ is None or sy is None or not sy.get("se"): continue
        bx_y.append(ex["beta"]); by_y.append(bxy_); se_y.append(sy["se"])
    if len(bx_y) >= 2:
        ws = [(bx ** 2) / (sy ** 2) for bx, sy in zip(bx_y, se_y)]
        W = sum(ws)
        g = [by_ / bx_ for bx_, by_ in zip(bx_y, by_y)]
        beta_XY = sum(w * gi for w, gi in zip(ws, g)) / sum(w * (bx_ ** 2) for w, bx_ in zip(ws, bx_y)) * sum(ws) / sum(ws)
        # 上式简化为 Σ(w*g)/Σ(w) ; 直接:
        beta_XY = sum(w * gi for w, gi in zip(ws, g)) / W
    else:
        beta_XY = float("nan")
    rm, ry = [], []
    for rs, ex in M.items():
        bzx = align(ex["ea"], ex["nea"], a_XM.get(rs))   # β_ZX@M
        bzy = align(ex["ea"], ex["nea"], a_out.get(rs))  # β_ZY@M
        if bzx is None or bzy is None: continue
        rm.append(ex["beta"] - a_hat * bzx)              # resid_M
        ry.append(bzy - (beta_XY if not math.isnan(beta_XY) else 0) * bzx)  # resid_Y
    rho_res, lo_r, hi_r, n_res = pearson_ci(rm, ry)
    # ---- 主指标: 取 n 较大者 ----
    if n_Mr >= n_Xr:
        prim, plo, phi, pn, psrc = rho_M, lo_M, hi_M, n_Mr, "rho_M"
    else:
        prim, plo, phi, pn, psrc = rho_X, lo_X, hi_X, n_Xr, "rho_X"
    L(f"  ρ_M={rho_M:+.3f} (95%CI {lo_M:+.3f},{hi_M:+.3f}, n={n_Mr})  [仅缓存]")
    L(f"  ρ_X={rho_X:+.3f} (95%CI {lo_X:+.3f},{hi_X:+.3f}, n={n_Xr})  [新拉β_ZY@X]")
    L(f"  ρ_resid={rho_res:+.3f} (95%CI {lo_r:+.3f},{hi_r:+.3f}, n={n_res})  [残差化]")
    L(f"  主指标 primary_rho={prim:+.3f} (source={psrc}, n={pn})")
    # ---- 代入 S10: 经验 ρ vs rho=0 ----
    se_a = float(b["se_alpha"]); se_b = float(b["se_beta"])
    n_shared = int(float(b["n_shared"])); p_X = int(float(b["n_X"])); p_M = int(float(b["n_M"]))
    F = float(b["F_X"]); N_X = int(float(b["N_X"])); N_M = int(float(b["N_M"])); N_Y = int(float(b["N_Y"]))
    cov0, _, _ = estimate_cov_prod_mr(se_a, se_b, n_shared, p_X, p_M, F, N_X, N_M, N_Y, rho_MY=0)
    _, _, se_c0, w0 = corrected_se(float(b["alpha_hat"]), beta_hat, se_a, se_b, cov0)
    covE, _, _ = estimate_cov_prod_mr(se_a, se_b, n_shared, p_X, p_M, F, N_X, N_M, N_Y, rho_MY=prim)
    ind, se_naive, se_cE, wE = corrected_se(float(b["alpha_hat"]), beta_hat, se_a, se_b, covE)
    ci_cl = ind - 1.96 * se_cE; ci_ch = ind + 1.96 * se_cE
    naive_sig = "是" if abs(ind) > 1.96 * se_naive else "否"
    corr_sig = "是" if abs(ind) > 1.96 * se_cE else "否"
    flipE = "翻转!" if naive_sig != corr_sig else "无翻转"
    L(f"  widen_pct: rho=0 -> {w0:+.1f}% ; 经验ρ={prim:+.3f} -> {wE:+.1f}%")
    L(f"  CI(经验ρ): [{ci_cl:.4f},{ci_ch:.4f}]  naive_sig={naive_sig} corr_sig={corr_sig} -> {flipE}")
    notes = (f"β_XY(IVW)={beta_XY:.4f}; ρ_MY字面=样本重叠(元数据); 本估计量=遗传相关/方向一致性; "
             f"S320/S293 exp==med 退化已排除")
    res.append({"study_id": sid, "exposure": b["exposure"], "mediator": b["mediator"], "outcome": b["outcome"],
                "n_X": p_X, "n_M": p_M, "n_shared": n_shared, "pi_shared": b["pi_shared"],
                "rho_M": round(rho_M, 4), "rho_M_lo": round(lo_M, 4), "rho_M_hi": round(hi_M, 4), "n_rho_M": n_Mr,
                "rho_X": round(rho_X, 4), "rho_X_lo": round(lo_X, 4), "rho_X_hi": round(hi_X, 4), "n_rho_X": n_Xr,
                "rho_resid": round(rho_res, 4), "rho_resid_lo": round(lo_r, 4), "rho_resid_hi": round(hi_r, 4), "n_rho_resid": n_res,
                "primary_rho": round(prim, 4), "primary_source": psrc, "primary_n": pn,
                "widen_pct_rho0": round(w0, 1), "widen_pct_empirical": round(wE, 1), "flip_empirical": flipE,
                "ci_corr_lo_emp": round(ci_cl, 5), "ci_corr_hi_emp": round(ci_ch, 5),
                "naive_sig": naive_sig, "corr_sig_emp": corr_sig, "notes": notes})

with open(os.path.join(TEMP, "M4b_rhoMY_empirical_20260904.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=out_fields); w.writeheader(); w.writerows(res)
# ---- 汇总 ----
L("")
L("="*60); L("ρ_MY 实证估计汇总 (6 个干净非零重叠真实案例)")
pos = [r for r in res if r["primary_rho"] > 0]
L(f"  主指标为正(ρ>0): {len(pos)}/{len(res)}")
L(f"  primary_rho 范围: {min(r['primary_rho'] for r in res):+.3f} ~ {max(r['primary_rho'] for r in res):+.3f}")
L(f"  ρ_M 范围: {min(r['rho_M'] for r in res):+.3f} ~ {max(r['rho_M'] for r in res):+.3f}")
L(f"  ρ_X 范围: {min(r['rho_X'] for r in res):+.3f} ~ {max(r['rho_X'] for r in res):+.3f}")
L(f"  ρ_resid 范围: {min(r['rho_resid'] for r in res):+.3f} ~ {max(r['rho_resid'] for r in res):+.3f}")
L(f"  经验ρ下 widen_pct 范围: {min(r['widen_pct_empirical'] for r in res):+.1f}% ~ {max(r['widen_pct_empirical'] for r in res):+.1f}%")
L(f"  经验ρ下翻转: {sum(1 for r in res if r['flip_empirical'].startswith('翻转'))}")
with open(LOG, "w", encoding="utf-8") as f: f.write("\n".join(LOG_L))
L(f"[done] temp/M4b_rhoMY_empirical_20260904.csv ; log: {LOG}")
