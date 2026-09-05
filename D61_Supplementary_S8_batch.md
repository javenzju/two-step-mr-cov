# Supplementary Table S4. Phase-B batch re-estimation of published two-step MR mediation studies

Companion to §3.5 of the main manuscript. All numbers are taken directly from the Phase-B pipeline outputs `M4b_pishared_20260904.csv` (π_shared screen) and `M4b_stage2_recompute_20260904.csv` (per-candidate re-estimation).

## Methods summary

- **Phase A (local screen).** From the 333 two-step MR mediation studies, 70 had all three traits (exposure, mediator, outcome) resolvable to an OpenGWAS or FinnGen accession with mediator GWAS sample size N_M ≥ 20,000.

- **Phase B (REST re-estimation).** For each candidate we extracted clumped exposure and mediator instruments via the OpenGWAS `/tophits` endpoint and computed π_shared = |G_X ∩ G_M| / min(|G_X|, |G_M|). Re-estimation used `/associations` + harmonized IVW (S10 correction, ρ_MY = 0), gated by a validation check that first reproduced the D56 BMI→waist→CHD results to 2–3 decimals.

- **Sign convention.** widen_% < 0 means the S10-corrected indirect-effect SE is smaller (narrower CI) than the naive delta-method SE.

## Table S4.1. π_shared screen of all 70 Phase-A candidates

| study_id | n_X | n_M | n_shared | π_shared | F_X | status |
|---|---|---|---|---|---|---|
| S139 | 5 | 468 | 0 | 0.0 | 37.7 | 零重叠 |
| S147 | 2 | 264 | 0 | 0.0 | 44.0 | 零重叠 |
| S296 | 0 | 1 | 0 | NA | NA | 零重叠 |
| S247 | 2 | 21 | 0 | 0.0 | 46.4 | 零重叠 |
| S261 | 0 | 21 | 0 | NA | NA | 零重叠 |
| S268 | 12 | 21 | 0 | 0.0 | 54.8 | 零重叠 |
| S275 | 0 | 21 | 0 | NA | NA | 零重叠 |
| S309 | 24 | 21 | 0 | 0.0 | 82.6 | 零重叠 |
| S364 | 0 | 21 | 0 | NA | NA | 零重叠 |
| S376 | 2 | 1 | 0 | 0.0 | 44.0 | 零重叠 |
| S030 | 1 | 0 | 0 | NA | 31.1 | 零重叠 |
| S014 | 18 | 209 | 1 | 0.0556 | 178.1 | 非零重叠 |
| S260 | 5 | 209 | 0 | 0.0 | 37.7 | 零重叠 |
| S167 | 1 | 148 | 0 | 0.0 | 85.3 | 零重叠 |
| S253 | 2 | 352 | 0 | 0.0 | 44.0 | 零重叠 |
| S273 | 440 | 13 | 2 | 0.1538 | 89.5 | 非零重叠 |
| S249 | 0 | 408 | 0 | NA | NA | 零重叠 |
| S266 | 0 | 408 | 0 | NA | NA | 零重叠 |
| S282 | 0 | 408 | 0 | NA | NA | 零重叠 |
| S338 | 0 | 408 | 0 | NA | NA | 零重叠 |
| S348 | 3 | 408 | 0 | 0.0 | 104.6 | 零重叠 |
| S366 | 1 | 408 | 0 | 0.0 | 89.2 | 零重叠 |
| S370 | 2 | 408 | 0 | 0.0 | 32.3 | 零重叠 |
| S379 | 2 | 408 | 0 | 0.0 | 50.1 | 零重叠 |
| S255 | 408 | 226 | 1 | 0.0044 | 151.9 | 非零重叠 |
| S259 | 2 | 226 | 0 | 0.0 | 44.0 | 零重叠 |
| S272 | 0 | 226 | 0 | NA | NA | 零重叠 |
| S373 | 43 | 226 | 0 | 0.0 | 41.8 | 零重叠 |
| S137 | 105 | 220 | 2 | 0.019 | 213.7 | 非零重叠 |
| S314 | 21 | 114 | 0 | 0.0 | 52.7 | 零重叠 |
| S329 | 0 | 114 | 0 | NA | NA | 零重叠 |
| S263 | 9 | 1 | 0 | 0.0 | 209.3 | 零重叠 |
| S140 | 2 | 248 | 0 | 0.0 | 44.0 | 零重叠 |
| S320 | 2 | 2 | 2 | 1.0 | 32.3 | 非零重叠 |
| S333 | 12 | 2 | 0 | 0.0 | 54.8 | 零重叠 |
| S334 | 0 | 2 | 0 | NA | NA | 零重叠 |
| S217 | 9 | 10 | 1 | 0.1111 | 209.3 | 非零重叠 |
| S150 | 105 | 113 | 0 | 0.0 | 213.7 | 零重叠 |
| S353 | 0 | 113 | 0 | NA | NA | 零重叠 |
| S343 | 1 | 16 | 0 | 0.0 | 32.6 | 零重叠 |
| S179 | 0 | 57 | 0 | NA | NA | 零重叠 |
| S237 | 0 | 48 | 0 | NA | NA | 零重叠 |
| S267 | 88 | 53 | 3 | 0.0566 | 217.7 | 非零重叠 |
| S278 | 41 | 52 | 0 | 0.0 | 85.4 | 零重叠 |
| S306 | 0 | 52 | 0 | NA | NA | 零重叠 |
| S279 | 1 | 2 | 0 | 0.0 | 31.7 | 零重叠 |
| S134 | 0 | 9 | 0 | NA | NA | 零重叠 |
| S295 | 16 | 12 | 0 | 0.0 | 42.7 | 零重叠 |
| S387 | 0 | 0 | 0 | NA | NA | 零重叠 |
| S159 | 1 | 2 | 0 | 0.0 | 32.6 | 零重叠 |
| S189 | 0 | 2 | 0 | NA | NA | 零重叠 |
| S210 | 0 | 2 | 0 | NA | NA | 零重叠 |
| S246 | 0 | 2 | 0 | NA | NA | 零重叠 |
| S271 | 114 | 2 | 0 | 0.0 | 138.0 | 零重叠 |
| S281 | 0 | 2 | 0 | NA | NA | 零重叠 |
| S293 | 2 | 2 | 2 | 1.0 | 44.0 | 非零重叠 |
| S299 | 13 | 2 | 0 | 0.0 | 73.4 | 零重叠 |
| S312 | 3 | 2 | 0 | 0.0 | 77.3 | 零重叠 |
| S321 | 0 | 2 | 0 | NA | NA | 零重叠 |
| S355 | 0 | 2 | 0 | NA | NA | 零重叠 |
| S367 | 1 | 2 | 0 | 0.0 | 31.9 | 零重叠 |
| S317 | 0 | 2 | 0 | NA | NA | 零重叠 |
| S354 | 62 | 2 | 0 | 0.0 | 144.0 | 零重叠 |
| S389 | 0 | 2 | 0 | NA | NA | 零重叠 |
| S349 | NA | NA | NA | NA | NA | 暴露或中介未解析,跳过 |
| S152 | 1 | 2 | 0 | 0.0 | 31.1 | 零重叠 |
| S208 | 48 | 2 | 0 | 0.0 | 202.4 | 零重叠 |
| S244 | 13 | 2 | 0 | 0.0 | 73.4 | 零重叠 |
| S375 | 123 | 2 | 0 | 0.0 | 44.7 | 零重叠 |
| S352 | NA | NA | NA | NA | NA | 暴露或中介未解析,跳过 |

**Summary:** 70 screened; 42 analyzable (usable instruments for both exposure and mediator, n_X ≥ 1 and n_M ≥ 1); 28 not analyzable (no EUR-clumped instruments returned, predominantly non-European, UKB non-EUR, or specialized protein/QTL traits). Among the 42 analyzable, 8 (19.0%) had genuine SNP overlap (π_shared > 0); the remaining 34 used effectively disjoint instrument sets.

## Table S4.2. Re-estimation of the 4 of 6 adequately powered overlapping studies (TwoSampleMR-validated, ρ_MY = 0)

| study_id | exposure | mediator | outcome | n_X | n_M | n_shared | π_shared | α̂ (SE_α) | β̂ (SE_β) | indirect | SE_naive | SE_corr | widen_% | naive_sig | corr_sig | flip |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S014 | T1DM | hypertension | peripheral atherosclerosis(PAS)/coronary atherosclerosis(CAS) | 18 | 209 | 1 | 0.0556 | 0.00591 (0.00345) | 0.1242 (0.0112) | 7.34e-04 | 4.34e-04 | 3.95e-04 | -9.0 | 否 | 否 | 无翻转 |
| S273 | inflammatory factors / gut microbiota / blood cell traits (炎症因子/肠道菌群/血细胞, 3暴露) | immune traits (免疫性状) | IgAN (IgA nephropathy, IgA肾病) | 440 | 13 | 2 | 0.1538 | 0.00392 (0.00115) | 1.963 (1.265) | 0.00769 | 0.00545 | 0.00541 | -0.7 | 否 | 否 | 无翻转 |
| S137 | 25-hydroxyvitamin D(25(OH)D) | serum calcium(血清钙) | migraine(偏头痛) | 105 | 220 | 2 | 0.019 | 0.0221 (0.0299) | 0.00163 (0.00143) | 3.60e-05 | 5.80e-05 | 5.50e-05 | -5.9 | 否 | 否 | 无翻转 |
| S217 | rheumatoid arthritis(RA, 类风湿关节炎) | immunosuppressants(免疫抑制剂使用) | bronchiectasis(支气管扩张症) | 9 | 10 | 1 | 0.1111 | 44.853 (6.464) | 0.1986 (0.0543) | 8.908 | 2.753 | 2.750 | -0.1 | 是 | 是 | 无翻转 |

*Note:* S255 and S267 could not be re-estimated through TwoSampleMR (allele-harmonisation conflict at the FinnGen outcome GWAS; the package returned a non-finite estimate). They are not estimable through the gold-standard pipeline and excluded from the validated flip count.

---

## Table S5. Empirical ρ_MY for the six overlapping trios (companion to §3.5.1, main manuscript Table 3b)

**Why this table exists.** In the main manuscript, ρ_MY is treated as a sensitivity parameter (0 by default). A reviewer would reasonably ask what the ρ_MY distribution actually is in the real overlapping cases. This table answers that with data, using the harmonized per-SNP effect sizes already pulled by the Phase-B pipeline: β_ZM (mediator GWAS), β_ZY (outcome GWAS), and β_ZX (exposure GWAS), all aligned to the OpenGWAS reference allele.

**Estimators.**
- **ρ_g (primary)** — Pearson correlation between β_ZM and β_ZY at the instruments, reported on the larger-n instrument set (mediator instruments n_M = 10–226, or exposure instruments n_X = 9–440 where that set is larger), with Fisher-z 95% CI. This is the data-driven proxy for the M–Y association that drives the positive-ρ_MY regime. Because n_s (the shared-instrument count feeding this correlation) is only 1–3 per trio, ρ_g point estimates carry wide sampling uncertainty (e.g., S217's 95% CI spans [0.37, 0.95] from a single shared SNP's neighborhood); the M-instrument / X-instrument / residualized variants below serve as a robustness cross-check against this instability, not merely supplementary detail.
- **ρ_g (M-instruments)** and **ρ_g (X-instruments)** — the same correlation computed separately on the mediator-instrument set and the exposure-instrument set, as a robustness cross-check (the latter required one additional `/associations` pull per trio).
- **ρ_g (residualized)** — β_ZM and β_ZY each residualized on β_ZX (exposure-mediated component removed) before correlating; isolates the pleiotropic M–Y concordance.
- **Sample overlap** — the literal S10 parameter (M–Y GWAS sample-overlap proportion), classified from GWAS catalog metadata: *high* when both mediator and outcome derive from UK Biobank (ieu-b / ebi-a / ukb-d accessions), *≈ 0* when the outcome is a FinnGen (finn-b) GWAS. This is approximate because exact cohort overlap requires metadata not released with summary statistics.
- **widen_% (ρ=0)** and **widen_% (ρ_g)** — S10 correction at ρ_MY = 0 vs the empirical primary ρ_g, computed on the TwoSampleMR-validated α̂/β̂/SEs for the 4 validated trios and on the screening pipeline for S255/S267 (indicative, marked *).

| study_id | primary ρ_g | 95% CI | ρ_g (M-inst) | ρ_g (X-inst) | ρ_g (resid) | sample overlap | widen% (ρ=0) | widen% (ρ_g) | widen% (ρ_g upper CI) | Δ (pp) | Flip | Flip (worst case) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S014 | +0.597 | [0.50, 0.68] | +0.597 | +0.813 | +0.591 | high (UKB–UKB) | −9.0 | −8.6 | −8.6 | +0.4 | none | none |
| S273 | +0.070 | [−0.02, 0.16] | +0.079 | +0.070 | −0.015 | high (UKB–UKB) | −0.7 | −0.7 | −0.7 | +0.01 | none | none |
| S255 | +0.186 | [0.06, 0.31] | +0.186 | +0.211 | +0.188 | ≈0 (UKB–FinnGen) | −0.0* | −0.0* | −0.0* | +0.0* | none | none |
| S137 | +0.218 | [0.09, 0.34] | +0.218 | −0.481 | +0.235 | high (UKB–UKB) | −5.9 | −5.8 | −5.8 | +0.07 | none | none |
| S217 | +0.810 | [0.37, 0.95] | +0.810 | +0.755 | +0.616 | high (UKB–UKB) | −0.1 | −0.1 | −0.1 | +0.00 | none | none |
| S267 | −0.102 | [−0.31, 0.11] | −0.027 | −0.102 | −0.330 | ≈0 (UKB–FinnGen) | −1.6 | −1.6 | −1.6 | +0.0 | none | none |

**Empirical distribution.** 5/6 overlapping trios show positive mediator–outcome genetic concordance (range +0.07 to +0.81; the single negative case, S267, is a UKB–FinnGen pair whose 95% CI includes zero). Independently, 4/6 trios draw both mediator and outcome from UK Biobank-derived GWAS, so their literal M–Y sample overlap is substantial. **Despite this uniformly positive (or high-overlap) ρ_MY, re-entering the empirical values into S10 changed the corrected SE by at most 0.40 percentage points and narrowed every CI with zero flips** — because the shared-instrument covariance is dominated by the structurally negative denominator term, which for n_s = 1–3 SNPs overwhelms the positive ρ_MY contribution. The "ρ_MY > 0 widens" effect demonstrated in the §3.2 sweep therefore operates in the high-π_shared / large-n_s regime, not in the realized same-sign mediation literature.

**Worst-case robustness check.** Because four of six trios have ρ_g 95% CIs that exclude zero, we additionally re-ran the S10 correction using the *upper* bound of each trio's 95% CI — the value least favorable to the narrowing conclusion — rather than the point estimate. All six trios still show a corrected SE smaller than the naive SE (narrowing preserved) with zero significance flips, even under this conservative substitution; the worst-case correction is identical to the point-estimate correction to the displayed precision (the largest deviation from the ρ_MY = 0 baseline is +0.4 percentage points, study S014). This confirms the zero-flip conclusion is not an artifact of using ρ_g point estimates and is robust to the sampling uncertainty in the correlation estimate itself. The `widen% (ρ_g upper CI)` column in the table reports these values and is shown alongside the point-estimate `widen% (ρ_g)` for direct comparison.

**Source files.** `M4b_rhoMY_empirical_20260904.py` (estimation script), `temp/M4b_rhoMY_empirical_20260904.csv` (per-trio output), `log/M4b_rhoMY_empirical_20260904.log` (run log).