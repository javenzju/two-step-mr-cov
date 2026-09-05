#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D61 新颖性查重脚本（novelty check）
==================================
用途：用第7组（查重）检索式 + 宽式补充，核查 2024-2026 年内是否已有其他团队
发表"两步法(product-method) MR 中介的工具变量重叠 / 样本重叠协方差 Cov(α̂,β̂)
闭式解"——即本文主张的 gap。这是审稿人最可能挑战的点，需仔细过一遍。

实现说明：
- 纯标准库 urllib 实现，不依赖 Biopython（本机 venv 未装），规避依赖问题。
- 用 ProxyHandler({}) 强制绕过本机常下线的 127.0.0.1:10808 代理，直连 NCBI eutils。
- 每个检索式先 esearch 拿 PMID 列表，再 esummary 拿标题/年份/期刊，过滤 2024-2026
  窗口，逐条列出供人工判断是否属于同一 gap。

输出：与本脚本同目录的 D61_novelty_check.txt（带时间戳日志），同时打印到 stdout。
"""
import urllib.request
import urllib.parse
import json
import time
import os
import sys
from datetime import datetime

NCBI_EMAIL = "up2016y@gmail.com"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "D61_novelty_check.txt")

op = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def log(m):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {m}"
    print(line)
    with open(OUT, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def esearch(term, retmax=500):
    url = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed"
           "&retmode=json&retmax=%d&term=%s" % (retmax, urllib.parse.quote(term)))
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0",
                                                 "email": NCBI_EMAIL})
    with op.open(req, timeout=30) as r:
        d = json.loads(r.read())
    return d["esearchresult"]["idlist"]


def esummary(ids):
    if not ids:
        return {}
    out = {}
    for i in range(0, len(ids), 200):
        chunk = ids[i:i + 200]
        url = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed"
               "&retmode=json&id=%s" % ",".join(chunk))
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0",
                                                     "email": NCBI_EMAIL})
        with op.open(req, timeout=30) as r:
            d = json.loads(r.read())
        res = d.get("result", {})
        for k, v in res.items():
            if k == "uids":
                continue
            out[k] = v
        time.sleep(0.34)
    return out


# ===== 查重检索式 =====
# 第7组（用户原样，两条）
G7 = [
    'instrument overlap[Title/Abstract] AND Mendelian randomization[Title/Abstract] AND covariance[Title/Abstract]',
    '"instrument overlap"[Title/Abstract] AND mediation[Title/Abstract]',
]
# 宽式补充：防止用词差异（overlapping instruments / shared instrument / product method + overlap / covariance）漏掉真正竞品
WIDE = [
    'instrument overlap[Title/Abstract] AND Mendelian randomization[Title/Abstract]',
    '"overlapping instruments"[Title/Abstract] AND Mendelian randomization[Title/Abstract]',
    'shared instrument[Title/Abstract] AND Mendelian randomization[Title/Abstract] AND mediation[Title/Abstract]',
    'Mendelian randomization[Title/Abstract] AND mediation[Title/Abstract] AND covariance[Title/Abstract]',
    '"two-step" Mendelian randomization[Title/Abstract] AND overlap[Title/Abstract]',
    'product method[Title/Abstract] AND Mendelian randomization[Title/Abstract] AND overlap[Title/Abstract]',
]

WINDOW = ("2024", "2025", "2026")


def in_window(pubdate):
    if not pubdate:
        return False
    return any(pubdate.startswith(y) for y in WINDOW)


def main():
    open(OUT, "w", encoding="utf-8").close()  # 清空
    log("="*70)
    log("D61 新颖性查重开始")
    log("="*70)

    # ---- 第7组（核心查重式） ----
    log("\n########## 第7组（用户指定查重式）##########")
    for q in G7:
        log(f"\n>>> 检索式: {q}")
        try:
            ids = esearch(q, retmax=500)
        except Exception as e:
            log(f"  esearch 失败: {e}")
            continue
        log(f"  命中总数: {len(ids)}")
        summ = esummary(ids)
        cnt_win = 0
        for pmid in ids:
            v = summ.get(pmid, {})
            title = v.get("title", "(无标题)")
            pubdate = v.get("pubdate", "")
            src = v.get("source", "")
            tag = "  <<< 2024-2026" if in_window(pubdate) else ""
            if in_window(pubdate):
                cnt_win += 1
            log(f"  PMID:{pmid} [{pubdate}] {src} | {title}{tag}")
        log(f"  → 2024-2026 窗口内命中: {cnt_win}")
        time.sleep(0.34)

    # ---- 宽式补充 ----
    log("\n########## 宽式补充（防用词差异漏检）##########")
    for q in WIDE:
        log(f"\n>>> 检索式: {q}")
        try:
            ids = esearch(q, retmax=500)
        except Exception as e:
            log(f"  esearch 失败: {e}")
            continue
        log(f"  命中总数: {len(ids)}")
        summ = esummary(ids)
        cnt_win = 0
        for pmid in ids:
            v = summ.get(pmid, {})
            title = v.get("title", "(无标题)")
            pubdate = v.get("pubdate", "")
            src = v.get("source", "")
            tag = "  <<< 2024-2026" if in_window(pubdate) else ""
            if in_window(pubdate):
                cnt_win += 1
            log(f"  PMID:{pmid} [{pubdate}] {src} | {title}{tag}")
        log(f"  → 2024-2026 窗口内命中: {cnt_win}")
        time.sleep(0.34)

    log("\n" + "="*70)
    log("D61 新颖性查重结束。请逐条核对 2024-2026 命中是否为同一 gap。")
    log("="*70)


if __name__ == "__main__":
    main()
