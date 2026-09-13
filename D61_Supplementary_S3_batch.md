# Supplementary Table S3. Phase-B batch re-estimation of published two-step MR mediation studies

Companion to §3.5 of the main manuscript. All numbers are taken directly from the Phase-B pipeline outputs `M4b_pishared_20260904.csv` (π_shared screen) and `M4b_stage2_recompute_20260904.csv` (per-candidate re-estimation).

## Methods summary

- **Phase A (local screen).** From the 333 two-step MR mediation studies, 70 had all three traits (exposure, mediator, outcome) resolvable to an OpenGWAS or FinnGen accession with mediator GWAS sample size N_M ≥ 20,000.

- **Phase B (REST re-estimation).** For each candidate we extracted clumped exposure and mediator instruments via the OpenGWAS `/tophits` endpoint and computed π_shared = |G_X ∩ G_M| / min(|G_X|, |G_M|). Re-estimation used `/associations` + harmonized IVW (S10 correction, ρ_MY = 0), gated by a validation check that first reproduced the D56 BMI→waist→CHD results to 2–3 decimals.

- **Sign convention.** widen_% < 0 means the S10-corrected indirect-effect SE is smaller (narrower CI) than the naive delta-method SE.

## Table S3.1. π_shared screen of all 70 Phase-A candidates

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

## Table S3.2. Re-estimation of the 4 of 6 adequately powered overlapping studies (TwoSampleMR-validated, ρ_MY = 0)

| study_id | exposure | mediator | outcome | n_X | n_M | n_shared | π_shared | α̂ (SE_α) | β̂ (SE_β) | indirect | SE_naive | SE_corr | widen_% | naive_sig | corr_sig | flip |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S014 | T1DM | hypertension | peripheral atherosclerosis(PAS)/coronary atherosclerosis(CAS) | 18 | 209 | 1 | 0.0556 | 0.00591 (0.00345) | 0.1242 (0.0112) | 7.34e-04 | 4.34e-04 | 3.95e-04 | -9.0 | 否 | 否 | 无翻转 |
| S273 | inflammatory factors / gut microbiota / blood cell traits (炎症因子/肠道菌群/血细胞, 3暴露) | immune traits (免疫性状) | IgAN (IgA nephropathy, IgA肾病) | 440 | 13 | 2 | 0.1538 | 0.00392 (0.00115) | 1.963 (1.265) | 0.00769 | 0.00545 | 0.00541 | -0.7 | 否 | 否 | 无翻转 |
| S137 | 25-hydroxyvitamin D(25(OH)D) | serum calcium(血清钙) | migraine(偏头痛) | 105 | 220 | 2 | 0.019 | 0.0221 (0.0299) | 0.00163 (0.00143) | 3.60e-05 | 5.80e-05 | 5.50e-05 | -5.9 | 否 | 否 | 无翻转 |
| S217 | rheumatoid arthritis(RA, 类风湿关节炎) | immunosuppressants(免疫抑制剂使用) | bronchiectasis(支气管扩张症) | 9 | 10 | 1 | 0.1111 | 44.853 (6.464) | 0.1986 (0.0543) | 8.908 | 2.753 | 2.750 | -0.1 | 是 | 是 | 无翻转 |

*Note:* S255 and S267 could not be re-estimated through TwoSampleMR (allele-harmonisation conflict at the FinnGen outcome GWAS; the package returned a non-finite estimate). They are not estimable through the gold-standard pipeline and excluded from the validated flip count.

---
