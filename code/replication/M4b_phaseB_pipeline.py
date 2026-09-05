# -*- coding: utf-8 -*-
"""
M4b Phase B : 纯 Python 两步法 MR 中介真实重算流水线 (OpenGWAS REST, 绕开段错误 R 包)
=================================================================================
等价映射 (对照 M4_realdata_pipeline.R):
  extract_instruments(id, p1=5e-8, clump=TRUE, r2=0.001, kb=10000)
      -> POST /tophits?id=..&pval=5e-8&clump=1&r2=0.001&kb=10000&preclumped=1&pop=EUR
  extract_outcome_data(snps=iv$SNP, outcomes=id) + harmonise_data + mr(ivw)
      -> POST /associations?variant=..&id=..&proxies=0&align_alleles=1&population=EUR
         + 本模块内做等位基因方向匹配 + IVW

本文件既是 D56 验证门, 也是后续批量候选的复用核心。

运行: python M4b_phaseB_pipeline.py            # 仅跑 D56 验证门
      python M4b_phaseB_pipeline.py --batch    # 跑候选(占位, 待用户确认候选清单后接)
所有 API 响应缓存到 temp/ 避免重复网络调用。脚本须有详细日志(同名 .log)。
"""
import os, sys, json, time, csv, argparse
import urllib.request, urllib.parse

PROJ   = r"D:/WorkBuddy/两步法MR中介"
TEMP   = os.path.join(PROJ, "③ 真实数据应用", "temp")
LOGD  = os.path.join(PROJ, "③ 真实数据应用", "log")
TOKF   = r"C:/Users/up201/.workbuddy/_ogw_token.txt"
BASE   = "https://api.opengwas.io/api"
CLUMP_PARAMS = {"pval":5e-8,"clump":1,"r2":0.001,"kb":10000,"preclumped":1,"pop":"EUR"}

os.makedirs(TEMP, exist_ok=True); os.makedirs(LOGD, exist_ok=True)
SCRIPT = os.path.abspath(__file__)
LOG    = SCRIPT[:-3] + ".log"

def L(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line); LOG_LINES.append(line)

LOG_LINES = []
TOK = open(TOKF, encoding="utf-8").read().strip()
OP  = urllib.request.build_opener(urllib.request.ProxyHandler({}))

def _post(path, params, retries=4):
    parts = []
    for k, v in params.items():
        if isinstance(v, list):
            for it in v: parts.append(f"{k}={urllib.parse.quote(str(it))}")
        else:
            parts.append(f"{k}={urllib.parse.quote(str(v))}")
    url = BASE + path + "?" + "&".join(parts)
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOK}", "User-Agent": "x"}, method="POST")
            raw = OP.open(req, timeout=180).read()
            return json.loads(raw)
        except urllib.error.HTTPError as e:
            last = e
            if attempt < retries-1:
                time.sleep(4 + attempt*4)   # 退避, 应对间歇性 401/5xx (rate-limit)
                continue
            raise
    if last:
        raise last

def _cache(name, fn):
    p = os.path.join(TEMP, name)
    if os.path.exists(p):
        L(f"  [cache hit] {name}")
        return json.load(open(p, encoding="utf-8"))
    r = fn(); json.dump(r, open(p, "w", encoding="utf-8"), ensure_ascii=False)
    L(f"  [fetched+saved] {name} ({len(r) if isinstance(r,list) else '?'})")
    return r

# ---------- 核心 API 封装 ----------
def get_tophits(gid):
    """返回 dict rsid -> {ea,nea,beta,se,p,n,chr,pos} (clumped, 与 R extract_instruments 一致)"""
    def fn():
        raw = _post("/tophits", {"id": gid, **CLUMP_PARAMS})
        d = {}
        for row in raw:
            d[row["rsid"]] = {"ea":row["ea"],"nea":row["nea"],"beta":float(row["beta"]),
                              "se":float(row["se"]),"p":float(row["p"]),"n":row.get("n"),
                              "chr":row.get("chr"),"pos":row.get("position")}
        return d
    return _cache(f"pb_tophits_{gid}.json", fn)

def get_associations(rsids, gid, chunk=20):
    """返回 dict rsid -> {ea,nea,beta,se,p,n} (align_alleles=1)。
    分块请求(默认20/批)避免单次过大触发 400。结果合并后整体缓存。"""
    rsids = list(rsids)
    def fn():
        merged = {}
        for i in range(0, len(rsids), chunk):
            batch = rsids[i:i+chunk]
            raw = _post("/associations", {"variant": batch, "id": [gid], "proxies":0,
                                         "align_alleles":1, "population":"EUR"})
            time.sleep(0.4)   # 降低突发请求, 规避间歇 401
            for row in raw:
                merged[row["rsid"]] = {"ea":row["ea"],"nea":row["nea"],"beta":float(row["beta"]),
                                       "se":float(row["se"]),"p":float(row["p"]),"n":row.get("n")}
        return merged
    key = f"pb_assoc_{gid}_{abs(hash(tuple(sorted(rsids))))%100000}.json"
    return _cache(key, fn)

# ---------- 等位基因方向匹配 + IVW (TwoSampleMR mr_ivw 等价) ----------
COMP = {"A":"T","T":"A","C":"G","G":"C"}
def harmonize_ivw(inst, assoc, random_effects=True):
    """
    等价 TwoSampleMR mr_ivw (Burgess-Thompson 回归过原点加权):
      对 SNP i: bx_i=暴露效应, by_i=结局效应(已按暴露效应等位是向匹配), sy_i=结局SE
      权重 w_i = bx_i^2 / sy_i^2
      b = Σ(w_i * bx_i*by_i) / Σ(w_i * bx_i^2)  =  Σ(w_i g_i)/Σ(w_i), g_i=by_i/bx_i
      固定效应 SE = 1/sqrt(Σ w_i)
      随机效应(默认, random_effects=TRUE):
        Q = Σ w_i (by_i - b*bx_i)^2  (回归残差异质性)
        tau2 = max(0,(Q-(k-1))/Σw_i)
        se_RE = sqrt(1/Σw_i + tau2)
    返回 (b, se, n_used, n_dropped, reasons, tau2, Q)
    等位方向: 结局 ea==暴露 ea -> 不翻转; 结局 ea==暴露 nea -> 翻转(负); 否则丢弃。
    """
    bx, by, sy = [], [], []; used = 0; dropped = 0; reasons = {}
    for rs, ex in inst.items():
        ay = assoc.get(rs)
        if ay is None:
            dropped += 1; reasons["missing_outcome"] = reasons.get("missing_outcome",0)+1; continue
        if ay["ea"] == ex["ea"]:
            b_out = ay["beta"]
        elif ay["ea"] == ex["nea"]:
            b_out = -ay["beta"]
        else:
            dropped += 1; reasons["ambiguous_allele"] = reasons.get("ambiguous_allele",0)+1; continue
        be, se_o = ex["beta"], ay["se"]
        if be == 0 or se_o == 0:
            dropped += 1; reasons["zero_beta_se"] = reasons.get("zero_beta_se",0)+1; continue
        bx.append(be); by.append(b_out); sy.append(se_o); used += 1
    if not bx:
        return (float("nan"), float("nan"), 0, dropped, reasons, None, None)
    ws = [(bxi**2)/(soi**2) for bxi, soi in zip(bx, sy)]
    W = sum(ws)
    b = sum(w*bxi*byi for w,bxi,byi in zip(ws,bx,by)) / sum(w*bxi**2 for w,bxi in zip(ws,bx))
    se_fe = 1.0/(W**0.5)
    tau2 = None; Q = None; se = se_fe
    if random_effects and len(bx) > 1:
        Q = sum(w*(byi - b*bxi)**2 for w,bxi,byi in zip(ws,bx,by))
        tau2 = max(0.0, (Q-(len(bx)-1))/W)
        se = (1.0/W + tau2)**0.5
    return (b, se, used, dropped, reasons, tau2, Q)

# ---------- D56 验证门 ----------
def validate_D56():
    L("="*70)
    L("D56 验证门: 纯 Python 流水线复现 BMI(ieu-a-2)->Waist(ieu-a-61)->CHD(ieu-a-7)")
    L("对照沉积 R 结果 M4_rerun_20260903/M4_results.csv (rho_MY=0 行)")
    DEP = {
        "alpha": (0.862894725304433, 0.0174075089859624),
        "beta_nat": (0.477334636004418, 0.0883770373649039),
        "beta_sh": (0.479563610811995, 0.064532226118295),
        "p_X": 78, "p_M": 41, "n_shared_nat": 13,
    }
    bmi = get_tophits("ieu-a-2")
    waist = get_tophits("ieu-a-61")
    L(f"  tophits BMI(ieu-a-2) SNPs={len(bmi)} (沉积 p_X=78)")
    L(f"  tophits Waist(ieu-a-61) SNPs={len(waist)} (沉积 p_M=41)")
    # Step1: BMI -> Waist
    a_waist = get_associations(list(bmi.keys()), "ieu-a-61")
    a_chd_from_bmi = get_associations(list(bmi.keys()), "ieu-a-7")
    a_chd_from_waist = get_associations(list(waist.keys()), "ieu-a-7")
    # 两种 IVW 口径都算, 选与沉积值更相近者
    def both(inst, assoc):
        fe = harmonize_ivw(inst, assoc, random_effects=False)
        re = harmonize_ivw(inst, assoc, random_effects=True)
        return fe, re
    fe1, re1 = both(bmi, a_waist)
    fe2, re2 = both(waist, a_chd_from_waist)
    fe3, re3 = both(bmi, a_chd_from_bmi)
    # 选 RE 若其 SE 更接近沉积(否则 FE)。先默认 RE 展示
    a_hat, se_a = re1[0], re1[1]
    b_nat, se_bn = re2[0], re2[1]
    b_sh, se_bs = re3[0], re3[1]
    def show(tag, fe, re, dep):
        L(f"  {tag}")
        L(f"    FE : b={fe[0]:.6f} se={fe[1]:.6f} (n={fe[2]},drop={fe[3]})")
        L(f"    RE : b={re[0]:.6f} se={re[1]:.6f} tau2={re[5]}")
        L(f"    沉积: b={dep[0]:.6f} se={dep[1]:.6f}")
    L("")
    show("Step1 BMI->Waist (alpha)", fe1, re1, DEP['alpha'])
    show("Step2(nat) Waist->CHD (beta_nat)", fe2, re2, DEP['beta_nat'])
    show("Step2(shared) Waist->CHD BMI-IVs (beta_sh)", fe3, re3, DEP['beta_sh'])
    def sig(b, se): return "显著(p<0.05)" if abs(b) > 1.96*se else "不显著"
    L("")
    L(f"  沉积 alpha 显著性: {sig(*DEP['alpha'])} ; 复现(RE) alpha 显著性: {sig(a_hat,se_a)}")
    ok = (abs(a_hat-DEP['alpha'][0])<0.01 and abs(se_a-DEP['alpha'][1])<0.01 and
          abs(b_nat-DEP['beta_nat'][0])<0.01 and abs(se_bn-DEP['beta_nat'][1])<0.01 and
          abs(b_sh-DEP['beta_sh'][0])<0.01 and abs(se_bs-DEP['beta_sh'][1])<0.01)
    L("")
    L("  验证门结论(采用随机效应RE口径, 对照 TwoSampleMR mr_ivw 默认): " +
      ("✅ 通过 (纯Python流水线复现R结果, 误差<0.01, 可复用新候选)"
       if ok else "❌ 未通过 (需停修流水线, 禁止用于新候选!)"))
    return ok, (a_hat,se_a,b_nat,se_bn,b_sh,se_bs)

# ---------- 主入口 ----------
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", action="store_true", help="跑候选(占位)")
    args = ap.parse_args()
    L(f"=== M4b Phase B 流水线启动 (PID无关) ===")
    L(f"Python={sys.version.split()[0]}  token_len={len(TOK)}")
    ok, _ = validate_D56()
    if not ok:
        L("验证门未通过 -> 终止, 不上新候选。")
        sys.exit(2)
    L("验证门已通过。批量候选逻辑待用户确认候选清单后接入 (本脚本已具备 get_tophits/get_associations/harmonize_ivw 复用核心)。")
    with open(LOG, "w", encoding="utf-8") as f:
        f.write("\n".join(LOG_LINES))
    L(f"[log saved] {LOG}")
