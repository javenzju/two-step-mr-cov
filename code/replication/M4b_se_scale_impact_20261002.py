# -*- coding: utf-8 -*-
"""
TwoSampleMR vs Python 管线 SE 口径差异 —— 对稿件结论的影响评估
================================================================
承接 M4b_s014_rootcause_20261002.py 的根因结论:

  根因(已 100% 定量证实): 两条管线不是同一个 IVW 方差估计器
    Python        : w=bx²/σY²,  se = 1/sqrt(Σw)                —— 固定效应
    TwoSampleMR   : w=1/σY²,    se = σ/sqrt(Σw·bx²), σ=加权残差sd
                    (0.7.6 mr_ivw, 乘性随机效应的欠离散校正形式)
    两者固定效应 SE 恒等(Σ bx²/σY² 相同), 差异 100% 来自 σ 的过度离散膨胀。
    σX 完全不参与(0.7.6 的 mr_ivw 不使用 se_exp); 回文 SNP 剔除仅贡献约 1%。

本脚本回答第二个问题: 这个 SE 尺度差异会不会动摇稿件结论?
------------------------------------------------------------------------
  Var_naive = β²se_α² + α²se_β²                      <- 与 se 的尺度平方成正比
  cov_total = f(F, N, p, n_shared, sd_prior)          <- 不依赖 se (仅受 |se_α se_β| 截断约束)
  2αβ·cov_total 恒为负                                 <- 稿件核心结论: naive 恒偏保守(变窄)

  => se 统一放大 k 倍时: widen(k) = sqrt(1 + x/k²) - 1,  x = 2αβ·cov / Var_naive(FE) < 0
     |widen(k)| < |widen(1)|, 但**符号不变**。
  真正要守的底线是"显著性翻转判定"(naive_sig vs corr_sig) 是否随口径改变。

输出: temp/M4b_secale_impact_20261002.csv + 同名 .log
"""
import os, sys, math, time, json, csv, glob, importlib.util

PROJ = r"D:/WorkBuddy/两步法MR中介"
RD   = os.path.join(PROJ, "③ 真实数据应用")
TEMP = os.path.join(RD, "temp")
LOGD = os.path.join(RD, "log")
os.makedirs(LOGD, exist_ok=True)

LOG = os.path.join(LOGD, "M4b_secale_impact_20261002.log")
_L = []
def L(m):
    s = f"[{time.strftime('%H:%M:%S')}] {m}"
    print(s); _L.append(s)

sys.path.insert(0, RD)
s10 = importlib.import_module("M4b_s10_cov")
estimate_cov_prod_mr = s10.estimate_cov_prod_mr
corrected_se = s10.corrected_se

# 复用根因脚本里的估计器
spec = importlib.util.spec_from_file_location("rc", os.path.join(RD, "M4b_s014_rootcause_20261002.py"))
rc = importlib.util.module_from_spec(spec); spec.loader.exec_module(rc)
prep = rc.prep
est_btivw_fe = rc.est_btivw_fe
est_tsmr_ivw = rc.est_tsmr_ivw


def load_cache(gid, must_include=None, min_overlap=0.8):
    """本地缓存里挑一份与 must_include 交集最大的 associations"""
    cands = sorted(glob.glob(os.path.join(TEMP, f"pb_assoc_{gid}_*.json")),
                   key=os.path.getsize, reverse=True)
    if not cands:
        return None
    if must_include is None:
        return json.load(open(cands[0], encoding="utf-8"))
    need = set(must_include)
    best = (0, None)
    for f in cands:
        try: d = json.load(open(f, encoding="utf-8"))
        except Exception: continue
        if not isinstance(d, dict): continue
        ov = len(need & set(d))
        if ov > best[0]: best = (ov, d)
    n = len(need)
    if best[0] < min_overlap * n:
        return None
    return best[1]


def main():
    L("=" * 80)
    L("SE 口径差异对稿件结论的影响评估 (TwoSampleMR 0.7.6 mr_ivw vs Python IVW-FE)")
    L("=" * 80)

    src = os.path.join(TEMP, "Task11_recompute6.csv")
    rows = list(csv.DictReader(open(src, encoding="utf-8-sig")))
    L(f"载入沉积结果 {len(rows)} 行: {[r['study_id'] for r in rows]}")

    out = []
    for r in rows:
        sid = r["study_id"]; eid = r["exp_id"]; mid = r["med_id"]; oid = r["out_id"]
        L(f"\n{'='*76}\n{sid}: {eid} -> {mid} -> {oid}")

        # ---------- 数据 ----------
        inst_X = rc.get_tophits(eid); inst_M = rc.get_tophits(mid)
        try: a_M = rc.get_associations(list(inst_X.keys()), mid)     # step1
        except Exception: a_M = load_cache(mid, list(inst_X.keys()))
        try: a_Y = rc.get_associations(list(inst_M.keys()), oid)     # step2
        except Exception: a_Y = load_cache(oid, list(inst_M.keys()))
        if a_M is None or a_Y is None:
            L(f"   数据不全 (step1={'ok' if a_M else 'MISS'}, step2={'ok' if a_Y else 'MISS'}) -> 仅做解析敏感性")
            out.append({"study_id": sid, "status": "数据不全(离线缓存)"}); continue

        t1, d1 = prep(inst_X, a_M); t2, d2 = prep(inst_M, a_Y)
        L(f"   step1 n={len(t1)} drop={d1} | step2 n={len(t2)} drop={d2}")

        # ---------- 两种口径 ----------
        a_fe, sa_fe, _ = est_btivw_fe(t1)
        b_fe, sb_fe, _ = est_btivw_fe(t2)
        a_mre, sa_mre, sg_a, _ = est_tsmr_ivw(t1, "ivw")
        b_mre, sb_mre, sg_b, _ = est_tsmr_ivw(t2, "ivw")
        L(f"   沉积(FE)  α={r['alpha_hat']:>12s} se={r['se_alpha']:>10s} | "
          f"β={r['beta_hat']:>12s} se={r['se_beta']:>10s}")
        L(f"   重算(FE)  α={a_fe:+.6f} se={sa_fe:.6f} | β={b_fe:+.6f} se={sb_fe:.6f}")
        L(f"   重算(TSMR)α={a_mre:+.6f} se={sa_mre:.6f} (σ={sg_a:.3f}) | "
          f"β={b_mre:+.6f} se={sb_mre:.6f} (σ={sg_b:.3f})")
        L(f"   -> SE 膨胀倍率: se_α ×{sa_mre/sa_fe:.3f}   se_β ×{sb_mre/sb_fe:.3f}")

        # ---------- 两种口径下的修正幅度 ----------
        p_X, p_M, nsh = int(r["p_X"]), int(r["p_M"]), int(r["n_shared"])
        F_X = float(r["F_X"])
        N_X, N_M, N_Y = float(r["N_X"]), float(r["N_M"]), float(r["N_Y"])

        def widen_for(alpha, beta, sea, seb):
            cov, csh, crho = estimate_cov_prod_mr(
                sea, seb, nsh, p_X, p_M, F_X, N_X, N_M, N_Y,
                rho_MY=0, alpha=alpha, beta=beta)
            ind, sn, sc, w = corrected_se(alpha, beta, sea, seb, cov)
            return cov, sn, sc, w, ind

        cov_fe, sn_fe, sc_fe, w_fe, ind_fe = widen_for(a_fe, b_fe, sa_fe, sb_fe)
        cov_mre, sn_mre, sc_mre, w_mre, ind_mre = widen_for(a_mre, b_mre, sa_mre, sb_mre)
        L(f"   cov_total  FE={cov_fe:.4e}  TSMR={cov_mre:.4e}  (比值 {cov_mre/cov_fe if cov_fe else float('nan'):.3f})")
        L(f"   widen_pct  FE={w_fe:+.2f}%   TSMR(乘性随机效应)={w_mre:+.2f}%")
        sig = lambda ind, se: "显著" if abs(ind) > 1.96 * se else "不显著"
        L(f"   naive 显著性  FE={sig(ind_fe, sn_fe)}  TSMR={sig(ind_mre, sn_mre)}")
        L(f"   corr  显著性  FE={sig(ind_fe, sc_fe)}  TSMR={sig(ind_mre, sc_mre)}")
        flip_fe = sig(ind_fe, sn_fe) != sig(ind_fe, sc_fe)
        flip_mre = sig(ind_mre, sn_mre) != sig(ind_mre, sc_mre)
        L(f"   翻转判定     FE={'翻转' if flip_fe else '无翻转'}  TSMR={'翻转' if flip_mre else '无翻转'}"
          f"   >> 是否一致: {'是' if flip_fe == flip_mre else '否 ***'}")
        L(f"   沉积 widen_pct_rho0 = {r['widen_pct_rho0']}%  (对照)")

        out.append({
            "study_id": sid, "status": "OK",
            "sigma_alpha": round(sg_a, 4), "sigma_beta": round(sg_b, 4),
            "se_alpha_FE": round(sa_fe, 6), "se_alpha_TSMR": round(sa_mre, 6),
            "se_beta_FE": round(sb_fe, 6), "se_beta_TSMR": round(sb_mre, 6),
            "SE_inflation_alpha": round(sa_mre / sa_fe, 3),
            "SE_inflation_beta": round(sb_mre / sb_fe, 3),
            "cov_FE": f"{cov_fe:.6e}", "cov_TSMR": f"{cov_mre:.6e}",
            "widen_pct_FE": round(w_fe, 2), "widen_pct_TSMR": round(w_mre, 2),
            "naive_sig_FE": sig(ind_fe, sn_fe), "corr_sig_FE": sig(ind_fe, sc_fe),
            "naive_sig_TSMR": sig(ind_mre, sn_mre), "corr_sig_TSMR": sig(ind_mre, sc_mre),
            "flip_FE": flip_fe, "flip_TSMR": flip_mre,
            "flip_conclusion_stable": flip_fe == flip_mre,
            "deposited_widen_pct": r["widen_pct_rho0"],
        })

    # ---------- 解析敏感性: se 统一放大 k 倍时 widen 与翻转判定 ----------
    L(f"\n{'='*76}")
    L("解析敏感性: 设 α̂,β̂ 的点估计不变, se 统一放大 k 倍 (k=σ 实测 ~2.2-2.3)")
    L("   widen(k) = sqrt(1 + x/k²) - 1,  x = 2αβ·cov / Var_naive(FE) < 0")
    for r in rows:
        sid = r["study_id"]
        w1 = float(r["widen_pct_rho0"])
        x = (1 + w1 / 100) ** 2 - 1          # 反解 x
        line = f"   {sid}: widen(FE)={w1:+.2f}%  x={x:+.4f} -> "
        for k in (1.0, 1.5, 2.0, 2.25, 2.5, 3.0):
            wk = (math.sqrt(1 + x / k ** 2) - 1) * 100
            line += f"k={k}:{wk:+.2f}%  "
        L(line)

    fld = list(out[0].keys()) if out else ["study_id", "status"]
    with open(os.path.join(TEMP, "M4b_secale_impact_20261002.csv"), "w",
              newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fld); w.writeheader(); w.writerows(out)
    L(f"\n[done] -> temp/M4b_secale_impact_20261002.csv")


if __name__ == "__main__":
    try:
        main()
    finally:
        open(LOG, "w", encoding="utf-8").write("\n".join(_L))
