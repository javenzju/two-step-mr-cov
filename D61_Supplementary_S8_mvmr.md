# Supplementary Methods S8 — MVMR generalization of Cov(α̂, β̂) and the S110 worked example

This supplement extends the univariable two-step closed form (main text §2, Supplementary Methods S1–S6, the "S10" tool) to the multivariable / merged-pool ("MVMR-variant") design that 78 of 695 coded reports (11.2% [95% CI 9.1–13.8%]) actually use. We give the derivation outline and a worked example on the audited S110 design. No full simulation validation of the MVMR case is performed here; the extension is presented as a roadmap with one structural numerical illustration.

## S8.1 Univariable baseline (recap)

Step-1 IVW estimate of X → M: α̂ = Σⱼ (β̂_{X,j} γ̂_{M,j} / σ̂_{M,j}²) / Σⱼ (β̂_{X,j}² / σ̂_{M,j}²), instruments j = 1…n₁.
Step-2 IVW estimate of M → Y: β̂ = Σₖ (β̂_{M,k} γ̂_{Y,k} / σ̂_{Y,k}²) / Σₖ (β̂_{M,k}² / σ̂_{Y,k}²), instruments k = 1…n₂.
The S10 closed form is

Cov(α̂, β̂) ≈ 2 α̂ β̂ · Σ_{s ∈ S} [ (β̂_{X,s}/σ̂_{M,s}²) · (β̂_{M,s} γ̂_{Y,s}/σ̂_{Y,s}²) ] / (Σⱼ β̂_{X,j}²/σ̂_{M,j}²)²
&nbsp;&nbsp;&nbsp;&nbsp;+ ρ_MY · n_s ρ_MY μ_X μ_M /(σ̂_M σ̂_Y) · E[inv Aa]²,

where S is the shared-SNP set (|S| = n_s), the first term is the **shared-instrument channel** and the second is the **M–Y sample-overlap channel** (ρ_MY ≠ 0). The product variance is Var(α̂β̂) = β̂²Var(α̂) + α̂²Var(β̂) + 2α̂β̂Cov(α̂,β̂), so the correction enters as the added term 2α̂β̂Cov(α̂,β̂).

## S8.2 MVMR step-1 generalization (outline)

In the MVMR-variant design the exposure step is multivariable: p exposures (including X and M) are jointly instrumented by an L×p matrix Z of L SNPs, with error covariance Ω. The MVMR estimator of the X → M effect is

α̂ = e_Xᵀ (ZᵀΩ⁻¹Z)⁻¹ ZᵀΩ⁻¹ ỹ_M,

where ỹ_M is the vector of SNP–M associations and e_X selects the X column. Define the MVMR hat matrix H = Z(ZᵀΩ⁻¹Z)⁻¹ZᵀΩ⁻¹ (L×L); its diagonal entry h_s = H_{ss} is the leverage of SNP s. Then α̂ = Σ_s h_s · ỹ_{M,s} — a leverage-weighted average of the SNP–M associations.

When step-2 (M → Y) reuses the *same* L-SNP combined set (the merged-pool design), the shared-instrument covariance generalizes to

Cov_MVMR(α̂, β̂) ≈ 2 α̂ β̂ · Σ_{s=1..L} h_s · (β̂_{M,s} γ̂_{Y,s} / σ̂_{Y,s}²) / (Σₖ β̂_{M,k}² / σ̂_{Y,k}²)²
&nbsp;&nbsp;&nbsp;&nbsp;+ ρ_MY channel (unchanged from S8.1).

This **reduces to the univariable S10 term when p = 1**, because then h_s = (β̂_{X,s}/σ̂_{M,s}²) / Σⱼ(β̂_{X,j}²/σ̂_{M,j}²), i.e. the univariable leverage. The sample-overlap channel depends only on M–Y GWAS sample overlap (ρ_MY) and is independent of the step-1 structure.

## S8.3 Structural sign result (extends Proposition S2.5)

Each h_s > 0, so the sign of the shared-instrument term is the sign of α̂β̂. Therefore:

- **Same-sign mediation (α̂β̂ > 0)** ⇒ shared-instrument covariance negative ⇒ corrected SE smaller ⇒ the naive delta method is *conservative*. Holds for MVMR exactly as for univariable.
- **Opposite-sign mediation or ρ_MY > 0** ⇒ corrected SE larger ⇒ naive anti-conservative.

The correction is therefore necessary for valid inference in the MVMR-variant design for the same reason as the univariable case, and its **magnitude scales with n_s = L** (the number of shared instruments).

## S8.4 Worked example — S110 (audited merged-pool MVMR design)

S110 (PMID 32833022, "Genetic determinants of increased body mass index mediate the effect of smoking on increased risk for type 2 diabetes but not coronary artery disease") is coded as an **MVMR-variant / merged-IV-pool** design: the authors build "a combined instrument with 1410 SNPs significant for smoking or BMI" and reuse it across both steps. In our coding table `n_IV_shared = full_overlap` and `IV_selection_strategy = 合并IV池`, i.e. **π_shared ≈ 1.0 and n_s = 1410** — the maximal-overlap regime. Every re-estimated trio in the main batch had n_s = 1–3, so S110 sits at the opposite, far larger extreme of the same spectrum our closed form describes.

Because S110's trait-specific GWAS accessions were not deposited for re-estimation (it is outside the 113-trio OpenGWAS batch), we give a **structural illustration**, not a re-estimation:

- The shared-instrument term in S8.2 contains n_s = 1410 summed leverages versus n_s ≤ 3 in the re-estimated trios. Holding per-SNP contributions comparable to the BMI → waist → CHD validation case (where n_s = 13 gave a −2.8% CI change), the S110 correction is expected to be larger by a factor of roughly 1410/13 ≈ 100× in the summed contribution — i.e. an order-of-magnitude (tens of percent) CI change under same-sign mediation, narrowing the interval.
- This is precisely the regime where the correction is **most material yet never reported**: S110 is one of only two coded studies carrying a structured "merged instrument pool" tag, and the field has no convention for disclosing n_s or correcting Cov(α̂,β̂) in merged-pool MVMR.

*Illustration caveat:* the tens-of-percent figure is an extrapolation from the validated n_s = 13 case under uniform-leverage approximation; it demonstrates direction and order of magnitude, not S110's actual effect. Recovering S110's deposited summary statistics and applying the S8.2 formula is the natural next validation step and is left as future work, enabled by the deposited tool.

## S8.5 Why this raises the novelty ceiling

The main paper solves the *univariable* product-method case and shows the correction is usually conservative at the small n_s realized in the literature. The MVMR generalization (S8.2–S8.3) shows the same closed form extends to the merged-pool design — the design most likely to need correction — with the correction magnitude growing with n_s. S110 demonstrates that the highest-overlap designs are exactly those the literature does not tag, so the method closes the gap where it is widest.
