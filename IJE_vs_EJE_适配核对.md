# IJE vs EJE 适配核对（2026-09-13）

> 目的：核对"先投 IJE（赌上限）→ 被拒即转 EJE"这一顺序策略的真实成本。
> 结论摘要：**IJE 不是"零返工的试投"**——现行的稿子（主文 ~6,100 词、6 表 + 4 图、图为 PDF）**会被 IJE 的硬性投稿规则挡在门外**，需要"瘦身改写 + 重做图件"，这是**换一篇更薄的论文**，而非格式微调。

---

## 一、硬性规则对照（已核实，来源见文末）

| 项目 | **EJE**（现稿目标） | **IJE** | 现稿状态 |
|---|---|---|---|
| Original Article 正文词数 | **无上限**（只有 Short Communications 限 2000 词） | **≤ 3,000 词**（不含摘要/Key Messages/致谢/参考文献/图表/补充材料） | **~6,100 词 → 超 IJE 一倍以上** ❌ |
| 显示项（图+表）合计 | 无硬性上限 | **≤ 8 个** | **6 表 + 4 图 = 10 个** ❌ |
| 参考文献上限 | 无硬性上限 | ≤ 50 | 41 ✅ |
| 摘要 | 150–250 词 | ≤ 250 词，四段 Background/Methods/Results/Conclusions | 232 词，四段 ✅ |
| 关键词 | 4–6 | 3–10 | 6 ✅ |
| Key Messages | 不需要 | **必须**：3 条各为一完整句，置于关键词与引言之间 | **缺** ❌ |
| Running head + 词数标注 | 不要求 | **要求**（置于标题页标题下方；词数写在标题页） | **缺** ❌ |
| 图件格式 | TIFF/EPS/JPEG，彩图 ≥300 dpi（line art ≥1000 dpi 等效） | **不得用 PDF**；须 eps/tiff/png/jpg，≥300 dpi，**最小宽度 300 mm = 3600 px** | 现为 **PDF**，且最宽仅 3402 px ❌ |
| 表格格式 | 可编辑 Word/Excel | 可编辑 Word/Excel、**禁止竖线** | docx 三线表 ✅ |
| 语言/排版 | 英式或美式统一即可 | **须 UK English**；双倍行距、页边距 2.5 cm、全页编号、**正文禁脚注** | 现为单倍/1.15、无页编号 ❌ |
| 统计表述 | 无特别规定 | 用斜体 *P*、斜体 *n*；**不鼓励 "statistically significant"/"significant"** | 文中多处 "significance flips" ⚠ |
| Alt text | 不要求 | **每个图必须**在图注下方给出，前缀 "Alt text:" | **缺** ❌ |
| 其他行政件 | 常规声明 | 需 **Authorship Form（签名）+ COI Form** | 未备 ⚠ |
| 补充材料 | 常规 | 标注 'Supplementary file (for online publication only)'，正文加 "Supplementary data are available at *IJE* online" | 未加 ⚠ |

## 二、IJE 需要做的改动 = 不是微调，而是重写

1. **主文从 ~6,100 词砍到 ≤3,000 词（砍掉 >50%）**。这意味着：§3.1–§3.7 的推导叙述、κ 可靠性细节、§3.7 的反事实验证说明、Limitations 1–5 都要大幅压缩，**大部分内容只能移入 Supplementary**。
   - ⚠ 直接后果：**我们刚强化的"证据强度"（可核查的完整证据链）在正文里会被压缩**，reviewer 看到的正文会明显变薄。这与"投 IJE 是为了影响力"的初衷可能相抵。
2. **显示项从 10 降到 ≤8**：需合并/移走 2 个表或图（候选：Table 3 水平多效性 → 补充材料；Table 6 对比表 → 补充材料或并入正文文字）。
3. **重做全部 8 张图**：IJE 不接受 PDF；且要求最小宽度 3600 px。现有 PNG 最宽 3402 px（FigS1），其余 2200–3300 px。需以 ≥3600 px 重新导出（矢量图可另存 EPS 规避像素限制）。
4. **补 IJE 专属件**：Key Messages（3 句）、Running head、标题页词数、每图 Alt text。
5. **排版改写**：UK English（如 "analyzed"→"analysed" 等按需）、双倍行距、2.5 cm 页边距、页编号、去掉正文脚注、避免 "significant" 措辞。
6. **行政件**：Authorship Form（通讯作者代签）+ COI Form。

预估工作量：**正文重写 1–2 轮 + 图件全部重导 + 新增件**，非"零成本试投"。

## 三、EJE 侧复核（好消息）

- Springer 官方指南**只为 Short Communications 设了 2000 词上限；Original Article 无正文字数上限**——现稿 ~6,100 词合规。
- 摘要 150–250 词（现 232 ✅）、关键词 4–6（现 6 ✅）、编号制方括号引用（与本稿一致 ✅）。
- 不要求 Highlights / Graphical Abstract ✅；无图/表数量上限（6 表 + 4 图无碍）✅。
- **唯一待确认的小项**：EJE 是否偏好**非结构化**摘要。Springer 原文只写 "provide an abstract of 150 to 250 words"，未强制结构；但第三方模板标注为 unstructured。建议对照 EJE 近期 2–3 篇原文再定（若要改，改动量 5 分钟）。

## 四、两种策略的真实成本

| 策略 | 时间成本 | 风险 | 备注 |
|---|---|---|---|
| **A. 直接投 EJE**（现稿即就绪） | **≈0**（今天就能投） | 2 区非 Top 的天花板 | 稿件已完全合规，仅剩 `git push` |
| **B. 先投 IJE，被拒转 EJE** | **高**：需先做"IJE 瘦身版"（正文砍半 + 图重做 + 新增件 + 行政件） | Top 期刊编辑初筛对"纯方法学"更苛刻；且正文变薄可能反而降低说服力 | "被拒就转 EJE"仍成立，但**转投前已付出的成本不小**，不是免费 |
| C. 投 EJE；若被拒/要求大改，再做 IJE 瘦身版 | 中（按需） | 低 | **推荐**：先拿一个明确决定，再决定要不要为 IJE 重写 |

## 五、来源

- IJE 官方 General Instructions（academic.oup.com/ije/pages/General_Instructions）：Original Articles "No more than 3000" 正文词、Up to 8 图表、"Up to 50" 参考文献；摘要 ≤250 词四段；Key Messages 3 条；图 "eps 或高分辨率 tiff、png、jpg"，"不可 PDF"，"最低分辨率 300 dpi，最小宽度 300 mm（3600 pixels）"；关键词 3–10。
- IJE 期刊内页 Information for Contributors（2003/2014/2022 各年一致）："Manuscripts should be prepared in the Vancouver Style … and should be less than 3000 words"；"should not normally exceed 3000 words but review articles may be twice this length"。
- EJE 官方 Submission guidelines（link.springer.com/journal/10654/submission-guidelines）：仅 Short Communications 限 2000 词；Original Article 无词数上限；摘要 150–250 词；关键词 4–6。
- 中科院 2025 分区：EJE 2 区（Top 否，订阅制免 APC）；IJE 2 区（**Top 是**，订阅制免 APC，OA APC ≈ US$3,845）；Genetic Epidemiology **4 区**（Top 否，订阅制免 APC）。
