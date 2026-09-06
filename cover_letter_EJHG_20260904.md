# Cover Letter — Draft for Zone-2 Submission

**Target journal (first choice):** *European Journal of Human Genetics* (EJHG; CAS 2025 升级版: 大类 生物学 2区 / 小类 遗传学 2区; JCR Q1 GENETICS & HEREDITY; IF ≈ 4.6; non-OA subscription, no APC — fits provincial-funding constraint). EJHG's scope explicitly includes *Statistical and computational genetics*, the natural home for a closed-form MR-method derivation.
**Within-Q2 genetics alternative:** *Journal of Medical Genetics* (CAS 2025: 大类 医学 2区 / 小类 遗传学 2区; JCR Q2; IF ≈ 3.4; non-OA).
**Q2 general-epidemiology fall-back:** *American Journal of Epidemiology* / *Epidemiology* (both 2区, non-OA).
**Q3 methods fall-back:** *Statistics in Medicine* / *Genetic Epidemiology* (3区, best methods-reviewer fit — only if a Q2 venue declines).

---

Dear Dr. Alisdair McNeill, Editor-in-Chief, *European Journal of Human Genetics*,

Editorial Office, European Journal of Human Genetics, University of Sheffield, Sheffield, UK (EJHG@sheffield.ac.uk)

We submit our manuscript entitled **"Correcting for instrument overlap in two-step summary-data Mendelian randomization mediation"** for consideration as an Original Article in the *European Journal of Human Genetics*.

**What the paper does.** Two-step (product-method) MR mediation is now widely used across human and statistical genetics, yet it inherits a standard but routinely unchecked assumption: that the exposure-step and mediator-step instrument sets are independent. We derive the **first closed-form expression for Cov(α̂, β̂) under instrument overlap or mediator–outcome sample overlap**, closing the open gap that Lin *et al.* (2025, *Statistics in Medicine*) explicitly left for the product method. The correction is exactly zero when instruments are disjoint, reduces to the Lin *et al.* independent-sample expression under three independent samples, and becomes material whenever instruments are shared or samples overlap. We further prove a structural consequence (Proposition S2.5): whenever α̂ and β̂ share a sign — the typical mediation configuration — the shared-instrument covariance is provably negative, so the naive delta-method SE is conservative rather than anti-conservative.

**Why it is of interest to your readership (statistical & computational genetics).**
1. **A closed-form solution to a known open problem.** Lin *et al.* (2025) derived the independent-sample case and flagged the overlapping-instrument covariance for the product method as unsolved. We close it analytically and validate the correction across 192 simulation cells (conservative SE coverage restored; a Monte-Carlo fallback covers the weak-instrument corner).
2. **A field audit quantifying prevalence.** Screening 333 published two-step MR mediation studies, **39.3%** use an instrument-selection design capable of producing non-independent (α̂, β̂); a batch re-estimation resolving 42 trios to public GWAS accessions confirmed genuine SNP overlap in **19.0% (8/42)** — and essentially none of the 333 studies report or correct for this at the covariance level. This is, to our knowledge, the first quantification of how prevalent the problem is in the published literature.
3. **Honest empirical result, with the missing piece filled.** Applying the correction to the adequately powered overlapping trios we could recover and validate through the standard TwoSampleMR R package (4 of 6 identified; 2 FinnGen-outcome trios were not allele-harmonisable), the correction *narrowed* every confidence interval (mean −3.9%, range −9.0% to −0.1%) with **zero significance flips**. Crucially, we went beyond treating ρ_MY as an assumed-zero sensitivity parameter: we estimated it empirically for **all six** overlapping trios directly from the harmonized GWAS effect sizes. Five of six showed positive mediator–outcome genetic concordance (up to +0.81) and four drew both mediator and outcome from UK Biobank–derived GWAS (substantial sample overlap) — yet re-entering these empirical values into the correction changed the corrected SE by at most 0.40 percentage points and preserved the narrowing with zero flips, even under a worst-case substitution using each trio's ρ_MY 95% CI upper bound. The benign direction is thus a *documented structural property* (the dominant shared-instrument covariance is negative regardless of ρ_MY sign), not good fortune.
4. **A usable, released remedy.** We provide a diagnostic tool (`estimate_cov_prod_mr()`) with conservative reliability bounds, released as TwoSampleMR-compatible R and ieugwasr-compatible Python wrappers, so analysts can compute n_s from published summary statistics and apply the correction without full reanalysis.

**Fit.** EJHG's scope explicitly includes statistical and computational genetics; a closed-form correction for a widely used MR-mediation design — accompanied by a published prevalence audit and a released, validated tool — sits squarely within that remit. The manuscript is submitted as a non-OA (subscription) article with no open-access fee requested; all code and GWAS accessions are publicly available.

We declare no competing interests. We suggest [X, Y] as potential reviewers. Thank you for your consideration.

Sincerely,
Yan Chen, Jianfeng Wang
Department of General Practice / Respiratory Medicine, First Affiliated Hospital of Zhejiang Chinese Medical University (Zhejiang Provincial Hospital of Chinese Medicine)

---

*Note (internal): adapt the editor address per the chosen venue. The "39.3% / 19.0% / 4-of-6" figures must stay exactly as in the manuscript. If switching to *Journal of Medical Genetics*, keep the same derivation-led framing (JMG also publishes statistical-genetics methods). If switching to *American Journal of Epidemiology* / *Epidemiology*, re-lead with the field-audit prevalence (point 2). *Statistics in Medicine* / *Genetic Epidemiology* are the Q3 methods fallback only.*
