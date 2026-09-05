#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
D61_verify_refs.py  (v2)
Verify reference metadata against PubMed by candidate PMID, then VALIDATE the
returned title against expected keywords. A wrong PMID is auto-rejected because
the returned title will not contain the expected keywords, so nothing unverified
can enter the reference list.

Outputs:
  数据中间产物/D61_refs_verified_classic.csv
  log/D61_verify_refs.log
"""
import os, csv, json, time, urllib.request, urllib.parse, io

HERE = os.path.dirname(os.path.abspath(__file__))
SUB  = os.path.dirname(HERE); ROOT = os.path.dirname(SUB)
TMP  = os.path.join(ROOT, "数据中间产物"); LOGDIR = os.path.join(ROOT, "log")
os.makedirs(TMP, exist_ok=True); os.makedirs(LOGDIR, exist_ok=True)
OUT = os.path.join(TMP, "D61_refs_verified_classic.csv")
LOG = os.path.join(LOGDIR, "D61_verify_refs.log")

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

def esearch_ids(term, n=8):
    u = BASE + "esearch.fcgi?" + urllib.parse.urlencode(
        {"db": "pubmed", "term": term, "retmax": str(n), "retmode": "json",
         "sort": "relevance"})
    t = get(u)
    if not t: return []
    try: return json.loads(t)["esearchresult"].get("idlist", [])
    except Exception: return []

def esummary(pmid):
    u = BASE + "esummary.fcgi?" + urllib.parse.urlencode(
        {"db": "pubmed", "id": pmid, "retmode": "json"})
    t = get(u)
    if not t: return None
    try: return json.loads(t)["result"][str(pmid)]
    except Exception: return None

def build_cit(s, pmid):
    title = (s.get("title", "") or "").rstrip(".")
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
    return dict(pmid=pmid, authors=astr, title=title, journal=jour, year=year,
                volume=vol, issue=iss, pages=pages, doi=doi, citation=cit)

# label, candidate PMID, expected keywords (ALL must appear, case-insensitive)
CANDS = [
 ("mrv_multi", "24114802", ["multiple genetic variants", "summarized data"]),
 ("weak",      "21653540", ["weak instruments"]),
 ("network",   "25150977", ["network mendelian randomization"]),
 ("overlap",   "27625185", ["participant overlap"]),
 ("carter",    "33961203", ["mediation analysis"]),
 ("ftest",     "26661904", ["weak instrument f-test"]),
 ("egger",     "26626044", ["egger regression"]),
 ("presso",    "29686387", ["horizontal pleiotropy"]),
 ("mrbase",    "29846171", ["mr-base"]),
 ("mrpkg",     "28398548", ["mendelianrandomization"]),
 ("strobe",    "34375962", ["strengthening the reporting"]),
 ("mvmr",      "30825946", ["multivariable mendelian randomization"]),
 ("reading",   "30052728", ["reading mendelian randomisation"]),
 ("allele",    "26893891", ["allele score"]),
 ("pierce",    "23863760", ["efficient design"]),
 ("anchor",    "25064373", ["genetic anchors"]),
 ("ldsc",      "25642630", ["ld score regression"]),
 ("lawlor",    "18971930", ["genes as instruments"]),
 ("median",    "25896065", ["weighted median"]),
 ("mvmr_weak", "33684295", ["pleiotropic instruments"]),
]

log("=" * 74)
log("D61_verify_refs.py v2 — PMID fetch + title-keyword validation")
log("=" * 74)

rows, rejected = [], []
for key, pmid, kws in CANDS:
    log(f"[{key}] PMID {pmid}  expect: {kws}")
    s = esummary(pmid); time.sleep(0.4)
    if not s:
        log("      !! fetch failed"); rejected.append((key, pmid, "fetch failed")); continue
    title = (s.get("title", "") or "").lower()
    ok = all(k.lower() in title for k in kws)
    rec = build_cit(s, pmid)
    if ok:
        rows.append(dict(key=key, **rec))
        log(f"      MATCH  {rec['journal']} {rec['year']};{rec['volume']}:{rec['pages']}")
        log(f"             {rec['citation'][:118]}")
    else:
        rejected.append((key, pmid, rec["title"][:70]))
        log(f"      REJECT title={rec['title'][:70]}")

log("")
if rejected:
    log(f"Rejected {len(rejected)} (will resolve by search):")
    for k, p, t in rejected:
        log(f"   {k:10s} PMID {p}  -> {t}")

# --- resolve rejected by keyword search, picking best title match
if rejected:
    log("")
    log("--- resolving rejects by search ---")
    SEARCH_TERMS = {
      "mrv_multi": "Mendelian randomization analysis with multiple genetic variants using summarized data",
      "weak": "Avoiding bias from weak instruments in Mendelian randomization studies",
      "network": "Network Mendelian randomization mediation causal pathways",
      "overlap": "Bias due to participant overlap in two-sample Mendelian randomization",
      "carter": "Mendelian randomisation for mediation analysis current methods challenges",
      "ftest": "weak instrument F-test linear IV models multiple endogenous variables",
      "egger": "Mendelian randomization invalid instruments Egger regression",
      "presso": "Detection of widespread horizontal pleiotropy Mendelian randomization",
      "mrbase": "MR-Base platform systematic causal inference human phenome",
      "mrpkg": "MendelianRandomization R package summarized data",
      "strobe": "STROBE-MR strengthening reporting observational studies Mendelian randomization",
      "mvmr": "multivariable Mendelian randomization single-sample two-sample summary data",
      "reading": "Reading Mendelian randomisation studies guide glossary checklist clinicians",
      "allele": "Combining information multiple instrumental variables allele score summarized data",
      "pierce": "Efficient design Mendelian randomization subsample two-sample instrumental variable",
      "anchor": "Mendelian randomization genetic anchors causal inference epidemiological studies",
      "ldsc": "LD Score regression distinguishes confounding from polygenicity",
      "lawlor": "Mendelian randomization using genes as instruments causal inferences epidemiology",
      "median": "Weighted median estimator Mendelian randomization invalid instruments",
      "mvmr_weak": "Testing correcting weak pleiotropic instruments two-sample multivariable Mendelian randomization",
    }
    for key, pmid, _t in list(rejected):
        kw = dict((c[0], c[2]) for c in CANDS)[key]
        ids = esearch_ids(SEARCH_TERMS.get(key, ""), n=8); time.sleep(0.4)
        found = None
        for pid in ids:
            s = esummary(pid); time.sleep(0.4)
            if not s: continue
            tl = (s.get("title", "") or "").lower()
            if all(k.lower() in tl for k in kw):
                found = build_cit(s, pid); break
        if found:
            rows.append(dict(key=key, **found))
            log(f"  [{key}] RESOLVED -> PMID {found['pmid']} {found['journal']} {found['year']}")
            log(f"           {found['citation'][:118]}")
        else:
            log(f"  [{key}] UNRESOLVED (dropped)")

with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["key","pmid","authors","title","journal",
                                      "year","volume","issue","pages","doi","citation"])
    w.writeheader(); w.writerows(rows)
log("")
log(f"[OK] verified {len(rows)} / {len(CANDS)} -> {OUT}")
log("DONE.")
open(LOG, "w", encoding="utf-8").write(_log.getvalue())
