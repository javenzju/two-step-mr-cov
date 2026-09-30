# -*- coding: utf-8 -*-
"""
符号残差直接复检 (2026-09-30)
==============================
用户要求: 锁定 "校正项恒为负 / naive 恒保守" 口径前, 跑 direct test 确认不变宽。
原始 spec: opposite-sign, rho_MY>0, n_s=0 —— 但 n_s=0 时两条通道都归零(平凡不变宽, 测不到东西)。
因此本脚本跑两组有意义配置:
  (A) opposite-sign (alpha*beta<0), rho_MY=0, n_s in {1,2,5,10,25,50}  -> 检验 shared 通道是否恒负
  (B) opposite-sign (alpha>0,beta<0), rho_MY>0, n_s>0                  -> 检验 rho_MY 通道是否会变宽
  (C) same-sign   (alpha>0,beta>0),  rho_MY>0, n_s>0                  -> 对照: rho_MY 通道变宽条件
  (D) n_s=0 角落 (含 rho_MY>0)                                          -> 平凡: 两通道均 0

复用 M4b_s10_cov.estimate_cov_prod_mr (已修符号 bug)。
"""
import sys, math
sys.path.insert(0, r"D:/WorkBuddy/两步法MR中介/③ 真实数据应用")
from M4b_s10_cov import estimate_cov_prod_mr, corrected_se

# 典型 GWAS 尺度
N_X = N_M = N_Y = 300000
p_X = p_M = 50
F_levels = {"weak F~10": 10.0, "moderate F~90": 90.0, "strong F~1000": 1000.0}
n_s_grid = [1, 2, 5, 10, 25, 50]

def minmax_widen(grid):
    mins, maxs, worst = [], [], None
    for a, b in grid:
        for F in F_levels.values():
            for n_s in n_s_grid:
                ct, cs, cr = estimate_cov_prod_mr(0.05, 0.05, n_s, p_X, p_M, F,
                                                 N_X, N_M, N_Y, rho_MY=0.0,
                                                 alpha=a, beta=b)
                _, sn, sc, w = corrected_se(a, b, 0.05, 0.05, ct)
                mins.append(w); maxs.append(w)
                if worst is None or w > worst[0]:
                    worst = (w, a, b, F, n_s)
    return min(mins), max(maxs), worst

print("=== (A) opposite-sign, rho_MY=0, n_s>0 : shared 通道 ===")
mn, mx, worst = minmax_widen([(0.5, -0.5), (-0.5, 0.5)])
print(f"  widen_pct range = [{mn:+.3f}%, {mx:+.3f}%]  全样本最小/最大")
print(f"  最宽格点 = {worst[0]:+.3f}% (alpha={worst[1]}, beta={worst[2]}, F={worst[3]}, n_s={worst[4]})")
print(f"  -> 是否全部 <=0 (恒变窄)? {all(x<=1e-9 for x in [mn,mx])}")

print("\n=== (B) opposite-sign (alpha>0,beta<0), rho_MY>0, n_s>0 : rho_MY 通道 ===")
print(f"  {'rho_MY':>7} {'n_s':>4} {'F':>5} {'cov_total':>12} {'cov_shared':>12} {'cov_rho':>12} {'widen%':>9}")
for rho in [0.1, 0.3, 0.6]:
    for n_s in [5, 25, 50]:
        ct, cs, cr = estimate_cov_prod_mr(0.05, 0.05, n_s, p_X, p_M, 1000.0,
                                         N_X, N_M, N_Y, rho_MY=rho,
                                         alpha=0.5, beta=-0.5)
        _, sn, sc, w = corrected_se(0.5, -0.5, 0.05, 0.05, ct)
        print(f"  {rho:>7.1f} {n_s:>4} {'1000':>5} {ct:>+12.3e} {cs:>+12.3e} {cr:>+12.3e} {w:>+9.3f}")

print("\n=== (C) same-sign (alpha>0,beta>0), rho_MY>0, n_s>0 : 对照 ===")
for rho in [0.1, 0.3, 0.6]:
    for n_s in [5, 25, 50]:
        ct, cs, cr = estimate_cov_prod_mr(0.05, 0.05, n_s, p_X, p_M, 1000.0,
                                         N_X, N_M, N_Y, rho_MY=rho,
                                         alpha=0.5, beta=0.5)
        _, sn, sc, w = corrected_se(0.5, 0.5, 0.05, 0.05, ct)
        print(f"  rho={rho:.1f} n_s={n_s:>2} F=1000 cov_total={ct:>+12.3e} cov_rho={cr:>+12.3e} widen%={w:>+9.3f}")

print("\n=== (D) n_s=0 角落 (rho_MY>0) : 平凡 ===")
ct, cs, cr = estimate_cov_prod_mr(0.05, 0.05, 0, p_X, p_M, 1000.0, N_X, N_M, N_Y,
                                  rho_MY=0.6, alpha=0.5, beta=-0.5)
_, sn, sc, w = corrected_se(0.5, -0.5, 0.05, 0.05, ct)
print(f"  n_s=0 -> cov_total={ct:.3e} widen%={w:.3f} (两通道均归零)")
