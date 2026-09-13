# Supplementary Table S4. Empirical rho_MY for the six overlapping trios
(companion to main-manuscript Section 3.5 and Table 4)

## Table S4. Empirical ρ_MY for the six overlapping trios (companion to §3.5, main manuscript Table 4)

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
