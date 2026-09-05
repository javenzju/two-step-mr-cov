#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
D61_pick_recent_refs.py
Parse D61_references_pubmed.txt (1364 real PubMed records) and extract
2025-2026 publications as candidate references for the manuscript.

Record layout (blank-line separated):
  line0: Journal. YEAR Mon;vol(issue). doi: ...
  line1: Title
  line2: Authors
  line3: PMID: ... PMCID: ... DOI: ...
  then "Abstract" + body

Outputs:
  temp/D61_refs_year_counts.csv      - year distribution
  temp/D61_refs_2025_2026.csv        - all 2025-2026 records w/ full metadata
  log/D61_pick_recent_refs.log       - run log (same basename as script)
"""
import os, re, csv, sys, io

# --- self-detect project root: script lives in <root>/⑤ 投稿文件_20260904/references/
HERE = os.path.dirname(os.path.abspath(__file__))
SUB  = os.path.dirname(HERE)                 # ⑤ 投稿文件_20260904
ROOT = os.path.dirname(SUB)                  # project root

SRC      = os.path.join(HERE, "D61_references_pubmed.txt")
TMP      = os.path.join(ROOT, "数据中间产物")
LOGDIR   = os.path.join(ROOT, "log")
os.makedirs(TMP, exist_ok=True)
os.makedirs(LOGDIR, exist_ok=True)

YEAR_CSV = os.path.join(TMP, "D61_refs_year_counts.csv")
REC_CSV  = os.path.join(TMP, "D61_refs_2025_2026.csv")
LOG      = os.path.join(LOGDIR, "D61_pick_recent_refs.log")

_log = io.StringIO()
def log(msg):
    print(msg)
    _log.write(str(msg) + "\n")

log("=" * 70)
log("D61_pick_recent_refs.py — extract 2025-2026 candidate references")
log("=" * 70)
log(f"Source: {SRC}")
log(f"Exists: {os.path.exists(SRC)}")
if not os.path.exists(SRC):
    log("FATAL: source file missing.")
    open(LOG, "w", encoding="utf-8").write(_log.getvalue())
    sys.exit(1)

raw = open(SRC, encoding="utf-8", errors="replace").read()
log(f"File size: {len(raw)} chars")

# split on blank lines
chunks = [c.strip() for c in re.split(r"\n\s*\n", raw) if c.strip()]
log(f"Chunks after blank-line split: {len(chunks)}")

YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")
records = []
skipped = 0
for c in chunks:
    lines = [l.strip() for l in c.split("\n") if l.strip()]
    if len(lines) < 3:
        skipped += 1
        continue
    head = lines[0]
    m = YEAR_RE.search(head)
    if not m:
        skipped += 1
        continue
    year = int(m.group(0))
    if not (1990 <= year <= 2027):
        skipped += 1
        continue
    # journal = text before the year
    journal = head[:m.start()].strip().rstrip(".,; ")
    title   = lines[1] if len(lines) > 1 else ""
    authors = lines[2] if len(lines) > 2 else ""
    ids     = " ".join(lines[3:6])
    pmid = ""
    doi  = ""
    mp = re.search(r"PMID:\s*(\d+)", ids)
    if mp:
        pmid = mp.group(1)
    md = re.search(r"DOI:\s*([^\s]+)", ids)
    if md:
        doi = md.group(1).rstrip(".")
    if not doi:
        md2 = re.search(r"doi:\s*([^\s]+)", head, re.I)
        if md2:
            doi = md2.group(1).rstrip(".")
    records.append(dict(year=year, journal=journal, title=title,
                        authors=authors, pmid=pmid, doi=doi))

log(f"Parsed records: {len(records)}   skipped: {skipped}")

# --- year distribution
from collections import Counter
cnt = Counter(r["year"] for r in records)
log("")
log("Year distribution:")
for y in sorted(cnt, reverse=True):
    log(f"  {y}: {cnt[y]}")

with open(YEAR_CSV, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["year", "n"])
    for y in sorted(cnt, reverse=True):
        w.writerow([y, cnt[y]])
log(f"[OK] wrote {YEAR_CSV}")

# --- 2025-2026 (dedup by title)
recent = [r for r in records if r["year"] >= 2025]
seen = set()
dedup = []
for r in recent:
    k = re.sub(r"[^a-z0-9]", "", r["title"].lower())
    if k in seen or not k:
        continue
    seen.add(k)
    dedup.append(r)
dedup.sort(key=lambda r: (-r["year"], r["journal"]))
log("")
log(f"2025-2026 records: {len(recent)}  (after title-dedup: {len(dedup)})")

with open(REC_CSV, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["year", "journal", "authors", "title", "pmid", "doi"])
    for r in dedup:
        w.writerow([r["year"], r["journal"], r["authors"], r["title"],
                    r["pmid"], r["doi"]])
log(f"[OK] wrote {REC_CSV}")

log("")
log("First 40 of 2025-2026 (year | journal | title):")
for r in dedup[:40]:
    t = r["title"][:95]
    log(f"  {r['year']} | {r['journal'][:28]:28s} | {t}")

log("")
log("DONE.")
open(LOG, "w", encoding="utf-8").write(_log.getvalue())
