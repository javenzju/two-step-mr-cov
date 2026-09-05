#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
D61_check_citations.py  (v2 — position-safe)
Verify every citation rule the user specified for the final manuscript:

 1. Numbering strictly follows order of first appearance (1,2,3,...,N).
 2. Every reference is cited exactly ONCE.
 3. No sentence contains more than one citation marker.
 4. Every citation marker sits immediately BEFORE the sentence-ending period.
 5. Introduction carries 15 refs, Discussion 20, Methods the remainder.
 6. Reference list has N entries numbered 1..N.
 7. 2025-2026 share of the reference list is ~50%.

NOTE: table / maths / heading lines are blanked in a *masked* copy that preserves
character offsets, so marker positions always refer to the original text.

Output: log/D61_check_citations.log
"""
import os, re, io
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
SUB  = os.path.dirname(HERE); ROOT = os.path.dirname(SUB)
LOGDIR = os.path.join(ROOT, "log")
os.makedirs(LOGDIR, exist_ok=True)
MANUS = os.path.join(SUB, "D61_论文终稿_20260906.md")
LOG = os.path.join(LOGDIR, "D61_check_citations.log")

_log = io.StringIO()
def log(m=""):
    print(m); _log.write(str(m) + "\n")

log("=" * 74)
log("D61_check_citations.py v2 — citation rule verification")
log("=" * 74)
raw = open(MANUS, encoding="utf-8").read()
log(f"Manuscript: {MANUS}   ({len(raw)} chars)")

m = re.search(r"^## References\s*$", raw, re.M)
body, refsec = raw[:m.start()], raw[m.end():]

# ---------- reference list ----------
ref_lines = []
for ln in refsec.split("\n"):
    mm = re.match(r"^\s*(\d+)\.\s+(.+)$", ln)
    if mm and len(mm.group(2)) > 40:
        ref_lines.append((int(mm.group(1)), mm.group(2)))
log("")
log(f"Reference list entries : {len(ref_lines)}")
log("  " + ("OK numbered 1..N" if [n for n,_ in ref_lines]==list(range(1,len(ref_lines)+1))
          else "!! numbering broken"))
years = []
for n, c in ref_lines:
    ym = re.search(r"\.\s+((?:19|20)\d{2})[;\.]", c)
    years.append(int(ym.group(1)) if ym else None)
recent = sum(1 for y in years if y and y >= 2025)
log(f"  2025-2026 refs       : {recent} / {len(ref_lines)}  ({100.0*recent/len(ref_lines):.1f}%)")

# ---------- masked copy (preserve offsets) ----------
def blank(ln):
    s = ln.strip()
    return (s.startswith("|") or s.startswith("$") or s.startswith("!")
            or s.startswith("#") or s.startswith("---"))
masked = "".join((" " * len(ln) if blank(ln) else ln) + "\n" for ln in body.split("\n"))
masked = masked[:len(body)]

# ---------- section lookup (on original offsets) ----------
heads = [(mm.start(), mm.group(1)) for mm in re.finditer(r"^##\s+(.+)$", body, re.M)]
def section_of(pos):
    cur = "(front matter)"
    for p, name in heads:
        if p <= pos: cur = name
        else: break
    return cur.split(".")[0].strip()

markers = list(re.finditer(r"\[(\d+)\]", body))
log("")
log(f"Citation markers in body: {len(markers)}")

# ---------- rule 4 ----------
bad = []
for x in markers:
    tail = body[x.end():x.end()+2]
    if not re.match(r"^\.(?:\s|$)", tail):
        bad.append((x.group(0), repr(body[max(0,x.start()-40):x.end()+6])))
log("")
if bad:
    log(f"  !! markers NOT immediately before a period ({len(bad)}):")
    for a, b_ in bad[:10]: log(f"     {a}  {b_}")
else:
    log("  OK  every marker is immediately followed by '.'  (rule: citation before the period)")

# ---------- rules 1 & 2 ----------
seq = [int(x.group(1)) for x in markers]
if seq == list(range(1, len(seq)+1)):
    log("  OK  strict sequential numbering 1..N by first appearance")
else:
    log(f"  !! numbering broken: {seq[:40]}")
dupes = sorted({n for n in seq if seq.count(n) > 1})
log("  " + (f"!! duplicates: {dupes}" if dupes else "OK  each reference cited exactly once"))
missing = sorted(set(range(1, len(ref_lines)+1)) - set(seq))
log("  " + (f"!! never cited: {missing}" if missing else "OK  every listed reference is cited"))

# ---------- rule 3 ----------
sents = re.split(r"(?<=[.!?])\s+(?=[A-Z(])", masked)
multi = [(len(re.findall(r"\[\d+\]", s)), s.strip()[:110]) for s in sents
         if len(re.findall(r"\[\d+\]", s)) > 1]
log("")
if multi:
    log(f"  !! sentences with >1 citation ({len(multi)}):")
    for k, s in multi: log(f"     ({k}) {s}")
else:
    log("  OK  no sentence carries more than one citation marker")

# ---------- rule 5 ----------
sec_first, sec_cnt = {}, Counter()
for x in markers:
    s = section_of(x.start())
    sec_cnt[s] += 1
    sec_first.setdefault(s, []).append(int(x.group(1)))
log("")
log("Citations by section:")
for s in sorted(sec_first, key=lambda k: min(sec_first[k])):
    log(f"  {s:22s} n={sec_cnt[s]:<3d} refs {min(sec_first[s])}-{max(sec_first[s])}")

# ---------- verdict ----------
ok = True
def chk(cond, msg):
    global ok
    log(("  PASS  " if cond else "  FAIL  ") + msg); ok = ok and cond
n_intro = sec_cnt.get("1", 0); n_disc = sec_cnt.get("4", 0)
log("")
log("SUMMARY")
chk(len(ref_lines) >= 35, f"total references >= 35 (got {len(ref_lines)})")
chk(n_intro == 15, f"Introduction refs == 15 (got {n_intro})")
chk(n_disc == 20,  f"Discussion refs == 20 (got {n_disc})")
chk(abs(100.0*recent/len(ref_lines) - 50.0) < 6,
    f"2025-2026 share ~50% (got {100.0*recent/len(ref_lines):.1f}%)")
chk(not bad,   "all citations placed before the sentence-ending period")
chk(seq == list(range(1, len(seq)+1)), "strict sequential numbering")
chk(not dupes, "each reference cited exactly once")
chk(not multi, "at most one citation per sentence")
log("")
log("ALL CHECKS PASSED." if ok else "SOME CHECKS FAILED — see above.")
open(LOG, "w", encoding="utf-8").write(_log.getvalue())
