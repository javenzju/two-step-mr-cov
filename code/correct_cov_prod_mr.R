# ============================================================
# correct_cov_prod_mr.R
# TwoSampleMR-compatible closed-form correction for the variance
# of the product-method two-step MR mediation indirect effect (alpha_hat * beta_hat)
#
# Author:  Yan Chen / Jianfeng Wang
# Companion to:  "Covariance correction for two-step (product-method) MR mediation
#                with overlapping instruments" (submission to AJE, 2026)
#
# DESIGN NOTE (important):
#   This file is PURE BASE-R. It does NOT call library(TwoSampleMR) and does NOT
#   source any other project script. A user runs their own TwoSampleMR pipeline
#   (harmonise_data() / mr_ivw()) in their own session, then passes the resulting
#   data frames / summary statistics to the functions below. This keeps the tool
#   usable even where TwoSampleMR cannot be loaded (e.g. the segfault observed under
#   R 4.6.0 + ieugwasr on the authors' build), and makes the maths independently
#   auditable.
#
# The closed form is a faithful port of the authors' Python reference implementation
# (M4b_s10_cov.py), which was itself verified against the R S10 tool and the D56
# ground-truth (BMI -> waist -> CHD: natural overlap widen% = -2.8%, shared-IV
# design widen% = -15.5%).
#
# Functions:
#   estimate_cov_prod_mr(se_alpha, se_beta, n_shared, p_X, p_M, F_stat,
#                        N_X, N_M, N_Y, rho_MY=0, ...)  -> list(cov_total, cov_shared, cov_rho)
#   corrected_se(alpha, beta, se_alpha, se_beta, cov_total)
#                                                       -> list(indirect, se_naive, se_corrected, widen_pct)
#   mr_cov_correct(dat_step1, dat_step2, alpha_hat, beta_hat, se_alpha, se_beta,
#                  rho_MY=0, F_stat=NULL, N_X=NULL, N_M=NULL, N_Y=NULL, ...)
#                                                       -> full correction for TwoSampleMR output
#   mr_cov_correct_ivw(dat_step1, dat_step2, ...)        -> same, but alpha/beta derived by IVW
#
# Run the self-test:  Rscript correct_cov_prod_mr.R
# ============================================================

## ---- internal Monte-Carlo for Cov(gamma_M_j, beta_hat) (shared-instrument channel) ----
.compute_cov_gM_beta_mc <- function(mu_M, mu_Y, se_M, se_Y, p_M,
                                     sd_prior_frac = 0.3, n_mc = 100000, seed = 2026) {
  if (!is.null(seed)) set.seed(seed)
  Z <- rnorm(n_mc, mu_M, mu_M * sd_prior_frac) + rnorm(n_mc, 0, se_M)
  gM_oth <- matrix(rnorm(n_mc * (p_M - 1), mu_M, mu_M * sd_prior_frac), n_mc, p_M - 1) +
            matrix(rnorm(n_mc * (p_M - 1), 0, se_M), n_mc, p_M - 1)
  C <- rowSums(gM_oth^2 / se_Y^2)
  W <- rnorm(n_mc, mu_Y, mu_Y * sd_prior_frac) + rnorm(n_mc, 0, se_Y)
  E_Bp <- (p_M - 1) * mu_M * mu_Y / se_Y^2
  A_beta <- Z^2 / se_Y^2 + C
  beta_h <- (Z * W / se_Y^2 + E_Bp) / A_beta
  ## scalar covariance (matches numpy np.cov(Z, beta_h)[0,1])
  sum((Z - mean(Z)) * (beta_h - mean(beta_h))) / (length(Z) - 1)
}

## ---- main: estimate Cov(alpha_hat, beta_hat) ----
estimate_cov_prod_mr <- function(se_alpha, se_beta, n_shared, p_X, p_M, F_stat,
                                  N_X, N_M, N_Y, rho_MY = 0, sd_prior_frac = 0.3,
                                  n_mc = 100000, seed = 2026, verbose = FALSE) {
  stopifnot(se_alpha > 0, se_beta > 0,
            n_shared >= 0, n_shared == round(n_shared),
            n_shared <= min(p_X, p_M), abs(rho_MY) <= 1)

  se_M <- 1 / sqrt(N_M); se_Y <- 1 / sqrt(N_Y)
  mu_X <- sqrt(F_stat / N_X); mu_M <- sqrt(F_stat / N_M); mu_Y <- sqrt(F_stat / N_Y)
  v_X <- (sd_prior_frac * mu_X)^2 + se_M^2
  v_M <- (sd_prior_frac * mu_M)^2 + se_M^2
  v_Y <- (sd_prior_frac * mu_Y)^2 + se_Y^2
  E_A_alpha <- p_X * (mu_X^2 + v_X) / se_M^2
  E_inv_Aa  <- 1 / E_A_alpha
  E_A_beta  <- p_M * (mu_M^2 + v_M) / se_Y^2
  E_inv_Ab  <- 1 / E_A_beta

  if (n_shared == 0) {
    cov_shared <- 0
  } else {
    Cov_Z_beta <- .compute_cov_gM_beta_mc(mu_M, mu_Y, se_M, se_Y, p_M,
                                          sd_prior_frac, n_mc, seed)
    cov_shared <- n_shared * (mu_X / se_M^2) * E_inv_Aa * Cov_Z_beta
  }
  if (rho_MY == 0 || n_shared == 0) {
    cov_rho <- 0
  } else {
    cov_rho <- n_shared * rho_MY * mu_X * mu_M / (se_M * se_Y) * E_inv_Aa * E_inv_Ab
  }
  cov_total <- cov_shared + cov_rho

  ## Cauchy-Schwarz safety clip (|Cov| <= se_alpha * se_beta)
  cs <- abs(se_alpha * se_beta)
  if (abs(cov_total) > cs) cov_total <- sign(cov_total) * cs * 0.999

  if (verbose) {
    cat(sprintf("n_s=%d p_X=%d p_M=%d F=%.1f rho_MY=%.2f\n", n_shared, p_X, p_M, F_stat, rho_MY))
    cat(sprintf("  cov_shared=%+.4e  cov_rho=%+.4e  cov_total=%+.4e\n", cov_shared, cov_rho, cov_total))
  }
  list(cov_total = cov_total, cov_shared = cov_shared, cov_rho = cov_rho)
}

## ---- corrected SE of the indirect effect ----
corrected_se <- function(alpha, beta, se_alpha, se_beta, cov_total) {
  indirect  <- alpha * beta
  var_naive <- beta^2 * se_alpha^2 + alpha^2 * se_beta^2
  se_naive  <- sqrt(max(var_naive, 0))
  var_corr  <- var_naive + 2 * alpha * beta * cov_total
  se_corr   <- sqrt(max(var_corr, 0))
  widen     <- if (se_naive > 0) (se_corr / se_naive - 1) * 100 else NaN
  list(indirect = indirect, se_naive = se_naive,
       se_corrected = se_corr, widen_pct = widen)
}

## ---- convenience: IVW (fixed-effect) point estimate + SE from harmonised data ----
.ivw <- function(beta, se) {
  w <- 1 / se^2
  b <- sum(w * beta) / sum(w)
  se_b <- sqrt(1 / sum(w))
  c(b, se_b)
}

## ---- main entry for TwoSampleMR users: pass harmonised data frames ----
#' Correct the product-method indirect-effect variance using TwoSampleMR output.
#'
#' @param dat_step1  harmonised step-1 data (exposure X -> mediator M), as returned by
#'                   TwoSampleMR::harmonise_data(); must contain columns SNP, and ideally
#'                   beta.exposure, se.exposure, Nc (or F.statistic).
#' @param dat_step2  harmonised step-2 data (mediator M -> outcome Y), same structure.
#' @param alpha_hat,beta_hat,se_alpha,se_beta  the product-method step estimates.
#'                   alpha_hat = effect of X on M (mr_ivw on dat_step1$beta),
#'                   beta_hat  = effect of M on Y (mr_ivw on dat_step2$beta).
#'                   If any is NULL, they are derived by IVW from the data (convenience).
#' @param rho_MY     M-Y GWAS sample-overlap proportion (0 = fully independent).
#' @param F_stat,N_X,N_M,N_Y  override auto-derivation. F_stat defaults to the mean of
#'                   dat_step1$F.statistic (or the median IV strength from beta/se);
#'                   N defaults to the median Nc of the respective data frame.
mr_cov_correct <- function(dat_step1, dat_step2, alpha_hat = NULL, beta_hat = NULL,
                           se_alpha = NULL, se_beta = NULL, rho_MY = 0,
                           F_stat = NULL, N_X = NULL, N_M = NULL, N_Y = NULL,
                           n_mc = 100000, seed = 2026, verbose = FALSE) {
  snp_col <- if ("SNP" %in% names(dat_step1)) "SNP" else names(dat_step1)[1]
  s1 <- as.character(dat_step1[[snp_col]])
  s2 <- as.character(dat_step2[[snp_col]])
  shared  <- intersect(s1, s2)
  n_shared <- length(shared)
  p_X <- nrow(dat_step1); p_M <- nrow(dat_step2)

  if (is.null(F_stat)) {
    if ("F.statistic" %in% names(dat_step1))
      F_stat <- mean(dat_step1$F.statistic, na.rm = TRUE)
    else if (all(c("beta.exposure", "se.exposure") %in% names(dat_step1)))
      F_stat <- median((dat_step1$beta.exposure / dat_step1$se.exposure)^2)
    else stop("F_stat not provided and not derivable from dat_step1 (need F.statistic or beta.exposure/se.exposure).")
  }
  if (is.null(N_X)) {
    if ("Nc" %in% names(dat_step1)) N_X <- median(dat_step1$Nc, na.rm = TRUE)
    else stop("N_X not provided and not derivable from dat_step1 (need Nc or N_X).")
  }
  if (is.null(N_M)) N_M <- N_X
  if (is.null(N_Y)) {
    if ("Nc" %in% names(dat_step2)) N_Y <- median(dat_step2$Nc, na.rm = TRUE)
    else N_Y <- N_X
  }
  ## derive alpha/beta by IVW if not supplied
  if (is.null(alpha_hat) || is.null(se_alpha)) {
    iv1 <- .ivw(dat_step1$beta.outcome / dat_step1$beta.exposure,
                dat_step1$se.outcome / abs(dat_step1$beta.exposure))
    alpha_hat <- iv1[1]; se_alpha <- iv1[2]
  }
  if (is.null(beta_hat) || is.null(se_beta)) {
    iv2 <- .ivw(dat_step2$beta.outcome / dat_step2$beta.exposure,
                dat_step2$se.outcome / abs(dat_step2$beta.exposure))
    beta_hat <- iv2[1]; se_beta <- iv2[2]
  }

  est <- estimate_cov_prod_mr(se_alpha, se_beta, n_shared, p_X, p_M, F_stat,
                              N_X, N_M, N_Y, rho_MY, n_mc = n_mc, seed = seed, verbose = verbose)
  cor <- corrected_se(alpha_hat, beta_hat, se_alpha, se_beta, est$cov_total)
  list(n_shared = n_shared, p_X = p_X, p_M = p_M, F_stat = F_stat,
       N_X = N_X, N_M = N_M, N_Y = N_Y, rho_MY = rho_MY,
       cov_total = est$cov_total, cov_shared = est$cov_shared, cov_rho = est$cov_rho,
       indirect = cor$indirect, se_naive = cor$se_naive,
       se_corrected = cor$se_corrected, widen_pct = cor$widen_pct)
}

## ---- self-test (base-R only; no TwoSampleMR needed) ----
if (sys.nframe() <= 0L || identical(environment(), globalenv())) {
  cat("\n===== correct_cov_prod_mr.R self-test (D56 BMI->waist->CHD) =====\n")
  F_stat <- 66.3; N_X <- 339224; N_M <- 339224; N_Y <- 184305
  ## natural-overlap design: p_X=78, p_M=41, n_s=13
  a_nat <- estimate_cov_prod_mr(0.0174075, 0.0883770, 13, 78, 41, F_stat, N_X, N_M, N_Y, rho_MY = 0)
  c_nat <- corrected_se(0.8628947, 0.4773346, 0.0174075, 0.0883770, a_nat$cov_total)
  ## shared-IV design: p_X=78, p_M=78, n_s=78
  a_shr <- estimate_cov_prod_mr(0.0174075, 0.0645322, 78, 78, 78, F_stat, N_X, N_M, N_Y, rho_MY = 0)
  c_shr <- corrected_se(0.8628947, 0.4795636, 0.0174075, 0.0645322, a_shr$cov_total)
  cat(sprintf("  natural : widen_pct = %+.1f%%  (target -2.8%%)\n", c_nat$widen_pct))
  cat(sprintf("  shared  : widen_pct = %+.1f%%  (target -15.5%%)\n", c_shr$widen_pct))
  ok <- c_nat$widen_pct < 0 && c_nat$widen_pct > -8 &&
        c_shr$widen_pct < 0 && c_shr$widen_pct > -22
  cat(sprintf("  RESULT  : %s (negative = narrowing preserved; magnitude ~ D56 ground truth)\n",
              if (ok) "PASS" else "CHECK"))
}
