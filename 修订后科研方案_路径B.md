# 修订后科研方案（路径 B：方法 + 工具论文）

> 适用：两步法 MR 中介协方差修正稿，目标从"Original Article（重叠是隐藏威胁）"改为  
> "Methods / 方法学论文（给出修正估计量 + 标定修正何时不可忽略 + 开源工具）"。  
> 生成日期：2026-09-30。依据：独立验证脚本 `temp/verify_sign_issue.py`（30 万次 bootstrap + MC 积分）  
> 已证明修正恒变窄、naive 恒偏保守。



---

## 进度状态（2026-09-30 更新）

| 项 | 状态 | 说明 |
|---|---|---|
| ① AI 披露如实改写 | ✅ 完成 | 主文 L225 + 作者贡献 L213，κ 叙事重构为 AI↔人 |
| ② 符号 bug 叙事重写 | ✅ 完成 | 摘要/§3.5/§3.6/§3.7/Table4/讨论，全部改"恒变窄" |
| ③ 生产工具 bug 修复 | ✅ 完成 | `M4b_s10_cov.py`：μ_X/μ_Y 带 sign(α)/sign(β)，MC scale 用 abs |
| ④ Table 4 真实值 | ✅ 完成 | −70.4/−65.3/−61.2/−60.7/−14.8/−15.3；provisional 已撤 |
| ⑤ §3.8 regime map | ✅ 完成 | 非循环因果 DGP 模拟；naive 全重叠下高估真实 SD 55–65% |
| ⑥ S2.4 半解析 + S2.5 修正 | ✅ 完成 | 新增 Remark S2.5a（恒负证明）/S2.5b（ρ_MY 通道分离） |
| ⑦ 重叠计数口径统一 | ✅ 完成 | S3 澄清：8 = 5+2退化+1亚阈值，分母 42 vs 108 不可比 |
| ⑧ Table2 vs S3.2 矛盾 | ✅ 完成 | S3 管线澄清：方向一致、点估计/显著性因工具集差异 |
| ⑨ 补充材料形式清理 | ✅ 完成 | S1-S6 整篇英文化+去内部日志；S3/S7 中文清零；STROBE-MR 改编号 S10；Codebook 重写为英文读者版；内部路径→公开仓库 |
| ⑩ 重建 docx 至 EJE/ | ✅ 完成 | `D62_build_submission_package.py`；EJE/ 17 文件全部重建，TOTAL CJK=0 |
| ⑪ Fig S3 重制 | ✅ 完成 | 旧 flip 图退役，新 FigS3_regime_map（通道分离、符号正确） |
| ⑫ §3.1.1 flip-loss 撤回 | ✅ 完成 | 全篇"flip-loss 结构不可能"；撤回 10.4%；摘要同步 |
| ⑬ 摘要补 regime map 量级 | ✅ 完成 | full overlap 下 naive 区间可宽 65% |

**投稿包就绪：`EJE/`（17 文件，TOTAL CJK=0）**，可直接上传。目标期刊决策：**EJE 方法学论文**（新增 regime map 恢复实质影响力，二区）。

---

## 0. 一句话定调

原论文的灵魂假设"**SNP 重叠会隐藏地推翻两步法 MR 中介结论**"已被证伪。  
修正项 `2·αβ·Cov(α̂,β̂)` 在所有已考察的同号/异号 × 样本重叠配置下**恒为负** →  
修正恒让 SE 变窄、naive delta **恒偏保守**（过度估计不确定性、损失功效）。  
因此论文从"警告式发现"改为"**精化式方法贡献**"：提供正确估计量、标定其何时重要、给出工具。

---

## 1. 新论文结构（Path B 大纲）

| 节           | 内容                                              | 动作          |
| ----------- | ----------------------------------------------- | ----------- |
| Title       | 含 "Covariance-corrected" + "tool" 字样            | 重写          |
| Abstract    | 诚实结论 + 工具交付                                     | 重写（见 §4 草案） |
| 1 Intro     | 重叠-capable 设计普遍、但处理/披露缺失                        | 保留，去"威胁"措辞  |
| 2 Methods   | 半解析协方差推导（改"closed-form"→"semi-analytic"）        | 改措辞 + 补推导边界 |
| 2.5         | **新增**：协方差调整估计量（δ-corrected）实现                  | 新增          |
| 3 Sim       | **重写**：非循环 DGP，含 γ_Y=β·γ_M 因果结构，扫参标定 regime     | 重写（见 §3）    |
| 3.4         | 真实重估 108 研究（重叠罕见小）                              | 保留，统一口径     |
| 3.x         | **新增**：regime map（修正>30% 的参数区：高重叠×大|αβ|×弱工具/小N） | 新增          |
| 4 Disc      | "naive 偏保守、少数场景需修正"                             | 重写          |
| AI 披露       | 如实声明 AI 参与初筛/编码                                 | 重写（见 §4 草案） |
| Supp S1–S6  | 推导（semi-analytic 措辞）                            | 改措辞         |
| **Supp S8** | MVMR 变体 + **修正估计量验证**                           | 补模拟验证       |
| **新增 Supp** | 工具包使用说明（R/Python）                               | 新增          |

---

## 2. 必须新增（Path B 的核心增量）

1. **协方差调整估计量**：在 IVW 两步法上给出 `SE_corrected = sqrt(SE_naive² + 2αβ·Cov)` 的  
   可调用实现；封装为 R（`TwoSampleMR` 扩展）与 Python 函数，附 GitHub/Zenodo。
2. **规范模拟（修掉原循环 DGP）**：
   - DGP 必须含因果结构 `γ_Y = β·γ_M + ε`（异号中介自然出现），不再独立抽正均值；
   - 扫 `overlap_frac ∈ {0,0.1,0.25,0.5}` × `|αβ| ∈ {0.2,0.5,1.0}` × `F-stat ∈ {10,30,100}`；
   - 输出：corr/naive 比值分布、CI 覆盖率、功效差（naive vs corrected）。
3. **Regime map 图**：用热力图标定"修正幅度 >30%" 落在哪个参数区 → 这是方法论文的"卖点图"。
4. **工具包 + 真实数据 demo**：用 D56（BMI→腰围→CHD，n_s=13）作唯一非零重叠自然演示。

---

## 3. 必须删除 / 重写（基于证伪证据）

- 摘要 "19/20 widen, up to 38.3%"、"positive when they differ" → 删。
- §3.7 "correction widens whenever α̂β̂<0 … Nineteen of twenty widen (+38.3%)" → 改为"恒变窄/偏保守"。
- Table 4（counterfactual widening）→ 改为"修正幅度分布表"（全为负，附 regime 注释）。
- Fig S3 Panel B（异号变宽）→ 改为"corr/naive <1 全配置"证据图。
- 核心卖点 "cannot be assumed benign / 重叠是隐藏威胁" → 改为"naive 偏保守，但高重叠场景需修正"。
- "closed-form" → "semi-analytic / partially numerical"（S2.4 实为 n_MC=10⁵ MC 积分）。

---

## 4. 阻塞项改写草案（先确认再动源文件）

### 4.1 摘要（重写草案）

> Two-step MR mediation routinely reuses SNPs as instruments for both the exposure→mediator and  
> mediator→outcome steps, inducing covariance between the two estimated effects. We derive the  
> covariance term Cov(α̂,β̂) in **semi-analytic** form and show that, under standard IVW assumptions,  
> the conventional first-order delta-method variance that ignores it is **always conservative**  
> (the correction narrows confidence intervals). In a re-estimation of 108 two-step MR mediation  
> studies, genuine SNP overlap was rare (5 studies, 4.6%; 95% CI 2.0–10.4%) and, when present,  
> narrowed intervals by only −0.2% to −16.0%. Among overlap-capable designs, 39.3% did not report  
> overlap handling. We provide a **covariance-corrected estimator and an open tool**, and recommend  
> routine reporting of the number of shared instruments (n_s).

### 4.2 §3.7（重写草案，替换原 L156–158）

> Contrary to the intuition that overlapping instruments could inflate uncertainty, the covariance  
> correction term `2·αβ·Cov(α̂,β̂)` is negative under all examined configurations (same-sign and  
> opposite-sign mediation, with and without sample overlap). The naive delta-method variance is  
> therefore **conservative**—it overstates uncertainty and slightly reduces power. In our 108-study  
> re-estimation the correction narrowed intervals by −0.2% to −16.0%; no study widened. The correction  
> is non-negligible only in designed high-overlap regimes (see §3.x), which are rare in published practice.

### 4.3 AI 披露（重写草案，替换原 L225）

> The initial literature screening and study coding were performed with AI assistance; a sealed  
> AI-generated coding key was independently re-coded blind by co-author C.Y. (Chen Yan), yielding  
> κ = 0.78 (AI↔human agreement). All coding decisions and reported numbers were subsequently verified  
> by human authors (J.W., C.Y.).

---

## 5. 必改数字/一致性项（改写时一并修）

| 项              | 问题                                             | 修正                      |
| -------------- | ---------------------------------------------- | ----------------------- |
| 引用年            | L128 "(Bowden et al., 2017)" 幽灵年（ref#9 为 2015） | → 2015                  |
| Table2 vs S3.2 | S014、S273 同研究显著性直接相反（主表 yes/yes，S3.2 否/否）      | 统一为一套重估或明确标注两套并解释       |
| 重叠计数           | 8 / 7 / 5 三套口径                                 | 统一为 5（非退化）/ 7（含退化），注明分母 |
| §3.6 CI        | 5/108 给 3.2–12.8%（实为 7/108 的 CI）               | → 2.0–10.4%（Wilson）     |
| 39.3% 分母       | 333 中仅 54 可评估、279 不可评估                         | 补分母构成说明                 |
| 作者名            | C. Yan / C.Y. / Chen Yan 不统一                   | 统一为 Chen Yan (C.Y.)     |
| 补充材料           | 含内部日志/中文过程叙述、STROBE-MR 重名、Codebook S1 非读者版     | 清理为读者可读                 |

---

## 6. 目标期刊与节奏

- **首选**：*Genetic Epidemiology*（方法学友好，免 APC）或 *Statistics in Medicine*（方法验证）。
- **次选**：EJE **Methods** 短文（非 Original Article）；或 *IJE* 方法信。
- **节奏**：① 先修 AI 披露（诚信）→ ② 修符号 bug 重写核心章节 → ③ 补 Path B 新增（估计量/模拟/regime 图/工具）→ ④ 统一数字 → ⑤ 重投。

---

## 7. 已留存证据

- `temp/verify_sign_issue.py`：独立验证（不依赖生产代码），证明 corr/naive<1 全配置、复现 `mu_Y` 硬编码为正导致的虚假"+14.8% 变宽"。
- 生产 bug 位置：`③ 真实数据应用/M4b_s10_cov.py` L33 `mu_Y = math.sqrt(F_stat/N_Y)`（硬编码正）。
