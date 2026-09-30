# -*- coding: utf-8 -*-
"""
M4b regime map: 修正幅度何时不可忽略 (2026-09-30)
================================================================================
目的: 为稿件新增 §3.x "regime map" —— 标定协方差修正在什么参数区不可忽略。

与旧模拟 (S6) 的关键区别 —— 旧 DGP 是**循环的/非因果的**:
  旧: gamma_X, gamma_M, gamma_Y 各自独立从正均值正态抽取, 没有 gamma_M=alpha*gamma_X、
      gamma_Y=beta*gamma_M 的因果结构, 因此从未真正模拟出异号中介。
新 DGP (本脚本) 内建因果链:
      gamma_M = alpha * gamma_X           (X -> M)
      gamma_Y = beta  * gamma_M           (M -> Y)   =>  gamma_Y = alpha*beta*gamma_X
  异号中介 (beta<0) 自然出现; 且**共享 SNP 在两步之间复用同一份含噪 gamma_M_hat**,
  这正是 Cov(alphahat, betahat) 的共享SNP通道来源 (旧模拟未建模此点)。

设计:
  网格: n_s(共享SNP数) x beta(含正负) x 工具强度(F)
  每个格子 R 次重复, 用蒙特卡洛经验 Var/Cov 计算:
      naive   = beta^2 Var(ahat) + alpha^2 Var(bhat)
      correct = naive + 2*alpha*beta*Cov(ahat,bhat)
      dSE%    = (sqrt(correct)/sqrt(naive) - 1)*100
  并报告 95% CI 覆盖率 (naive vs corrected) 与一阶近似的准确性。

输出: temp/M4b_regime_map_20260930.csv
"""
import os, csv, math
import numpy as np

PROJ = r"D:/WorkBuddy/两步法MR中介"
TEMP = os.path.join(PROJ, "③ 真实数据应用", "temp")

R = 4000          # 每格重复次数
SEED = 20260930
P_X = 50          # step-1 SNP 数
P_M = 50          # step-2 SNP 数
ALPHA = 0.5       # X->M 真实效应 (固定)
N = 100_000       # 各 GWAS 样本量 -> se = 1/sqrt(N)


def simulate(n_shared, beta, mu_X, R=R, seed=SEED,
             p_X=P_X, p_M=P_M, alpha=ALPHA, N=N, sd_frac=0.3):
    """返回 (ahat, bhat) 两个长度 R 的数组"""
    rng = np.random.default_rng(seed)
    seX = seM = seY = 1.0 / math.sqrt(N)
    sd_g = sd_frac * mu_X                      # gamma_X 的先验散布
    ns = n_shared
    k1 = p_X - ns                              # 仅用于 step-1 的 SNP 数
    k2 = p_M - ns                              # 仅用于 step-2 的 SNP 数

    # ---- 真实 gamma_X ----
    gx_s = rng.normal(mu_X, sd_g, (R, ns)) if ns > 0 else np.zeros((R, 0))
    gx_1 = rng.normal(mu_X, sd_g, (R, k1)) if k1 > 0 else np.zeros((R, 0))
    gx_2 = rng.normal(mu_X, sd_g, (R, k2)) if k2 > 0 else np.zeros((R, 0))

    # ---- 观测值 (加估计噪声) ----
    ghx_s = gx_s + rng.normal(0, seX, gx_s.shape)
    ghx_1 = gx_1 + rng.normal(0, seX, gx_1.shape)
    # 共享 SNP 的 gamma_M_hat 只有一份 —— 同时进入 alpha_hat 和 beta_hat (协方差来源)
    ghm_s = alpha * gx_s + rng.normal(0, seM, gx_s.shape)
    ghm_1 = alpha * gx_1 + rng.normal(0, seM, gx_1.shape)
    ghm_2 = alpha * gx_2 + rng.normal(0, seM, gx_2.shape)
    # gamma_Y (仅 step-2 的 SNP 需要)
    ghy_s = beta * (alpha * gx_s) + rng.normal(0, seY, gx_s.shape)
    ghy_2 = beta * (alpha * gx_2) + rng.normal(0, seY, gx_2.shape)

    # ---- IVW: alpha_hat = sum(gM*gX/seM^2) / sum(gX^2/seM^2) ----
    num_a = (np.sum(ghm_s * ghx_s, axis=1) + np.sum(ghm_1 * ghx_1, axis=1)) / seM ** 2
    den_a = (np.sum(ghx_s ** 2, axis=1) + np.sum(ghx_1 ** 2, axis=1)) / seM ** 2
    ahat = num_a / den_a
    # ---- IVW: beta_hat = sum(gY*gM/seY^2) / sum(gM^2/seY^2) ----
    num_b = (np.sum(ghy_s * ghm_s, axis=1) + np.sum(ghy_2 * ghm_2, axis=1)) / seY ** 2
    den_b = (np.sum(ghm_s ** 2, axis=1) + np.sum(ghm_2 ** 2, axis=1)) / seY ** 2
    bhat = num_b / den_b
    return ahat, bhat


def cell(n_shared, beta, mu_X):
    ahat, bhat = simulate(n_shared, beta, mu_X)
    va = float(np.var(ahat, ddof=1))
    vb = float(np.var(bhat, ddof=1))
    cab = float(np.cov(ahat, bhat)[0, 1])
    var_naive = beta ** 2 * va + ALPHA ** 2 * vb
    var_corr = var_naive + 2 * ALPHA * beta * cab
    se_n = math.sqrt(max(var_naive, 0)); se_c = math.sqrt(max(var_corr, 0))
    dSE = (se_c / se_n - 1) * 100 if se_n > 0 else float("nan")
    prod = ahat * bhat
    sd_emp = float(np.std(prod, ddof=1))          # 乘积估计量真实的抽样SD (金标准)
    true_ab = ALPHA * beta
    mean_prod = float(np.mean(prod))
    bias = mean_prod - true_ab                    # 点估计偏倚 (IVW含噪分母导致的O(1/F)衰减)
    # 覆盖率: (a) 围绕真实值 (受点估计偏倚污染)  (b) 围绕估计量自身期望 (隔离方差校准)
    cov_n = float(np.mean(np.abs(prod - true_ab) <= 1.96 * se_n))
    cov_c = float(np.mean(np.abs(prod - true_ab) <= 1.96 * se_c))
    cov_n_c = float(np.mean(np.abs(prod - mean_prod) <= 1.96 * se_n))
    cov_c_c = float(np.mean(np.abs(prod - mean_prod) <= 1.96 * se_c))
    bal = (abs(beta) * math.sqrt(va)) / (abs(ALPHA) * math.sqrt(vb))
    F = (mu_X / (1.0 / math.sqrt(N))) ** 2
    F_M = (ALPHA * mu_X / (1.0 / math.sqrt(N))) ** 2     # step-2 (中介) 侧的工具强度
    return {"n_shared": n_shared, "beta": beta, "alpha_beta": ALPHA * beta,
            "mu_X": mu_X, "F_per_SNP": round(F, 1), "F_mediator": round(F_M, 1),
            "var_alpha": va, "var_beta": vb, "cov_ab": cab,
            "se_naive": se_n, "se_corr": se_c, "dSE_pct": dSE,
            "sd_empirical": sd_emp,
            "ratio_corr_over_sd": se_c / sd_emp if sd_emp > 0 else float("nan"),
            "ratio_naive_over_sd": se_n / sd_emp if sd_emp > 0 else float("nan"),
            "bias": bias, "bias_over_sd": bias / sd_emp if sd_emp > 0 else float("nan"),
            "cov95_naive": round(cov_n, 3), "cov95_corr": round(cov_c, 3),
            "cov95_naive_centered": round(cov_n_c, 3), "cov95_corr_centered": round(cov_c_c, 3),
            "balance_ratio": round(bal, 3)}


def main():
    rng_master = np.random.default_rng(SEED)
    strengths = [("weak F~10", 0.01), ("strong F~90", 0.03), ("v.strong F~1000", 0.10)]
    betas = [0.5, 1.0, -0.5, -1.0]
    nss = [0, 10, 25, 50]

    rows = []
    print("=" * 118)
    print("regime map: dSE% = (SE_corrected / SE_naive - 1)*100   (负 = 变窄 = naive 偏保守)")
    print(f"p_X=p_M={P_X}, alpha={ALPHA}, R={R}/格, N={N}")
    print("=" * 118)
    for label, mu in strengths:
        print(f"\n### 工具强度: {label} (mu_X={mu})")
        print(f"{'n_s':>4} | " + " ".join(f"{'beta='+format(b,'+.1f'):>14}" for b in betas) + " | 平衡比范围")
        print("-" * 118)
        for ns in nss:
            line = f"{ns:>4} | "
            brs = []
            for b in betas:
                r = cell(ns, b, mu)
                r["strength"] = label
                rows.append(r)
                line += f"{r['dSE_pct']:>+13.2f}% "
                brs.append(r["balance_ratio"])
            print(line + f" | {min(brs):.2f}-{max(brs):.2f}")
    print("=" * 118)

    # ---- 汇总: 是否全部变窄 ----
    pos = [r for r in rows if r["dSE_pct"] > 0]
    print(f"\n【总检】共 {len(rows)} 格; dSE>0 (变宽) 的格子: {len(pos)}")
    if pos:
        for r in pos:
            print(f"  [!] n_s={r['n_s'] if 'n_s' in r else r['n_shared']}, beta={r['beta']}, "
                  f"{r['strength']}: dSE={r['dSE_pct']:+.2f}%")
    else:
        print("  => 全部变窄: 含真实因果结构(含异号)的模拟同样证实 naive 恒偏保守。")
    print(f"  dSE 范围: {min(r['dSE_pct'] for r in rows):+.2f}% ~ {max(r['dSE_pct'] for r in rows):+.2f}%")

    # ---- 幅度最大的格子 (regime) ----
    big = sorted(rows, key=lambda r: -abs(r["dSE_pct"]))[:6]
    print("\n【修正幅度最大的 6 个格子 (即 'regime': 修正不可忽略的参数区)】")
    print(f"{'n_s':>4} {'beta':>6} {'alpha*beta':>11} {'强度':>12} {'dSE%':>9} {'平衡比':>8} {'cov95_n':>8} {'cov95_c':>8}")
    for r in big:
        print(f"{r['n_shared']:>4} {r['beta']:>+6.1f} {r['alpha_beta']:>+11.3f} {r['strength']:>12} "
              f"{r['dSE_pct']:>+9.2f} {r['balance_ratio']:>8.2f} {r['cov95_naive']:>8.3f} {r['cov95_corr']:>8.3f}")

    # ---- 方差校准: se_corr / SD(prod) 应≈1; se_naive / SD(prod) 应>1 (保守) ----
    print("\n【方差校准】se/SD(α̂β̂): =1 表示方差公式正确; >1 表示高估(保守)")
    print(f"{'强度':>16} {'n_s':>4} {'beta':>6} {'SD(prod)':>10} {'se_corr/SD':>11} {'se_naive/SD':>12} "
          f"{'偏倚/SD':>9} {'cov95_n':>8} {'cov95_c':>8} {'cov95_c(居中)':>13}")
    print("-" * 118)
    for label, mu in strengths:
        for ns in [0, 25, 50]:
            for b in [1.0, -1.0]:
                r = next(x for x in rows if x["strength"] == label
                         and x["n_shared"] == ns and x["beta"] == b)
                print(f"{label:>16} {ns:>4} {b:>+6.1f} {r['sd_empirical']:>10.5f} "
                      f"{r['ratio_corr_over_sd']:>11.3f} {r['ratio_naive_over_sd']:>12.3f} "
                      f"{r['bias_over_sd']:>+9.2f} {r['cov95_naive']:>8.3f} {r['cov95_corr']:>8.3f} "
                      f"{r['cov95_corr_centered']:>13.3f}")
    print("-" * 118)
    print("注: cov95(围绕真值) 会被 IVW 含噪分母导致的 O(1/F) 衰减偏倚污染;")
    print("    cov95_c(居中) = 围绕估计量自身期望的覆盖率, 用于隔离'方差校准'本身。")

    OUT = os.path.join(TEMP, "M4b_regime_map_20260930.csv")
    flds = ["strength", "n_shared", "beta", "alpha_beta", "mu_X", "F_per_SNP", "F_mediator",
            "var_alpha", "var_beta", "cov_ab", "se_naive", "se_corr", "dSE_pct",
            "sd_empirical", "ratio_corr_over_sd", "ratio_naive_over_sd",
            "bias", "bias_over_sd",
            "cov95_naive", "cov95_corr", "cov95_naive_centered", "cov95_corr_centered",
            "balance_ratio"]
    with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=flds, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)
    print(f"\n[done] -> {OUT}")


if __name__ == "__main__":
    main()
