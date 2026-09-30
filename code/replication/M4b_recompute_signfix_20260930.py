# -*- coding: utf-8 -*-
"""
M4b 符号 bug 修复后重算 (2026-09-30)
================================================================================
背景: M4b_s10_cov.py 原 mu_X/mu_Y = sqrt(F/N) 恒正, 使 beta<0 (异号中介) 时
      Cov(Z, beta_h) 的符号被弄反 -> 虚假产生 "变宽(+widen%)"。
修复: mu_M 取正作参照, mu_X 带 sign(alpha), mu_Y 带 sign(beta) (见 M4b_s10_cov.py 文档串)。

本脚本对 M4b_stage2_all_20260906.csv 的 113 个 trio, 在 "反事实合并池" 配置下
(n_s = min(n_X, n_M), rho_MY = 0) 同时计算:
    dSE_legacy : 修复前(恒正 mu)的 SE 变化%  <- 原 Table 4 的错误数值
    dSE_fixed  : 修复后(带符号 mu)的 SE 变化% <- 应全部为负(变窄)
并专门输出 Table 4 的 6 个研究, 供稿件替换 provisional (‡) 数值。

输出: temp/M4b_signfix_20260930.csv
"""
import os, csv, math, sys, importlib.util

PROJ = r"D:/WorkBuddy/两步法MR中介"
DIR = os.path.join(PROJ, "③ 真实数据应用")
TEMP = os.path.join(DIR, "temp")
sys.path.insert(0, DIR)
s10 = importlib.import_module("M4b_s10_cov")
estimate_cov_prod_mr = s10.estimate_cov_prod_mr
corrected_se = s10.corrected_se

SRC = os.path.join(TEMP, "M4b_stage2_all_20260906.csv")
T4 = ["S366", "S271", "S247", "S390", "S348", "S150"]   # Table 4 的 6 行


def fnum(x, default=float("nan")):
    try:
        if x is None or str(x).strip() == "":
            return default
        return float(x)
    except Exception:
        return default


def run(sid, r, n_mc=100000):
    """返回 dict: 该 trio 在反事实合并池下的 legacy / fixed 结果"""
    a = fnum(r["alpha_hat"]); sa = fnum(r["se_alpha"])
    bh = fnum(r["beta_hat"]); sb = fnum(r["se_beta"])
    pX = int(fnum(r["n_X"], 0)); pM = int(fnum(r["n_M"], 0))
    F = fnum(r["F_X"]); NX = int(fnum(r["N_X"], 0)); NM = int(fnum(r["N_M"], 0)); NY = int(fnum(r["N_Y"], 0))
    if min(pX, pM) <= 0 or not (F > 0) or min(NX, NM, NY) <= 0:
        return None
    ns = min(pX, pM)                       # 反事实合并池
    out = {"study_id": sid, "n_shared_cf": ns, "alpha": a, "beta": bh,
           "se_alpha": sa, "se_beta": sb, "p_X": pX, "p_M": pM, "F_X": F}
    # legacy: 不传 alpha/beta -> 恒正 mu (原 bug 行为)
    cov_l, _, _ = estimate_cov_prod_mr(sa, sb, ns, pX, pM, F, NX, NM, NY,
                                       rho_MY=0, n_mc=n_mc, alpha=None, beta=None)
    # fixed: 传入 alpha/beta -> 带符号 mu
    cov_f, _, _ = estimate_cov_prod_mr(sa, sb, ns, pX, pM, F, NX, NM, NY,
                                       rho_MY=0, n_mc=n_mc, alpha=a, beta=bh)
    ind, se_n, _, _ = corrected_se(a, bh, sa, sb, 0.0)
    _, _, _, w_l = corrected_se(a, bh, sa, sb, cov_l)
    _, _, _, w_f = corrected_se(a, bh, sa, sb, cov_f)
    out.update({"SE_naive": se_n, "dSE_legacy_pct": w_l, "dSE_fixed_pct": w_f,
                "cov_legacy": cov_l, "cov_fixed": cov_f,
                "lambda_naive": abs(ind) / se_n if se_n > 0 else float("nan"),
                "opposite_sign": "yes" if (a * bh < 0) else "no"})
    return out


def main():
    rows = list(csv.DictReader(open(SRC, encoding="utf-8-sig")))
    print("=" * 108)
    print(f"源文件: {os.path.basename(SRC)}  共 {len(rows)} 个 trio")
    print("配置: 反事实合并池 n_s = min(n_X, n_M), rho_MY = 0")
    print("=" * 108)

    res = []
    for r in rows:
        o = run(r["study_id"], r)
        if o:
            res.append(o)

    # ---- 1) Table 4 六行 ----
    print("\n【Table 4 六行】legacy(原错误值) vs fixed(修复后真实值)")
    print("-" * 108)
    print(f"{'study':6} {'α̂':>12} {'β̂':>12} {'n_s':>5} | {'legacy%':>9} {'fixed%':>9} | {'λ_naive':>8} {'判定':>8}")
    print("-" * 108)
    t4rows = []
    for sid in T4:
        o = next((x for x in res if x["study_id"] == sid), None)
        if o is None:
            print(f"{sid:6}  (参数缺失, 无法计算)")
            continue
        verdict = "变窄" if o["dSE_fixed_pct"] < 0 else ("变宽!" if o["dSE_fixed_pct"] > 0 else "不变")
        print(f"{sid:6} {o['alpha']:>12.5g} {o['beta']:>12.5g} {o['n_shared_cf']:>5d} | "
              f"{o['dSE_legacy_pct']:>+9.1f} {o['dSE_fixed_pct']:>+9.1f} | "
              f"{o['lambda_naive']:>8.2f} {verdict:>8}")
        o2 = dict(o); o2["verdict"] = verdict
        t4rows.append(o2)
    print("-" * 108)

    # ---- 2) 全部异号 trio (原本声称"变宽"的群体) ----
    opp = [o for o in res if o["opposite_sign"] == "yes"]
    opp_pos = [o for o in opp if o["dSE_fixed_pct"] > 0]
    print(f"\n【异号中介 trio (α̂β̂<0)】共 {len(opp)} 个")
    print(f"  修复后 dSE>0 (变宽) 的个数: {len(opp_pos)} / {len(opp)}")
    print(f"  修复后 dSE<=0 (变窄) 的个数: {len(opp) - len(opp_pos)} / {len(opp)}")
    if opp_pos:
        print("  [!] 仍存在变宽者: " + ", ".join(f"{o['study_id']}({o['dSE_fixed_pct']:+.1f}%)" for o in opp_pos))
    else:
        print("  => 全部变窄: 证实 naive 一阶 delta 恒偏保守 (不存在'异号变宽' regime)")

    # ---- 3) 全样本 ----
    all_pos = [o for o in res if o["dSE_fixed_pct"] > 0]
    print(f"\n【全样本】可计算 {len(res)} 个 trio; 修复后变宽 {len(all_pos)} 个, 变窄 {len(res)-len(all_pos)} 个")
    if res:
        print(f"  修复后 dSE 范围: {min(o['dSE_fixed_pct'] for o in res):+.1f}% ~ "
              f"{max(o['dSE_fixed_pct'] for o in res):+.1f}%")

    # ---- 输出 CSV ----
    OUT = os.path.join(TEMP, "M4b_signfix_20260930.csv")
    flds = ["study_id", "opposite_sign", "n_shared_cf", "p_X", "p_M", "F_X",
            "alpha", "beta", "se_alpha", "se_beta", "SE_naive", "lambda_naive",
            "cov_legacy", "cov_fixed", "dSE_legacy_pct", "dSE_fixed_pct", "verdict"]
    for o in res:
        o.setdefault("verdict", "变窄" if o["dSE_fixed_pct"] < 0 else ("变宽!" if o["dSE_fixed_pct"] > 0 else "不变"))
    with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=flds, extrasaction="ignore")
        w.writeheader(); w.writerows(res)
    print(f"\n[done] -> {OUT}")


if __name__ == "__main__":
    main()
