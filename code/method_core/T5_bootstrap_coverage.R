suppressMessages(library(ieugwasr))
suppressMessages(library(TwoSampleMR))
src <- "C:/Users/up201/.workbuddy/m4src/"
options(S10_script_dir = src)
source(paste0(src, "S10_prod_mr_cov_tool.R"))
options(timeout=300)

# ---- 向量化独立先验 DGP（按 n_reps 列生成矩阵，避免 R for 循环）----
sim_ab <- function(n_reps, p_X, p_M, n_shared, F_stat, rho_MY, N,
                   alpha_true, beta_true, sd_prior_frac = 0.3, seed = NULL) {
  if (!is.null(seed)) set.seed(seed)
  mu_X <- sqrt(F_stat / N); se <- 1/sqrt(N)
  mu_M <- alpha_true * mu_X; mu_Y <- beta_true * mu_M
  # Step1: X -> M
  gX_t <- matrix(rnorm(p_X*n_reps, mu_X, sd_prior_frac*mu_X), p_X, n_reps)
  gX   <- gX_t + matrix(rnorm(p_X*n_reps, 0, se), p_X, n_reps)
  gM_t1 <- matrix(rnorm(p_X*n_reps, mu_M, sd_prior_frac*mu_M), p_X, n_reps)
  eM1  <- matrix(rnorm(p_X*n_reps, 0, se), p_X, n_reps)
  gM1  <- gM_t1 + eM1
  Aa <- colSums(gX^2)/se^2; Ba <- colSums(gX*gM1)/se^2
  alpha_hat <- Ba/Aa
  # Step2: M -> Y
  if (n_shared > 0) { gM_shared <- gM1[1:n_shared, , drop=FALSE]; eM_shared <- eM1[1:n_shared, , drop=FALSE]
  } else { gM_shared <- matrix(0,0,n_reps); eM_shared <- matrix(0,0,n_reps) }
  n_m <- p_M - n_shared
  if (n_m > 0) {
    gM_to <- matrix(rnorm(n_m*n_reps, mu_M, sd_prior_frac*mu_M), n_m, n_reps) + matrix(rnorm(n_m*n_reps,0,se), n_m, n_reps)
    eM_to <- matrix(rnorm(n_m*n_reps, 0, se), n_m, n_reps)
    gM_m <- gM_to; eM_m <- eM_to
  } else { gM_m <- matrix(0,0,n_reps); eM_m <- matrix(0,0,n_reps) }
  gM2 <- rbind(gM_shared, gM_m); eM2 <- rbind(eM_shared, eM_m)
  gY_t <- matrix(rnorm(p_M*n_reps, mu_Y, sd_prior_frac*mu_Y), p_M, n_reps)
  eY <- rho_MY*(se/se)*eM2 + sqrt(max(0,1-rho_MY^2))*matrix(rnorm(p_M*n_reps,0,se), p_M, n_reps)
  gY <- gY_t + eY
  Ab <- colSums(gM2^2)/se^2; Bb <- colSums(gM2*gY)/se^2
  beta_hat <- Bb/Ab
  list(alpha = alpha_hat, beta = beta_hat, ab = alpha_hat*beta_hat)
}

# ---- 覆盖率验证 ----
grid <- expand.grid(F = c(15, 30), pi_shared = c(0.3, 0.7), rho = c(0.3, 0.6))
p_X <- 20; p_M <- 20
alpha_true <- 0.5; beta_true <- 0.5     # 正向效应（cov<0 区，naive 过度保守）；cov>0 对称区见 T6 结构分析
true_ind <- alpha_true * beta_true           # 0.25
N <- 50000; B_batches <- 100; n_reps <- 1000

rows <- list()
for (i in seq_len(nrow(grid))) {
  g <- grid[i, ]; Fs <- g$F; pi <- g$pi_shared; rho <- g$rho
  n_sh <- round(pi * p_M)
  cov_naive <- 0; cov_s10 <- 0; cov_mc <- 0
  w_naive <- c(); w_s10 <- c(); w_mc <- c()
  for (bb in seq_len(B_batches)) {
    s <- sim_ab(n_reps, p_X, p_M, n_sh, Fs, rho, N, alpha_true, beta_true, seed = 1000*i + bb)
    ma <- mean(s$alpha); mb <- mean(s$beta); abm <- ma*mb
    sea <- sd(s$alpha); seb <- sd(s$beta)
    vn <- mb^2*sea^2 + ma^2*seb^2; sen <- sqrt(vn)
    lo_n <- abm - 1.96*sen; hi_n <- abm + 1.96*sen
    res <- estimate_cov_prod_mr(se_alpha = sea, se_beta = seb, n_shared = n_sh, p_X = p_X,
                                p_M = p_M, F_stat = Fs, rho_MY = rho, N = N,
                                alpha_hat_obs = ma, beta_hat_obs = mb, verbose = FALSE, n_mc = 1000)
    vc <- max(mb^2*sea^2 + ma^2*seb^2 + 2*ma*mb*res$cov_total, 0); sec <- sqrt(vc)
    lo_s <- abm - 1.96*sec; hi_s <- abm + 1.96*sec
    q <- quantile(s$ab, c(0.025, 0.975)); lo_m <- q[1]; hi_m <- q[2]
    cov_naive <- cov_naive + (lo_n <= true_ind && true_ind <= hi_n)
    cov_s10  <- cov_s10  + (lo_s <= true_ind && true_ind <= hi_s)
    cov_mc   <- cov_mc   + (lo_m <= true_ind && true_ind <= hi_m)
    w_naive <- c(w_naive, 2*1.96*sen); w_s10 <- c(w_s10, 2*1.96*sec); w_mc <- c(w_mc, q[2]-q[1])
  }
  rows[[i]] <- data.frame(F = Fs, pi_shared = pi, rho_MY = rho, n_shared = n_sh,
    coverage_naive = round(cov_naive/B_batches*100, 1),
    coverage_s10   = round(cov_s10/B_batches*100, 1),
    coverage_mc    = round(cov_mc/B_batches*100, 1),
    width_naive = round(mean(w_naive), 4),
    width_s10   = round(mean(w_s10), 4),
    width_mc    = round(mean(w_mc), 4))
  cat(sprintf("cell %d/%d F=%g pi=%.1f rho=%.1f | cov naive=%.1f s10=%.1f mc=%.1f\n",
    i, nrow(grid), Fs, pi, rho, rows[[i]]$coverage_naive, rows[[i]]$coverage_s10, rows[[i]]$coverage_mc))
}
res <- do.call(rbind, rows)
out <- "C:/Users/up201/.workbuddy/m4src/T5_coverage.csv"
write.csv(res, out, row.names = FALSE)
cat("\n=== T5 coverage summary (nominal 95%) ===\n")
print(res)
cat("\n[done] ->", out, "\n")
