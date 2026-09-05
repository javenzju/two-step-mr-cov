# Correction tool for two-step (product-method) MR mediation — user guide

This package ships the closed-form covariance correction for the indirect-effect
variance `Var(α̂β̂)` described in the manuscript, in two forms that slot directly
into the two standard MR software stacks:

| File | Stack | Language | Loads the stack at runtime? |
|---|---|---|---|
| `correct_cov_prod_mr.R` | **TwoSampleMR** | base-R | **No** — you pass `harmonise_data()` / `mr_ivw()` output in |
| `correct_from_ieugwasr.py` | **ieugwasr** | Python | **No** — you pass `extract_instruments()` / `extract_outcome_data()` frames in |

> **Why "no load":** the tools accept the *data frames* that TwoSampleMR / ieugwasr
> produce. They never call `library(TwoSampleMR)` / `import ieugwasr`, so they run
> even where those packages cannot be loaded (e.g. the `R 4.6.0 + ieugwasr` segfault
> on the authors' build), and the maths is independently auditable.

---

## 1. TwoSampleMR (R)

```r
source("correct_cov_prod_mr.R")

# ---- your normal TwoSampleMR pipeline ----
library(TwoSampleMR)
dat1  <- harmonise_data(exposure = "ieu-a-2",  outcome = "ieu-a-61")   # X -> M
dat2  <- harmonise_data(exposure = "ieu-a-61", outcome = "ieu-a-7")    # M -> Y
fit1  <- mr_ivw(dat1); fit2 <- mr_ivw(dat2)
alpha_hat <- fit1$beta;  se_alpha <- fit1$se
beta_hat  <- fit2$beta;  se_beta  <- fit2$se

# ---- correction (data frames in, corrected SE out) ----
res <- mr_cov_correct(dat1, dat2, alpha_hat, beta_hat, se_alpha, se_beta,
                      rho_MY = 0)        # set rho_MY > 0 if M/Y GWAS overlap
res$widen_pct            # % change in indirect-effect SE (negative = CI narrows)
res$se_corrected         # corrected SE of alpha_hat * beta_hat
res$n_shared             # SNPs shared between the two instrument sets
```

`mr_cov_correct()` auto-derives `F_stat` (mean `F.statistic`, else median IV
strength) and `N` (median `Nc`) from the frames; pass them explicitly to override.
If you omit `alpha_hat`/`beta_hat`, they are derived by IVW from the data.

Self-test (base-R, no TwoSampleMR): `Rscript test_correct_cov_prod_mr.R`
→ reproduces the D56 BMI→waist→CHD ground truth (natural −2.8%, shared −15.5%).

---

## 2. ieugwasr (Python)

```python
from correct_from_ieugwasr import mr_mediation_correct_from_frames
import pandas as pd

# harm_dat: harmonised X->M->Y frame (SNP, beta.exposure, se.exposure,
#           beta.outcome, se.outcome); snps_step1/2: the two instrument rsID sets
res = mr_mediation_correct_from_frames(
    harm_dat, snps_step1, snps_step2,
    N_X=339224, N_M=339224, N_Y=184305,
    rho_MY=0,                       # M/Y GWAS sample overlap (0 = independent)
    alpha_hat=0.86, se_alpha=0.017,
    beta_hat=0.48,  se_beta=0.088)
print(res["widen_pct"], res["se_corrected"], res["n_shared"])
```

Self-test: `python correct_from_ieugwasr.py`
→ same D56 ground truth as the R tool (natural −2.8%, shared −15.5%).

---

## 3. Validation status

Both wrappers were cross-checked against (a) the authors' R `S10_prod_mr_cov_tool.R`
and (b) the deposited D56 ground truth (BMI→waist→CHD, natural `n_s = 13` and
shared-IV `n_s = 78`). All three implementations agree on the sign (negative =
CI narrows) and the magnitude (within the ~1 pp Monte-Carlo variance of the
shared-instrument channel). The closed form is the same equation verified in
§3.1–§3.2 of the manuscript; the wrappers add only the instrument-set bookkeeping
(`n_shared = |G'_X ∩ G'_M|`, `p_X`, `p_M`) and the optional auto-derivation of
`F_stat` / `N`.
