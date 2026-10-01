# Supplementary Table S3. Phase-B batch re-estimation of published two-step MR mediation studies

Companion to §3.5 of the main manuscript. All numbers are taken directly from the Phase-B pipeline outputs `M4b_pishared_20260904.csv` (π_shared screen) and `M4b_stage2_recompute_20260904.csv` (per-candidate re-estimation).

## Methods summary

- **Phase A (local screen).** From the 333 two-step MR mediation studies, 70 had all three traits (exposure, mediator, outcome) resolvable to an OpenGWAS or FinnGen accession with mediator GWAS sample size N_M ≥ 20,000.

- **Phase B (REST re-estimation).** For each candidate we extracted clumped exposure and mediator instruments via the OpenGWAS `/tophits` endpoint and computed π_shared = |G_X ∩ G_M| / min(|G_X|, |G_M|). Re-estimation used `/associations` + harmonized IVW (S10 correction, ρ_MY = 0), gated by a validation check that first reproduced the D56 BMI→waist→CHD results to 2–3 decimals.

- **Sign convention.** ΔSE_% < 0 means the S10-corrected indirect-effect SE is smaller (narrower CI) than the naive delta-method SE.

## Table S3.1. π_shared screen of all 70 Phase-A candidates

| study_id | n_X | n_M | n_shared | π_shared | F_X | status |
|---|---|---|---|---|---|---|
| S139 | 5 | 468 | 0 | 0.0 | 37.7 | zero overlap |
| S147 | 2 | 264 | 0 | 0.0 | 44.0 | zero overlap |
| S296 | 0 | 1 | 0 | NA | NA | zero overlap |
| S247 | 2 | 21 | 0 | 0.0 | 46.4 | zero overlap |
| S261 | 0 | 21 | 0 | NA | NA | zero overlap |
| S268 | 12 | 21 | 0 | 0.0 | 54.8 | zero overlap |
| S275 | 0 | 21 | 0 | NA | NA | zero overlap |
| S309 | 24 | 21 | 0 | 0.0 | 82.6 | zero overlap |
| S364 | 0 | 21 | 0 | NA | NA | zero overlap |
| S376 | 2 | 1 | 0 | 0.0 | 44.0 | zero overlap |
| S030 | 1 | 0 | 0 | NA | 31.1 | zero overlap |
| S014 | 18 | 209 | 1 | 0.0556 | 178.1 | non-zero overlap |
| S260 | 5 | 209 | 0 | 0.0 | 37.7 | zero overlap |
| S167 | 1 | 148 | 0 | 0.0 | 85.3 | zero overlap |
| S253 | 2 | 352 | 0 | 0.0 | 44.0 | zero overlap |
| S273 | 440 | 13 | 2 | 0.1538 | 89.5 | non-zero overlap |
| S249 | 0 | 408 | 0 | NA | NA | zero overlap |
| S266 | 0 | 408 | 0 | NA | NA | zero overlap |
| S282 | 0 | 408 | 0 | NA | NA | zero overlap |
| S338 | 0 | 408 | 0 | NA | NA | zero overlap |
| S348 | 3 | 408 | 0 | 0.0 | 104.6 | zero overlap |
| S366 | 1 | 408 | 0 | 0.0 | 89.2 | zero overlap |
| S370 | 2 | 408 | 0 | 0.0 | 32.3 | zero overlap |
| S379 | 2 | 408 | 0 | 0.0 | 50.1 | zero overlap |
| S255 | 408 | 226 | 1 | 0.0044 | 151.9 | non-zero overlap |
| S259 | 2 | 226 | 0 | 0.0 | 44.0 | zero overlap |
| S272 | 0 | 226 | 0 | NA | NA | zero overlap |
| S373 | 43 | 226 | 0 | 0.0 | 41.8 | zero overlap |
| S137 | 105 | 220 | 2 | 0.019 | 213.7 | non-zero overlap |
| S314 | 21 | 114 | 0 | 0.0 | 52.7 | zero overlap |
| S329 | 0 | 114 | 0 | NA | NA | zero overlap |
| S263 | 9 | 1 | 0 | 0.0 | 209.3 | zero overlap |
| S140 | 2 | 248 | 0 | 0.0 | 44.0 | zero overlap |
| S320 | 2 | 2 | 2 | 1.0 | 32.3 | non-zero overlap |
| S333 | 12 | 2 | 0 | 0.0 | 54.8 | zero overlap |
| S334 | 0 | 2 | 0 | NA | NA | zero overlap |
| S217 | 9 | 10 | 1 | 0.1111 | 209.3 | non-zero overlap |
| S150 | 105 | 113 | 0 | 0.0 | 213.7 | zero overlap |
| S353 | 0 | 113 | 0 | NA | NA | zero overlap |
| S343 | 1 | 16 | 0 | 0.0 | 32.6 | zero overlap |
| S179 | 0 | 57 | 0 | NA | NA | zero overlap |
| S237 | 0 | 48 | 0 | NA | NA | zero overlap |
| S267 | 88 | 53 | 3 | 0.0566 | 217.7 | non-zero overlap |
| S278 | 41 | 52 | 0 | 0.0 | 85.4 | zero overlap |
| S306 | 0 | 52 | 0 | NA | NA | zero overlap |
| S279 | 1 | 2 | 0 | 0.0 | 31.7 | zero overlap |
| S134 | 0 | 9 | 0 | NA | NA | zero overlap |
| S295 | 16 | 12 | 0 | 0.0 | 42.7 | zero overlap |
| S387 | 0 | 0 | 0 | NA | NA | zero overlap |
| S159 | 1 | 2 | 0 | 0.0 | 32.6 | zero overlap |
| S189 | 0 | 2 | 0 | NA | NA | zero overlap |
| S210 | 0 | 2 | 0 | NA | NA | zero overlap |
| S246 | 0 | 2 | 0 | NA | NA | zero overlap |
| S271 | 114 | 2 | 0 | 0.0 | 138.0 | zero overlap |
| S281 | 0 | 2 | 0 | NA | NA | zero overlap |
| S293 | 2 | 2 | 2 | 1.0 | 44.0 | non-zero overlap |
| S299 | 13 | 2 | 0 | 0.0 | 73.4 | zero overlap |
| S312 | 3 | 2 | 0 | 0.0 | 77.3 | zero overlap |
| S321 | 0 | 2 | 0 | NA | NA | zero overlap |
| S355 | 0 | 2 | 0 | NA | NA | zero overlap |
| S367 | 1 | 2 | 0 | 0.0 | 31.9 | zero overlap |
| S317 | 0 | 2 | 0 | NA | NA | zero overlap |
| S354 | 62 | 2 | 0 | 0.0 | 144.0 | zero overlap |
| S389 | 0 | 2 | 0 | NA | NA | zero overlap |
| S349 | NA | NA | NA | NA | NA | exposure or mediator unresolved,skipped |
| S152 | 1 | 2 | 0 | 0.0 | 31.1 | zero overlap |
| S208 | 48 | 2 | 0 | 0.0 | 202.4 | zero overlap |
| S244 | 13 | 2 | 0 | 0.0 | 73.4 | zero overlap |
| S375 | 123 | 2 | 0 | 0.0 | 44.7 | zero overlap |
| S352 | NA | NA | NA | NA | NA | exposure or mediator unresolved,skipped |

**Summary:** 70 screened; 42 analyzable (usable instruments for both exposure and mediator, n_X ≥ 1 and n_M ≥ 1); 28 not analyzable (no EUR-clumped instruments returned, predominantly non-European, UKB non-EUR, or specialized protein/QTL traits). Among the 42 analyzable, 8 (19.0%) had genuine SNP overlap (π_shared > 0); the remaining 34 used effectively disjoint instrument sets.

**Reconciliation of the overlap counts (2026-09-30).** Three different overlap counts appear in this package and they are *not* in conflict — they use different denominators and different inclusion rules. The 8 above is the Phase-A π_shared screen (denominator 42 analyzable) and decomposes as:

- **5** non-degenerate trios above the reporting threshold (S014, S137, S217, S273, S267);
- **2** degenerate self-mediating designs (S320, S293: exposure ≡ mediator accession, so α̂ = 1.0 exactly and π_shared = 1.0);
- **1** sub-threshold case (S255, π_shared = 0.0044 < 0.019).

The main-text headline uses the **all-Python Phase-B pipeline** (113 candidates → 108 successfully re-estimated) and the strictest definition: **5/108 (4.6%, 95% CI 2.0–10.4%)** non-degenerate overlaps; counting the two degenerate designs gives **7/108 (6.5%, 95% CI 3.2–12.8%)**. The Phase-A figure of 8/42 (19.0%) is therefore **not comparable** to the headline: it has a different denominator (42 vs 108), an earlier instrument-extraction pass, and does not apply the degeneracy or threshold exclusions. Only the 5/108 and 7/108 figures should be quoted as the prevalence estimate.

## Table S3.2. Re-estimation of the 4 of 6 adequately powered overlapping studies (TwoSampleMR-validated, ρ_MY = 0)

| study_id | exposure | mediator | outcome | n_X | n_M | n_shared | π_shared | α̂ (SE_α) | β̂ (SE_β) | indirect | SE_naive | SE_corr | ΔSE_% | naive_sig | corr_sig | flip |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S014 | T1DM | hypertension | peripheral atherosclerosis(PAS)/coronary atherosclerosis(CAS) | 18 | 209 | 1 | 0.0556 | 0.00591 (0.00345) | 0.1242 (0.0112) | 7.34e-04 | 4.34e-04 | 3.95e-04 | -9.0 | no | no | none |
| S273 | inflammatory factors / gut microbiota / blood cell traits (inflammatory factors / gut microbiota / blood cell traits, 3exposure) | immune traits (immune traits) | IgAN (IgA nephropathy, IgAnephropathy) | 440 | 13 | 2 | 0.1538 | 0.00392 (0.00115) | 1.963 (1.265) | 0.00769 | 0.00545 | 0.00541 | -0.7 | no | no | none |
| S137 | 25-hydroxyvitamin D(25(OH)D) | serum calcium(serum calcium) | migraine(migraine) | 105 | 220 | 2 | 0.019 | 0.0221 (0.0299) | 0.00163 (0.00143) | 3.60e-05 | 5.80e-05 | 5.50e-05 | -5.9 | no | no | none |
| S217 | rheumatoid arthritis(RA, rheumatoid arthritis) | immunosuppressants(immunosuppressant use) | bronchiectasis(bronchiectasis) | 9 | 10 | 1 | 0.1111 | 44.853 (6.464) | 0.1986 (0.0543) | 8.908 | 2.753 | 2.750 | -0.1 | yes | yes | none |

*Note:* S255 and S267 could not be re-estimated through TwoSampleMR (allele-harmonisation conflict at the FinnGen outcome GWAS; the package returned a non-finite estimate). They are not estimable through the gold-standard pipeline and excluded from the validated flip count.

**Pipeline reconciliation (2026-09-30).** Table S3.2 is the TwoSampleMR cross-check; Table 2 of the main text is the all-Python pipeline. The two agree on the quantity that matters for this paper — the correction is **negative (narrowing) in every study under both pipelines** (S3.2: −9.0%, −0.7%, −5.9%, −0.1%; Table 2: −16.0%, −1.1%, −14.2%, −0.2%) — so the direction result is robust to the implementation. They differ, however, in point estimates and standard errors for some studies and consequently in significance calls: S014 (α̂ = 0.00591, SE 0.00345 here vs 0.00378, SE 0.00096 in Table 2) and S273 (α̂ = 0.00392, SE 0.00115 here vs 0.00721, SE 0.00081 in Table 2) are significant under the all-Python estimates and not significant under TwoSampleMR. These differences do not arise from instrument-set or allele-harmonisation choices. Re-implementing both estimators in Python (`M4b_s014_rootcause_20261002.py`) shows that TwoSampleMR 0.7.6 `mr_ivw` fits `lm(b_out ~ 0 + b_exp, weights = 1/SE_out^2)` and returns SE = [σ/√(Σ w·b_exp^2)] / min(1, σ) with σ the weighted residual dispersion, whereas our pipeline returns the unscaled fixed-effects SE 1/√(Σ b_exp^2/SE_out^2). The two fixed-effects SEs are algebraically identical, so the whole discrepancy is the multiplicative dispersion factor σ, not harmonisation: on the identical 203-SNP S014 set our re-implementation returns b = 0.123031, SE = 0.011014 against TwoSampleMR's b = 0.124242, SE = 0.011243, and adding TwoSampleMR's palindromic-SNP filter closes the residual gap to < 0.1% on both. Table S3.3 gives the full decomposition and confirms that the discrepancy is a pure SE-scale effect: the absolute magnitude of the correction shrinks under random effects while its sign and every significance call relative to the naive interval are unchanged, which is the quantity this paper claims. Note also that fixed-effects SEs make the relative correction appear *larger*, so retaining the all-Python estimates for the headline numbers is not a conservative choice for our own claim; the reason is coverage and uniformity, not magnitude — TwoSampleMR cannot harmonise two FinnGen outcomes (S255, S267) — and the direction conclusion is identical under both estimators. Because the all-Python pipeline has wider coverage (it recovers S267, which TwoSampleMR cannot harmonise) and is applied consistently to all 108 re-estimations, it is the source of the main-text headline numbers; Table S3.2 should be read as a cross-check on the *direction and order of magnitude* of the correction, not as a replication of the point estimates or of the significance calls.

## Table S3.3. Decomposition of the TwoSampleMR vs all-Python discrepancy (S014)

Computed on ieu-b-5144 (mediator) → ukb-d-I9_CORATHER (outcome), 209 clumped instruments, 203 with outcome data. "Palindromic filter" adds TwoSampleMR's removal of the five palindromic intermediate-frequency SNPs (rs1870735, rs199794659, rs2280405, rs2760061, rs6812640).

| Estimator | n SNP | β̂ | SE(β̂) | Ratio vs A |
|---|---|---|---|---|
| A. All-Python IVW, fixed effects (w = b_exp²/SE_out²) | 203 | 0.128323 | 0.004938 | 1.000 |
| B. A + Burgess second-moment random effects | 203 | 0.128323 | 0.004938 | 1.000 |
| C. Ratio meta-analysis, fixed effects (SE_ratio includes SE_exp) | 203 | 0.104500 | 0.005160 | 1.045 |
| D. Ratio meta-analysis, DerSimonian–Laird random effects | 203 | 0.114281 | 0.008306 | 1.682 |
| E. TwoSampleMR 0.7.6 `mr_ivw_fe` (w = 1/SE_out²) | 203 | 0.123031 | 0.004938 | 1.000 |
| F. TwoSampleMR 0.7.6 `mr_ivw_mre` (no under-dispersion correction) | 203 | 0.123031 | 0.011014 | 2.231 |
| G. TwoSampleMR 0.7.6 `mr_ivw` (default; = F because σ = 2.23 > 1) | 203 | 0.123031 | 0.011014 | 2.231 |
| H. **G + palindromic filter (= TwoSampleMR as reported)** | **198** | **0.124242** | **0.011243** | **2.276** |

Rows A and E give *identical* standard errors, confirming that the two fixed-effects variances coincide algebraically (Σ b_exp²/SE_out² = Σ w·b_exp² with w = 1/SE_out²). Row H reproduces the value reported by TwoSampleMR (β̂ = 0.124242, SE = 0.011243) to six decimal places. The 2.276-fold SE difference therefore decomposes as 2.231 (weighted residual dispersion σ) × 1.021 (palindromic-SNP filter); instrument harmonisation accounts for ~2% of the gap and the SE_exp term for ~4%, neither of which is the cause.

## Table S3.4. Effect of the SE scale on the correction and on significance calls

Same four trios, both pipelines, identical covariance model (ρ_MY = 0). ΔSE% is the change in the indirect-effect SE under the correction.

| Study | ΔSE% (all-Python FE) | ΔSE% (TwoSampleMR) | Naive sig (FE) | Corr. sig (FE) | Naive sig (TSMR) | Corr. sig (TSMR) | Flip (FE) | Flip (TSMR) |
|---|---|---|---|---|---|---|---|---|
| S014 | −16.0 | −9.0 | yes | yes | no | no | no | no |
| S273 | −1.1 | −0.7 | yes | yes | no | no | no | no |
| S137 | −14.2 | −5.9 | no | no | no | no | no | no |
| S217 | −0.2 | −0.1 | yes | yes | yes | yes | no | no |

The absolute size of the correction is systematically smaller under random effects, as expected because Var_naive scales with SE² while Cov(α̂, β̂) does not. The sign of the correction (always negative, i.e. narrowing) and — critically — every significance call *relative to the naive interval* are identical under both estimators: no trio flips under either pipeline. The paper's headline claim therefore does not depend on the choice of variance estimator.

---
