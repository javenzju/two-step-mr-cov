# 外部独立编码（Inter-coder reliability）材料包

本文件说明如何委托一名**完全独立的外部编码者**（非本文共同作者）对 50 例分层抽样研究重编码，
以复现或取代稿件中基于共同作者盲态重编码（C.Y.）的 Cohen's κ。
目的是在修回（major revision）时回应审稿人对"κ 来自团队内部"的可靠性质疑。

## 1. 材料清单（均已在仓库内）

| 文件 | 路径（相对项目根） | 用途 |
|---|---|---|
| 盲态编码模板（待填） | `③ 真实数据应用/kappa_second_coder_template.csv` | 50 例（study_id / pmid / 作者年 / 期刊 / 标题），**不含任何 AI 编码判断列**，供外部编码者填写 |
| 编码手册 | `③ 真实数据应用/temp/kappa_codebook_S1_20260903.md` | Codebook S1：三字段（design_type / IV_selection_strategy / reports_overlap_risk）的判定规则 |
| 密封答案 | `③ 真实数据应用/temp/_sealed_do_not_open/kappa_answer_key_20260903.csv` | AI 原始编码答案键；**外部编码者编码前不得打开** |
| 全文包 | `③ 真实数据应用/temp/kappa_recode_fulltext/` | 按 pmid 存放 50 篇原文全文（txt），供编码者依据原文独立判断 |
| κ 计算脚本 | `③ 真实数据应用/compute_kappa_2nd.py` | 以外码者真实 CSV 对密封答案键算 κ（绝不编造标签；无填充文件则打印指引并退出） |

> 抽样设计：conservative（合并IV池 / MVMR联合估计）5 例、typical_additional（分开选IV 且未报告重叠）15 例、not_at_risk 30 例，`random.seed(2026)` 固定可复现。

## 2. 外部编码者工作流

1. 阅读编码手册 `kappa_codebook_S1_20260903.md`，理解三字段定义。
2. 打开 `kappa_recode_fulltext/` 中对应 pmid 的原文，依据原文（不参考原编码表）判断三字段，填入
   `kappa_second_coder_template.csv` 的对应列，另存为 `kappa_external_coder_filled.csv`
   （可直接在原模板文件上填写后改名）。
3. 运行（在 `③ 真实数据应用/` 目录）：
   ```bash
   python compute_kappa_2nd.py --second kappa_external_coder_filled.csv
   ```
4. 输出 `③ 真实数据应用/temp/kappa_2nd_report.csv`：每字段的 n / Po / Pe / κ / 95% CI，
   以及 macro-averaged κ。将报告中的 κ 替换稿件 §3.2 "Reproducibility" 段的外部 κ（若优于团队内 κ 则取代之）。

## 3. 注意事项

- 脚本仅做"真实外码 CSV vs 密封键"的比对，**不会**在缺失外码文件时凭空生成 κ。
- 密封答案键在编码完成前须保持封存；若需审计，可在编码结束后打开核对。
- 若 Editor 不要求外部编码，本包也可作为"团队内盲态重编码"的材料留档（当前稿件 §3.2 已报告 C.Y. 盲态重编码结果：design_type 100% 一致 / PABAK 1.00；IV_selection_strategy κ=0.44；reports_overlap_risk κ=0.78；macro κ=0.61）。
- Cover letter 已写明：如 Editor 要求，将在修回时委托完全独立外部编码者重编码该 50 例；本包使其可"一条命令复现"。
