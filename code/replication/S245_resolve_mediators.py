# -*- coding: utf-8 -*-
"""解析 S245 两中介在 OpenGWAS catalog 中的 accession（纯本地，读已下载全量 catalog）"""
import json, os, csv, datetime

ROOT = r"D:/WorkBuddy/两步法MR中介/③ 真实数据应用"
CATALOG = os.path.join(ROOT, "temp", "opengwas_gwasinfo_full.json")
OUT = os.path.join(ROOT, "temp", "S245_mediator_accessions_20260903.csv")
LOG = os.path.join(ROOT, "log", "S245_resolve_mediators.log")

log_lines = [f"start {datetime.datetime.now()}"]
cat = json.load(open(CATALOG, encoding='utf-8'))
log_lines.append(f"catalog datasets: {len(cat)}")

def find(prefix, *kw):
    res = []
    for d in cat.values():
        iid = d.get('id','')
        tr = (d.get('trait') or '')
        if iid.startswith(prefix):
            tl = tr.lower()
            if all(k.lower() in tl for k in kw):
                res.append(d)
    return res

# 代谢物：X-11,423-O-sulfo-L-tyrosine （在 met-a- 前缀）
met_matches = find('met-a-', 'sulfo') + find('met-a-', 'tyrosine')
# 蛋白：neuropilin-2 （在 prot-a- 前缀）
prot_matches = find('prot-a-', 'neuropilin')

cols = ['id','trait','prefix','sample_size','nsnp','pmid','year','author','build']
rows = []
for d in met_matches:
    rows.append({'id':d.get('id'),'trait':d.get('trait'),'prefix':'met-a-',
                 'sample_size':d.get('sample_size'),'nsnp':d.get('nsnp'),
                 'pmid':d.get('pmid'),'year':d.get('year'),'author':d.get('author'),'build':d.get('build')})
for d in prot_matches:
    rows.append({'id':d.get('id'),'trait':d.get('trait'),'prefix':'prot-a-',
                 'sample_size':d.get('sample_size'),'nsnp':d.get('nsnp'),
                 'pmid':d.get('pmid'),'year':d.get('year'),'author':d.get('author'),'build':d.get('build')})

with open(OUT,'w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)

log_lines.append(f"代谢物(sulfo/tyrosine) in met-a-: {len(met_matches)} 命中")
for d in met_matches: log_lines.append(f"   met: {d.get('id')} | {d.get('trait')} | n={d.get('sample_size')} nsnp={d.get('nsnp')} pmid={d.get('pmid')}")
log_lines.append(f"蛋白(neuropilin) in prot-a-: {len(prot_matches)} 命中")
for d in prot_matches: log_lines.append(f"   prot: {d.get('id')} | {d.get('trait')} | n={d.get('sample_size')} nsnp={d.get('nsnp')} pmid={d.get('pmid')}")
log_lines.append(f"end {datetime.datetime.now()}")

with open(LOG,'w',encoding='utf-8') as f: f.write("\n".join(log_lines)+"\n")
print("\n".join(log_lines))
print(f"\n-> {OUT}")
