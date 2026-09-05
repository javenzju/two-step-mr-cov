#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D61 参考文献检索脚本（全8组，标题版）
====================================
按论文各论点分组的8组17条检索式抓取 PubMed，生成 D61_references_pubmed.txt（含
分组标题 + PMID + 年份 + 期刊 + 标题，供筛选参考文献；摘要可按需后续补充）。

与根据检索词抓取_PubMed_记录_D61引用检索版.py 同源检索式，但本版：
- 纯标准库 urllib 实现，不依赖 Biopython；
- ProxyHandler({}) 绕过本机常下线代理，直连 NCBI eutils；
- 输出标题版（esummary，比 efetch 全文更快、更稳），带分组与去重统计。
"""
import urllib.request
import urllib.parse
import json
import time
import os
from datetime import datetime

NCBI_EMAIL = "up2016y@gmail.com"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "D61_references_pubmed.txt")
op = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def esearch(term, retmax=500):
    url = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed"
           "&retmode=json&retmax=%d&term=%s" % (retmax, urllib.parse.quote(term)))
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "email": NCBI_EMAIL})
    with op.open(req, timeout=30) as r:
        d = json.loads(r.read())
    return d["esearchresult"]["idlist"]


def esummary(ids):
    out = {}
    if not ids:
        return out
    for i in range(0, len(ids), 200):
        chunk = ids[i:i + 200]
        url = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed"
               "&retmode=json&id=%s" % ",".join(chunk))
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "email": NCBI_EMAIL})
        with op.open(req, timeout=30) as r:
            d = json.loads(r.read())
        res = d.get("result", {})
        for k, v in res.items():
            if k == "uids":
                continue
            out[k] = v
        time.sleep(0.34)
    return out


# ===== 8组检索式（用户 D61引用检索版，按论文论点分组）=====
GROUPS = [
    ("1) 两步法/network MR 中介核心方法学",
     ['"two-step" [Title/Abstract] AND "Mendelian randomization" [Title/Abstract] AND mediation[Title/Abstract]',
      'network Mendelian randomization[Title/Abstract] AND mediation[Title/Abstract]',
      'product of coefficients[Title/Abstract] AND Mendelian randomization[Title/Abstract]']),
    ("2) MVMR 中介（讨论区分）",
     ['multivariable Mendelian randomization[Title/Abstract] AND mediation[Title/Abstract]']),
    ("3) 样本重叠 / 弱工具 / winner's curse（Cov 推导直接相关）",
     ['sample overlap[Title/Abstract] AND "Mendelian randomization"[Title/Abstract]',
      'weak instrument bias[Title/Abstract] AND "two-sample" [Title/Abstract] AND Mendelian randomization[Title/Abstract]',
      "winner's curse[Title/Abstract] AND Mendelian randomization[Title/Abstract]"]),
    ("4) Lin et al. 2025 及其引用者（接棒文献）",
     ['summary data Mendelian randomization[Title/Abstract] AND mediation[Title/Abstract] AND variance[Title/Abstract]',
      'Lin[Author] AND mediation[Title/Abstract] AND Mendelian randomization[Title/Abstract] AND 2025[Date - Publication]']),
    ("5) delta method / 比值估计量方差",
     ['delta method[Title/Abstract] AND instrumental variable[Title/Abstract] AND variance[Title/Abstract]',
      'ratio estimator[Title/Abstract] AND Mendelian randomization[Title/Abstract]']),
    ("6) STROBE-MR 报告规范",
     ['STROBE-MR[Title/Abstract]',
      'reporting guideline[Title/Abstract] AND Mendelian randomization[Title/Abstract]']),
    ("7) 查重（novelty check）",
     ['instrument overlap[Title/Abstract] AND Mendelian randomization[Title/Abstract] AND covariance[Title/Abstract]',
      '"instrument overlap"[Title/Abstract] AND mediation[Title/Abstract]']),
    ("8) TwoSampleMR / OpenGWAS 工具引用",
     ['TwoSampleMR[Title/Abstract]',
      'OpenGWAS[Title/Abstract] OR IEU GWAS[Title/Abstract]']),
]


def main():
    seen = set()
    lines = []
    lines.append("=" * 72)
    lines.append("D61 参考文献检索结果（8组检索式，标题版；eutils esummary）")
    lines.append("生成时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    lines.append("说明：本清单供筛选参考文献，含 PMID/年份/期刊/标题；摘要可后续按需补充。")
    lines.append("=" * 72)
    total = 0
    for gname, qs in GROUPS:
        lines.append("\n" + "#" * 72)
        lines.append("## " + gname)
        lines.append("#" * 72)
        for q in qs:
            try:
                ids = esearch(q, retmax=500)
            except Exception as e:
                lines.append("  [esearch 失败] %s : %s" % (q, e))
                continue
            summ = esummary(ids)
            lines.append("\n  >>> %s  (命中 %d)" % (q, len(ids)))
            for pmid in ids:
                if pmid in seen:
                    continue
                seen.add(pmid)
                total += 1
                v = summ.get(pmid, {})
                title = v.get("title", "(无标题)")
                pubdate = v.get("pubdate", "")
                src = v.get("source", "")
                lines.append("  PMID:%s | [%s] %s | %s" % (pmid, pubdate, src, title))
            time.sleep(0.34)
    lines.append("\n" + "=" * 72)
    lines.append("去重后总计: %d 条" % total)
    lines.append("=" * 72)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("完成：%d 条去重记录写入 %s" % (total, OUT))


if __name__ == "__main__":
    main()
