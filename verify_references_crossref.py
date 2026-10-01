# -*- coding: utf-8 -*-
"""
参考文献真实性逐条核对（Crossref REST API）
- 解析稿件末节 "## References" 的编号条目
- 优先用 DOI 直查 Crossref；查无/不匹配时退回按标题+年份检索
- 比对：作者姓、年份、期刊名（规范化前缀匹配）、卷、期、页码
- 输出 temp/refs_crossref_report.csv + 控制台摘要
运行前需绕过失效代理：HTTP_PROXY= HTTPS_PROXY= http_proxy= https_proxy= python verify_references_crossref.py
"""
import re, os, json, time, urllib.parse, urllib.request, csv

for k in list(os.environ):
    if k.upper().endswith("_PROXY"):
        os.environ[k] = ""
os.environ["NO_PROXY"] = "*"

BASE = os.path.dirname(os.path.abspath(__file__))
MD = os.path.join(BASE, "D61_论文终稿_20260906.md")
OUT_CSV = os.path.join(BASE, "temp", "refs_crossref_report.csv")
MAILTO = "javenzju@gmail.com"
HEAD = {"User-Agent": f"refcheck/1.0 (mailto:{MAILTO})", "Accept": "application/json"}


def log(m):
    print(m, flush=True)


def get_json(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=HEAD)
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except Exception as e:
            if i == tries - 1:
                return {"__err__": f"{type(e).__name__}: {e}"}
            time.sleep(1.5 + 1.5 * i)
    return {}


# ---------- 解析 ----------
def parse_ref(text):
    text = re.sub(r"\s+", " ", text).strip()
    d = re.search(r"doi:\s*([^\s;,]+)", text, re.I)
    doi = d.group(1).rstrip(".") if d else ""
    if d:
        text = (text[:d.start()] + " " + text[d.end():]).strip()
    # 定位 "期刊名. YYYY;" 或 "期刊名. YYYY."（in-press / preprint 无卷期页）
    jm = list(re.finditer(r"([A-Za-z][^.;\[\]]{1,80}?)\s*\.?\s+(\d{4})\s*[;.]", text))
    if jm:
        mm = jm[-1]
        journal, year = mm.group(1).strip(), mm.group(2)
        head, rest = text[:mm.start()], text[mm.end():]
    else:
        ym = re.search(r"(\d{4});", text)
        if ym:
            head, rest, year = text[:ym.start()], text[ym.end():], ym.group(1)
        else:
            head, rest, year = text, "", ""
        journal = ""
    seg = head.split(". ")
    authors = seg[0].strip().rstrip(".,;")
    title = " ".join(seg[1:]).strip() if len(seg) > 1 else ""
    title = re.sub(r"\.$", "", title)
    return dict(authors=authors, title=title, journal=journal, year=year,
                rest=rest.strip(), doi=doi)


def surnames(authors):
    """作者段 -> {姓}：按逗号切每位作者，末段若像缩写则取前一段"""
    out = set()
    for a in re.split(r",\s*| and ", authors):
        toks = [t.strip().strip(".") for t in a.split() if t.strip()]
        if not toks:
            continue
        if len(toks[-1]) <= 2 and len(toks) > 1:
            sn = toks[-2]
        else:
            sn = toks[-1]
        low = sn.lower()
        if low in ("et", "al") or "consort" in low or "collaborat" in low or "group" in low:
            continue
        sn = re.sub(r"[^A-Za-z\-]", "", sn)
        if re.fullmatch(r"[A-Za-z\-]{3,20}", sn) or low in ("lee", "day", "liu"):
            out.add(sn.lower())
    return out


def norm(s):
    s = s.lower().replace("&", "and")
    s = re.sub(r"[^\w\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


# ---------- Crossref ----------
def cr_by_doi(doi):
    if not doi.startswith("10."):
        return {"found": False, "err": "无 DOI"}
    j = get_json("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="") +
                 ("?mailto=" + MAILTO if MAILTO else ""))
    if "__err__" in j:
        return {"found": False, "err": j["__err__"]}
    return cr_item(j.get("message") if isinstance(j.get("message"), dict) else j)


def cr_by_title(title, year):
    q = (title[:180] + (" " + year if year else ""))
    u = ("https://api.crossref.org/works?rows=5&select=DOI,title,container-title,issued,"
         "volume,issue,page,article-number,author&query.bibliographic=" + urllib.parse.quote(q))
    if year:
        u += "&filter=from-pub-date:%d-01-01,until-pub-date:%d-12-31" % (int(year), int(year))
    u = u.replace("&amp;", "&")
    if MAILTO:
        u += "&mailto=" + MAILTO
    j = get_json(u)
    if "__err__" in j:
        return {"found": False, "err": j["__err__"]}
    items = j.get("message", {}).get("items", [])
    return cr_item(items[0]) if items else {"found": False, "err": "Crossref 检索无结果"}


def cr_item(it):
    if not isinstance(it, dict) or "__err__" in it:
        return {"found": False, "err": (it or {}).get("__err__", "空响应")}
    try:
        yr = it.get("issued", {}).get("date-parts", [[None]])[0][0]
        return dict(
            found=True, print_year=str(it.get("published-print", {}).get("date-parts", [[None]])[0][0]) if it.get("published-print") else "",
            doi=it.get("DOI", ""),
            title=re.sub(r"\s+", " ", (it.get("title") or [""])[0]),
            journal=re.sub(r"\s+", " ", (it.get("container-title") or [""])[0]),
            year=str(yr), volume=str(it.get("volume", "")), issue=str(it.get("issue", "")),
            page=str(it.get("page", "")), artno=str(it.get("article-number", "")),
            authors=sorted({re.sub(r"[^a-z\-]", "", ((a.get("family") or "").lower().split() or [""])[-1])
                            for a in (it.get("author") or []) if a.get("family")} - {""}),
        )
    except Exception as e:
        return {"found": False, "err": f"解析失败:{e}"}


def check(parsed, ent):
    issues, ok = [], True
    crf = set(f for f in (ent.get("authors") or []) if f)
    ours = surnames(parsed["authors"])
    if crf and ours:
        missing = [t for t in sorted(ours) if not any(t == f or t.startswith(f) or f.startswith(t) for f in crf)]
        if missing:
            ok = False
            issues.append("作者姓不符(稿件缺:%s | CR前5:%s)" % (",".join(missing), ",".join(sorted(crf)[:5])))
    if parsed["year"] and ent.get("year"):
        cayear = str(ent["year"])
        pryear = str(ent.get("print_year") or "")   # 由调用侧补齐
        if parsed["year"] not in (cayear, pryear) and pryear != cayear:
            ok = False
            issues.append("年份不符(稿件%s vs CR在线%s/刊期%s)" % (parsed["year"], cayear, pryear))
    if parsed["journal"] and ent.get("journal"):
        at = {w for w in norm(parsed["journal"]).split() if len(w) > 1}
        bt = set(norm(ent["journal"]).replace("amp", " ").split())
        hit = lambda w: any(b.startswith(w) for b in bt)
        if at and not all(hit(w) for w in at):
            ok = False
            issues.append("期刊名不符(稿件:'%s' vs CR:'%s')" % (parsed["journal"], ent["journal"]))
    m = re.match(r"^(\d+)\((\d*)\)?\s*(?::\s*([\d\-–—]+))?", parsed["rest"])
    if ok and m and ent.get("volume") and m.group(1) != ent["volume"]:
        ok = False
        issues.append("卷不符(稿件%s vs CR %s)" % (m.group(1), ent["volume"]))
    if ok and m and ent.get("page"):
        mp = re.sub(r"[^0-9\-]", "", ent["page"])
        if m.group(3) and m.group(3) not in mp:
            ok = False
            issues.append("页码不符(稿件%s vs CR %s)" % (m.group(3), ent["page"]))
    return ("OK" if ok else "MISMATCH", "; ".join(issues))


def main():
    raw = open(MD, "rb").read().decode("utf-8").replace("\r\n", "\n")
    m = re.search(r"^#+\s*References\s*$(.*)$", raw, re.M | re.S)
    seg = m.group(1) if m else raw
    refs = [(int(a), b.strip()) for a, b in re.findall(r"^(\d+)\.\s+(.*)$", seg, re.M)]
    log("解析到 %d 条参考文献\n" % len(refs))

    rows = []
    for n, text in refs:
        p = parse_ref(text)
        ent, src = None, ""
        if p["doi"]:
            ent = cr_by_doi(p["doi"])
            src = "DOI直查"
        if not ent.get("found"):
            ent = cr_by_title(p["title"], p["year"])
            src = "标题回查"
        verdict, detail = check(p, ent) if ent.get("found") else ("NOT_FOUND", ent.get("err", ""))
        rows.append(dict(ref=n, authors=p["authors"], title=p["title"][:110], journal=p["journal"],
                         year=p["year"], vol_iss_page=p["rest"], doi_in_manuscript=p["doi"],
                         lookup=src, cr_doi=ent.get("doi", ""), cr_journal=ent.get("journal", ""),
                         cr_year=ent.get("year", ""), cr_vol=ent.get("volume", ""),
                         cr_iss=ent.get("issue", ""), cr_page=ent.get("page", ""),
                         cr_title=(ent.get("title", "") or "")[:110],
                         verdict=verdict, detail=detail))
        log("[%s] #%d %s | %s | %s | %s%s" % (
            verdict, n, p["authors"][:34], p["journal"][:26], p["year"],
            p["rest"][:22], "" if verdict == "OK" else "  <-- " + detail))
        time.sleep(0.4)

    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    bad = [r for r in rows if r["verdict"] != "OK"]
    log("\n" + "=" * 72)
    log("总计 %d 条；通过 %d；问题 %d" % (len(rows), len(rows) - len(bad), len(bad)))
    for r in bad:
        log("  [%s] #%d %s %s %s -> %s" % (r["verdict"], r["ref"], r["authors"][:30], r["journal"], r["year"], r["detail"]))
    log("=" * 72)
    log("明细: " + OUT_CSV)


if __name__ == "__main__":
    main()
