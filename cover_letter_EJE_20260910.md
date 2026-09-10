# Cover Letter — *European Journal of Epidemiology* (EJE)

**Target journal:** *European Journal of Epidemiology* (EJE; Springer; CAS 2025 大类 医学 2区 / 小类 公共卫生与流行病学 2区; JCR Q1; IF 6.6 (2025), 5-year 8.8; **Hybrid — no APC under the subscription model**, which fits the provincial-funding constraint). Submission to first decision (median): 8 days.

**Why EJE:** scope explicitly covers "epidemiologic and **statistical methods**" and the journal "publishes ... **methodological developments**"; EJE also maintains an ongoing open collection on **Epidemiologic Methods** ("novel epidemiologic methods and updates on methodological topics"), which is the exact category of this manuscript.

---

Dear Professor Hofman, Editor-in-Chief, *European Journal of Epidemiology*,

We submit our manuscript entitled **"Correcting for instrument overlap in two-step summary-data Mendelian randomization mediation: a closed-form covariance and its empirical prevalence"** for consideration as an **Original Article** in the *European Journal of Epidemiology*.

**Why this manuscript fits EJE.** EJE is dedicated to all fields of epidemiologic research *and to epidemiologic and statistical methods*, and it publishes methodological developments. Our paper reports a methodological development that is immediately applicable to a design now used in hundreds of published studies, and it is, to our knowledge, the first quantification of how prevalent the underlying problem is. Specifically: (i) a **systematic literature audit** (PRISMA 2020 flow; 695 records screened → 333 coded two-step MR mediation studies) showing that **39.3% (95% CI 34.2–44.7%)** use an instrument-selection design capable of violating the independence assumption, with essentially none reporting or correcting for the induced covariance; (ii) a **closed-form derivation** of the omitted Cov(α̂, β̂) for the product estimand under two overlap channels, validated on a 180-cell simulation grid and a 200-cell flip-probability scan, with a conservative reliability bound and a Monte-Carlo fallback for the weak-instrument corner; and (iii) an **empirical application** re-estimating 108 trios directly from public GWAS summary statistics. The paper is a documented design vulnerability plus a usable remedy — **not** a claim that any specific published conclusion is wrong.

**What the paper does, point by point.**

1. **A closed-form solution to an explicitly open problem.** Lin *et al.* (2025, *Statistics in Medicine*) derived the independent-sample case for summary-data MR mediation and flagged the overlapping-instrument covariance for the product method as unsolved. We close it analytically and show the correction restores nominal coverage across the simulation grid.
2. **The first field-level quantification.** 39.3% of 333 audited studies can produce non-independent (α̂, β̂); batch re-estimation of 113 resolvable trios (108 succeeded) found genuine SNP overlap in **6.5% (95% CI 3.2–12.8%; 7/108)**. Overlap handling was assessable in only 54/333 studies, of which 19 (35.2%) reported or adjusted for it.
3. **An honest empirical result, with its imprecision stated.** In the five non-degenerate overlapping trios the correction narrowed every confidence interval (0.2–16.0%) with **zero significance flips**. We report explicitly that this null result is imprecise — the 95% CI for the underlying flip rate implied by 0/5 is **0–43.4%** — and must not be read as evidence that flips are rare. We further show the benign direction is a *documented structural property* (the dominant shared-instrument covariance is negative when α̂ and β̂ share a sign), not good fortune, and that the opposite regime — discordant mediation or mediator–outcome sample overlap — makes the uncorrected interval anti-conservative, with flip probability up to **10.4%**.
4. **Actionable guidance and a released tool.** Because the sign of the covariance cannot be anticipated, the correction should be routine rather than conditional on an expected direction. We give an explicit decision rule (n_s, π_shared, ρ_MY) and release `estimate_cov_prod_mr()` with TwoSampleMR-compatible R and ieugwasr-compatible Python wrappers, so the correction can be applied from published summary statistics without full reanalysis. We also estimated ρ_MY empirically (5/6 positive, up to +0.81) rather than assuming it zero.

**Limitations we disclose up front.** The real-data re-estimation is restricted to the subset resolvable to public, EUR-clumped GWAS accessions and is therefore a lower-bound characterization of the resolvable, EUR-ancestry literature rather than an estimate generalizable to the full audited corpus. Inter-coder reliability comes from a second blinded coding pass by co-author C. Yan (C.Y.), independent of the original coder (J.W., excluded) and blind to the sealed answer key and hypothesis — not from a fully independent external rater (100% observed agreement on `design_type`; κ = 0.44 on `IV_selection_strategy`; κ = 0.78 on `reports_overlap_risk`). The blind re-coding template, sealed answer key, filled sheet and `compute_kappa_2nd.py` are deposited so an independent collaborator can reproduce or supersede this κ in one command. The audit searched PubMed only. We note that the lower-reliability field carries no reported result: the 39.3% headline rests only on `design_type` (complete agreement) and on the *absence* of overlap-handling disclosure, so it is conservative with respect to coding error.

**Accompanying items.** Completed PRISMA 2020 checklist (Supplementary Table S3); STROBE-MR reporting checklist; Supplementary Methods S1–S9 and Supplementary Tables S1, S6; figures supplied as vector PDF; code and data deposited in a public GitHub repository. We request publication under the **subscription model (no APC)**.

We declare no competing interests. Thank you for your consideration.

Sincerely,
Yan Chen, Jianfeng Wang
Department of General Practice / Department of Respiratory Diseases, The First Affiliated Hospital of Zhejiang Chinese Medical University (Zhejiang Provincial Hospital of Chinese Medicine), Hangzhou, China
Correspondence: Jianfeng Wang — 2001m@163.com

---

*Internal notes (verify before submission):*
1. EiC confirmed as **Albert Hofman, MD, PhD** (Erasmus MC, Rotterdam; Harvard University) from the EJE masthead, September 2026.
2. EJE requires a structured abstract of 150–250 words — our abstract is **238 words** with Background / Methods / Results / Conclusions. Keywords: 6 (EJE requires 4–6).
3. EJE has **no stated word limit for Original Articles** (limits apply only to Short Communications, 2000 words, and Letters, 1000 words). Current main text is ~5,660 words; expect a possible request to shorten at revision.
4. Do **not** include Highlights or a Graphical Abstract — those are Elsevier/JCE requirements, not EJE.
5. The "39.3% / 6.5% / 0–43.4% / 10.4%" figures must stay exactly as in the manuscript.
6. Replace the Zenodo DOI placeholder `10.5281/zenodo.XXXXXXX` in Data availability with the minted DOI once available.
7. If suggesting reviewers is permitted, add 2–3 names with affiliation and e-mail before submission; consider MR-methods researchers not connected to the authors' institution.
