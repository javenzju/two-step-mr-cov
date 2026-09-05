#!/usr/bin/env python3
"""
从检索式抓取 PubMed PMID，并下载记录输出纯文本（支持 >1000 条文献）
每条记录格式：
Front Pharmacol. 2025 Aug 26:16:1625003. doi: 10.3389/fphar.2025.1625003. eCollection 2025.
标题
作者1, 作者2, ...
PMID: 12345678 PMCID: PMCxxxxxx DOI: 10.xxx/xxx

Abstract
摘要段落...
Keywords: 关键词1; 关键词2; ...

本版本用途：为《Correcting for instrument overlap in two-step summary-data
Mendelian randomization mediation》（D61 稿）补充/核对参考文献与查重（novelty check）。
检索式按论文各部分的关键论点分组，见下方 QUERIES 的注释。
建议流程：
  1) 运行本脚本，生成 pubmed_records.txt；
  2) 按 PMID/标题人工筛选与论文相关的条目；
  3) 重点核对"查重"分组（第7组）——确认 2024-2026 年内没有其他团队
     已经发表"两步法MR中介工具变量重叠协方差闭式解"，以维持论文
     "首次推导 Cov(α̂,β̂) 闭式解" 的新颖性主张（Introduction/Abstract 用语）。
"""

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import time
import sys
from Bio import Entrez

# ===== 设置邮箱（NCBI 要求） =====
NCBI_EMAIL = "up2016y@gmail.com"
Entrez.email = NCBI_EMAIL

# ===== PubMed 检索式（按论文论点分组，写作/投稿参考文献用） =====
QUERIES = [
    # 1) 核心方法学基础：两步法（乘积法）/ network MR 中介
    '"two-step" [Title/Abstract] AND "Mendelian randomization" [Title/Abstract] AND mediation[Title/Abstract]',
    'network Mendelian randomization[Title/Abstract] AND mediation[Title/Abstract]',
    'product of coefficients[Title/Abstract] AND Mendelian randomization[Title/Abstract]',

    # 2) 多变量 MR 中介 (MVMR)，用于讨论/区分 §2.5、S7.4
    'multivariable Mendelian randomization[Title/Abstract] AND mediation[Title/Abstract]',

    # 3) 样本重叠 / 弱工具偏倚 —— Cov(alpha,beta) 推导的核心相关文献
    'sample overlap[Title/Abstract] AND "Mendelian randomization"[Title/Abstract]',
    'weak instrument bias[Title/Abstract] AND "two-sample" [Title/Abstract] AND Mendelian randomization[Title/Abstract]',
    'winner\'s curse[Title/Abstract] AND Mendelian randomization[Title/Abstract]',

    # 4) 直接竞争/被本文"接棒"的文献 —— Lin et al. 2025 及其引用者
    'summary data Mendelian randomization[Title/Abstract] AND mediation[Title/Abstract] AND variance[Title/Abstract]',
    'Lin[Author] AND mediation[Title/Abstract] AND Mendelian randomization[Title/Abstract] AND 2025[Date - Publication]',

    # 5) delta method / 比值估计量方差，用于 §2.2/§2.3 方法学引用
    'delta method[Title/Abstract] AND instrumental variable[Title/Abstract] AND variance[Title/Abstract]',
    'ratio estimator[Title/Abstract] AND Mendelian randomization[Title/Abstract]',

    # 6) 报告规范 / 文献综述方法学（支撑 §2.5 文献编码与 STROBE-MR 合规性）
    'STROBE-MR[Title/Abstract]',
    'reporting guideline[Title/Abstract] AND Mendelian randomization[Title/Abstract]',

    # 7) 查重（novelty check）：确认近两年是否已有团队解决同一 gap
    'instrument overlap[Title/Abstract] AND Mendelian randomization[Title/Abstract] AND covariance[Title/Abstract]',
    '"instrument overlap"[Title/Abstract] AND mediation[Title/Abstract]',

    # 8) 工具与数据平台引用（支撑方法/数据可用性部分）
    'TwoSampleMR[Title/Abstract]',
    'OpenGWAS[Title/Abstract] OR IEU GWAS[Title/Abstract]',
]

OUTPUT_FILE = "D61_references_pubmed.txt"


# ===== 抓取 PMID（支持分页，避免丢失 >1000 条） =====
def fetch_pmids(queries):
    pmid_set = set()
    for query in queries:
        print(f"\n检索: {query}")
        retstart = 0
        retmax = 500
        while True:
            handle = Entrez.esearch(
                db="pubmed",
                term=query,
                retstart=retstart,
                retmax=retmax
            )
            record = Entrez.read(handle)
            handle.close()
            ids = record["IdList"]
            if not ids:
                break
            pmid_set.update(ids)
            print(f"已获取 {retstart + len(ids)} 条 PMID")
            retstart += retmax
            time.sleep(0.34)
    return sorted(list(pmid_set))


# ===== 分块下载 PubMed XML =====
def fetch_pubmed_xml_chunk(pmids):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
        "rettype": "abstract",
        "email": NCBI_EMAIL,
        "tool": "pubmed_fetcher_script"
    }
    url = base_url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Python PubMed Fetcher")
    with urllib.request.urlopen(req) as response:
        return response.read()


# ===== XML 解析函数 =====
def parse_articles(xml_data):
    root = ET.fromstring(xml_data)
    articles = []
    for article_elem in root.findall(".//PubmedArticle"):
        try:
            journal = article_elem.find(".//Journal")
            if journal is None:
                continue
            iso_abbr = journal.findtext("ISOAbbreviation", "")
            title = journal.findtext("Title", "")
            if not iso_abbr and title:
                iso_abbr = title

            pubdate_elem = journal.find(".//JournalIssue/PubDate")
            year = pubdate_elem.findtext("Year", "")
            month = pubdate_elem.findtext("Month", "")
            day = pubdate_elem.findtext("Day", "")
            medline_date = pubdate_elem.findtext("MedlineDate", "")

            volume = journal.findtext(".//JournalIssue/Volume", "")
            issue = journal.findtext(".//JournalIssue/Issue", "")
            pages = journal.findtext(".//Pagination/MedlinePgn", "")
            eloc_id = article_elem.find(".//ELocationID[@EIdType='doi']")
            doi = eloc_id.text.strip() if eloc_id is not None else ""

            article_title = article_elem.findtext(".//ArticleTitle", "")

            authors = []
            for author in article_elem.findall(".//Author"):
                last = author.findtext("LastName", "")
                initials = author.findtext("Initials", "")
                if last:
                    authors.append(f"{last} {initials}" if initials else last)
            author_line = ", ".join(authors)

            pmid = article_elem.findtext(".//PMID", "")
            pmc_id = ""
            for aid in article_elem.findall(".//ArticleIdList/ArticleId"):
                if aid.get("IdType") == "pmc":
                    pmc_id = aid.text.strip()
                    break

            abstract_parts = []
            for abstract_text in article_elem.findall(".//Abstract/AbstractText"):
                label = abstract_text.get("Label", "")
                text = abstract_text.text or ""
                abstract_parts.append(f"{label}: {text}" if label else text)
            abstract = "\n".join(abstract_parts)

            keywords = [kw.text.strip() for kw in article_elem.findall(".//KeywordList/Keyword")]
            keywords_line = "; ".join(keywords)

            date_str = medline_date if medline_date else " ".join(filter(None, [year, month, day]))

            cite_line = iso_abbr
            if date_str:
                cite_line += f". {date_str}"
            if volume:
                cite_line += f";{volume}" + (f"({issue})" if issue else "")
                if pages:
                    cite_line += f":{pages}"
            elif pages:
                cite_line += f":{pages}"
            if doi:
                cite_line += f". doi: {doi}"

            articles.append({
                "cite_line": cite_line,
                "title": article_title,
                "authors": author_line,
                "pmid": pmid,
                "pmc_id": pmc_id,
                "doi": doi,
                "abstract": abstract,
                "keywords": keywords_line
            })
        except Exception as e:
            print(f"解析文献出错: {e}", file=sys.stderr)
            continue
    return articles


# ===== 格式化输出 =====
def format_record(art):
    lines = [
        art["cite_line"],
        art["title"],
        art["authors"]
    ]
    id_parts = [f"PMID: {art['pmid']}"]
    if art["pmc_id"]:
        id_parts.append(f"PMCID: {art['pmc_id']}")
    if art["doi"]:
        id_parts.append(f"DOI: {art['doi']}")
    lines.append(" ".join(id_parts))
    lines.append("")
    lines.append("Abstract")
    if art["abstract"]:
        lines.append(art["abstract"])
    lines.append("")
    lines.append(f"Keywords: {art['keywords']}" if art["keywords"] else "Keywords: ")
    return "\n".join(lines)


# ===== 主函数 =====
def main():
    print("正在抓取全部 PMID ...")
    pmid_list = fetch_pmids(QUERIES)
    print(f"共抓取到 {len(pmid_list)} 条 PMID")

    articles = []
    chunk_size = 200
    for i in range(0, len(pmid_list), chunk_size):
        chunk = pmid_list[i:i + chunk_size]
        print(f"\n下载 {i + 1} - {i + len(chunk)}")
        try:
            xml_data = fetch_pubmed_xml_chunk(chunk)
            arts = parse_articles(xml_data)
            articles.extend(arts)
        except Exception as e:
            print(f"该批次下载失败: {e}")
        time.sleep(0.5)

    if not articles:
        print("未解析到任何记录，请检查网络或检索式。")
        return

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for i, art in enumerate(articles):
            if i > 0:
                f.write("\n\n----------------------------------------\n\n")
            f.write(format_record(art))

    print(f"\n成功！已保存 {len(articles)} 条记录到 {OUTPUT_FILE}")


if __name__ == "__main__":
    main()