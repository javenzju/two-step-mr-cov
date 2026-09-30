# Supplementary Methods S1–S6 — Analytic derivation of Cov(α̂, β̂) and validation of the full indirect-effect variance

**Corresponds to:** Supplementary Methods S1–S6 of the main manuscript.
**Notation:** identical to the Methods section of the main text (notation table, S0).

---

## S0. Notation

| Symbol | Meaning | Range / expression |
|---|---|---|
| $G'_X$ | Step-1 instrument set (SNPs for exposure → mediator) | fixed set, $\lvert G'_X\rvert = p_X$ |
| $G'_M$ | Step-2 instrument set (SNPs for mediator → outcome) | fixed set, $\lvert G'_M\rvert = p_M$ |
| $\mathcal{S}$ | shared SNP set, $\mathcal{S} = G'_X \cap G'_M$ | $n_s = \lvert\mathcal{S}\rvert \in [0, \min(p_X,p_M)]$ |
| $\hat\gamma_{Xj}$ | GWAS estimate of SNP $j$'s effect on X (X-GWAS) | $\hat\gamma_{Xj} = \gamma_{Xj} + \varepsilon^X_j$ |
| $\hat\gamma_{Mj}$ | GWAS estimate of SNP $j$'s effect on M (M-GWAS) | $\hat\gamma_{Mj} = \gamma_{Mj} + \varepsilon^M_j$ |
| $\hat\gamma_{Yk}$ | GWAS estimate of SNP $k$'s effect on Y (Y-GWAS) | $\hat\gamma_{Yk} = \gamma_{Yk} + \varepsilon^Y_k$ |
| $\sigma^2_{Xj}$ | sampling variance of $\hat\gamma_{Xj}$, $= 1/N_X$ | — |
| $\sigma^2_M$, $\sigma^2_Y$ | sampling variances of the M-GWAS / Y-GWAS, $\approx 1/N_M$, $1/N_Y$ | — |
| $\mu_X, \mu_M, \mu_Y$ | $E[\gamma_{Xj}]$, $E[\gamma_{Mj}]$, $E[\gamma_{Yj}]$ (signed prior means) | $\lvert\cdot\rvert = \sqrt{F/N}$ |
| $\rho_{MY}$ | sample-overlap coefficient between M-GWAS and Y-GWAS | $[0,1]$ |
| $\hat\alpha$ | step-1 IVW estimator (causal effect X → M) | — |
| $\hat\beta$ | step-2 IVW estimator (causal effect M → Y) | — |
| $A_\alpha$ | IVW denominator of $\hat\alpha$: $\sum_{j\in G'_X}\hat\gamma^2_{Xj}/\sigma^2_M$ | — |
| $A_\beta$ | IVW denominator of $\hat\beta$: $\sum_{k\in G'_M}\hat\gamma^2_{Mk}/\sigma^2_Y$ | — |
| $A^{(-j)}_\beta$ | $A_\beta$ with the $j$-th term removed | $A_\beta - \hat\gamma^2_{Mj}/\sigma^2_Y$ |

---

## S1. Exact expressions for the IVW estimators

The IVW estimators of the two-step product-method MR are

$$\hat\alpha = \frac{\displaystyle\sum_{j \in G'_X} \hat\gamma_{Xj}\hat\gamma_{Mj}/\sigma^2_M}{\displaystyle\sum_{j \in G'_X} \hat\gamma_{Xj}^2/\sigma^2_M} \equiv \frac{B_\alpha}{A_\alpha},
\qquad
\hat\beta = \frac{\displaystyle\sum_{k \in G'_M} \hat\gamma_{Mk}\hat\gamma_{Yk}/\sigma^2_Y}{\displaystyle\sum_{k \in G'_M} \hat\gamma_{Mk}^2/\sigma^2_Y} \equiv \frac{B_\beta}{A_\beta}.$$

**Key structural observation.**

- $A_\alpha$ depends only on $\hat\gamma_{Xj}^2$ (X-GWAS) and is therefore **independent** of $\hat\gamma_{Mj}$ and of $\hat\beta$.
- For $j \in \mathcal{S}$, the *same* noisy mediator association $\hat\gamma_{Mj}$ is reused: it appears in $B_\alpha$ (first power), in $A_\beta$ (squared) and in $B_\beta$ (first power). This is the structural origin of the covariance.

---

## S2. The shared-instrument channel: $\text{Cov}_{\text{shared}}(\hat\alpha, \hat\beta)$

### S2.1 Assumptions

**A1 (sampling independence).** The X-GWAS, M-GWAS and Y-GWAS use independent samples ($\rho_{MY}=0$); estimation errors of distinct SNPs are mutually independent.

**A2 (weak-instrument regularity).** $F \ge 10$, i.e. $\mu_M/\sigma_M \ge \sqrt{10}$, so that the first-order Taylor error is acceptable (precision diagnostics in S4).

**A3 (prior means).** $\mu_X, \mu_M, \mu_Y \neq 0$, matching the "valid instrument" simulation setting ($\gamma \sim \mathcal{N}(\mu, (0.3\mu)^2)$). The *signs* of these means are not fixed; they carry the direction of each causal effect (see Remark S2.5a).

### S2.2 Structural decomposition of the covariance

Because $A_\alpha \perp \hat\gamma_M$ (A1) and the estimation errors of non-shared SNPs are independent,

$$\text{Cov}(\hat\alpha, \hat\beta) = E\!\left[\frac{1}{A_\alpha}\right] \cdot \text{Cov}(B_{\alpha,\mathcal{S}},\ \hat\beta) + \underbrace{\text{Cov}(B_{\alpha,\mathcal{S}^c}/A_\alpha,\ \hat\beta)}_{=\,0\ \text{(non-shared SNPs are independent of }\hat\beta)},$$

where $B_{\alpha,\mathcal{S}} = \sum_{j \in \mathcal{S}} \hat\gamma_{Xj}\hat\gamma_{Mj}/\sigma^2_M$. Since $\hat\gamma_{Xj} \perp \hat\gamma_{Mj}$ (X-GWAS and M-GWAS are independent),

$$\text{Cov}(B_{\alpha,\mathcal{S}}, \hat\beta) = \sum_{j \in \mathcal{S}} E[\hat\gamma_{Xj}] \cdot \text{Cov}(\hat\gamma_{Mj}/\sigma^2_M,\ \hat\beta) = \frac{n_s \mu_X}{\sigma^2_M} \cdot \text{Cov}(\hat\gamma_{Mj},\ \hat\beta)$$

(by symmetry, each $j \in \mathcal{S}$ contributes identically).

### S2.3 Exact computation of $\text{Cov}(\hat\gamma_{Mj}, \hat\beta)$

Let $Z = \hat\gamma_{Mj}$, $W = \hat\gamma_{Yj}$, $B' = \sum_{k \neq j,\, k \in G'_M} \hat\gamma_{Mk}\hat\gamma_{Yk}/\sigma^2_Y$, and $C = A^{(-j)}_\beta$. By A1, $Z \perp W$, $Z \perp B'$, $Z \perp C$, and

$$\hat\beta = \frac{Z W/\sigma^2_Y + B'}{Z^2/\sigma^2_Y + C}.$$

Expanding (using that $W, B'$ are independent of $(Z,C)$),

$$\text{Cov}(Z, \hat\beta) = \underbrace{\mu_Y \cdot \text{Cov}\!\left(Z,\ \frac{Z/\sigma^2_Y}{A_\beta}\right)}_{W\text{-term}} + \underbrace{E[B'] \cdot \text{Cov}\!\left(Z,\ \frac{1}{A_\beta}\right)}_{B'\text{-term}},$$

with $E[B'] = (p_M - 1)\mu_M\mu_Y/\sigma^2_Y$ and $A_\beta = Z^2/\sigma^2_Y + C$.

**Sign analysis.** $\text{Cov}(Z, Z/A_\beta) > 0$ (the numerator grows slightly faster than the denominator); $\text{Cov}(Z, 1/A_\beta) < 0$ ($Z$ increasing raises $A_\beta$, hence lowers $1/A_\beta$); and $E[B'] \gg \mu_Y/\sigma^2_Y$ since $p_M - 1 \gg 1$. The $B'$-term therefore dominates, giving $\text{Cov}(Z,\hat\beta)$ the sign of $-\mu_Y$ — the basis of Remark S2.5a.

### S2.4 Semi-analytic result

$$\boxed{\text{Cov}_{\text{shared}}(\hat\alpha, \hat\beta) = n_s \cdot \frac{\mu_X}{\sigma^2_M} \cdot E\!\left[\frac{1}{A_\alpha}\right] \cdot \text{Cov}(\hat\gamma_{Mj},\ \hat\beta)}$$

$\text{Cov}(\hat\gamma_{Mj}, \hat\beta)$ is evaluated by numerical integration (Monte Carlo, $n_{MC} = 10^5$); no further approximation is made.

**Terminology.** Because this last step is evaluated numerically rather than in closed form, the result is **semi-analytic**, not closed-form. The wording throughout the manuscript and supplements is "semi-analytic"; the "closed-form" phrasing used in an earlier version was an overstatement and is corrected here.

**Boundary condition.** $n_s = 0 \Rightarrow \text{Cov}_{\text{shared}} = 0$ (algebraically exact).

### S2.5 Proposition: the sign of the shared-instrument covariance

For any shared SNP $j\in\mathcal{S}$, with $Z=\hat\gamma_{Mj}$, $W=\hat\gamma_{Yj}\perp Z$, $B'=\sum_{k\neq j}\hat\gamma_{Mk}\hat\gamma_{Yk}/\sigma^2_Y$ (so $E[B']=(p_M-1)\mu_M\mu_Y/\sigma^2_Y$) and $C=A^{(-j)}_\beta$ independent of $Z$, we have $\hat\beta=(ZW/\sigma^2_Y+B')/(Z^2/\sigma^2_Y+C)$ and

$$\text{Cov}(Z,\hat\beta)=\mu_Y\,\text{Cov}\!\left(Z,\frac{Z/\sigma^2_Y}{A_\beta}\right)+E[B']\,\text{Cov}\!\left(Z,\frac{1}{A_\beta}\right).$$

**Proposition.** *Under A1–A3, if (i) $p_M\ge 3$, then $\text{sign}\big(\text{Cov}_{\text{shared}}(\hat\alpha,\hat\beta)\big) = -\text{sign}(\hat\alpha\hat\beta)$; consequently the correction term $2\hat\alpha\hat\beta\,\text{Cov}_{\text{shared}}$ is negative for both same-sign and opposite-sign mediation.*

*Proof.* Because $A_\beta=Z^2/\sigma^2_Y+C$ with $Z\perp C$, $A_\beta$ is strictly increasing in $|Z|$, so $\text{Cov}(Z,1/A_\beta)<0$; and $\text{Cov}(Z, Z/A_\beta)>0$ since $z\mapsto z/(z^2/\sigma^2_Y+C)$ is odd and increasing near the origin. The two terms are weighted by $\mu_Y$ and by $E[B']=(p_M-1)\mu_M\mu_Y/\sigma^2_Y$, whose ratio satisfies

$$\frac{E[B']}{\mu_Y}=\frac{(p_M-1)\mu_M}{\sigma^2_Y}=(p_M-1)\sqrt{F\,N_M}\gg 1$$

for any realistic $p_M\ge 3$ (instrument strength $F\gtrsim 10$, sample size $N_M\gg 1$). Writing the $\mu_Y$-independent bracket as $K=\text{Cov}(Z,Z/A_\beta)+\frac{(p_M-1)\mu_M}{\sigma^2_Y}\text{Cov}(Z,1/A_\beta)$, dominance gives $K<0$, hence

$$\text{Cov}(Z,\hat\beta)=\mu_Y\cdot K,\qquad \text{sign}\big(\text{Cov}(Z,\hat\beta)\big)=-\text{sign}(\mu_Y).$$

Taking $\mu_M>0$ as the reference direction for the instrument's effect on the mediator, the causal parameterisation gives $\alpha=\mu_M/\mu_X$ and $\beta=\mu_Y/\mu_M$, so $\text{sign}(\mu_X)=\text{sign}(\alpha)$ and $\text{sign}(\mu_Y)=\text{sign}(\beta)$. With the prefactor $n_s\,E[1/A_\alpha]/\sigma^2_M>0$,

$$\text{sign}\big(\text{Cov}_{\text{shared}}\big)=\text{sign}(\alpha)\cdot\big(-\text{sign}(\beta)\big)=-\text{sign}(\alpha\beta),$$

so $2\alpha\beta\,\text{Cov}_{\text{shared}}<0$ **irrespective of whether the mediation is same-signed or opposite-signed**. ∎

**Remark S2.5a (the earlier "sign reversal" claim is withdrawn).** A previous version of this supplement asserted that the covariance sign "can reverse only under opposite-sign (suppressor) mediation". That assertion was an artefact of holding $\mu_Y>0$ while allowing $\beta<0$ — an internally inconsistent combination, because $\beta=\mu_Y/\mu_M$ forces $\mu_Y<0$ whenever $\beta<0$. Once $\mu_Y$ carries $\text{sign}(\beta)$, the alleged reversal disappears: the shared-instrument channel always *narrows* the interval.

**Remark S2.5b (the $\rho_{MY}$ channel is separate and not sign-definite).** The sample-overlap channel contributes $\text{Cov}_\rho=n_s\,\rho_{MY}\,\mu_X\mu_M/(\sigma_M\sigma_Y)\cdot E[1/A_\alpha]E[1/A_\beta]$, whose correction term carries sign $\text{sign}(\beta)\cdot\rho_{MY}$ and is in principle positive. The two channels must be reported separately; they were conflated in an earlier version of Fig. S3. In every configuration examined (main-text §3.1 and §3.5, and the regime map of §3.8) the shared channel dominates and the *total* correction remains negative, but the $\rho_{MY}$ channel is not claimed to be sign-definite in general.

**Consequence.** The corrected indirect-effect variance is
$$\text{Var}(\hat\alpha\hat\beta)\approx\beta^2\text{Var}(\hat\alpha)+\alpha^2\text{Var}(\hat\beta)+2\hat\alpha\hat\beta\,\text{Cov}(\hat\alpha,\hat\beta).$$
By Remark S2.5a the term $2\hat\alpha\hat\beta\,\text{Cov}_{\text{shared}}$ is negative for **both** same-sign and opposite-sign mediation, so the corrected SE is strictly smaller than the naive delta-method SE in either case: the naive estimator is conservative and overstates uncertainty, and **no shared-instrument "widening" regime exists.** The empirical zero-flip finding of §3.1.1 is therefore a structural consequence of the shared-instrument denominator term, not a coincidence of the sampled studies. The correction nevertheless remains necessary, because its *magnitude* is not bounded away from zero — §3.8 shows that in high-overlap designs the naive interval is up to ~65% wider than the true sampling variability of $\hat\alpha\hat\beta$, so ignoring the covariance costs power rather than validity. See Remark S2.5b for the separate $\rho_{MY}$ channel.

---

## S3. The sample-overlap channel: $\text{Cov}_\rho(\hat\alpha, \hat\beta)$

### S3.1 Assumptions

**A4 (sample-overlap structure).** The M-GWAS and Y-GWAS share $n_{MY}$ individuals; define the overlap coefficient $\rho_{MY}=n_{MY}/\sqrt{N_M N_Y}$, so that for a shared SNP $j\in\mathcal{S}$,
$$\text{Cov}(\hat\gamma_{Mj},\ \hat\gamma_{Yj}) = \rho_{MY}\,\sigma_M\,\sigma_Y.$$

**A5 (transmission condition).** $n_s>0$ — this channel *requires* shared SNPs as carriers. When $n_s=0$ the channel does not exist (boundary condition below).

### S3.2 Delta-method expansion

For a shared SNP $j \in \mathcal{S}$,
$$\frac{\partial\hat\alpha}{\partial\hat\gamma_{Mj}} \approx \frac{\mu_X}{\sigma^2_M\,E[A_\alpha]}, \qquad \frac{\partial\hat\beta}{\partial\hat\gamma_{Yj}} \approx \frac{\mu_M}{\sigma^2_Y\,E[A_\beta]}.$$
The two derivatives act on *different* random quantities ($\hat\gamma_{Mj}$ and $\hat\gamma_{Yj}$) whose joint fluctuation is governed by A4:
$$\text{Cov}_\rho(\hat\alpha, \hat\beta) = \sum_{j \in \mathcal{S}} \frac{\partial\hat\alpha}{\partial\hat\gamma_{Mj}} \cdot \frac{\partial\hat\beta}{\partial\hat\gamma_{Yj}} \cdot \text{Cov}(\hat\gamma_{Mj}, \hat\gamma_{Yj}),$$
$$\boxed{\text{Cov}_\rho(\hat\alpha, \hat\beta) = n_s\,\rho_{MY}\,\frac{\mu_X \mu_M}{\sigma_M \sigma_Y\,E[A_\alpha]\,E[A_\beta]}}$$

### S3.3 The two channels do not double-count

- The **shared-SNP channel** is driven by $\text{Var}(\hat\gamma_{Mj})=\sigma^2_M$ — the M-GWAS internal variance of the *same* random variable influencing both estimators.
- The **$\rho_{MY}$ channel** is driven by $\text{Cov}(\hat\gamma_{Mj},\hat\gamma_{Yj})=\rho_{MY}\sigma_M\sigma_Y$ — the joint fluctuation of *two different* random variables (M-GWAS and Y-GWAS).

In the Taylor expansion these correspond to $(\partial\hat\alpha/\partial\hat\gamma_{Mj})^2\,\text{Var}(\hat\gamma_{Mj})$ and $(\partial\hat\alpha/\partial\hat\gamma_{Mj})(\partial\hat\beta/\partial\hat\gamma_{Yj})\,\text{Cov}(\hat\gamma_{Mj},\hat\gamma_{Yj})$ respectively; they are algebraically disjoint and are **not double-counted**.

---

## S4. Precision diagnostics: where the first-order approximation holds

The first-order delta-method error has two independent sources.

### S4.1 Shared-instrument channel

$$\kappa_1 = \frac{\text{Var}[A_\beta]}{(E[A_\beta])^2} = \frac{4\mu_M^2 v_M + 2v_M^2}{p_M(\mu_M^2 + v_M)^2}, \qquad v_M = (0.3\mu_M)^2 + \sigma^2_M,$$
is the Jensen correction to $1/A_\beta$: $E[1/A_\beta] - 1/E[A_\beta] \approx \kappa_1/E[A_\beta]$.

**Thresholds.** $\kappa_1 < 0.03$ (low risk), $0.03 \le \kappa_1 < 0.05$ (moderate), $\kappa_1 \ge 0.05$ (high).

### S4.2 Sample-overlap channel

$$\kappa_2 = \frac{|\rho_{MY}|}{\sqrt{F}}$$
measures the relative shift of $E[\hat\beta]$ induced by $\rho_{MY}$: $\delta E[\hat\beta] \approx \kappa_2\,\mu_Y/\mu_M$.

**Thresholds.** $\kappa_2 < 0.05$ (low risk), $0.05 \le \kappa_2 < 0.10$ (moderate), $\kappa_2 \ge 0.10$ (high).

### S4.3 Numerical validation

| $F$ | $\rho_{MY}$ | $\kappa_1$ | $\kappa_2$ | Observed error | Risk |
|---|---|---|---|---|---|
| 30 | 0 | 0.021 | 0.000 | <6% | low |
| 30 | 0.5 | 0.021 | 0.091 | 4% | moderate |
| 30 | 0.8 | 0.021 | 0.146 | 11% | high |
| 10 | 0 | 0.029 | 0.000 | <8% | low |
| 10 | 0.5 | 0.029 | 0.158 | 5% | high |
| 10 | 1.0 | 0.029 | 0.316 | 30% | high |

---

## S5. Consistency with the existing literature

### S5.1 Lin et al. (2025) as a special case

Setting $\pi_s = 0$ ($n_s = 0$) and $\rho_{MY} = 0$ gives
$$\text{Cov}_{\text{shared}} = 0,\quad \text{Cov}_\rho = 0 \implies \text{Cov}(\hat\alpha, \hat\beta) = 0,$$
so $\text{Var}(\hat\alpha\hat\beta)$ reduces to the additive delta-method expression assumed by Lin et al. (2025). Our formula **recovers that framework exactly** in the independent three-sample case. ✓

### S5.2 Burgess et al. (2017) single-step covariance

Burgess et al. (2017) treat the covariance *within* a single IVW estimator (the same set of $\gamma_{Mj}$ and $\gamma_{Yj}$), i.e. the variance structure of $\hat\beta$ itself (including the $\rho_{MY}$ correction). Our $\text{Cov}(\hat\alpha,\hat\beta)$ is a **cross-step** covariance — an extension of the Burgess et al. (2017) framework — which degenerates to zero when $\pi_s=0$ (the two step estimates become independent), consistent with their assumptions. ✓

### S5.3 Analogy with the difference method

When Lin et al. (2025) discuss the difference method ($\hat\tau=\hat\delta_1-\hat\delta_2$), $\text{Cov}(\hat\delta_1,\hat\delta_2)$ arises because both regressions reuse the *same* full instrument set — a **structural sharing**. Our shared-SNP channel is analogous but produces covariance only for SNPs in $\mathcal{S}$: the two designs are closest at $\pi_s=1$ (complete overlap), whereas at $\pi_s=0$ our channel vanishes while the difference method retains a covariance (its instrument sets fully coincide). The two are therefore **not interchangeable**, and no sign transfer between them should be assumed. ✓

---

## S6. Validating the full indirect-effect variance: beyond Cov(α̂, β̂)

### S6.0 Motivation

S1–S5 derive and validate the semi-analytic expression for $\text{Cov}(\hat\alpha,\hat\beta)$ (validation A: relative error <20% in 10/10 non-zero cases). The full indirect-effect variance,
$$\text{Var}(\hat\alpha\hat\beta) \approx \beta^2\text{Var}(\hat\alpha) + \alpha^2\text{Var}(\hat\beta) + 2\alpha\beta\,\text{Cov}(\hat\alpha,\hat\beta),$$
additionally requires accurate expressions for $\text{Var}(\hat\alpha)$ and $\text{Var}(\hat\beta)$ themselves, which had not previously been checked independently. This section supplies that check and identifies, derives and validates two previously omitted analytic terms.

### S6.1 Omitted term 1 — the full-variance decomposition of the ratio estimator

#### S6.1.1 Problem

The conditional variance $\text{Var}(\hat\alpha\mid\hat\gamma_X)$ satisfies (from S1)
$$\text{Var}(\hat\alpha\mid\hat\gamma_X) = \frac{v_M}{\sigma_M^2\,A_\alpha}.$$
Earlier implementations used only $E_{\hat\gamma_X}[\text{Var}(\hat\alpha\mid\hat\gamma_X)] \approx (v_M/\sigma_M^2)E[1/A_\alpha]$ as the full approximation to $\text{Var}(\hat\alpha)$. The law of total variance requires
$$\text{Var}(\hat\alpha) = \underbrace{E\!\left[\text{Var}(\hat\alpha\mid\hat\gamma_X)\right]}_{\text{implemented}} + \underbrace{\text{Var}\!\left(E[\hat\alpha\mid\hat\gamma_X]\right)}_{\text{previously omitted}}.$$
The second term had been dropped entirely; numerically its magnitude is comparable to the first (it is not a negligible higher-order correction).

#### S6.1.2 Derivation of the second term

With $S_1=\sum_{j\in G_X'}\hat\gamma_{Xj}$ and $S_2=\sum_{j\in G_X'}\hat\gamma_{Xj}^2$, we have $E[\hat\alpha\mid\hat\gamma_X]=\mu_M S_1/S_2$ (using $A_\alpha=S_2/\sigma_M^2$). Expanding $S_1/S_2$ by the delta method ($\hat\gamma_{Xj}\overset{iid}{\sim}N(\mu_X,v_X)$, $v_X=(0.3\mu_X)^2+\sigma_X^2$, $Q_X=\mu_X^2+v_X$):
$$\boxed{\text{Var}\!\left(E[\hat\alpha\mid\hat\gamma_X]\right) = \frac{\mu_M^2}{p_X}\left[\frac{v_X}{Q_X^2} - \frac{4\mu_X^2 v_X}{Q_X^3} + \frac{\mu_X^2(4\mu_X^2v_X+2v_X^2)}{Q_X^4}\right]}$$

#### S6.1.3 Numerical validation

The first term was verified by conditional simulation (fixing $\hat\gamma_X$ and re-randomising only $\hat\gamma_M$; $n=20000$, theory/simulation ratio 1.03), and the closed form for the second term by an independent simulation (ratio 0.98). Combined, under a common independent-prior DGP:

| $F$ | Full expression (both terms) | Simulated (marginal, $n=15000$) | Full / simulated |
|---|---|---|---|
| 10 | 0.012892 | 0.013310 | 0.969 |
| 30 | 0.009421 | 0.009641 | 0.977 |

($p_X=20$, $N=50000$ standard configuration.) The old expression using only the first term systematically underestimates, by a factor of ~3–6 (ratios 0.32 and 0.16); the full expression agrees to >0.96. The corresponding second term for $\text{Var}(\hat\beta)$ is isomorphic ($X\to M$, $M\to Y$).

### S6.2 Omitted term 2 — variance compression of $\text{Var}(\hat\beta)$ under sample overlap

#### S6.2.1 Problem

M-GWAS/Y-GWAS overlap ($\rho_{MY}$) had been modelled only as an independent channel affecting $\text{Cov}(\hat\alpha,\hat\beta)$ (S3). But $\rho_{MY}$ also changes the magnitude of $\text{Var}(\hat\beta)$ *itself*; the earlier expression had no $\rho_{MY}$ dependence at all.

#### S6.2.2 Mechanism and derivation

Write $\hat\gamma_{Yk}=\hat\gamma_{Yk}^{true}+\rho_{MY}(\sigma_Y/\sigma_M)\varepsilon_{Mk}+\sqrt{1-\rho_{MY}^2}\,\sigma_Y z_k$, where $\varepsilon_{Mk}$ is the measurement-error component of $\hat\gamma_{Mk}$. Conditioning on $\hat\gamma_{Mk}$ (with $\hat\gamma_{Mk}=\gamma_{Mk}^{true}+\varepsilon_{Mk}$, independent components of variances $s_M^2=(0.3\mu_M)^2$ and $\sigma_M^2$), the standard conditional-normal result gives $\text{Var}(\varepsilon_{Mk}\mid\hat\gamma_{Mk}) = \sigma_M^2 s_M^2/v_M$ (a constant), so the conditional variance $\text{Var}(\hat\gamma_{Yk}\mid\hat\gamma_{Mk})$ is compressed from $v_Y$ to
$$\boxed{v_Y' = v_Y - \rho_{MY}^2\,\sigma_Y^2\,\frac{\sigma_M^2}{v_M}}$$
and the conditional mean $E[\hat\gamma_{Yk}\mid\hat\gamma_{Mk}]$ is linear in $\hat\gamma_{Mk}$ with slope $\rho_{MY}\sigma_M\sigma_Y/v_M$, so the coefficient $\mu_Y$ in the S6.1 second-term formula becomes
$$\mu_Y' = \mu_Y - \rho_{MY}\,\sigma_M\sigma_Y\,\frac{\mu_M}{v_M}.$$
The full $\text{Var}(\hat\beta)$ expression is the S6.1 two-term formula with $v_Y\to v_Y'$ and $\mu_Y\to\mu_Y'$.

#### S6.2.3 Numerical validation

Isolated setting ($n_s=0$ to exclude the shared-SNP channel; $F=30$, $p_M=20$, $N=50000$):

| $\rho_{MY}$ | Old (no $\rho$ correction) theory/sim | New (with $\rho$ correction) theory/sim |
|---|---|---|
| 0.0 | 1.02 | 1.02 |
| 0.5 | 0.90 | 1.02 |
| 1.0 | 0.78 | 1.02 |

The new expression is uniformly accurate; the old one systematically overestimates $\text{Var}(\hat\beta)$ as $\rho_{MY}$ grows (up to 22%).

### S6.3 Combined validation of $\text{Var}(\hat\alpha\hat\beta)$

With both S6.1 and S6.2 in place, over the grid $F\in\{10,30\}\times\rho_{MY}\in\{0,0.5,1.0\}\times\pi_{shared}\in\{0.1,0.3,0.7,1.0\}$ (24 combinations; $n_{reps}=15000$; $\hat\alpha,\hat\beta$ simulated directly with a single data-generating process throughout, no closed-form shortcuts):

| Version | Mean relative error | Max relative error |
|---|---|---|
| Standard delta method (S1–S5 covariance + uncorrected marginal variances, $\text{Var}(\hat\alpha)\approx E[1/A_\alpha]$) | 93.0% | 145.7% |
| + S6.1 (second full-variance term) | 10.7% | 34.2% |
| + S6.1 + S6.2 | 4.8% | 13.3% |
| + S6.1 + S6.2 + Jensen correction ($E[1/A]\approx 1/E[A]+\text{Var}(A)/E[A]^3$) | **4.1%** | **12.5%** |

The maximum error occurs where weak instruments ($F<15$) coincide with high shared-instrument proportion ($\pi_{shared}>0.5$); in that corner we recommend a parametric simulation cross-check (the bootstrap fallback in the deposited code) rather than reliance on the analytic expression alone.

### S6.4 Relation to S1–S5

The two corrections above **do not affect** the semi-analytic expression for $\text{Cov}(\hat\alpha,\hat\beta)$ itself (the boxed results of S2.4 and S3.2, and the 10/10 result of validation A, are unchanged). Under the standard assumptions (independent M- and Y-GWAS priors, A1–A3), $E[\hat\beta\mid\hat\gamma_X]$ does not depend on $\hat\gamma_X$, so the corresponding cross-term in the full covariance is identically zero. S6.1 and S6.2 concern $\text{Var}(\hat\alpha)$ and $\text{Var}(\hat\beta)$ *individually*; they are orthogonal to the cross-step covariance mechanism and supplement, rather than amend, the core contribution of S1–S5.

### S6.5 Sampling noise of the Taylor anchor

The validations of S6.1–S6.3 used the batch-mean of the simulated estimates ($\overline{\hat\alpha}$, $\overline{\hat\beta}$, $n_{reps}=15000$) as the Taylor anchor. In real applications only the **single point estimate** reported by one paper is available as an anchor, and whether substituting it introduces bias had not been checked.

**Check.** For four representative configurations, each replicate's own $\hat\alpha$/$\hat\beta$ was used as the anchor and compared with the batch-mean anchor.

**Result.** Using the single point estimate as anchor **does not introduce systematic bias**; on the four configurations it is in fact slightly more accurate (relative error 1.0–2.6% versus 2.2–4.1% for the batch-mean anchor). This is expected: the single-point anchor corresponds to taking the expectation of the exact joint-normal product variance under its true sampling distribution, which is unbiased, whereas the finite-batch mean is only an approximation to that expectation.

**Caveat (for the Limitations).** Although unbiased on average, the *spread* for any single application is substantial: across the four configurations the 5–95% interval of the output spans roughly ±25% to ±35% of the mean (e.g. $F=10$, $\rho=0$, $\pi=0.7$: $[0.0107,\,0.0187]$ around a mean of 0.014422). This spread is pure sampling noise of the point estimate, independent of — and additive to — the systematic error of the delta-method expression itself (S6.3: 4.1% mean / 12.5% max with the Jensen correction). The tool's output for $\text{Var}(\hat\alpha\hat\beta)$ is therefore unbiased but, for any single paper, carries more uncertainty than the formula error alone; it should be read as **the centre of a plausible range, not an exact value.**
