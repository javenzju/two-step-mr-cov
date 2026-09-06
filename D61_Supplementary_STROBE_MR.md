# Supplementary Material S8 — STROBE-MR Reporting Checklist (adapted)

We report the present study against the STROBE-MR (Strengthening the Reporting of Observational
Studies in Epidemiology–Mendelian Randomization) checklist of Skrivankova et al. (JAMA 2021;326:1614–1621),
extended with two overlap-disclosure items (marked *) that our results show are missing from the
two-step MR mediation literature.

| # | STROBE-MR item | Recommendation | Reported in our manuscript |
|---|---------------|----------------|----------------------------|
| 1 | Title & Abstract | Identify the study as MR; summarize objectives, methods, results, conclusions in abstract. | Title; Abstract (§0) |
| 2 | Background / Rationale | Explain scientific background and rationale for the MR mediation question. | §1 Introduction |
| 3 | Objectives | State specific objectives, including the (α̂, β̂) overlap-covariance gap. | §1 (last paragraph) |
| 4 | Study design & data source | Describe design (two-step product-method MR mediation) and summary-data sources. | §2.1; Data and code availability |
| 5 | Search / screening of GWAS | Describe how GWAS were identified/selected for the 333-study screen and the 70-trio batch. | §3.1; §3.4; code/replication |
| 6 | Eligibility criteria of GWAS | Give inclusion/exclusion (e.g., EUR-clumped, OpenGWAS/FinnGen resolvable). | §3.1; §3.4 (28/70 excluded) |
| 7 | Variable selection (exposure, mediator, outcome) | Define each trait and how IVs were selected for every step. | §2.2; Table 2; §3.5 |
| 8 | Causal diagram & assumptions | Provide the DAG and state the no-overlap / no-sample-overlap assumption explicitly. | §2.2 (Fig 2); §2.3 |
| 9 | MR assumptions per path | Relevance, independence, exclusion restriction for X→M, M→Y, X→Y. | §2.2; §3.5 |
| 10 | Statistical methods — effect estimation | State IVW / product method and SE formulae. | §2.3 (Eqs 3–6); §2.4 |
| 11 | Statistical methods — mediation decomposition | Direct, indirect, total effects and their SEs. | §2.3; §2.4 (S10 correction) |
| 12 | Sensitivity / pleiotropy / heterogeneity | Pleiotropy, heterogeneity, weak-instrument, bootstrap fallback. | §2.5; §3.2 (T2, T5); Limitations |
| 13 | Software | Name packages/scripts (TwoSampleMR, ieugwasr, our tool). | Data and code availability; code/ |
| 14* | **Instrument-overlap disclosure (added)** | Report step-1 and step-2 instrument sets and their intersection n_s = \|IV₁∩IV₂\|. | §2.4; §3.3; Table 3; S1–S2 |
| 15 | Results — GWAS characteristics | Populations, sample sizes, consortia for every trait. | §3.5; Data and code availability |
| 16 | Results — descriptive (IV strength) | Number of IVs, F-statistics, clumping thresholds per step. | Table 2; Table 3; §3.5 |
| 17 | Results — X→M, M→Y, X→Y estimates | Present each path estimate with CI. | §3.5; Table 3; Fig 4 |
| 18 | Results — mediation decomposition | Indirect / direct / total with corrected CIs. | §3.5; Table 3; Fig 3; S2 |
| 19 | Results — sensitivity analyses | ρ_MY empirical substitution, upper-95% CI, bootstrap. | §3.5; Table 4 (S5); Limitations |
| 20 | Results — assessment of MR assumptions | Overlap prevalence, weak-instrument, pleiotropy checks. | §3.3; §3.6; Fig 4 |
| 21* | **Results — overlap diagnostics (added)** | Report n_s / π_shared and the corrected vs naive CI for every trio. | §3.5; Table 3; S2 |
| 22 | Discussion — key results, limits, interpretation, generalizability, funding, ethics | Summarise, state limits, funding, ethical approval. | §4; Acknowledgments; Ethical approval; Competing interests |

*Items 14 and 21 are **proposed extensions** to STROBE-MR. We recommend they become mandatory for any
multi-step MR design (two-step mediation, two-sample multivariable MR, network MR) in which the same
or overlapping instruments, or the same or overlapping samples, enter more than one estimating equation,
because without n_s (or the sample-intersection size) no reader can recover the omitted covariance term
Cov(α̂, β̂).
