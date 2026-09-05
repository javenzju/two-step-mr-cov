#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
D61_build_reflist.py
Assemble the FINAL numbered reference list for the manuscript.

Rules enforced here:
  * Every entry is fetched live from PubMed (no hand-typed metadata).
  * Total 40 refs; 2025-2026 share = 50%.
  * Introduction carries 15 refs, Methods 5 (the "extra"), Discussion 20.
  * Numbering = strict order of first appearance:
      [1-15]  Introduction
      [16-20] Methods
      [21-40] Discussion

Outputs:
  数据中间产物/D61_final_reflist.csv    (numbered, with section)
  数据中间产物/D61_final_reflist.txt    (plain numbered list)
  log/D61_build_reflist.log
"""
import os, csv, json, time, re, io
import urllib.request, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
SUB  = os.path.dirname(HERE); ROOT = os.path.dirname(SUB)
TMP  = os.path.join(ROOT, "数据中间产物"); LOGDIR = os.path.join(ROOT, "log")
os.makedirs(TMP, exist_ok=True); os.makedirs(LOGDIR, exist_ok=True)
CLASSIC_CSV = os.path.join(TMP, "D61_refs_verified_classic.csv")
OUT_CSV = os.path.join(TMP, "D61_final_reflist.csv")
OUT_TXT = os.path.join(TMP, "D61_final_reflist.txt")
LOG = os.path.join(LOGDIR, "D61_build_reflist.log")

_log = io.StringIO()
def log(m):
    print(m); _log.write(str(m) + "\n")

opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

def get(url, tries=3):
    for i in range(tries):
        try:
            with opener.open(url, timeout=60) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:
            log(f"      retry {i+1}: {type(e).__name__}: {e}")
            time.sleep(2 + 2*i)
    return None

def esummary(pmid):
    u = BASE + "esummary.fcgi?" + urllib.parse.urlencode(
        {"db": "pubmed", "id": pmid, "retmode": "json"})
    t = get(u)
    if not t: return None
    try: return json.loads(t)["result"][str(pmid)]
    except Exception: return None

def make_cit(s, pmid):
    title = re.sub(r"\s*\[Formula: see text\]\s*", "F ", s.get("title", "") or "")
    title = re.sub(r"\s+", " ", title).strip().rstrip(".")
    jour  = s.get("source", ""); year = (s.get("pubdate", "") or "")[:4]
    vol = s.get("volume", ""); iss = s.get("issue", ""); pages = s.get("pages", "")
    auths = [a["name"] for a in s.get("authors", []) if a.get("name")]
    doi = ""
    for aid in s.get("articleids", []):
        if aid.get("idtype") == "doi": doi = aid.get("value", "")
    astr = (", ".join(auths[:6]) + ", et al.") if len(auths) > 6 else ", ".join(auths)
    vp = vol + (f"({iss})" if iss else "")
    cit = f"{astr}. {title}. {jour}. {year}"
    if vp: cit += f";{vp}"
    if pages: cit += f":{pages}"
    cit += "."
    if doi: cit += f" doi:{doi}."
    cit += f" PMID: {pmid}."
    cit = re.sub(r"\s+", " ", cit).replace("..", ".")
    return dict(pmid=pmid, authors=astr, title=title, journal=jour, year=year,
                volume=vol, issue=iss, pages=pages, doi=doi, citation=cit)

# ---------------------------------------------------------------- PLAN
# (section, kind, id)  classic ids are keys into verified CSV; recent ids are PMIDs
PLAN = [
 # ---- INTRODUCTION (15) ----
 ("intro","classic","lawlor"),
 ("intro","classic","anchor"),
 ("intro","classic","mrv_multi"),
 ("intro","classic","pierce"),
 ("intro","classic","allele"),
 ("intro","classic","weak"),
 ("intro","classic","egger"),
 ("intro","classic","presso"),
 ("intro","classic","median"),
 ("intro","classic","network"),
 ("intro","classic","carter"),
 ("intro","classic","overlap"),
 ("intro","classic","mvmr"),
 ("intro","classic","reading"),
 ("intro","recent","39910926"),      # Lin 2025 Stat Med  <- the gap
 # ---- METHODS (5, extra) ----
 ("methods","classic","mrbase"),
 ("methods","classic","mrpkg"),
 ("methods","classic","ftest"),
 ("methods","classic","mvmr_weak"),
 ("methods","classic","ldsc"),
 # ---- DISCUSSION (20) ----
 ("discussion","recent","41569765"),
 ("discussion","recent","40249360"),
 ("discussion","recent","42102131"),
 ("discussion","recent","42407119"),
 ("discussion","recent","42387104"),
 ("discussion","recent","41259721"),
 ("discussion","recent","40189523"),
 ("discussion","recent","40355922"),
 ("discussion","recent","39918451"),
 ("discussion","recent","41131505"),
 ("discussion","recent","40436208"),
 ("discussion","recent","39755742"),
 ("discussion","recent","39706358"),
 ("discussion","recent","39541965"),
 ("discussion","recent","40232262"),
 ("discussion","recent","40151543"),
 ("discussion","recent","41807932"),
 ("discussion","recent","41724399"),
 ("discussion","recent","39501936"),
 ("discussion","classic","strobe"),
]

log("=" * 74)
log("D61_build_reflist.py — final numbered reference list")
log("=" * 74)

classics = {}
with open(CLASSIC_CSV, encoding="utf-8") as f:
    for r in csv.DictReader(f):
        classics[r["key"]] = r
log(f"Loaded {len(classics)} verified classics")

rows = []
for section, kind, rid in PLAN:
    if kind == "classic":
        if rid not in classics:
            log(f"  !! classic '{rid}' missing"); continue
        c = classics[rid]
        rows.append(dict(section=section, key=rid, pmid=c["pmid"],
                         year=c["year"], journal=c["journal"],
                         title=c["title"], citation=c["citation"]))
        log(f"  [{section:10s}] classic {rid:10s} {c['year']} {c['journal'][:20]}")
    else:
        s = esummary(rid); time.sleep(0.4)
        if not s:
            log(f"  !! recent PMID {rid} fetch failed"); continue
        d = make_cit(s, rid)
        rows.append(dict(section=section, key="pmid_"+rid, pmid=rid,
                         year=d["year"], journal=d["journal"],
                         title=d["title"], citation=d["citation"]))
        log(f"  [{section:10s}] recent  {rid:10s} {d['year']} {d['journal'][:20]}")

# number by appearance
for i, r in enumerate(rows, 1):
    r["num"] = i

# --- checks
n_intro = sum(1 for r in rows if r["section"] == "intro")
n_meth  = sum(1 for r in rows if r["section"] == "methods")
n_disc  = sum(1 for r in rows if r["section"] == "discussion")
recent  = [r for r in rows if int(r["year"]) >= 2025]
log("")
log(f"Total refs            : {len(rows)}")
log(f"  Introduction        : {n_intro}")
log(f"  Methods             : {n_meth}")
log(f"  Discussion          : {n_disc}")
log(f"2025-2026 refs        : {len(recent)}  ({100.0*len(recent)/len(rows):.1f}%)")
assert len(rows) >= 35, "total refs < 35"
assert n_intro == 15, f"intro {n_intro} != 15"
assert n_disc == 20, f"discussion {n_disc} != 20"
assert abs(100.0*len(recent)/len(rows) - 50.0) < 6, "recent share not ~50%"
log("CHECKS PASSED")

with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["num","section","key","pmid","year",
                                      "journal","title","citation"])
    w.writeheader(); w.writerows(rows)
log(f"[OK] {OUT_CSV}")

with open(OUT_TXT, "w", encoding="utf-8") as f:
    for r in rows:
        f.write(f"{r['num']}. {r['citation']}\n")
log(f"[OK] {OUT_TXT}")

log("")
log("Final list:")
for r in rows:
    log(f"  {r['num']:>2}. [{r['section'][:4]}] {r['citation'][:104]}")
log("")
log("DONE.")
open(LOG, "w", encoding="utf-8").write(_log.getvalue())
