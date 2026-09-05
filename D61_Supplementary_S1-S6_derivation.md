# Supplementary Appendix：Cov(α̂, β̂) 解析推导
## 两步法乘积MR的协方差结构

**对应论文章节**：Supplementary Methods S1–S6
**符号体系**：与正文 Methods 节一致（见符号表 Table S1）
**2026-07-06更新**：并入原`D19_supplementary_S6_full_variance_validation.md`为S6节（完整
Var(间接效应)验证），并追加S6.5（Taylor锚点抽样噪声caveat，D21第二节）。D19原文档已归档，
不再单独维护，后续修改直接在本文件进行。

---

## S0. 符号表

| 符号 | 含义 | 取值范围 |
|---|---|---|
| $G'_X$ | 第一步工具变量集合（X→M 的 SNP） | 固定集合，$|G'_X| = p_X$ |
| $G'_M$ | 第二步工具变量集合（M→Y 的 SNP） | 固定集合，$|G'_M| = p_M$ |
| $\mathcal{S}$ | 共享 SNP 集合，$\mathcal{S} = G'_X \cap G'_M$ | $n_s = |\mathcal{S}| \in [0, \min(p_X, p_M)]$ |
| $\hat\gamma_{Xj}$ | SNP $j$ 对 X 效应的 GWAS 估计（X-GWAS） | $\hat\gamma_{Xj} = \gamma_{Xj} + \varepsilon^X_j$ |
| $\hat\gamma_{Mj}$ | SNP $j$ 对 M 效应的 GWAS 估计（M-GWAS） | $\hat\gamma_{Mj} = \gamma_{Mj} + \varepsilon^M_j$ |
| $\hat\gamma_{Yk}$ | SNP $k$ 对 Y 效应的 GWAS 估计（Y-GWAS） | $\hat\gamma_{Yk} = \gamma_{Yk} + \varepsilon^Y_k$ |
| $\sigma^2_{Xj}$ | $\hat\gamma_{Xj}$ 的抽样方差，$= 1/N_X$ | — |
| $\sigma^2_M$, $\sigma^2_Y$ | M-GWAS/Y-GWAS 的抽样方差，$\approx 1/N_M$, $1/N_Y$ | — |
| $\mu_X, \mu_M, \mu_Y$ | $E[\gamma_{Xj}]$、$E[\gamma_{Mj}]$、$E[\gamma_{Yj}]$（正的先验均值）| $= \sqrt{F/N}$ |
| $\rho_{MY}$ | M-GWAS 与 Y-GWAS 的样本重叠系数 | $[0, 1]$ |
| $\hat\alpha$ | 第一步 IVW 估计量（X→M 因果效应） | — |
| $\hat\beta$ | 第二步 IVW 估计量（M→Y 因果效应） | — |
| $A_\alpha$ | $\hat\alpha$ 的 IVW 分母：$\sum_{j \in G'_X} \hat\gamma^2_{Xj}/\sigma^2_M$ | — |
| $A_\beta$ | $\hat\beta$ 的 IVW 分母：$\sum_{k \in G'_M} \hat\gamma^2_{Mk}/\sigma^2_Y$ | — |
| $A^{(-j)}_\beta$ | $A_\beta$ 中去掉第 $j$ 项的余量 | $A_\beta - \hat\gamma^2_{Mj}/\sigma^2_Y$ |

---

## S1. IVW 估计量的精确表达式

两步乘积 MR 的 IVW 估计量定义如下：

$$\hat\alpha = \frac{\displaystyle\sum_{j \in G'_X} \hat\gamma_{Xj}\hat\gamma_{Mj}/\sigma^2_M}{\displaystyle\sum_{j \in G'_X} \hat\gamma_{Xj}^2/\sigma^2_M} \equiv \frac{B_\alpha}{A_\alpha}$$

$$\hat\beta = \frac{\displaystyle\sum_{k \in G'_M} \hat\gamma_{Mk}\hat\gamma_{Yk}/\sigma^2_Y}{\displaystyle\sum_{k \in G'_M} \hat\gamma_{Mk}^2/\sigma^2_Y} \equiv \frac{B_\beta}{A_\beta}$$

**关键结构观察**：

- $A_\alpha$ 仅含 $\hat\gamma_{Xj}^2$（X-GWAS），与 $\hat\gamma_{Mj}$ 和 $\hat\beta$ **完全独立**。
- 对于 $j \in \mathcal{S}$，$\hat\gamma_{Mj}$ **原样复用**（同一份 M-GWAS 估计值）同时出现在 $B_\alpha$（一次方）和 $A_\beta$（平方）、$B_\beta$（一次方）中。这是协方差的结构性来源。

---

## S2. 共享 SNP 通道：$\text{Cov}_{\text{shared}}(\hat\alpha, \hat\beta)$

### S2.1 假设

**A1**（抽样独立性）：X-GWAS、M-GWAS、Y-GWAS 使用独立样本（$\rho_{MY} = 0$）；不同 SNP 的估计误差相互独立。

**A2**（弱工具变量正则性）：$F \geq 10$，即 $\mu_M/\sigma_M \geq \sqrt{10}$，确保一阶 Taylor 展开误差可接受（见 S4 节的精度诊断）。

**A3**（先验正均值）：$\mu_X, \mu_M, \mu_Y > 0$，对应"有效工具变量"的模拟设定（$\gamma \sim \mathcal{N}(\mu, (0.3\mu)^2)$）。

### S2.2 协方差的结构分解

由于 $A_\alpha \perp \hat\gamma_M$（假设 A1），以及非共享 SNP 的估计误差独立：

$$\text{Cov}(\hat\alpha, \hat\beta) = E\!\left[\frac{1}{A_\alpha}\right] \cdot \text{Cov}(B_{\alpha,\mathcal{S}},\ \hat\beta) + \underbrace{\text{Cov}(B_{\alpha,\mathcal{S}^c}/A_\alpha,\ \hat\beta)}_{=0,\ \text{非共享SNP与}\hat\beta\text{独立}}$$

其中 $B_{\alpha,\mathcal{S}} = \sum_{j \in \mathcal{S}} \hat\gamma_{Xj}\hat\gamma_{Mj}/\sigma^2_M$。

进一步，由于 $\hat\gamma_{Xj} \perp \hat\gamma_{Mj}$（X-GWAS 与 M-GWAS 独立）：

$$\text{Cov}(B_{\alpha,\mathcal{S}}, \hat\beta) = \sum_{j \in \mathcal{S}} E[\hat\gamma_{Xj}] \cdot \text{Cov}(\hat\gamma_{Mj}/\sigma^2_M,\ \hat\beta) = \frac{n_s \mu_X}{\sigma^2_M} \cdot \text{Cov}(\hat\gamma_{Mj},\ \hat\beta)$$

（最后一步利用各 SNP 的对称性，每个 $j \in \mathcal{S}$ 的贡献相同。）

### S2.3 精确计算 $\text{Cov}(\hat\gamma_{Mj}, \hat\beta)$

设 $Z = \hat\gamma_{Mj}$，$W = \hat\gamma_{Yj}$，$B' = \sum_{k \neq j, k \in G'_M} \hat\gamma_{Mk}\hat\gamma_{Yk}/\sigma^2_Y$，$C = A^{(-j)}_\beta$。

独立性关系（由假设 A1 保证）：$Z \perp W$，$Z \perp B'$，$Z \perp C$（$C$ 不含 SNP $j$ 的贡献）。

$$\hat\beta = \frac{Z \cdot W/\sigma^2_Y + B'}{Z^2/\sigma^2_Y + C}$$

展开 $\text{Cov}(Z, \hat\beta)$（利用 $W, B'$ 独立于 $(Z, C)$）：

$$\text{Cov}(Z, \hat\beta) = \underbrace{\mu_Y \cdot \text{Cov}\!\left(Z,\ \frac{Z/\sigma^2_Y}{A_\beta}\right)}_{\text{W项（正）}} + \underbrace{E[B'] \cdot \text{Cov}\!\left(Z,\ \frac{1}{A_\beta}\right)}_{\text{B'项（负，主导）}}$$

其中 $E[B'] = (p_M - 1)\mu_M\mu_Y/\sigma^2_Y$，$A_\beta = Z^2/\sigma^2_Y + C$。

**符号分析**：$\text{Cov}(Z, Z/A_\beta) > 0$（分子增速略快于分母）；$\text{Cov}(Z, 1/A_\beta) < 0$（$Z$ 增大使 $A_\beta$ 增大，$1/A_\beta$ 减小）；$E[B'] \gg \mu_Y/\sigma^2_Y$（因 $p_M - 1 \gg 1$），故 B' 项主导，$\text{Cov}(Z, \hat\beta) < 0$。

### S2.4 闭式结果

$$\boxed{\text{Cov}_{\text{shared}}(\hat\alpha, \hat\beta) = n_s \cdot \frac{\mu_X}{\sigma^2_M} \cdot E\!\left[\frac{1}{A_\alpha}\right] \cdot \text{Cov}(\hat\gamma_{Mj},\ \hat\beta)}$$

$\text{Cov}(\hat\gamma_{Mj}, \hat\beta)$ 通过数值积分（Monte Carlo，$n_{MC} = 10^5$）精确计算，无需进一步近似。

**边界条件**：$n_s = 0 \Rightarrow \text{Cov}_{\text{shared}} = 0$（代数精确，见验证 B）。

### S2.5 Proposition: a sufficient condition for a negative shared-instrument covariance

The sign of $\text{Cov}_{\text{shared}}(\hat\alpha,\hat\beta)$ is not an empirical accident of the sampled studies; it follows from the IVW algebra under the typical same-sign mediation configuration. Recall from S2.2–S2.3 that for any shared SNP $j\in\mathcal{S}$, with $Z=\hat\gamma_{Mj}$, $W=\hat\gamma_{Yj}\perp Z$, and $B'=\sum_{k\neq j}\hat\gamma_{Mk}\hat\gamma_{Yk}/\sigma^2_Y$ (so that $E[B']=(p_M-1)\mu_M\mu_Y/\sigma^2_Y$),

$$\hat\beta=\frac{ZW/\sigma^2_Y+B'}{Z^2/\sigma^2_Y+C},\qquad A_\beta=Z^2/\sigma^2_Y+C,$$

where $C=A^{(-j)}_\beta$ is independent of $Z$. Then

$$\text{Cov}(Z,\hat\beta)=\mu_Y\,\text{Cov}\!\left(Z,\frac{Z/\sigma^2_Y}{A_\beta}\right)+E[B']\,\text{Cov}\!\left(Z,\frac{1}{A_\beta}\right).$$

**Proposition.** *Under Assumptions A1–A3, if (i) $\hat\alpha$ and $\hat\beta$ share the same sign (equivalently $\mu_X$ and $\mu_Y$ have the same sign — the typical mediation configuration), and (ii) $p_M\ge 3$, then $\text{Cov}_{\text{shared}}(\hat\alpha,\hat\beta)<0$.*

*Proof.* Because $A_\beta=Z^2/\sigma^2_Y+C$ with $Z\perp C$, $A_\beta$ is strictly increasing in $|Z|$, so $\text{Cov}(Z,1/A_\beta)<0$ (the function is monotone decreasing in the square of an independent variate). Meanwhile $\text{Cov}(Z, Z/A_\beta)=\text{Cov}(Z, Z/(Z^2/\sigma^2_Y+C))>0$ since $z\mapsto z/(z^2/\sigma^2_Y+C)$ is odd and increasing near the origin. The two terms are weighted by $\mu_Y$ (positive under (i)) and by $E[B']=(p_M-1)\mu_M\mu_Y/\sigma^2_Y$. Their ratio satisfies

$$\frac{E[B']}{\mu_Y}=\frac{(p_M-1)\mu_M}{\sigma^2_Y}=(p_M-1)\sqrt{F\,N_M}\gg 1$$

for any realistic $p_M\ge 3$ (instrument strength $F\gtrsim 10$ and sample size $N_M\gg 1$), so the negative $B'$-term dominates the positive $W$-term and $\text{Cov}(Z,\hat\beta)<0$. From S2.4,

$$\text{Cov}_{\text{shared}}=n_s\frac{\mu_X}{\sigma^2_M}E[1/A_\alpha]\cdot\text{Cov}(Z,\hat\beta),$$

and the prefactor $n_s\mu_X E[1/A_\alpha]/\sigma^2_M>0$ under (i) (where $\mu_X>0$). Hence $\text{Cov}_{\text{shared}}<0$. ∎

**Consequence.** The corrected indirect-effect variance is $\text{Var}(\hat\alpha\hat\beta)\approx\beta^2\text{Var}(\hat\alpha)+\alpha^2\text{Var}(\hat\beta)+2\hat\alpha\hat\beta\,\text{Cov}(\hat\alpha,\hat\beta)$. Whenever $\hat\alpha\hat\beta>0$ (same-sign mediation) the correction term $2\hat\alpha\hat\beta\,\text{Cov}_{\text{shared}}$ is negative, so the corrected SE is strictly smaller than the naive delta-method SE — i.e. the naive estimator is conservative, and significance flips in this direction are impossible. This proves that the empirical zero-flip finding of §3.5.1 is a structural consequence of the shared-instrument denominator term, not a coincidence of the sampled studies, and it holds whenever conditions (i)–(ii) are satisfied. The sign can reverse only under opposite-sign (suppressor) mediation or through the $\rho_{MY}$ channel (S3), which is why the correction remains necessary even though realized same-sign cases narrow.

---

## S3. 样本重叠通道：$\text{Cov}_\rho(\hat\alpha, \hat\beta)$

### S3.1 假设

**A4**（样本重叠结构）：M-GWAS 与 Y-GWAS 有 $n_{MY}$ 个重叠个体，定义重叠系数 $\rho_{MY} = n_{MY}/\sqrt{N_M N_Y}$，使得对共享 SNP $j \in \mathcal{S}$：

$$\text{Cov}(\hat\gamma_{Mj},\ \hat\gamma_{Yj}) = \rho_{MY} \cdot \sigma_M \cdot \sigma_Y$$

**A5**（传导条件）：$n_s > 0$——此通道**依赖共享 SNP 作为载体**。当 $\pi_s = 0$ 时 $n_s = 0$，通道不存在（见下方边界条件）。

### S3.2 Delta Method 展开

对共享 SNP $j \in \mathcal{S}$，对应偏导：

$$\frac{\partial\hat\alpha}{\partial\hat\gamma_{Mj}} \approx \frac{\mu_X}{\sigma^2_M \cdot E[A_\alpha]}, \qquad \frac{\partial\hat\beta}{\partial\hat\gamma_{Yj}} \approx \frac{\mu_M}{\sigma^2_Y \cdot E[A_\beta]}$$

两个偏导对应**不同随机量**（$\hat\gamma_{Mj}$ 和 $\hat\gamma_{Yj}$），其联合波动由 $\text{Cov}(\hat\gamma_{Mj}, \hat\gamma_{Yj})$（假设 A4）决定：

$$\text{Cov}_\rho(\hat\alpha, \hat\beta) = \sum_{j \in \mathcal{S}} \frac{\partial\hat\alpha}{\partial\hat\gamma_{Mj}} \cdot \frac{\partial\hat\beta}{\partial\hat\gamma_{Yj}} \cdot \text{Cov}(\hat\gamma_{Mj}, \hat\gamma_{Yj})$$

$$\boxed{\text{Cov}_\rho(\hat\alpha, \hat\beta) = n_s \cdot \rho_{MY} \cdot \frac{\mu_X \mu_M}{\sigma_M \sigma_Y \cdot E[A_\alpha] \cdot E[A_\beta]}}$$

### S3.3 两通道无重复计数的证明

共享 SNP 通道的驱动量是 $\text{Var}(\hat\gamma_{Mj}) = \sigma^2_M$（M-GWAS 内部方差，同一随机变量 $\hat\gamma_{Mj}$ 影响两个估计量）。

$\rho_{MY}$ 通道的驱动量是 $\text{Cov}(\hat\gamma_{Mj}, \hat\gamma_{Yj}) = \rho_{MY}\sigma_M\sigma_Y$（M-GWAS 和 Y-GWAS **不同随机变量**的联合波动）。

在 Taylor 展开中，两项分别对应 $(\partial\hat\alpha/\partial\hat\gamma_{Mj})^2 \cdot \text{Var}(\hat\gamma_{Mj})$ 和 $(\partial\hat\alpha/\partial\hat\gamma_{Mj}) \cdot (\partial\hat\beta/\partial\hat\gamma_{Yj}) \cdot \text{Cov}(\hat\gamma_{Mj}, \hat\gamma_{Yj})$，代数上互不交叉，**无重复计数**。

---

## S4. 精度诊断：一阶近似的适用边界

一阶 delta method 的误差来自两个独立来源：

### S4.1 共享 SNP 通道的精度指标

$$\kappa_1 = \frac{\text{Var}[A_\beta]}{(E[A_\beta])^2} = \frac{4\mu^2_M v_M + 2v^2_M}{p_M({\mu^2_M + v_M})^2}$$

其中 $v_M = (0.3\mu_M)^2 + \sigma^2_M$。$\kappa_1$ 代表 $1/A_\beta$ 的 Jensen 不等式修正项，即 $E[1/A_\beta] - 1/E[A_\beta] \approx \kappa_1/E[A_\beta]$。

**阈值**：$\kappa_1 < 0.03$（低风险），$0.03 \leq \kappa_1 < 0.05$（中风险），$\kappa_1 \geq 0.05$（高风险）。

### S4.2 样本重叠通道的精度指标

$$\kappa_2 = \frac{|\rho_{MY}|}{\sqrt{F}}$$

$\kappa_2$ 代表 $\rho_{MY}$ 引起的 $E[\hat\beta]$ 偏移（相对值）：$\delta E[\hat\beta] \approx \kappa_2 \cdot \mu_Y/\mu_M$。

**阈值**：$\kappa_2 < 0.05$（低风险），$0.05 \leq \kappa_2 < 0.10$（中风险），$\kappa_2 \geq 0.10$（高风险）。

### S4.3 数值验证（模拟支撑）

| F | $\rho_{MY}$ | $\kappa_1$ | $\kappa_2$ | 实测误差 | 风险等级 |
|---|---|---|---|---|---|
| 30 | 0 | 0.021 | 0.000 | <6% | 低 |
| 30 | 0.5 | 0.021 | 0.091 | 4% | 中 |
| 30 | 0.8 | 0.021 | 0.146 | 11% | 高 |
| 10 | 0 | 0.029 | 0.000 | <8% | 低 |
| 10 | 0.5 | 0.029 | 0.158 | 5% | 高 |
| 10 | 1.0 | 0.029 | 0.316 | 30% | 高 |

---

## S5. 与已有文献的内部一致性

### S5.1 Lin et al. (2025) 特例

令 $\pi_s = 0$（$n_s = 0$）且 $\rho_{MY} = 0$：

$$\text{Cov}_{\text{shared}} = 0,\quad \text{Cov}_\rho = 0 \implies \text{Cov}(\hat\alpha, \hat\beta) = 0$$

此时 $\text{Var}(\hat\alpha\hat\beta)$ 由 delta method 加法给出（Lin et al. 2025 的原始假设），本公式在三样本独立情形下**精确还原**该框架。✓

### S5.2 Burgess et al. (2017) 单步协方差

Burgess et al. (2017) 处理的是**单个 IVW 估计量内部**（同一组 $\gamma_{Mj}$ 和 $\gamma_{Yj}$）的协方差，对应的是 $\hat\beta$ 自身的方差结构（含 $\rho_{MY}$ 修正）。本文的 $\text{Cov}(\hat\alpha, \hat\beta)$ 是**跨步骤**的协方差，属于 Burgess et al. (2017) 框架的扩展，在 $\pi_s = 0$ 时退化为零（两步估计量独立），与其假设一致。✓

### S5.3 Difference method 的类比

Lin et al. (2025) 讨论 difference method（$\hat\tau = \hat\delta_1 - \hat\delta_2$）时，$\text{Cov}(\hat\delta_1, \hat\delta_2)$ 来自两者共享同一组工具变量对 X、Y 的回归——这是**结构性共享**（每次回归都用全套 IV）。本文的共享 SNP 通道类似，但仅对 $\mathcal{S}$ 中的 SNP 产生协方差，在 $\pi_s = 1$（完全重叠）时两者结构最接近，$\pi_s = 0$ 时本文通道消失而 difference method 仍有协方差（因为 IV 集合完全重叠）。两者**不可直接互相替代**，不存在符号迁移问题。✓

---

## S6. 完整间接效应方差的验证——超越 Cov(α̂,β̂) 本身，验证 Var(α̂β̂) 的完整delta method精度

**并入说明**：本节原为独立文档 `D19_supplementary_S6_full_variance_validation.md`（2026-07-05），
2026-07-06按决定并入本附录作为S6正式小节。除S16引用路径已同步更新为FIXED版外，内容与原文一致。

### S6.0 动机

S1–S5推导并验证了 $\text{Cov}(\hat\alpha,\hat\beta)$ 的闭式表达式（验证A：10/10非零情形相对误差<20%）。
但间接效应的完整方差

$$\text{Var}(\hat\alpha\hat\beta) \approx \beta^2\text{Var}(\hat\alpha) + \alpha^2\text{Var}(\hat\beta) + 2\alpha\beta\,\text{Cov}(\hat\alpha,\hat\beta)$$

这一标准delta method组合公式，除了需要 $\text{Cov}(\hat\alpha,\hat\beta)$ 之外，还需要 $\text{Var}(\hat\alpha)$、
$\text{Var}(\hat\beta)$ 各自的精确表达式——此前的验证从未独立检验过这两项本身的精度。本节补齐这一验证，
并识别、推导、验证了两个此前被忽略的解析项。

### S6.1 缺失项一：比值估计量方差的全方差分解

#### S6.1.1 问题

$\hat\alpha=B_\alpha/A_\alpha$ 的条件方差 $\text{Var}(\hat\alpha\mid\hat\gamma_X)$ 满足精确关系（见S1）：

$$\text{Var}(\hat\alpha\mid\hat\gamma_X) = \frac{v_M}{\sigma_M^2 \cdot A_\alpha}$$

此前的实现仅取 $E_{\hat\gamma_X}\!\left[\text{Var}(\hat\alpha\mid\hat\gamma_X)\right] \approx (v_M/\sigma_M^2)\cdot E[1/A_\alpha]$
作为 $\text{Var}(\hat\alpha)$ 的完整近似。但全方差公式（law of total variance）要求：

$$\text{Var}(\hat\alpha) = \underbrace{E\!\left[\text{Var}(\hat\alpha\mid\hat\gamma_X)\right]}_{\text{已实现}} + \underbrace{\text{Var}\!\left(E[\hat\alpha\mid\hat\gamma_X]\right)}_{\text{此前缺失}}$$

第二项此前完全未被纳入，实测发现其量级与第一项相当（不是可忽略的高阶修正）。

#### S6.1.2 第二项的闭式推导

记 $S_1=\sum_{j\in G_X'}\hat\gamma_{Xj}$，$S_2=\sum_{j\in G_X'}\hat\gamma_{Xj}^2$，则
$E[\hat\alpha\mid\hat\gamma_X]=\mu_M\cdot S_1/S_2$（利用 $A_\alpha=S_2/\sigma_M^2$）。对 $S_1/S_2$ 做delta method展开
（$\hat\gamma_{Xj}\overset{iid}{\sim}N(\mu_X,v_X)$，$v_X=(0.3\mu_X)^2+\sigma_X^2$，$Q_X=\mu_X^2+v_X$）：

$$\boxed{\text{Var}\!\left(E[\hat\alpha\mid\hat\gamma_X]\right) = \frac{\mu_M^2}{p_X}\left[\frac{v_X}{Q_X^2} - \frac{4\mu_X^2 v_X}{Q_X^3} + \frac{\mu_X^2(4\mu_X^2v_X+2v_X^2)}{Q_X^4}\right]}$$

#### S6.1.3 数值验证

用"固定 $\hat\gamma_X$、仅重新随机化 $\hat\gamma_M$"的条件模拟独立验证第一项（$n=20000$，理论/实测比值1.03）；
用另一组独立模拟直接验证第二项闭式解（理论/实测比值0.98）。两项加总后，在统一的独立先验DGP下
（与S6.3最终验证使用同一套数据生成过程）边际验证：

| F | 完整式（两项加总） | 实测（边际模拟，$n=15000$） | 完整式/实测 |
|---|---|---|---|
| 10 | 0.012892 | 0.013310 | 0.969 |
| 30 | 0.009421 | 0.009641 | 0.977 |

（$p_X=20$，$N=50000$ 标准配置；仅取第一项的旧式在两个F值下均系统性低估，
比值分别为0.32、0.16——即低估约3–6倍，完整式吻合度>0.96）

$\text{Var}(\hat\beta)$ 的对应第二项完全同构（互换 $X\to M$、$M\to Y$ 下标）。

### S6.2 缺失项二：样本重叠对 $\text{Var}(\hat\beta)$ 自身的方差压缩效应

#### S6.2.1 问题

M-GWAS/Y-GWAS样本重叠（$\rho_{MY}$）此前只被建模为影响 $\text{Cov}(\hat\alpha,\hat\beta)$ 的一条独立通道（S3）。
但 $\rho_{MY}$ 同时会改变 $\text{Var}(\hat\beta)$ **自身**的量级——此前的公式完全没有 $\rho_{MY}$ 依赖项。

#### S6.2.2 机制与闭式推导

$\hat\gamma_{Yk}=\hat\gamma_{Yk}^{true}+\rho_{MY}(\sigma_Y/\sigma_M)\varepsilon_{Mk}+\sqrt{1-\rho_{MY}^2}\,\sigma_Y z_k$，
其中 $\varepsilon_{Mk}$ 是 $\hat\gamma_{Mk}$ 的测量误差分量。利用两个独立正态变量给定和后的条件分布标准结果
（$\hat\gamma_{Mk}=\gamma_{Mk}^{true}+\varepsilon_{Mk}$，两者独立、方差分别为 $s_M^2=(0.3\mu_M)^2$、$\sigma_M^2$），
条件在 $\hat\gamma_{Mk}$ 已知时：

$$\text{Var}(\varepsilon_{Mk}\mid\hat\gamma_{Mk}) = \frac{\sigma_M^2 s_M^2}{v_M} \quad(\text{常数，不依赖}\hat\gamma_{Mk}\text{取值})$$

代入后，条件方差 $\text{Var}(\hat\gamma_{Yk}\mid\hat\gamma_{Mk})$ 从 $v_Y$ **压缩为**：

$$\boxed{v_Y' = v_Y - \rho_{MY}^2\,\sigma_Y^2\,\frac{\sigma_M^2}{v_M}}$$

条件均值 $E[\hat\gamma_{Yk}\mid\hat\gamma_{Mk}]$ 线性于 $\hat\gamma_{Mk}$，系数为 $\rho_{MY}\sigma_M\sigma_Y/v_M$，
相应地 S6.1 第二项公式中的系数 $\mu_Y$ 需替换为：

$$\mu_Y' = \mu_Y - \rho_{MY}\,\sigma_M\sigma_Y\,\frac{\mu_M}{v_M}$$

完整 $\text{Var}(\hat\beta)$ 公式为S6.1两项公式中 $v_Y\to v_Y'$、$\mu_Y\to\mu_Y'$ 代入的结果。

#### S6.2.3 数值验证

隔离场景（$n_s=0$，排除共享SNP通道干扰，$F=30$，$p_M=20$，$N=50000$）：

| $\rho_{MY}$ | 旧式（无$\rho$修正）理论/实测 | 新式（含$\rho$修正）理论/实测 |
|---|---|---|
| 0.0 | 1.02 | 1.02 |
| 0.5 | 0.90 | 1.02 |
| 1.0 | 0.78 | 1.02 |

新式在全部 $\rho_{MY}$ 取值下保持一致的高精度，旧式随 $\rho_{MY}$ 增大而系统性高估 $\text{Var}(\hat\beta)$（最高偏差22%）。

### S6.3 完整 Var(间接效应) 的综合验证

补齐S6.1、S6.2两项后，对 $F\in\{10,30\}\times\rho_{MY}\in\{0,0.5,1.0\}\times\pi_{shared}\in\{0.1,0.3,0.7,1.0\}$
共24组合（$n_{reps}=15000$，直接模拟 $\hat\alpha,\hat\beta$ 本身，不借助任何闭式公式捷径，全程使用同一
数据生成过程以确保对比的一致性）：

| 版本 | 平均相对误差 | 最大相对误差 |
|---|---|---|
| 标准delta method（仅S1–S5闭式Cov + 未修正的边际Var，即 $\text{Var}(\hat\alpha)\approx E[1/A_\alpha]$） | 93.0% | 145.7% |
| + S6.1（全方差第二项） | 10.7% | 34.2% |
| + S6.1 + S6.2（完整修正，`S18_final_rho_correction_validation.R`，生产代码2026-07-06前版本） | 4.8% | 13.3% |
| + S6.1 + S6.2 + Jensen修正（`.E_inv_A_jensen()`，现行生产代码，D22第一节） | **4.1%** | **12.5%** |

最大误差出现在弱工具变量（$F<15$）与高共享比例（$\pi_{shared}>0.5$）同时成立的角，
提示这一区域建议以参数化模拟（`S16_bootstrap_fallback_indirect_var_FIXED.R`）作为交叉核对，
而非仅依赖闭式公式（原S16版本存在DGP不一致bug，已于2026-07-06修复替换，见D21第一节）。

**2026-08-06：Jensen修正版数字已实测确认，非转述**。过程记录如下，供追溯：

1. 用户上传了`S17_unified_dgp_test.R`、`S18_final_rho_correction_validation.R`、
   `final_v4_results.csv`三个文件。先原样运行S17+S18（相同种子`8000+i`、`n_reps=15000`），
   复现结果为均值4.8%/最大13.3%（最差格F=10,ρ=0,π=1.0，13.35%），与上传的
   `final_v4_results.csv`（均值4.78%/最大13.35%）精确吻合，确认这两个文件就是
   产出4.8%/13.3%这组数字的真实原始脚本，且脚本本身可完整独立复现，未被后续改动过。
2. 在此基础上写了真正的`S21_Jensen整合验证.R`——**不是重新实现，是在S18代码基础上
   只做一处改动**：把`Var_ratio_est_full`、`Var_ratio_est_with_rho`、`Cov_shared_theo`/
   `Cov_rho_theo`里所有`1/E_A`替换成D22第一节的Jensen二阶修正
   `E[1/A]≈1/E[A]+Var(A)/E[A]³`，DGP、`n_reps`、随机种子（`8000+i`）、S18原有的
   联合正态乘积二次修正项（`Var(α)·Var(β)+Cov²`，D18第七节7.1）全部原样保留，
   确保跟基线是同一套代码脉络上的单一变量对比。
3. **结果**：均值**4.13%**、最大**12.51%**（最差格仍是F=10,ρ=0,π=1.0，12.51%），
   与D22第二节报告的4.1%/12.5%几乎精确吻合。逐格对比也印证了D22原文的描述：
   24格里有**5格**误差不降反升，其中F=30,ρ_MY=1.0,π=1.0从6.26%变差到7.86%，
   与D22原文"F=30、ρ_MY=1.0附近……从约6.3%变差到约7.9%"的描述精确对应。
4. **结论：D22报告的4.1%/12.5%这两个数字确认无误，正式采用为S6.3表格的最终版本**
   （已更新到上表第四行）。此前2026-08-06较早的一次尝试（用逐字抄录但未拿到S17/S18
   原始文件的独立复现版本）得到的3.99%/3.52%等数字，现已确认是因为遗漏了S18的联合
   正态乘积二次修正项（`Var(α)·Var(β)+Cov²`）所致，非DGP本身的歧义——该版本已废弃，
   不再作为参考。

**已关闭的三项（原D20第六节四个开放项，现全部处理完毕）**：
- **两封邮件**：已确认不发送（用户决定，2026-08-06）。D22原文确认邮件2内容不受Jensen
  探索结果影响，不需要因此重新起草
- **D19并入D03**：已完成（2026-07-06）
- **Taylor锚点问题**：D21第二节"D18 §7.5的开放问题可以关闭"，点估计做锚点平均无偏，
  见S6.5
- **4.8%/13.3%要不要写进正式Limitation，以及具体数字本身**：本节已确认最终数字为
  4.1%/12.5%（Jensen修正版），建议连同S6.5的锚点抽样噪声caveat一并写入正式Limitation

**交付文件（建议归档进`scripts/`）**：`S21_Jensen整合验证.R`（本次产出，已实测通过）、
`v5_jensen_corrected_results.csv`（本次24组合网格完整结果，含逐格与基线的对比）

### S6.4 与S1–S5的关系

本节两处修正**不影响** $\text{Cov}(\hat\alpha,\hat\beta)$ 本身的闭式公式（S2.4、S3.2的boxed结果不变，
验证A的10/10结论不受影响）——因为在标准假设（M、Y的GWAS独立先验，见S2.1的A1–A3）下，
$E[\hat\beta\mid\hat\gamma_X]$ 不依赖 $\hat\gamma_X$，全协方差公式中对应的交叉项恒为零。S6.1、S6.2两处
缺失项是 $\text{Var}(\hat\alpha)$、$\text{Var}(\hat\beta)$ **各自**的问题，与跨步骤协方差机制正交，
不构成对S1–S5核心贡献的修正，而是对"如何用这些量拼出完整间接效应方差"这一下游步骤的补充。

### S6.5 Taylor展开锚点的抽样噪声（2026-07-06新增，D21第二节）

S6.1–S6.3的验证均以同批次模拟样本均值（$\text{mean}(\hat\alpha)$、$\text{mean}(\hat\beta)$，$n_{reps}=15000$）
作为Taylor展开锚点——但工具实际使用场景中，只有论文报告的**单次点估计**可用作锚点，此前未验证这一替换
是否引入新偏差。

**验证方法**：对4个代表性组合，把每次模拟自己的 $\hat\alpha$/$\hat\beta$ 当作"论文只报告了一次点估计"，
单独代入组合公式，与批次均值锚点做法对比。

**结论**：单次点估计做锚点，**平均而言不但没有引入系统性偏差，反而比用有限批次（$n_{reps}=15000$）样本
均值做锚点还稍微更准**（4组合上相对真值误差1.0%–2.6%，优于批次均值锚点的2.2%–4.1%）。这在数学上成立：
单点估计锚点对应的是"联合正态乘积"精确方差公式在其真实抽样分布下取期望，本身无偏；有限批次均值只是
对这个期望的一个近似。

**但存在一个新caveat，需要写入Limitation**：虽然平均无偏，**对任何单次实际应用（只有一篇论文报告一个
点估计），结果的波动范围相当大**——4个代表性组合的5%–95%区间大致是均值的±25%到±35%（例如F=10,
ρ=0,π=0.7一组：[0.0107, 0.0187]，均值0.014422）。这个波动纯粹来自点估计本身的抽样噪声，与delta method
公式的系统误差（S6.3报告的4.1%均值/12.5%最大，Jensen修正版）是两个独立来源、会叠加在一起。也就是说，工具输出的
$\text{Var}(\hat\alpha\hat\beta)$ 点估计本身没有系统性偏差，但对单篇论文而言，这个点估计自带的不确定性
比S6.3单独报告的公式误差更大，**建议在Limitation中明确说明工具输出应视为"合理估计范围的中心"而非精确值**。

