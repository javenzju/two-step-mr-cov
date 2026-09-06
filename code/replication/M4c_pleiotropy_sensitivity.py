# -*- coding: utf-8 -*-
"""
M4c : 水平多效性稳健性检验 (horizontal-pleiotropy sensitivity analysis)
========================================================================
对 §3.4 中 5 个非退化重叠三元组 (S014/S137/S217/S273/S267) 的每一步
(X->M, M->Y) 做:
  * MR-Egger 截距检验 (Bowden 2017) -> 方向性多效性是否存在
  * 加权中位数 (weighted median) 交叉验证点估计方向
目的: 证明即使存在水平多效性, IVW 乘积估计的方向与协方差修正符号
      未被多效性扭曲 (即修正的稳健性不依赖于"IVW 无偏"这一强假设)。

复用 M4b_phaseB_pipeline.py 的 OpenGWAS REST 核心 (get_tophits/get_associations,
ProxyHandler({}) 绕代理, 缓存到 temp/). 不依赖 scipy, t 分布 p 值自实现。

输出: temp/M4c_pleiotropy.csv + 控制台摘要表.
"""
import os, time, sys, csv, math
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import M4b_phaseB_pipeline as PB   # reuse REST core

HERE = os.path.dirname(os.path.abspath(__file__))
TEMP = PB.TEMP
OUT  = os.path.join(TEMP, "M4c_pleiotropy.csv")

# ---- 5 个非退化重叠三元组 (accession 来自 temp/M4b_stage2_all_20260906.csv) ----
TRIOS = {
    "S014": ("ebi-a-GCST90018925", "ieu-b-5144",        "ukb-d-I9_CORATHER"),
    "S137": ("ieu-b-4812",          "ebi-a-GCST90025990","ebi-a-GCST90038646"),
    "S217": ("ebi-a-GCST90038685",  "ebi-a-GCST90018991","ebi-a-GCST90018801"),
    "S273": ("ebi-a-GCST90029003",  "ebi-a-GCST90029016","ebi-a-GCST90018866"),
    "S267": ("ebi-a-GCST90025967",  "ebi-a-GCST90092943","finn-b-H7_OCUMUSCLE"),
}

# ---------- 自包含 t 分布 CDF (regularized incomplete beta, Numerical Recipes) ----------
def _betacf(a, b, x):
    MAXIT, EPS, FPMIN = 300, 3e-12, 1e-300
    qab, qap, qam = a + b, a + 0.5, a - 0.5
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < FPMIN: d = FPMIN
    d = 1.0 / d
    h = d
    for m in range(1, MAXIT + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN: d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN: c = FPMIN
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN: d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN: c = FPMIN
        d = 1.0 / d
        del_ = d * c - 1.0
        h *= d * c
        if abs(del_) < EPS:
            break
    return h

def _betai(a, b, x):
    if x <= 0.0: return 0.0
    if x >= 1.0: return 1.0
    lbeta = (math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
             + a * math.log(x) + b * math.log(1.0 - x))
    bt = math.exp(lbeta)
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    else:
        return 1.0 - bt * _betacf(b, a, 1.0 - x) / b

def t_sf(t, df):
    """two-sided p-value for t statistic with df degrees of freedom."""
    if df < 1: return float('nan')
    x = df / (df + t * t)
    return min(1.0, max(0.0, _betai(0.5 * df, 0.5, x)))

# ---------- 等位方向匹配 (复用 M4b 逻辑) ----------
COMP = {"A":"T","T":"A","C":"G","G":"C"}
def align(inst, assoc):
    """inst: tophits dict (rsid->{ea,nea,beta,se}); assoc: assoc dict (rsid->{ea,nea,beta,se}).
    对齐到 inst 的效应等位基因, 返回 (bx, by, sy) 数组 + n_drop."""
    bx, by, sy = [], [], []
    miss = amb = zero = 0
    for rs, ex in inst.items():
        ay = assoc.get(rs)
        if ay is None: miss += 1; continue
        if ay["ea"] == ex["ea"]:
            b_out = ay["beta"]
        elif ay["ea"] == ex["nea"]:
            b_out = -ay["beta"]
        else:
            amb += 1; continue
        if ex["beta"] == 0 or ay["se"] == 0:
            zero += 1; continue
        bx.append(ex["beta"]); by.append(b_out); sy.append(ay["se"])
    return np.asarray(bx,float), np.asarray(by,float), np.asarray(sy,float), (miss, amb, zero)

# ---------- MR-Egger (Bowden 2017) ----------
def mr_egger(bx, by, sy):
    w = 1.0/sy**2
    n = len(bx)
    xbar = np.sum(w*bx)/np.sum(w); ybar = np.sum(w*by)/np.sum(w)
    Sxx = np.sum(w*(bx-xbar)**2); Sxy = np.sum(w*(bx-xbar)*(by-ybar))
    slope = Sxy/Sxx
    intercept = ybar - slope*xbar
    resid = by - intercept - slope*bx
    rss = np.sum(w*resid**2)
    if n > 2:
        sigma2 = rss/(n-2)
        se_int = math.sqrt(sigma2/np.sum(w) + (xbar**2)*sigma2/Sxx)
        t = intercept/se_int
        p = t_sf(t, n-2)
    else:
        se_int, p = float('nan'), float('nan')
    # IVW slope (no intercept) for comparison
    b_ivw = np.sum(w*bx*by)/np.sum(w*bx*bx)
    se_ivw = 1.0/math.sqrt(np.sum(w))
    return dict(n=n, slope=slope, intercept=intercept, se_int=se_int, p_int=p,
                ivw=b_ivw, se_ivw=se_ivw)

# ---------- Weighted median (bootstrap SE) ----------
def weighted_median(bx, by, sy, n_boot=1000, seed=2026):
    rng = np.random.default_rng(seed)
    w = 1.0/sy**2
    ratios = by/bx
    order = np.argsort(np.abs(bx))
    bx = bx[order]; ratios = ratios[order]; w = w[order]
    cw = np.cumsum(w)/np.sum(w)
    # median point (linear interp)
    idx = np.searchsorted(cw, 0.5)
    if idx >= len(cw): idx = len(cw)-1
    if idx == 0:
        med = ratios[0]
    else:
        lo, hi = cw[idx-1], cw[idx]
        frac = 0.0 if hi == lo else (0.5-lo)/(hi-lo)
        med = ratios[idx-1] + frac*(ratios[idx]-ratios[idx-1])
    # bootstrap SE
    se = float('nan')
    if n_boot and len(bx) >= 3:
        bs = []
        for _ in range(n_boot):
            k = rng.integers(0, len(bx), len(bx))
            bws = w[k]; br = ratios[k]; bc = np.cumsum(bws)/np.sum(bws)
            j = np.searchsorted(bc, 0.5)
            if j >= len(bc): j = len(bc)-1
            if j == 0: m = br[0]
            else:
                lo2, hi2 = bc[j-1], bc[j]
                f2 = 0.0 if hi2 == lo2 else (0.5-lo2)/(hi2-lo2)
                m = br[j-1] + f2*(br[j]-br[j-1])
            bs.append(m)
        se = float(np.std(bs, ddof=1))
    return med, se

def main():
    rows = []
    print(f"{'Study':6} {'Step':5} {'n':>3} {'IVW':>10} {'Egger_int':>11} {'p_int':>8} {'WM':>10} {'WM_SE':>9}")
    print("-"*80)
    for sid, (X, M, Y) in TRIOS.items():
        tX = PB.get_tophits(X); tM = PB.get_tophits(M)
        aM_on_X = PB.get_associations(list(tX.keys()), M)   # step1 outcome M at X SNPs
        aY_on_M = PB.get_associations(list(tM.keys()), Y)   # step2 outcome Y at M SNPs
        bx1, by1, sy1, d1 = align(tX, aM_on_X)
        bx2, by2, sy2, d2 = align(tM, aY_on_M)
        eg1 = mr_egger(bx1, by1, sy1)
        eg2 = mr_egger(bx2, by2, sy2)
        wm1 = weighted_median(bx1, by1, sy1)
        wm2 = weighted_median(bx2, by2, sy2)
        print(f"{sid:6} {'X->M':5} {eg1['n']:>3} {eg1['ivw']:>10.5f} {eg1['intercept']:>11.4f} {eg1['p_int']:>8.3f} {wm1[0]:>10.5f} {str(wm1[1])[:9]:>9}")
        print(f"{sid:6} {'M->Y':5} {eg2['n']:>3} {eg2['ivw']:>10.5f} {eg2['intercept']:>11.4f} {eg2['p_int']:>8.3f} {wm2[0]:>10.5f} {str(wm2[1])[:9]:>9}")
        rows.append(dict(study=sid, step="X->M", n=eg1['n'], ivw=eg1['ivw'],
                         egger_intercept=eg1['intercept'], egger_p=eg1['p_int'],
                         wm=wm1[0], wm_se=wm1[1], dropped_step1=d1))
        rows.append(dict(study=sid, step="M->Y", n=eg2['n'], ivw=eg2['ivw'],
                         egger_intercept=eg2['intercept'], egger_p=eg2['p_int'],
                         wm=wm2[0], wm_se=wm2[1], dropped_step2=d2))
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["study","step","n","ivw","egger_intercept",
                                           "egger_p","wm","wm_se","dropped_step1","dropped_step2"])
        w.writeheader(); w.writerows(rows)
    print(f"\n[csv] {OUT}")

if __name__ == "__main__":
    main()
