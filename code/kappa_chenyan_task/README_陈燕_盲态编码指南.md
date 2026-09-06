# 陈燕 · 盲态第二编码任务指南（Cohen's κ 可靠性评估）

> 本文件夹是**只给你一个人**用的。里面只有你需要的材料，没有"标准答案"，所以请保持盲态。

---

## 一、这是什么任务

我们投稿的论文（两步法 MR 中介的 IV 重叠协方差校正）报告了一组文献编码结果（设计类型、IV 选择策略、是否讨论重叠风险）。为了诚实地说"这些编码可信"，需要**第二个人独立、盲态地重新编码同一批文献**，然后算编码者间一致性 **Cohen's κ**。

- 你就是这位"第二编码人"。
- 你是共同作者、且**没有参与**最初的编码方案设计与建 key，因此只要你对"标准答案"保持盲态，你的编码就是合规的"团队内盲态第二编码"（manuscript 已如实披露这一点）。
- **原始编码人（王建峰 J.W.）不参与本次编码**——用自己的 key 重编码是循环论证，κ 无效。

---

## 二、文件夹里有什么（就这 3 个，别找别的）

| 文件 | 是什么 | 你要做啥 |
|---|---|---|
| `kappa_second_coder_template_BLANK.csv` | 盲填表。前 5 列是 50 篇文献的书目信息（study_id / pmid / 作者_年 / 期刊 / 标题），后 3 列是空的，等你填 | **填这 3 列** |
| `D61_Supplementary_codebook_S1.md` | 编码规则手册（中文），讲每个字段怎么判 | **照着它判** |
| `compute_kappa_2nd.py` | 算 κ 的脚本。你填完跑一下，自动对密封 key 比对你填的，出报告 | **填完跑一下** |

⚠ **本文件夹刻意没有**"标准答案"（密封 key）和"已经填好的表"。请**不要**去翻上一级 `code/` 里的 `kappa_second_coder_template.csv`（已填好，会破盲）和 `code/kappa/` 里的 `kappa_answer_key_20260903.csv`（密封 key）。脚本会在你**提交之后**自动读 key 来比对，你本人不需要、也不应该打开它。

---

## 三、你要填的 3 列（判定规则）

逐篇打开全文（用 PMID 在 PubMed 搜），根据正文 Methods 填。**只看论文本身**，不要猜我们想要什么结果。

### 列 1：`design_type`（二分类，这 50 篇里全是两步法，所以实质是"是/否"）
| 填 | 条件 |
|---|---|
| `两步法MR中介` | Methods 里有明确的 **Step 1 / Step 2 两阶段结构**（不管它最后用 product method 还是 difference method 算间接效应） |
| `不属于两步法MR中介-排除` | 标题/摘要提了 mediation，但 Methods 里找不到两步或 MVMR 结构；或纯观察性中介、个体层 Cox 中介、单链 MR、或方法学/工具论文 |

> 口诀：**看 Methods 有没有 Step1/Step2 或 MVMR 直接/间接效应分解**，别被标题里的 "mediation" 带偏。"用了 difference method"不是排除理由。

### 列 2：`IV_selection_strategy`（三选一）
| 填 | 条件 |
|---|---|
| `分开选IV` | Step 1 和 Step 2 **各自独立**选工具变量（两步法最常见） |
| `MVMR联合估计` | 用多变量 MR（MVMR）**联合**估计直接+间接效应，不是分步骤的两步结构 |
| `无法判断` | 论文没说清楚 IV 来源，不足以分类（拿不准就选这个，别硬猜） |

> 提示：有些论文用 MVMR 只做"直接效应"的敏感性验证，但间接效应仍是序贯乘积法算的 → 这种填 `分开选IV`。

### 列 3：`reports_overlap_risk`（三选一）
| 填 | 条件 |
|---|---|
| `是` | 论文**明确讨论/意识到**了"暴露–中介或中介–结局 GWAS 样本重叠"这个风险本身 |
| `部分` | 提到了重叠但没量化、只是顺带一句 |
| `否` | 完全没讨论这件事 |

> 注意：只看"有没有讨论重叠风险"，**不管实际重叠状态如何**。

---

## 四、操作流程（照做即可）

**第 1 步｜填表**
- 打开 `kappa_second_coder_template_BLANK.csv`（用 Excel 或 VS Code 都行，是普通 CSV）。
- 对 50 行逐篇：用 PMID 找全文 → 照上面 3 列规则填 → 拿不准就填 `无法判断` / `不属于两步法MR中介-排除` 并在旁边 notes 记一句理由（CSV 没有 notes 列，可另开一个 txt 记，或直接在心里有数）。
- 平均每篇 5–10 分钟，总共约半天。

**第 2 步｜另存为**
- **务必另存**为 `kappa_second_coder_chenyan_FILLED.csv`（就放本文件夹里）。
- 不要覆盖 `kappa_second_coder_template_BLANK.csv`，那是母版。

**第 3 步｜跑脚本出 κ 报告**
在本文件夹里打开终端，运行：

```bash
python compute_kappa_2nd.py
```

（脚本默认就读你另存的 `kappa_second_coder_chenyan_FILLED.csv`，并自动从上级 `code/kappa/` 读密封 key 比对——你不用指定路径。若想显式写也行：
`python compute_kappa_2nd.py --second kappa_second_coder_chenyan_FILLED.csv`）

- 跑完会生成 `kappa_2nd_report.csv` + `compute_kappa_2nd.log`，并打印每字段的：
  - `Po` 观察一致率、`Pe` 偶然一致率、`kappa` Cohen's κ、`PABAK`、`bootstrap 95% CI`。

**第 4 步｜把报告发回王建峰**
- 把 `kappa_2nd_report.csv` 发给他即可。他会把你的真人 κ 替换进 manuscript 并署名。

---

## 五、报告怎么看（给你自己核对用）

- **`design_type` 大概率会显示 `kappa = 0.00`**——这不是你填得差，而是数学假象：密封 key 里这 50 篇**全部**被标成"两步法MR中介"，导致"偶然一致率 Pe→1"，κ 公式分母为 0 塌成 0。**此时看 `Po`（观察一致率）**，比如 94% 就是真一致率。脚本也会打印提示。
- **`IV_selection_strategy` / `reports_overlap_risk`** 的 κ 是有效值，0.5 左右算"中等"一致性。
- `bootstrap 95% CI` 是稳定性区间；`reports_overlap_risk` 只有 8 篇有值，样本太小，κ 仅供参考。

---

## 六、诚信红线（很重要）

- ❌ 不要打开 `code/kappa_second_coder_template.csv` 和 `code/kappa/kappa_answer_key_20260903.csv`。
- ❌ 不要照抄任何"看起来像答案"的内容。
- ✅ 凭你读全文的独立判断填；拿不准就标 `无法判断`/`排除`，这反而是最诚实的做法。
- ✅ 你的编码是真实的"人类第二编码"，manuscript 会据此报告并署名——所以务必是你自己读的、自己判的。

---

完成第 4 步就结束了。有问题直接问王建峰，但**编码过程中不要问他某篇该填啥**（那会破盲）；可以问"规则手册某句话啥意思"。
