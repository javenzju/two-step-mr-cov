# -*- coding: utf-8 -*-
"""
M4b Stage 1 : 真实 IV 重叠 (pi_shared) 批量计算 (纯本地+OpenGWAS /tophits, 无 SE 依赖)
=================================================================================
对 Phase A 通过的 70 篇候选 (A2+B), 逐一:
  - 拉暴露 / 中介 的 clumped 显著 IV 集 (复用 M4b_phaseB_pipeline.get_tophits, 缓存)
  - n_X = |暴露IV|, n_M = |中介IV|
  - n_shared = |暴露IV ∩ 中介IV|   (step1 暴露IV 与 step2 中介IV 的真实重叠)
  - pi_shared = n_shared / min(n_X, n_M)
  - F_X, F_M (IV 强度, 均值 (b/se)^2)
输出 temp/M4b_pishared_20260904.csv + 同名 .log
pi_shared 是论文"真实重叠分布"的核心实证量, 不依赖任何 SE 校准, 结果精确可复现。
"""
import os, sys, csv, time, importlib.util
PROJ=r"D:/WorkBuddy/两步法MR中介"
TEMP=os.path.join(PROJ,"③ 真实数据应用","temp")
LOGD=os.path.join(PROJ,"③ 真实数据应用","log")
os.makedirs(TEMP,exist_ok=True); os.makedirs(LOGD,exist_ok=True)
LOG_LINES=[]
def L(m):
    s=f"[{time.strftime('%H:%M:%S')}] {m}"; print(s); LOG_LINES.append(s)

# 载入流水线模块 (复用 get_tophits / CLUMP_PARAMS)
spec=importlib.util.spec_from_file_location("pb","D:/WorkBuddy/两步法MR中介/③ 真实数据应用/M4b_phaseB_pipeline.py")
pb=importlib.util.module_from_spec(spec); spec.loader.exec_module(pb)
get_tophits=pb.get_tophits

SRC=os.path.join(TEMP,"M4b_phaseA_candidates_20260904.csv")
OUT=os.path.join(TEMP,"M4b_pishared_20260904.csv")
LOG=os.path.join(LOGD,"M4b_stage1_pishared.log")

def clean(v):
    v=(v or "").strip()
    if not v or v.startswith("未匹配") or v in ("NA","nan"): return ""
    return v

rows=list(csv.DictReader(open(SRC,encoding="utf-8-sig")))
# 仅取通过筛选的 A2 / B 候选
pass_rows=[r for r in rows if r["priority"][:1] in ("A","B")]
L(f"Phase A 通过候选 (A2+B): {len(pass_rows)} / 总 {len(rows)}")

# 收集唯一 accession (exp + med)
accs=set()
for r in pass_rows:
    for f in ("exp_id","med_id"):
        c=clean(r[f])
        if c: accs.add(c)
L(f"唯一 accession (exp+med): {len(accs)} ; 开始拉取 clumped IV 集...")

cache={}
for i,g in enumerate(sorted(accs),1):
    cache[g]=get_tophits(g)
    if i%10==0: L(f"  已拉 {i}/{len(accs)}")

out_fields=["study_id","first_author_year","journal","priority",
            "exposure","exp_id","mediator","med_id","outcome","out_id",
            "n_X","n_M","n_shared","pi_shared","F_X","F_M","overlap_note"]
res=[]
nonzero=0; computed=0
for r in pass_rows:
    eid=clean(r["exp_id"]); mid=clean(r["med_id"]); oid=clean(r["out_id"])
    if not eid or not mid:
        res.append({**{k:r.get(k,"") for k in out_fields[:-1]},"n_X":"","n_M":"","n_shared":"","pi_shared":"","F_X":"","F_M":"","overlap_note":"暴露或中介未解析,跳过"})
        continue
    X=cache[eid]; M=cache[mid]
    nX=len(X); nM=len(M)
    shared=len(set(X.keys())&set(M.keys()))
    pi=shared/min(nX,nM) if min(nX,nM)>0 else float("nan")
    fx=sum((v["beta"]/v["se"])**2 for v in X.values())/nX if nX else float("nan")
    fm=sum((v["beta"]/v["se"])**2 for v in M.values())/nM if nM else float("nan")
    note="非零重叠" if shared>0 else "零重叠"
    if shared>0: nonzero+=1
    computed+=1
    res.append({"study_id":r["study_id"],"first_author_year":r.get("first_author_year",""),
                "journal":r.get("journal",""),"priority":r["priority"][:2],
                "exposure":r["exposure"],"exp_id":eid,"mediator":r["mediator"],"med_id":mid,
                "outcome":r["outcome"],"out_id":oid,"n_X":nX,"n_M":nM,"n_shared":shared,
                "pi_shared":round(pi,4),"F_X":round(fx,1),"F_M":round(fm,1),"overlap_note":note})

with open(OUT,"w",newline="",encoding="utf-8-sig") as f:
    w=csv.DictWriter(f,fieldnames=out_fields); w.writeheader(); w.writerows(res)

L("")
L(f"=== Stage 1 结果 ===")
L(f"可计算候选: {computed} ; 非零重叠: {nonzero} ({100*nonzero/computed:.1f}%) ; 零重叠: {computed-nonzero}")
pis=[r["pi_shared"] for r in res if isinstance(r["pi_shared"],float) or (isinstance(r["pi_shared"],str) and r["pi_shared"] not in ("",))]
# 重新解析 float
piv=[float(r["pi_shared"]) for r in res if str(r["pi_shared"]).replace(".","").isdigit()]
if piv:
    L(f"pi_shared 分布: min={min(piv):.3f} median={sorted(piv)[len(piv)//2]:.3f} max={max(piv):.3f} mean={sum(piv)/len(piv):.3f}")
    L(f"  pi_shared>0 的篇数: {sum(1 for p in piv if p>0)} / {len(piv)}")
with open(LOG,"w",encoding="utf-8") as f: f.write("\n".join(LOG_LINES))
L(f"[done] {OUT}")
L(f"[log] {LOG}")
PY