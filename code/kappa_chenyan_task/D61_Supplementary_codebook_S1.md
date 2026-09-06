# D10：文献人工编码操作指南（v2，与实际编码表schema同步）

**适用文件**：`literature_coding_table_ROUND2_DONE.xlsx`（原`literature_coding_table_PREFILLED.xlsx`的后续版本，已扩容）
**编码对象**：529篇候选池（原101篇 + 新增428篇，来自更宽泛的12条检索式），其中461篇design_type判定为两步法MR中介/MVMR变体
**最后更新**：2026-07-03（本次更新原因：发现v1版本描述的schema与实际Excel已配置的下拉菜单不一致，予以同步；详见文末"v1→v2变更记录"）

---

## 〇、与v1版本的关键差异（先看这里）

1. **规模变了**：v1写"预计30-40篇"两步法候选，是针对最初101篇文献的估计。现在候选池已扩容到529篇（追加检索式覆盖更广），候选文献数是461篇，**不是**30-40篇量级。第十节的统计目标公式仍然成立，但分母基数需要按当前规模理解。
2. **design_type是三分类，不是四分类**：实际Excel里`design_type`下拉菜单只有`两步法MR中介`/`MVMR变体`/`其他需排除`三个值，**没有**v1描述的独立`difference_method`类别。原因：`difference_method` vs `product_method`是"间接效应怎么算"这个维度，跟"设计框架是两步法还是MVMR"是另一个正交维度，两者用同一个字段表达不了同时属于"MVMR框架"又"用difference method计算"的论文（这种论文确实存在，如PMID 38725300）。所以实际Excel把这两个维度拆成了两个字段：`design_type`（框架层面）+`indirect_effect_method`（估计方法层面，见下）。
3. **新增字段`indirect_effect_method`**：下拉菜单`Product method,Difference method,MVMR,其他`。**这是v1文档完全没提到的字段**，但恰好承接了v1想用`difference_method`表达的信息。目前只有37篇（见下方覆盖状态）填写了此字段。
4. **`sample_overlap_reported`拆成了4个更细的列**：不再是单一字段，而是`M_GWAS_Y_GWAS_overlap`/`X_GWAS_M_GWAS_overlap`/`overlap_pct_reported`/`reports_overlap_risk`，见第五节更新。
5. **`n_IV_shared`补上了受控词表下拉菜单**（`0,likely_overlap,full_overlap,unclear`，与v1一致），但**覆盖率很低**：529篇里只有78篇（77篇MVMR类+1篇经核实的合并IV池案例）填写，其余383篇候选仍为空——这是当前最大的未完成工作量，见第七节。

---

## 一、准备工作（10分钟，只做一次，v1原文不变）

**分屏设置**：左边Excel（编码表），右边浏览器（PubMed）。

**PubMed检索最快方式**：直接在搜索框输入PMID数字，回车即跳转。

**Excel下拉菜单现状**（已全部配置好，不需要再手动设置）：

| 字段（列） | 下拉选项 |
|---|---|
| `design_type`（E列） | `两步法MR中介,MVMR变体,其他需排除` |
| `IV_selection_strategy`（P列） | `分开选IV,合并IV池,MVMR联合估计,无法判断` |
| `M_GWAS_Y_GWAS_overlap`（Q列） | `明确独立,明确重叠,可能重叠未披露,无法判断` |
| `X_GWAS_M_GWAS_overlap`（S列） | `明确独立,明确重叠,可能重叠未披露,无法判断` |
| `indirect_effect_method`（T列） | `Product method,Difference method,MVMR,其他` |
| `variance_method`（U列） | `Delta法(独立假设),Delta法(已校正协方差),Bootstrap,未说明` |
| `reports_overlap_risk`（V列） | `是,否,部分提及未量化` |
| `n_IV_shared`（N列，本次新增） | `0,likely_overlap,full_overlap,unclear` |
| `significant_as_reported`（AC列） | `是,否` |
| `risk_flag_for_reanalysis`（AD列） | `高风险(合并IV池或高重叠),中风险,低风险,不适用` |
| `data_availability`（AE列） | `summary stats公开可获取,部分公开,需联系作者,不可获取` |

---

## 二、核心原则：按字段批量过（v1原文不变）

不要坐下来把一篇论文的所有字段填完再去下一篇。正确做法：第一轮只填`design_type`（3分钟/篇）→ 筛出候选子集 → 第二轮对候选子集深读填其余字段（8分钟/篇）。

---

## 三、第一轮：`design_type`判定规则（已同步为实际枚举值）

**Ctrl+F关键词**：`two-step`、`Step 1`、`indirect`、`α×β`、`product method`、`difference method`、`multivariable MR`、`mediation`

| 填写值 | 判定条件 |
|---|---|
| `两步法MR中介` | Methods里有明确的Step1/Step2两阶段结构（不论最终用product method还是difference method算间接效应——这个信息填到`indirect_effect_method`，不影响这里的判断） |
| `MVMR变体` | 用多变量MR（MVMR）联合估计直接/间接效应，不是分步骤的two-step结构 |
| `其他需排除` | 摘要提"mediation"但Methods里找不到两步或MVMR结构；或纯观察性中介分析（无MR框架）；或方法学/工具论文非应用研究 |

**判定口诀**：先看Methods部分有没有明确的Step1/Step2结构或MVMR直接/间接效应分解——不要靠标题或摘要里的"mediation"这个词来判断。**"用了difference method"不是排除理由**，只要框架仍是two-step或MVMR，正常归入对应design_type，具体估计方法记在`indirect_effect_method`。

**当前进度**：529篇候选池中，396篇`两步法MR中介`，65篇`MVMR变体`，68篇`其他需排除`。全部已完成design_type判定，其中323篇经过全文核实（非仅关键词自动分类）。

---

## 四、`indirect_effect_method`判定规则（新增字段，替代v1的difference_method独立分类）

**Ctrl+F关键词**：`product method`、`product of coefficient`、`coefficient product`、`difference method`、`difference in coefficient`

| 填写值 | 判定条件 |
|---|---|
| `Product method` | 间接效应 = α̂ × β̂（两步法典型做法） |
| `Difference method` | 间接效应 = 总效应 − 直接效应（τ̂−δ̂，常见于MVMR框架，或two-step框架下检测到重叠时的替代做法） |
| `MVMR` | 框架本身就是MVMR联合估计，未明确用上述两种命名方式中的任一种 |
| `其他` | 用了α×β形式的公式但未见"product method"这类明确命名措辞；或方法学表述不足以判断 |

**特别注意**：少数论文会**根据是否存在样本重叠，在product method和difference method之间切换**（本次核实中发现的典型案例：PMID 38796576, SHBG→血脂→CHD，"当暴露与中介GWAS存在样本重叠时，改用difference method"）。这种情况填主分析方法（通常是无重叠时的默认方法product method），切换细节记在notes列。

**当前覆盖率**：529篇中仅37篇（9篇深度核实+28篇重叠专题核实）已填写此字段，覆盖率约7%，其余大部分候选文献此字段为空。

---

## 五、重叠相关字段判定规则（替代v1单一的sample_overlap_reported）

v1设计的是单一字段"是否报告了重叠"，实际Excel拆分为4个字段，判定更细但也更费时：

| 字段 | 判定内容 |
|---|---|
| `X_GWAS_M_GWAS_overlap` | 暴露GWAS与中介GWAS之间的重叠状态 |
| `M_GWAS_Y_GWAS_overlap` | 中介GWAS与结局GWAS之间的重叠状态 |
| `overlap_pct_reported` | 若论文给出了具体重叠比例数字，填在这里（自由文本） |
| `reports_overlap_risk` | 论文是否**意识到/讨论**了重叠风险这件事本身（是/否/部分提及未量化）——不管重叠实际状态如何，只看有没有讨论 |

每个重叠状态字段的枚举值：`明确独立`（论文明确说独立/不重叠）、`明确重叠`（论文明确说有重叠，通常带比例数字）、`可能重叠未披露`（数据来源本身高度提示可能重叠，如两个GWAS都主要来自UK Biobank，但论文未讨论）、`无法判断`（信息不足，最常见的情况）。

**重要提醒**：`可能重叠未披露`需要编码者主动判断数据来源（比如都用了UK Biobank数据），这是全表里少数需要"推断"而非"摘录事实"的字段，务必在notes列写清楚推断依据，方便复核。

**本次核实的重要发现**：在28篇"明确讨论重叠"的深度案例中，发现现有文献处理重叠问题的方式可归纳为6类（专用工具量化校正/主动排重设计/仅声明无重叠/切换估计方法/重叠过大放弃分析/仅作限制性讨论），**没有一篇将重叠校正做到中介比例的协方差层面**——这是本项目Gap论证的核心实证支持，完整清单见`重叠处理方式文献综述小结.md`。

---

## 六、`variance_method`判定规则（枚举值与v1概念一致，仅中文化）

**Ctrl+F关键词**：`bootstrap`、`delta method`、`covariance`、`SE`、`TwoSampleMR`

| 填写值 | 对应v1的英文概念 | 判定条件 |
|---|---|---|
| `Delta法(独立假设)` | `delta_additive` | 标准加法delta公式 α²Var(β)+β²Var(α)，或"用TwoSampleMR包计算"无进一步说明 |
| `Bootstrap` | `bootstrap` | 明确用bootstrap估计间接效应CI |
| `Delta法(已校正协方差)` | `delta_with_cov` | 公式含协方差项2αβCov(α̂,β̂)——**这是本项目要论证"现有文献几乎不存在"的类别，遇到请重点标记** |
| `未说明` | `unclear` | 未提及计算方法 |

**一篇同时用两种方法**：以主分析方法为准，次要分析在notes列注明（不要像本次核实中曾出现的"Delta法(独立假设)+Bootstrap"这种拼接写法，不是合法枚举值，Excel下拉菜单会报错）。

**当前发现**：529篇候选中，尚未发现`Delta法(已校正协方差)`案例（与D02预期"修正率预期几乎为零"一致）。

---

## 七、`n_IV_shared`判定规则与当前覆盖状态（v1原文规则不变，但需要说明现状）

| 填写值 | 判定条件 |
|---|---|
| 具体数字 | 找到两组SNP列表，数出真实交集数（**注意：全文正文极少直接给出这个数字，通常需要查Supplementary Table，而本次核实使用的是PMC全文XML转纯文本，不包含Supplementary附件内容**） |
| `likely_overlap` | Step1和Step2用同一表型的GWS SNP，但没有精确列表可数 |
| `full_overlap` | 论文明确说"合并IV池"/"combined instrument set" |
| `0` | 明确说两步用了完全不同的两组表型GWS SNP |
| `unclear` | 找不到IV具体列表，无法判断（**目前绝大多数论文属于此类**） |

**当前覆盖状态（重要，需要人工继续补）**：
- 461篇候选中，78篇已填写（77篇MVMR类论文统一填`unclear`+`MVMR联合估计`，因为MVMR框架下"共享IV数"这个概念本身不完全适用于two-step框架的定义；1篇合并IV池案例经核实填`full_overlap`）
- **383篇仍为空白**，这是当前最大的剩余工作量
- 尝试过基于全文关键词自动判定IV选择策略，但精度不理想（7个"合并IV池"自动匹配候选里，人工核实后6个是误报，比如把"combined instrument strength筛选标准"、"pooled多队列GWAS结果做meta分析"误判成了"合并IV池"）——**这个字段不建议再用自动化方式批量处理，需要人工逐篇查看，或者需要获取Supplementary Table的访问权限**

---

## 八、边界情况处理（v1原文不变）

**看不到全文**：只用摘要填`design_type`，其余填`unclear`/空白，在notes列记"全文不可及"。

**Preprint**：照常编码，notes列注明`preprint`。

**一篇同时用两种方法**：以主分析方法为准，次要分析notes列注明。

**拿不准的情况**：填`unclear`加notes备注，不要在一篇上卡超过10分钟。

---

## 九、编码后的统计目标（口径已更新以匹配实际字段名）

| 统计量 | v1描述 | 实际字段对应的计算方式 |
|---|---|---|
| 分母 | design_type=two_step_mediation总数 | `design_type`="两步法MR中介" 的行数（当前396篇，含少量`indirect_effect_method`="Difference method"的论文——**是否要把这部分从分母剔除，取决于研究者本次决策：已确认保留在Excel的二维schema里，不单独剔除，但可以在统计时用`indirect_effect_method`列做子集筛选**） |
| 风险分子 | n_IV_shared=likely_overlap/full_overlap/>0的比例 | 目前仅78/461篇已判定此字段，**统计前需要先完成第七节提到的剩余383篇编码**，否则这个比例会因为分母口径不完整而失真 |
| 披露率 | sample_overlap_reported=reported_has_overlap的比例 | 可用`reports_overlap_risk`="是"的比例近似，或更严格地用`X_GWAS_M_GWAS_overlap`/`M_GWAS_Y_GWAS_overlap`="明确重叠"的比例（口径需要研究者明确选定一种，二者不完全等价） |
| 修正率 | variance_method=delta_with_cov的比例 | `variance_method`="Delta法(已校正协方差)" 的比例，目前为0/529 |

**提醒**：在能完整算出"风险分子"这个核心统计量之前，第七节的383篇`n_IV_shared`空白是必须先解决的阻塞项，优先级应高于其他未完成工作。

---

## 十、文件保存规范（v1原文不变，路径已更新）

- 当前工作文件：`literature_coding_table_ROUND2_DONE.xlsx`
- 每次编码session结束后另存一份带日期的备份，防止意外覆盖
- notes列自由填写，遇到任何拿不准的情况都记在这里
- 配套参考文档：`重叠处理方式文献综述小结.md`（28篇重叠处理案例的分类综述，可直接用于论文Introduction/Discussion）

---

## v1→v2变更记录

**触发原因**：2026-07-03会话中，Claude按D10 v1的字段规范对实际编码表做核对时，发现v1文档描述的schema（英文枚举值、四分类design_type、单一sample_overlap_reported字段）与`literature_coding_table_PREFILLED.xlsx`及其后续版本实际配置的下拉菜单（中文枚举值、三分类design_type+独立indirect_effect_method字段、四个细分重叠字段）不一致。核对过程中同时发现并修复了8处Claude自己此前编码时引入的`variance_method`非法值、27篇遗漏的`indirect_effect_method`字段。

**用户决策**：design_type分类维度以实际Excel的二维schema为准，v1文档同步更新（即本文档）；`n_IV_shared`受控词表按v1原样补回Excel（已完成），覆盖率问题记录在案、留待后续人工/自动化混合方式处理。

**未解决事项**：第七节列出的383篇`n_IV_shared`空白仍是阻塞"风险分子"统计的关键缺口，且已验证纯自动化文本匹配在此字段上精度不可靠，需要另想办法（人工补齐，或争取Supplementary Table访问权限后重新自动化）。
