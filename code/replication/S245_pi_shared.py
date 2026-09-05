# -*- coding: utf-8 -*-
"""
S245 真实 π_shared 计算（纯 API+Python，绕开段错误的 R 包）
- 拉 TG(ieu-a-302) / 代谢物(met-a-509) / 蛋白(prot-a-2100) / MM(finn-b-CD2_MULTIPLE_MYELOMA_PLASMA_CELL) 的 tophits(P<5e-8, clump=False)
- 计算 TG∩中介 的真实重叠数与 π_shared = |shared| / min(|TG|,|mediator|)
- 附报 中介∩MM、TG∩MM（供参考）
"""
import urllib.request, json, os, csv, datetime

TOKEN = open(r"C:/Users/up201/.workbuddy/_ogw_token.txt", encoding='utf-8').read().strip()
ROOT = r"D:/WorkBuddy/两步法MR中介/③ 真实数据应用"
OUT = os.path.join(ROOT, "temp", "S245_pi_shared_20260903.csv")
LOG = os.path.join(ROOT, "log", "S245_pi_shared.log")
op = urllib.request.build_opener(urllib.request.ProxyHandler({}))

IDS = {
    "TG(ieu-a-302)": "ieu-a-302",
    "metabolite(met-a-509)": "met-a-509",
    "protein(prot-a-2100)": "prot-a-2100",
    "MM(finn-b-CD2_MULTIPLE_MYELOMA_PLASMA_CELL)": "finn-b-CD2_MULTIPLE_MYELOMA_PLASMA_CELL",
}

def tophits(iid):
    url = "https://api.opengwas.io/api/tophits"
    body = {"id": iid, "pval_threshold": 5e-8, "clump": False}
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}, method="POST")
    with op.open(req, timeout=120) as r:
        data = json.loads(r.read())
    return set(d['rsid'] for d in data if d.get('rsid'))

log_lines = [f"start {datetime.datetime.now()}"]
sets = {}
for label, iid in IDS.items():
    s = tophits(iid)
    sets[label] = s
    log_lines.append(f"{label} ({iid}): n_IV={len(s)}")

def overlap(a, b):
    return len(a & b)

A = sets["TG(ieu-a-302)"]
Bm = sets["metabolite(met-a-509)"]
Bp = sets["protein(prot-a-2100)"]
C = sets["MM(finn-b-CD2_MULTIPLE_MYELOMA_PLASMA_CELL)"]

rows = []
# 主指标：TG ∩ 中介
sh_met = overlap(A, Bm); pi_met = sh_met / min(len(A), len(Bm)) if min(len(A), len(Bm)) else float('nan')
sh_prot = overlap(A, Bp); pi_prot = sh_prot / min(len(A), len(Bp)) if min(len(A), len(Bp)) else float('nan')
rows.append({"pair": "TG ∩ metabolite(met-a-509)", "n_TG": len(A), "n_other": len(Bm),
             "n_shared": sh_met, "pi_shared_pct": round(pi_met*100, 4)})
rows.append({"pair": "TG ∩ protein(prot-a-2100)", "n_TG": len(A), "n_other": len(Bp),
             "n_shared": sh_prot, "pi_shared_pct": round(pi_prot*100, 4)})
# 附报
sh_mm_met = overlap(Bm, C); rows.append({"pair": "metabolite ∩ MM", "n_TG": len(Bm), "n_other": len(C), "n_shared": sh_mm_met, "pi_shared_pct": round(sh_mm_met/min(len(Bm),len(C))*100,4) if min(len(Bm),len(C)) else 'NA'})
sh_mm_prot = overlap(Bp, C); rows.append({"pair": "protein ∩ MM", "n_TG": len(Bp), "n_other": len(C), "n_shared": sh_mm_prot, "pi_shared_pct": round(sh_mm_prot/min(len(Bp),len(C))*100,4) if min(len(Bp),len(C)) else 'NA'})
sh_tg_mm = overlap(A, C); rows.append({"pair": "TG ∩ MM", "n_TG": len(A), "n_other": len(C), "n_shared": sh_tg_mm, "pi_shared_pct": round(sh_tg_mm/min(len(A),len(C))*100,4) if min(len(A),len(C)) else 'NA'})

with open(OUT, 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=["pair", "n_TG", "n_other", "n_shared", "pi_shared_pct"]); w.writeheader(); w.writerows(rows)

log_lines.append("=== π_shared 结果 ===")
for r in rows: log_lines.append(f"  {r['pair']}: n_shared={r['n_shared']} pi_shared%={r['pi_shared_pct']}")
log_lines.append(f"end {datetime.datetime.now()}")
with open(LOG, 'w', encoding='utf-8') as f: f.write("\n".join(log_lines)+"\n")
print("\n".join(log_lines))
print(f"\n-> {OUT}")
