# -*- coding: utf-8 -*-
"""
M4b Stage 2 : 非零重叠候选的真实重算 (α̂, β̂, 修正CI, 翻转检测)
=================================================================================
对 Phase 1 筛出的 6 篇"充分IV + 非零π_shared"候选 (S014/S273/S255/S137/S217/S267),
逐一拉真实数据重算两步法MR中介, 并用已验证的 S10 校正 (M4b_s10_cov.py) 算修正前后CI:
  Step1 (暴露->中介): 暴露IVs 作工具, 拉中介关联 -> α̂, se_α
  Step2 (中介->结局, 自然设计): 中介IVs 作工具, 拉结局关联 -> β̂, se_β
  n_shared=|暴露IV ∩ 中介IV|; p_X=n_X; p_M=n_M; F=F_X; N 取 catalog/关联样本量
  S10(rho_MY=0) -> cov_total -> 修正 Var(αβ) -> 修正SE/CI
  翻转判定: 间接效应 αβ 的 naive CI 与 corrected CI 是否跨越 p=0.05 (即是否跨越0)
输出 temp/M4b_stage2_recompute_20260904.csv + 同名 .log
注: 绝对SE可能因个别结局GWAS与TwoSampleMR内部协调差异存在校准偏差(已对D56验证点估计
    误差<4%, 校正幅度widen_pct精确); 翻转判定为筛查级, 最终需R/TwoSampleMR复核。
"""
import os, sys, csv, time, json, math, importlib.util
sys.path.insert(0, r"D:/WorkBuddy/两步法MR中介/③ 真实数据应用")
PROJ=r"D:/WorkBuddy/两步法MR中介"
TEMP=os.path.join(PROJ,"③ 真实数据应用","temp")
LOGD=os.path.join(PROJ,"③ 真实数据应用","log")
os.makedirs(TEMP,exist_ok=True); os.makedirs(LOGD,exist_ok=True)
LOG=os.path.join(LOGD,"M4b_stage2_recompute.log"); LOG_L=[]
def L(m):
    s=f"[{time.strftime('%H:%M:%S')}] {m}"; print(s); LOG_L.append(s)

# 载入依赖
spec=importlib.util.spec_from_file_location("pb","D:/WorkBuddy/两步法MR中介/③ 真实数据应用/M4b_phaseB_pipeline.py")
pb=importlib.util.module_from_spec(spec); spec.loader.exec_module(pb)
get_tophits=pb.get_tophits; get_associations=pb.get_associations; harmonize_ivw=pb.harmonize_ivw
import importlib
s10=importlib.import_module("M4b_s10_cov")
estimate_cov_prod_mr=s10.estimate_cov_prod_mr; corrected_se=s10.corrected_se

CAT=json.load(open(os.path.join(TEMP,"opengwas_gwasinfo_full.json"),encoding="utf-8"))
def cat_N(gid):
    v=CAT.get(gid)
    return v.get("sample_size") if v and v.get("sample_size") else None

SRC=os.path.join(TEMP,"M4b_phaseA_candidates_20260904.csv")
rows=list(csv.DictReader(open(SRC,encoding="utf-8-sig")))
TARGETS=["S014","S273","S255","S137","S217","S267"]
cands=[r for r in rows if r["study_id"] in TARGETS]
L(f"Stage 2 目标候选: {len(cands)} (非零重叠且IV充分)")

out_fields=["study_id","exposure","mediator","outcome","exp_id","med_id","out_id",
            "n_X","n_M","n_shared","pi_shared","F_X",
            "alpha_hat","se_alpha","beta_hat","se_beta",
            "indirect","se_naive","se_corrected","widen_pct",
            "ci_naive_lo","ci_naive_hi","ci_corr_lo","ci_corr_hi",
            "naive_sig","corr_sig","flip","N_X","N_M","N_Y","notes"]
res=[]
for r in cands:
    sid=r["study_id"]; eid=r["exp_id"].strip(); mid=r["med_id"].strip(); oid=r["out_id"].strip()
    L(f"\n--- {sid}: {r['exposure'][:20]} -> {r['mediator'][:20]} -> {r['outcome'][:20]} ---")
    if not(eid and mid and oid):
        L(f"  跳过(缺失accession): exp={eid} med={mid} out={oid}"); continue
    X=get_tophits(eid); M=get_tophits(mid)
    nX=len(X); nM=len(M)
    F_X=sum((v["beta"]/v["se"])**2 for v in X.values())/nX if nX else float("nan")
    shared=len(set(X.keys())&set(M.keys())); pi=shared/min(nX,nM) if min(nX,nM)>0 else 0
    # Step1: exposure -> mediator (IVs = X)
    a_med=get_associations(list(X.keys()), mid)
    a_hat,se_a,nu1,dr1,rs1,_,_=harmonize_ivw(X, a_med, random_effects=False)
    # Step2 natural: mediator -> outcome (IVs = M)
    a_out=get_associations(list(M.keys()), oid)
    b_hat,se_b,nu2,dr2,rs2,_,_=harmonize_ivw(M, a_out, random_effects=False)
    # N
    N_X=cat_N(eid) or int(sorted([v["n"] for v in X.values() if v.get("n")],reverse=True)[0]) if any(v.get("n") for v in X.values()) else 300000
    N_M=cat_N(mid) or int(sorted([v["n"] for v in M.values() if v.get("n")],reverse=True)[0]) if any(v.get("n") for v in M.values()) else 300000
    nY=[v["n"] for v in a_out.values() if v.get("n")]
    N_Y=int(sorted(nY,reverse=True)[0]) if nY else (cat_N(oid) or 300000)
    # S10 correction (rho=0)
    cov_total,_,_=estimate_cov_prod_mr(se_a, se_b, shared, nX, nM, F_X, N_X, N_M, N_Y, rho_MY=0)
    indirect, se_naive, se_corr, widen=corrected_se(a_hat, b_hat, se_a, se_b, cov_total)
    ci_nl=indirect-1.96*se_naive; ci_nh=indirect+1.96*se_naive
    ci_cl=indirect-1.96*se_corr;   ci_ch=indirect+1.96*se_corr
    naive_sig="是" if abs(indirect)>1.96*se_naive else "否"
    corr_sig ="是" if abs(indirect)>1.96*se_corr  else "否"
    flip = "翻转!" if naive_sig!=corr_sig else "无翻转"
    L(f"  α̂={a_hat:.4f}(se={se_a:.4f}) β̂={b_hat:.4f}(se={se_b:.4f}) n_sh={shared} π={pi:.3f} F={F_X:.1f}")
    L(f"  间接效应={indirect:.4f}  naiveSE={se_naive:.4f}  corrSE={se_corr:.4f}  widen={widen:+.1f}%")
    L(f"  naiveCI=[{ci_nl:.4f},{ci_nh:.4f}] corrCI=[{ci_cl:.4f},{ci_ch:.4f}]  naive_sig={naive_sig} corr_sig={corr_sig} -> {flip}")
    notes=f"step1_used={nu1}(drop{dr1}) step2_used={nu2}(drop{dr2}); N_Y={N_Y}"
    res.append({"study_id":sid,"exposure":r["exposure"],"mediator":r["mediator"],"outcome":r["outcome"],
        "exp_id":eid,"med_id":mid,"out_id":oid,"n_X":nX,"n_M":nM,"n_shared":shared,"pi_shared":round(pi,4),
        "F_X":round(F_X,1),"alpha_hat":round(a_hat,5),"se_alpha":round(se_a,5),"beta_hat":round(b_hat,5),
        "se_beta":round(se_b,5),"indirect":round(indirect,5),"se_naive":round(se_naive,5),
        "se_corrected":round(se_corr,5),"widen_pct":round(widen,1),"ci_naive_lo":round(ci_nl,5),
        "ci_naive_hi":round(ci_nh,5),"ci_corr_lo":round(ci_cl,5),"ci_corr_hi":round(ci_ch,5),
        "naive_sig":naive_sig,"corr_sig":corr_sig,"flip":flip,"N_X":N_X,"N_M":N_M,"N_Y":N_Y,"notes":notes})

with open(os.path.join(TEMP,"M4b_stage2_recompute_20260904.csv"),"w",newline="",encoding="utf-8-sig") as f:
    w=csv.DictWriter(f,fieldnames=out_fields); w.writeheader(); w.writerows(res)
L("")
L("=== Stage 2 汇总 ===")
L(f"候选: {len(res)} ; 翻转: {sum(1 for r in res if r['flip'].startswith('翻转'))}")
L(f"widen_pct 范围: {min(r['widen_pct'] for r in res):.1f}% ~ {max(r['widen_pct'] for r in res):.1f}%")
with open(LOG,"w",encoding="utf-8") as f: f.write("\n".join(LOG_L))
L(f"[done] temp/M4b_stage2_recompute_20260904.csv ; log: {LOG}")
