# -*- coding: utf-8 -*-
"""
180-cell coverage grid (2026-09-30) — 修复后口径一致的覆盖验证
============================================================
用途: 替代 2026-09-03 的旧 T2_simulation_grid (含符号bug/不同DGP, 且与§3.8矛盾)。
采用 regime-map DGP (M4b_regime_map_20260930.py 的同族):
  因果链 gamma_M=alpha*gamma_X, gamma_Y=beta*gamma_M;
  共享SNP两步复用同一份含噪 gamma_M_hat (协方差来源); rho_MY=0 (共享通道, 恒变窄)。
维度: n_s{0,10,25,40,50} x F{10,30,90,1000} x beta{-1,-0.5,1} x alpha{0.3,0.5,0.7} = 180 格。
每格 R=4000 重复, 计算:
  var_naive = beta^2 Var(a) + alpha^2 Var(b)
  var_corr  = var_naive + 2*alpha*beta*Cov(a,b)   (fixed sign: 恒负 -> 恒变窄)
  sd_emp    = SD(a*b)  金标准
覆盖率(围绕真值 true_ab, 受IVW衰减偏倚污染):
  cov_naive, cov_corr, cov_emp(用sd_emp作SE)
覆盖率(围绕估计量自身期望, 隔离方差校准): cov_corr_centered
输出: temp/M4b_coverage_grid_20260930.csv
"""
import os, csv, math
import numpy as np

PROJ = r"D:/WorkBuddy/两步法MR中介"
TEMP = os.path.join(PROJ, "③ 真实数据应用", "temp")
R = 4000
SEED = 20260930
P_X = P_M = 50
N = 100_000
SE = 1.0 / math.sqrt(N)

NSS = [0, 10, 25, 40, 50]
STRENGTHS = [("weak F~10", 10), ("moderate F~30", 30), ("strong F~90", 90), ("v.strong F~1000", 1000)]
BETAS = [-1.0, -0.5, 1.0]
ALPHAS = [0.3, 0.5, 0.7]


def simulate(n_s, beta, alpha, mu_X, seed):
    rng = np.random.default_rng(seed)
    sd_g = 0.3 * mu_X
    ns = n_s
    k1 = P_X - ns
    k2 = P_M - ns
    gx_s = rng.normal(mu_X, sd_g, (R, ns)) if ns > 0 else np.zeros((R, 0))
    gx_1 = rng.normal(mu_X, sd_g, (R, k1)) if k1 > 0 else np.zeros((R, 0))
    gx_2 = rng.normal(mu_X, sd_g, (R, k2)) if k2 > 0 else np.zeros((R, 0))
    ghx_s = gx_s + rng.normal(0, SE, gx_s.shape)
    ghx_1 = gx_1 + rng.normal(0, SE, gx_1.shape)
    ghm_s = alpha * gx_s + rng.normal(0, SE, gx_s.shape)
    ghm_1 = alpha * gx_1 + rng.normal(0, SE, gx_1.shape)
    ghm_2 = alpha * gx_2 + rng.normal(0, SE, gx_2.shape)
    ghy_s = beta * (alpha * gx_s) + rng.normal(0, SE, gx_s.shape)
    ghy_2 = beta * (alpha * gx_2) + rng.normal(0, SE, gx_2.shape)
    num_a = (np.sum(ghm_s * ghx_s, 1) + np.sum(ghm_1 * ghx_1, 1)) / SE ** 2
    den_a = (np.sum(ghx_s ** 2, 1) + np.sum(ghx_1 ** 2, 1)) / SE ** 2
    ahat = num_a / den_a
    num_b = (np.sum(ghy_s * ghm_s, 1) + np.sum(ghy_2 * ghm_2, 1)) / SE ** 2
    den_b = (np.sum(ghm_s ** 2, 1) + np.sum(ghm_2 ** 2, 1)) / SE ** 2
    bhat = num_b / den_b
    return ahat, bhat


def cell(n_s, beta, alpha, F):
    mu_X = math.sqrt(F) * SE
    # 用不同seed避免各格相关
    h = hash((n_s, round(beta, 3), round(alpha, 3), F)) & 0x7fffffff
    ahat, bhat = simulate(n_s, beta, alpha, mu_X, SEED + h)
    va = float(np.var(ahat, ddof=1)); vb = float(np.var(bhat, ddof=1))
    cab = float(np.cov(ahat, bhat)[0, 1])
    var_naive = beta ** 2 * va + alpha ** 2 * vb
    var_corr = var_naive + 2 * alpha * beta * cab
    se_n = math.sqrt(max(var_naive, 0)); se_c = math.sqrt(max(var_corr, 0))
    dSE = (se_c / se_n - 1) * 100 if se_n > 0 else float("nan")
    prod = ahat * bhat
    sd_emp = float(np.std(prod, ddof=1))
    true_ab = alpha * beta
    mean_prod = float(np.mean(prod))
    cov_n = float(np.mean(np.abs(prod - true_ab) <= 1.96 * se_n))
    cov_c = float(np.mean(np.abs(prod - true_ab) <= 1.96 * se_c))
    cov_e = float(np.mean(np.abs(prod - true_ab) <= 1.96 * sd_emp))
    cov_c_c = float(np.mean(np.abs(prod - mean_prod) <= 1.96 * se_c))
    return dict(n_s=n_s, F=F, beta=beta, alpha=alpha, dSE_pct=round(dSE, 3),
                se_naive=round(se_n, 6), se_corr=round(se_c, 6), sd_emp=round(sd_emp, 6),
                ratio_naive_over_sd=round(se_n / sd_emp, 4) if sd_emp > 0 else float("nan"),
                ratio_corr_over_sd=round(se_c / sd_emp, 4) if sd_emp > 0 else float("nan"),
                cov95_naive=round(cov_n, 4), cov95_corr=round(cov_c, 4),
                cov95_emp=round(cov_e, 4), cov95_corr_centered=round(cov_c_c, 4))


def main():
    rows = []
    for F in [s[1] for s in STRENGTHS]:
        for n_s in NSS:
            for beta in BETAS:
                for alpha in ALPHAS:
                    rows.append(cell(n_s, beta, alpha, F))
    # 汇总
    dSE = [r["dSE_pct"] for r in rows]
    widen = [r for r in rows if r["dSE_pct"] > 0]
    print(f"cells={len(rows)}  dSE range=[{min(dSE):+.2f},{max(dSE):+.2f}]  widening={len(widen)}")
    for tag in ["cov95_naive", "cov95_corr", "cov95_emp"]:
        v = [r[tag] for r in rows]
        print(f"  {tag}: mean={sum(v)/len(v):.4f} min={min(v):.4f} max={max(v):.4f}")
    # 按F汇总naive/corr/emp
    import collections
    byF = collections.defaultdict(list)
    for r in rows: byF[r["F"]].append(r)
    print("  F-level naive/corr/emp means:")
    for F in [10, 30, 90, 1000]:
        v = byF[F]
        print(f"    F={F:4d}: naive={sum(r['cov95_naive'] for r in v)/len(v):.3f} "
              f"corr={sum(r['cov95_corr'] for r in v)/len(v):.3f} "
              f"emp={sum(r['cov95_emp'] for r in v)/len(v):.3f} "
              f"naive/SD={sum(r['ratio_naive_over_sd'] for r in v)/len(v):.3f}")
    OUT = os.path.join(TEMP, "M4b_coverage_grid_20260930.csv")
    flds = ["n_s", "F", "beta", "alpha", "dSE_pct", "se_naive", "se_corr", "sd_emp",
            "ratio_naive_over_sd", "ratio_corr_over_sd", "cov95_naive", "cov95_corr",
            "cov95_emp", "cov95_corr_centered"]
    with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=flds); w.writeheader(); w.writerows(rows)
    print("saved", OUT)


if __name__ == "__main__":
    main()
