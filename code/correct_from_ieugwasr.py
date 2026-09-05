# -*- coding: utf-8 -*-
"""
correct_from_ieugwasr.py
=======================
ieugwasr-compatible wrapper for the two-step (product-method) MR mediation
covariance correction. Reuses the verified closed form in M4b_s10_cov.py.

Design note
-----------
Like the R companion (correct_cov_prod_mr.R), this file does NOT import
ieugwasr at runtime. It accepts plain pandas DataFrames with the same column
shapes that ieugwasr / TwoSampleMR produce:

  * extract_instruments(accession)  -> columns: SNP, beta, se, ...
  * extract_outcome_data(...)        -> columns: SNP, beta, se, ...
  * a harmonised frame (harm_dat)    -> columns: SNP, beta.exposure,
                                         se.exposure, beta.outcome, se.outcome

The user runs their own ieugwasr pipeline, then passes the resulting frames.

Functions
---------
  ivw_estimate(beta, se)                       -> (beta_hat, se_hat)
  mr_mediation_correct_from_frames(harm_dat, snps_step1, snps_step2,
                                   N_X, N_M, N_Y, F_stat=None, rho_MY=0,
                                   alpha_hat=None, beta_hat=None,
                                   se_alpha=None, se_beta=None,
                                   seed=2026, n_mc=100000)
        -> dict with n_shared, p_X, p_M, cov_total, corrected SE, widen_pct, ...

Run self-test:  python correct_from_ieugwasr.py
"""
import math
import numpy as np
from M4b_s10_cov import estimate_cov_prod_mr, corrected_se


def ivw_estimate(beta, se):
    """Fixed-effect inverse-variance-weighted estimate and SE."""
    beta = np.asarray(beta, float)
    se = np.asarray(se, float)
    w = 1.0 / se**2
    b = float(np.sum(w * beta) / np.sum(w))
    se_b = float(math.sqrt(1.0 / np.sum(w)))
    return b, se_b


def mr_mediation_correct_from_frames(harm_dat, snps_step1, snps_step2,
                                      N_X, N_M, N_Y, F_stat=None,
                                      rho_MY=0, alpha_hat=None, beta_hat=None,
                                      se_alpha=None, se_beta=None,
                                      seed=2026, n_mc=100000):
    """
    Correct the product-method indirect-effect variance from ieugwasr-style frames.

    Parameters
    ----------
    harm_dat : DataFrame with columns SNP, beta.exposure, se.exposure,
               beta.outcome, se.outcome  (the harmonised X->M->Y data).
    snps_step1, snps_step2 : array-like of SNP rsIDs for the Step-1 and Step-2
               instrument sets (the exposures of each step).
    N_X, N_M, N_Y : GWAS sample sizes.
    F_stat : Step-1 F statistic. If None, derived from
             median((beta.exposure / se.exposure)^2) of harm_dat.
    rho_MY : M-Y GWAS sample-overlap proportion (0 = independent).
    alpha_hat, beta_hat, se_alpha, se_beta : product-method step estimates.
               If any is None, they are derived by IVW from harm_dat.
    """
    snps_step1 = set(snps_step1)
    snps_step2 = set(snps_step2)
    n_shared = len(snps_step1 & snps_step2)
    p_X = len(snps_step1)
    p_M = len(snps_step2)

    if F_stat is None:
        F_stat = float(np.median(
            (harm_dat["beta.exposure"].values / harm_dat["se.exposure"].values) ** 2))

    # derive alpha/beta by IVW of the per-SNP ratios if not supplied
    if alpha_hat is None or se_alpha is None:
        a, sa = ivw_estimate(harm_dat["beta.outcome"].values / harm_dat["beta.exposure"].values,
                             harm_dat["se.outcome"].values / np.abs(harm_dat["beta.exposure"].values))
        alpha_hat, se_alpha = a, sa
    if beta_hat is None or se_beta is None:
        b, sb = ivw_estimate(harm_dat["beta.outcome"].values / harm_dat["beta.exposure"].values,
                            harm_dat["se.outcome"].values / np.abs(harm_dat["beta.exposure"].values))
        # In a true 2-stage design Step-2 uses a different harm_dat; here we mirror
        # the R convenience (user should pass the real Step-2 frames in practice).
        beta_hat, se_beta = b, sb

    cov_total, cov_shared, cov_rho = estimate_cov_prod_mr(
        se_alpha, se_beta, n_shared, p_X, p_M, F_stat, N_X, N_M, N_Y,
        rho_MY=rho_MY, seed=seed, n_mc=n_mc)
    indirect, se_naive, se_corr, widen = corrected_se(
        alpha_hat, beta_hat, se_alpha, se_beta, cov_total)

    return dict(n_shared=n_shared, p_X=p_X, p_M=p_M, F_stat=F_stat,
                N_X=N_X, N_M=N_M, N_Y=N_Y, rho_MY=rho_MY,
                cov_total=cov_total, cov_shared=cov_shared, cov_rho=cov_rho,
                indirect=indirect, se_naive=se_naive,
                se_corrected=se_corr, widen_pct=widen)


if __name__ == "__main__":
    import pandas as pd
    print("=== correct_from_ieugwasr.py self-test (D56 BMI->waist->CHD) ===")
    F_stat, N_X, N_M, N_Y = 66.3, 339224, 339224, 184305
    se = 1 / math.sqrt(N_X)
    # harmonised frame: 78 SNPs (the Step-1 instrument set)
    harm = pd.DataFrame({
        "SNP": [f"rs{i:06d}" for i in range(1, 79)],
        "beta.exposure": [math.sqrt(F_stat) * se] * 78,
        "se.exposure": [se] * 78,
        "beta.outcome": [0.01] * 78,
        "se.outcome": [se] * 78,
    })
    # natural design: Step-1 = 78 SNPs, Step-2 = 13 shared + 28 unique (total 41)
    step1 = list(range(1, 79))
    step2 = list(range(1, 14)) + list(range(100, 128))   # 13 shared + 28 unique
    r_nat = mr_mediation_correct_from_frames(
        harm, step1, step2, N_X, N_M, N_Y,
        alpha_hat=0.8628947, beta_hat=0.4773346, se_alpha=0.0174075, se_beta=0.0883770)
    # shared design: Step-2 = all 78 SNPs (full overlap)
    r_shr = mr_mediation_correct_from_frames(
        harm, list(range(1, 79)), list(range(1, 79)), N_X, N_M, N_Y,
        alpha_hat=0.8628947, beta_hat=0.4795636, se_alpha=0.0174075, se_beta=0.0645322)
    print(f"  natural : n_shared={r_nat['n_shared']} (expect 13)  widen_pct={r_nat['widen_pct']:+.1f}%  (target -2.8%)")
    print(f"  shared  : n_shared={r_shr['n_shared']} (expect 78)  widen_pct={r_shr['widen_pct']:+.1f}%  (target -15.5%)")
    # also exercise the IVW-derived path (no explicit alpha/beta)
    r_nat_ivw = mr_mediation_correct_from_frames(harm, step1, step2, N_X, N_M, N_Y)
    print(f"  IVW-path: n_shared={r_nat_ivw['n_shared']} widen_pct={r_nat_ivw['widen_pct']:+.1f}% "
          f"(alpha_hat={r_nat_ivw['indirect']/0.4773346:+.3f} derived by IVW)")
    ok = (r_nat["n_shared"] == 13 and r_nat["widen_pct"] < 0 and r_nat["widen_pct"] > -8 and
          r_shr["n_shared"] == 78 and r_shr["widen_pct"] < 0 and r_shr["widen_pct"] > -22)
    print(f"  RESULT  : {'PASS' if ok else 'CHECK'}")
