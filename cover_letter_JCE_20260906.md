# Cover Letter — *Journal of Clinical Epidemiology* (JCE)

**Target journal (first choice):** *Journal of Clinical Epidemiology* (JCE; CAS 2025 升级版: 大类 医学 2区 / 小类 公共卫生/流行病学 2区; JCR Q1 HEALTH CARE SCIENCES & SERVICES; IF ≈ 6.4; mixed OA, no APC if non-OA chosen — fits provincial-funding constraint). JCE's stated scope — "Metascience and innovative methods to improve population health" — explicitly welcomes evidence syntheses, simulation studies, and methods-focused articles, which are exactly the three components of this manuscript.

**Within-Q2 epidemiology / methods alternatives (if JCE declines):** *PLoS Genetics* (Forde 2026 precedent, direct competitor-adjacent) → *European Journal of Epidemiology* → *International Journal of Epidemiology*. *Statistics in Medicine* / *Genetic Epidemiology* retained as methods-reviewer-fit fall-backs.

---

Dear Professors Andrea Tricco and David Tovey, Editors-in-Chief, *Journal of Clinical Epidemiology*,

Editorial Office, Journal of Clinical Epidemiology, Elsevier Inc.

We submit our manuscript entitled **"Correcting for instrument overlap in two-step summary-data Mendelian randomization mediation: a closed-form covariance and its empirical prevalence"** for consideration as an Original Article in the *Journal of Clinical Epidemiology*.

**Why this manuscript fits JCE's mandate.** Your Instructions for Authors identify evidence syntheses, simulation studies, and methods-focused articles as welcomed contribution types. Our paper is structured around exactly these three: (i) a **systematic literature audit** (PRISMA 2020 flow; 695 records screened → 333 coded two-step MR mediation studies) quantifying how often the field uses an instrument-selection design capable of violating the independence assumption (39.3% [95% CI 34.2–44.7%]); (ii) a **simulation study** (180-cell coverage/MSE grid plus a 200-cell flip-probability scan) validating a closed-form correction and characterising the exact boundary conditions under which the omitted covariance overturns a conclusion; and (iii) a **methods-focused article** deriving the first closed-form Cov(α̂, β̂) for the two-step mediation product estimand, with a conservative reliability bound and a released, validated tool. The contribution is therefore a documented methodological vulnerability in a widely used design — and a reporting-infrastructure remedy — rather than a claim that any specific published clinical conclusion is wrong.

**What the paper does, point by point.**
1. **A closed-form solution to an open problem.** Lin *et al.* (2025, *Statistics in Medicine*) derived the independent-sample case and flagged the overlapping-instrument covariance for the product method as unsolved. We close it analytically and validate the correction across 180 simulation cells (conservative SE coverage restored; a Monte-Carlo fallback covers the weak-instrument corner).
2. **A field audit quantifying prevalence.** Screening 333 published two-step MR mediation studies, **39.3% (95% CI 34.2–44.7%)** use an instrument-selection design capable of producing non-independent (α̂, β̂); a batch re-estimation resolving 113 coded trios to public GWAS accessions (108 succeeded) found genuine SNP overlap in **6.5% (95% CI 3.2–12.8%; 7/108)** — and essentially none of the 333 studies report or correct for this at the covariance level. This is, to our knowledge, the first quantification of how prevalent the problem is in the published literature.
3. **Honest empirical result, with the sampling uncertainty stated.** Applying the correction to the five non-degenerate overlapping trios we could recover, the correction narrowed every confidence interval (0.2–16.0%) with **zero significance flips**. We report explicitly that this null result is imprecisely estimated: the 95% CI for the underlying flip rate implied by 0/5 observed flips is **0.0–43.4%**, so it should not be read as evidence that flips are rare in the wider literature. Crucially, we went beyond treating ρ_MY as an assumed-zero sensitivity parameter: we estimated it empirically for the overlapping trios directly from harmonized GWAS effect sizes (5/6 positive, up to +0.81). The benign direction is thus a *documented structural property* (the dominant shared-instrument covariance is negative when α̂ and β̂ share a sign), not good fortune.
4. **A usable, released remedy.** We provide a diagnostic tool (`estimate_cov_prod_mr()`) with conservative reliability bounds, released as TwoSampleMR-compatible R and ieugwasr-compatible Python wrappers, so analysts can compute n_s from published summary statistics and apply the correction without full reanalysis.

**Limitations we disclose up front (anticipating JCE's methods-review standards).** The real-data re-estimation is restricted to the subset resolvable to public, EUR-clumped GWAS accessions and is therefore a lower-bound characterization of the resolvable, EUR-ancestry literature, not the full audited corpus. The inter-coder reliability κ comes from a second blinded pass by the same research team, not a fully independent external rater; the blind re-coding template, sealed answer key, and `compute_kappa_2nd.py` are deposited so an independent collaborator can produce the definitive κ in one command, and arranging that rater is our stated priority before final submission.

**Fit.** JCE's mission — innovative methods that improve health-care decision-making — is served by a paper that quantifies a systematically unreported design vulnerability and supplies the reporting convention (n_s, π_shared, ρ_MY) and tool needed to detect it, rather than by a paper claiming retrospective corrections to clinical conclusions. The manuscript is submitted with no open-access fee requested; all code and GWAS accessions are publicly available.

**Accompanying submission items (JCE / Elsevier requirements).** We include (i) the JCE-required Highlights file (≤85 characters × 4 bullets); (ii) a Graphical Abstract (the conceptual Fig. 1); (iii) the completed PRISMA 2020 checklist as Supplementary Table S3; (iv) an AI-disclosure statement and a funder-no-role statement in the manuscript; and (v) a horizontal-pleiotropy sensitivity analysis (MR-Egger intercept and weighted-median on both steps of the five non-degenerate overlapping trios) in §3.4.1, confirming that no horizontal pleiotropy reverses the sign of α̂ or β̂ and that the covariance correction is robust to it.

We declare no competing interests. We suggest [X, Y] as potential reviewers. Thank you for your consideration.

Sincerely,
Yan Chen, Jianfeng Wang
Department of General Practice / Respiratory Medicine, First Affiliated Hospital of Zhejiang Chinese Medical University (Zhejiang Provincial Hospital of Chinese Medicine)

---

*Note (internal — verify before submission): (1) Confirm the current EiC names against the JCE masthead; as of the 2026 editorial the Editors-in-Chief are Andrea C. Tricco and David Tovey. (2) JCE uses a structured abstract (Objectives / Study Design and Setting / Methods / Results / Conclusion); map the manuscript's current prose abstract to those headings and confirm the word limit in the live Guide for Authors. (3) The "39.3% / 6.5% / 0–43.4%" figures must stay exactly as in the manuscript. (4) If switching to PLoS Genetics, re-lead with the Forde 2026 adjacency; if to EJE/IJE, re-lead with the field-audit prevalence.*
