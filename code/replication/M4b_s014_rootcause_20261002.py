# -*- coding: utf-8 -*-
"""
S014 TwoSampleMR vs 自建 Python 管线 SE 差异 —— 根因定量分解
=============================================================
背景
----
Task11_beta_SE_crossval.csv 显示 S014 (ieu-b-5144 -> ukb-d-I9_CORATHER):
    TwoSampleMR : b=0.124242  se=0.011243  (nsnp=203)
    Python      : b=0.128320  se=0.004940
即点估计仅差 -3.2%，标准误却差 +127.6% (2.28 倍)。

假说
----
两者不是同一 IVW 方差估计器：
  R 侧  TwoSampleMR::mr(har, method_list="mr_ivw") 取 method=="Inverse variance weighted"
        -> mr_ivw 对 ratio_i = bY_i/bX_i 做 metafor::rma(method="DL") 随机效应 meta；
        其中 Var(ratio_i) = seY_i^2/bX_i^2 + (bY_i^2 * seX_i^2)/bX_i^4  ← 二阶 delta，**同时含 σ_X 与 σ_Y**
  Py 侧 harmonize_ivw(random_effects=False)
        -> Burgess-Thompson 过原点加权回归 w_i = bX_i^2/seY_i^2,  se = 1/sqrt(Σw)
        Var 只用 σ_Y，**固定效应**，既无 τ² 也不含 σ_X

次要差异
--------
  harmonisation: TwoSampleMR 剔除回文+中等频率 SNP (S014 为 5 个:
                 rs1870735 rs199794659 rs2280405 rs2760061 rs6812640)
  proxy        : TwoSampleMR extract_outcome_data 默认 proxies=1 (S014 对 6 个 SNP 找代理);
                 Python 管线 proxies=0 (缺失即丢弃)
  -> 纳入分析的 SNP 集合不同 (203 vs 209)

本脚本做两件事
--------------
(A) 复现: 用同一份 OpenGWAS 数据，按上述 4 种估计器重算，看能否重现 R 的
    b=0.124242 / se=0.011243 与 Py 的 b=0.128320 / se=0.004940
(B) 鲁棒性: 在每一种 SE 口径下重算 S10 修正幅度 widen_pct，检验稿件核心结论
    (修正后区间收窄的相对幅度) 是否依赖 SE 绝对尺度

输出: temp/M4b_s014_rootcause_20261002.csv + 同名 .log
"""
import os, sys, math, time, json, csv, importlib.util
import urllib.request, urllib.parse

PROJ = r"D:/WorkBuddy/两步法MR中介"
RD   = os.path.join(PROJ, "③ 真实数据应用")
TEMP = os.path.join(RD, "temp")
LOGD = os.path.join(RD, "log")
os.makedirs(TEMP, exist_ok=True); os.makedirs(LOGD, exist_ok=True)

BASE   = "https://api.opengwas.io/api"
TOKF   = r"C:/Users/up201/.workbuddy/_ogw_token.txt"
CLUMP  = {"pval": 5e-8, "clump": 1, "r2": 0.001, "kb": 10000, "preclumped": 1, "pop": "EUR"}

LOG = os.path.join(LOGD, "M4b_s014_rootcause_20261002.log")
_L = []
def L(m):
    s = f"[{time.strftime('%H:%M:%S')}] {m}"
    print(s); _L.append(s)

# 复用既有管线的取数/协调逻辑，保证与稿件所用口径完全一致
sys.path.insert(0, RD)
spec = importlib.util.spec_from_file_location("pb", os.path.join(RD, "M4b_phaseB_pipeline.py"))
pb = importlib.util.module_from_spec(spec); spec.loader.exec_module(pb)
get_tophits, get_associations = pb.get_tophits, pb.get_associations
harmonize_ivw = pb.harmonize_ivw
COMP = pb.COMP


# ----------------------------------------------------------------- 估计器
def prep(inst, assoc, drop_rs=()):
    """暴露/结局按等位方向匹配后的逐 SNP 三联量 (bx, by, sx, sy) 与丢失归因"""
    tri, drop = {}, {"missing": 0, "ambig": 0, "zero": 0, "palindromic_drop": 0}
    for rs, ex in inst.items():
        ay = assoc.get(rs)
        if ay is None:
            drop["missing"] += 1; continue
        if rs in drop_rs:
            drop["palindromic_drop"] += 1; continue
        if ay["ea"] == ex["ea"]:
            b_out = ay["beta"]
        elif ay["ea"] == ex["nea"]:
            b_out = -ay["beta"]
        else:
            drop["ambig"] += 1; continue
        if ex["beta"] == 0 or ay["se"] == 0:
            drop["zero"] += 1; continue
        tri[rs] = (ex["beta"], b_out, ex["se"], ay["se"])
    return tri, drop


def est_btivw_fe(tri):
    """Python 口径: Burgess-Thompson 过原点 IVW 固定效应; Var 只含 σ_Y"""
    ws = [(bx ** 2) / (sy ** 2) for bx, by, sx, sy in tri.values()]
    W = sum(ws)
    b = sum(w * bx * by for w, (bx, by, sx, sy) in zip(ws, tri.values())) / \
        sum(w * bx ** 2 for w, (bx, by, sx, sy) in zip(ws, tri.values()))
    return b, 1.0 / math.sqrt(W), len(tri)


def est_btivw_re(tri):
    """Burgess 二阶矩 RE: se = sqrt(1/Σw + τ²) (不改点估计)"""
    b, se_fe, k = est_btivw_fe(tri)
    ws = [(bx ** 2) / (sy ** 2) for bx, by, sx, sy in tri.values()]
    W = sum(ws)
    Q = sum(w * (by - b * bx) ** 2 for w, (bx, by, sx, sy) in zip(ws, tri.values()))
    tau2 = max(0.0, (Q - (k - 1)) / W)
    return b, math.sqrt(1.0 / W + tau2), tau2, Q


def est_tsmr_ivw(tri, mode="ivw"):
    """精确复现 TwoSampleMR 0.7.6 (mr.R) 的三种 IVW。

    mr_ivw     : lm(b_out ~ -1 + b_exp, weights = 1/se_out^2)
                 b  = Σ(w bx by)/Σ(w bx^2)
                 sigma = sqrt(Σ w r^2 / df), df = n-1
                 se = [sigma/sqrt(Σ w bx^2)] / min(1, sigma)      # under-dispersion 校正
    mr_ivw_mre : 同上但不做 under-dispersion 校正, se = sigma/sqrt(Σ w bx^2)
    mr_ivw_fe  : 固定效应, se = 1/sqrt(Σ w bx^2)
    注意: 这三者**都不使用 se_exp**。
    """
    bx = [t[0] for t in tri.values()]
    by = [t[1] for t in tri.values()]
    sy = [t[3] for t in tri.values()]
    w = [1.0 / s ** 2 for s in sy]
    Swbx2 = sum(wi * x ** 2 for wi, x in zip(w, bx))
    b = sum(wi * x * y for wi, x, y in zip(w, bx, by)) / Swbx2
    df = len(bx) - 1
    rss = sum(wi * (y - b * x) ** 2 for wi, x, y in zip(w, bx, by))
    sigma = math.sqrt(rss / df) if df > 0 else float("nan")
    Q = sigma ** 2 * df
    se_fe = 1.0 / math.sqrt(Swbx2)
    se_mre = sigma / math.sqrt(Swbx2)
    se_ivw = se_mre / min(1.0, sigma)
    se = {"ivw": se_ivw, "mre": se_mre, "fe": se_fe}[mode]
    return b, se, sigma, Q


def est_ratio_meta(tri, random_effects=True):
    """TwoSampleMR mr_ivw 口径: ratio_i=bY/bX, se_ratio_i = sqrt(σY²/bX² + bY²σX²/bX⁴)
    再 metafor::rma(method='DL') —— 手工实现 DL"""
    th, se = [], []
    for bx, by, sx, sy in tri.values():
        th.append(by / bx)
        se.append(math.sqrt((sy ** 2) / (bx ** 2) + (by ** 2) * (sx ** 2) / (bx ** 4)))
    w = [1.0 / s ** 2 for s in se]
    W = sum(w)
    b_fe = sum(wi * ti for wi, ti in zip(w, th)) / W
    se_fe = math.sqrt(1.0 / W)
    if not random_effects or len(th) < 2:
        return b_fe, se_fe, 0.0, None
    Q = sum(wi * (ti - b_fe) ** 2 for wi, ti in zip(w, th))
    k = len(th)
    denom = W - sum(wi ** 2 for wi in w) / W          # DerSimonian-Laird 分母
    tau2 = max(0.0, (Q - (k - 1)) / denom)
    ws = [1.0 / (1.0 / wi + tau2) for wi in w]
    b_re = sum(wi * ti for wi, ti in zip(ws, th)) / sum(ws)
    se_re = math.sqrt(1.0 / sum(ws))
    return b_re, se_re, tau2, Q


# ----------------------------------------------------------------- 主流程
def pick_cache(gid):
    """离线取缓存中最大的一份 associations (OpenGWAS JWT 可能已过期)"""
    import glob
    cands = sorted(glob.glob(os.path.join(TEMP, f"pb_assoc_{gid}_*.json")),
                   key=lambda p: os.path.getsize(p), reverse=True)
    if not cands:
        raise SystemExit(f"无本地缓存 {gid}; 需刷新 OpenGWAS JWT")
    return json.load(open(cands[0], encoding="utf-8"))


def main():
    L("=" * 78)
    L("S014 根因分解: TwoSampleMR mr_ivw(RE) vs Python IVW(FE)")
    L("目标 (来自 Task11_beta_SE_crossval.csv):")
    L("   TwoSampleMR : b=0.124242  se=0.011243  nsnp=203")
    L("   Python      : b=0.128320  se=0.004940")
    L("=" * 78)

    MED, OUT = "ieu-b-5144", "ukb-d-I9_CORATHER"
    L(f"Step2 = {MED} -> {OUT}")
    L("注: OpenGWAS JWT 已于 2026-09-15 过期, 本次完全基于本地缓存离线复算")

    L("\n[1] 取数")
    inst = get_tophits(MED)
    L(f"    tophits {MED}: {len(inst)} SNPs")
    try:
        assoc = get_associations(list(inst.keys()), OUT)
    except Exception as e:
        L(f"    联网取数失败({type(e).__name__}: {e}) -> 回退本地缓存")
        assoc = pick_cache(OUT)
    L(f"    associations {OUT}: {len(assoc)} SNPs")
    miss = set(inst) - set(assoc)
    L(f"    结局缺失 {len(miss)} SNPs {sorted(miss)}")
    L(f"    -> Python(proxies=0) 直接丢弃; TwoSampleMR(proxies=1) 会尝试代理替换")

    PALIN = {"rs1870735", "rs199794659", "rs2280405", "rs2760061", "rs6812640"}
    L(f"\n[2] 两种纳入集合")
    tri_py, d_py = prep(inst, assoc, drop_rs=())
    L(f"    Python 口径     : n={len(tri_py):3d}  drop={d_py}")
    tri_r, d_r = prep(inst, assoc, drop_rs=PALIN)
    L(f"    TwoSampleMR 口径: n={len(tri_r):3d}  drop={d_r} (额外剔除 5 个回文中频 SNP)")
    L(f"    >> 注: R 侧还做 proxies=1, 本环境 proxies=0, 故两侧 {len(inst)-len(assoc)} 个缺漏 SNP 的处理也不同")

    L("\n[3] 四种估计器重算")
    rows = []

    def rec(tag, tri, fn_desc, b, se, extra=""):
        L(f"    {tag:42s} b={b:+.6f}  se={se:.6f}  {extra}")
        rows.append({"口径": tag, "n_snp": len(tri), "beta": round(b, 6),
                     "se": round(se, 6), "说明": fn_desc + extra})

    b, se, _ = est_btivw_fe(tri_py)
    rec("A. IVW-FE, Var=σY only (Python 现管线)", tri_py, "w=bx²/σY², se=1/sqrt(Σw)", b, se)

    b, se, tau2, Q = est_btivw_re(tri_py)
    rec("B. IVW-RE(Burgess), Var=σY only", tri_py, "se=sqrt(1/Σw+τ²)", b, se,
        f"  τ²={tau2:.3e} Q={Q:.1f}")

    b, se, tau2, Q = est_ratio_meta(tri_py, random_effects=False)
    rec("C. ratio meta FE, Var=σY&σX (TwoSampleMR式)", tri_py, "se_ratio=sqrt(σY²/bx²+by²σX²/bx⁴)", b, se)

    b, se, tau2, Q = est_ratio_meta(tri_py, random_effects=True)
    rec("D. ratio meta DL-RE (TwoSampleMR mr_ivw)", tri_py, "rma(method='DL')", b, se,
        f"  τ²={tau2:.3e} Q={Q:.1f}")

    b, se, tau2, Q = est_ratio_meta(tri_r, random_effects=True)
    rec("D'. 同上 + 剔回文中频SNP (最贴近R)", tri_r, "rma DL, R-like SNP set", b, se,
        f"  τ²={tau2:.3e} Q={Q:.1f}")

    L("    ---- TwoSampleMR 0.7.6 实际实现 (mr.R, obj='mr_ivw') ----")
    b, se, sigma, Q = est_tsmr_ivw(tri_py, "fe")
    rec("E. TSMR 0.7.6 mr_ivw_fe (w=1/σY²)", tri_py, "se=1/sqrt(Σw·bx²)", b, se,
        f"  σ={sigma:.3f} Q={Q:.1f}")
    b, se, sigma, Q = est_tsmr_ivw(tri_py, "mre")
    rec("F. TSMR 0.7.6 mr_ivw_mre (无欠离散校正)", tri_py, "se=σ/sqrt(Σw·bx²)", b, se,
        f"  σ={sigma:.3f} Q={Q:.1f}")
    b, se, sigma, Q = est_tsmr_ivw(tri_py, "ivw")
    rec("G. TSMR 0.7.6 mr_ivw (默认, 欠离散校正)", tri_py, "se=se_mre/min(1,σ)", b, se,
        f"  σ={sigma:.3f} Q={Q:.1f}")
    b, se, sigma, Q = est_tsmr_ivw(tri_r, "ivw")
    rec("G'. 同上 + 剔回文中频SNP (最贴近R全集)", tri_r, "se=se_mre/min(1,σ)", b, se,
        f"  σ={sigma:.3f} Q={Q:.1f}")

    # 对照靶值
    L("\n[4] 与靶值比对")
    TGT_R = (0.124242486970895, 0.0112433700352803)
    TGT_P = (0.128320000000000, 0.004940000000000)

    def cmp(tag, b, se, tb, ts):
        db = (b - tb) / abs(tb) * 100 if tb else float('nan')
        ds = (se - ts) / ts * 100
        L(f"    {tag:42s} Δb={db:+7.2f}%  Δse={ds:+8.2f}%")
        return db, ds

    byn = {r["口径"]: r for r in rows}
    L(f"    靶 TwoSampleMR b={TGT_R[0]:.6f} se={TGT_R[1]:.6f}")
    L(f"    靶 Python      b={TGT_P[0]:.6f} se={TGT_P[1]:.6f}")
    L("")
    for tag, tgt in [("A. IVW-FE, Var=σY only (Python 现管线)", TGT_P),
                     ("D. ratio meta DL-RE (TwoSampleMR mr_ivw)", TGT_R),
                     ("D'. 同上 + 剔回文中频SNP (最贴近R)", TGT_R),
                     ("E. TSMR 0.7.6 mr_ivw_fe (w=1/σY²)", TGT_R),
                     ("F. TSMR 0.7.6 mr_ivw_mre (无欠离散校正)", TGT_R),
                     ("G. TSMR 0.7.6 mr_ivw (默认, 欠离散校正)", TGT_R),
                     ("G'. 同上 + 剔回文中频SNP (最贴近R全集)", TGT_R)]:
        r = byn[tag]
        cmp(tag, r["beta"], r["se"], tgt[0], tgt[1])

    # SE 比值分解
    L("\n[5] SE 差异的定量归因 (相对 Python FE)")
    se_A = byn["A. IVW-FE, Var=σY only (Python 现管线)"]["se"]
    se_C = byn["C. ratio meta FE, Var=σY&σX (TwoSampleMR式)"]["se"]
    se_D = byn["D. ratio meta DL-RE (TwoSampleMR mr_ivw)"]["se"]
    se_Dp = byn["D'. 同上 + 剔回文中频SNP (最贴近R)"]["se"]
    L(f"    A (IVW-FE, σY only)            = {se_A:.6f}  baseline")
    L(f"    C (ratio FE, σY+σX)            = {se_C:.6f}  ×{se_C/se_A:.3f}   <- 含σX的方差贡献")
    L(f"    D (ratio DL-RE)                = {se_D:.6f}  ×{se_D/se_A:.3f}   <- 叠加 τ² (异质性)")
    L(f"    D'(+剔回文)                    = {se_Dp:.6f}  ×{se_Dp/se_A:.3f}")
    L(f"    观察到的 R/Py 比值             = {0.0112433700352803/0.00494:.3f}")

    with open(os.path.join(TEMP, "M4b_s014_rootcause_20261002.csv"), "w",
              newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["口径", "n_snp", "beta", "se", "说明"])
        w.writeheader(); w.writerows(rows)
    L(f"\n[done] -> temp/M4b_s014_rootcause_20261002.csv")


if __name__ == "__main__":
    try:
        main()
    finally:
        open(LOG, "w", encoding="utf-8").write("\n".join(_L))
