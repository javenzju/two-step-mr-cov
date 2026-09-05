# ============================================================
# S16_bootstrap_fallback_indirect_var.R
# 【2026-07-03，对应D18第五节建议1：任务5重新打开，目标改为高pi_shared区间兜底】
#
# 背景：D18实测发现，只要 n_shared>0，weak_instrument_threshold() 给出的
# delta-method相对误差上界B就不再是"Var(indirect effect)"的可靠保护（详见
# weak_instrument_threshold_FIXED.R 里新加的 shared_channel_uncovered 门控）。
# 这里提供一个不依赖delta method线性化的替代估计：直接用与D18验证过的同一套
# 因果SEM结构做参数化模拟（不是重跑真实GWAS个体数据的经典bootstrap——summary
# 统计量层面拿不到个体数据，这里做的是"用summary统计量反推的参数校准模拟"，
# 命名沿用"bootstrap fallback"是延续D11任务5的叫法，实质是MC模拟）。
#
# 依赖：与 S15_B_delta_method_validation.R 用的是同一套已验证DGP逻辑，直接复用。
# ============================================================

# ============================================================
# 【2026-07-06 补丁，FIXED版】修复DGP不一致bug（用户要求做最差角交叉核对时实测发现）：
#
# 原版sim_one()用的是"因果SEM"DGP：gammaM_true_j = alpha_true * gammaX_true_j（逐SNP
# 确定性绑定），这是S07/S15第一版验证"F→∞时偏倚收敛到0"时用的DGP（见D18第二节），
# 目的是排查模拟是否正确编码了因果结构。
#
# 但S10当前落地的Var(alpha_hat)/Var(beta_hat)完整公式（.var_ratio_est_full()/
# .var_beta_with_rho()），是D19 S6.1/S6.2在D05原始"独立先验"DGP（gammaM_true、
# gammaY_true各自独立于自己的先验分布抽样，不逐SNP绑定gammaX_true/gammaM_true）下
# 推导和验证的（D18第七节："统一到同一套DGP（D05原始独立先验设定）后重新测试"）。
#
# 实测发现：用原版（因果SEM）DGP跑MC兜底，在D18/D19报告的最差角（F=10,pi_shared=0.7
# 和1.0）上，Var_indirect_MC系统性低估真实值约30-35%（两个独立种子结果几乎一致，
# 差异<1.5%，说明不是MC噪声，是DGP选择本身导致的系统偏差）——比它要兜底的delta method
# 本身（12-13%误差）还差，起不到"安全网"的作用。换成独立先验DGP重新验证后，
# 结果与真实值的误差降到<3%。
#
# 本FIXED版把sim_one()内部的gammaM_true/gammaY_true改为独立先验抽样（与S10/S17/S18
# 一致），alpha_true/beta_true只用来决定独立先验的均值位置（mu_M=alpha_true*mu_X，
# mu_Y=beta_true*mu_M），不再逐SNP确定性绑定。函数接口、返回值结构不变，
# 调用方（S10的estimate_cov_prod_mr()）无需修改即可切换使用。
# ============================================================

estimate_var_indirect_MC <- function(se_alpha, se_beta, n_shared, p_X, p_M, F_stat,
                                      rho_MY = 0, N, alpha_hat_obs = NULL, beta_hat_obs = NULL,
                                      n_reps = 10000, sd_prior_frac = 0.3, seed = NULL) {
  if (!is.null(seed)) set.seed(seed)

  used_placeholder <- is.null(alpha_hat_obs) || is.null(beta_hat_obs)
  alpha_true <- if (is.null(alpha_hat_obs)) 1 else alpha_hat_obs
  beta_true  <- if (is.null(beta_hat_obs))  1 else beta_hat_obs

  # ---- 单次模拟：改为独立先验DGP（与S10/S17/S18一致，见上方补丁说明）----
  sim_one <- function() {
    mu_X <- sqrt(F_stat / N); se_X <- 1/sqrt(N); se_M <- 1/sqrt(N); se_Y <- 1/sqrt(N)
    mu_M <- alpha_true * mu_X   # 用alpha_true定位独立先验的均值，不再逐SNP绑定
    mu_Y <- beta_true  * mu_M   # 同理

    gammaX_true <- rnorm(p_X, mu_X, sd_prior_frac * mu_X)
    gammaX_hat  <- gammaX_true + rnorm(p_X, 0, se_X)

    gammaM_true_for_step1 <- rnorm(p_X, mu_M, sd_prior_frac * mu_M)  # 独立先验，不绑定gammaX_true
    eps_M_step1 <- rnorm(p_X, 0, se_M)
    gammaM_hat_for_step1 <- gammaM_true_for_step1 + eps_M_step1

    A_alpha <- sum(gammaX_hat^2 / se_M^2)
    B_alpha <- sum(gammaX_hat * gammaM_hat_for_step1 / se_M^2)
    alpha_hat <- B_alpha / A_alpha

    if (n_shared > 0) {
      gammaM_hat_shared  <- gammaM_hat_for_step1[1:n_shared]
      eps_M_shared        <- eps_M_step1[1:n_shared]
    } else {
      gammaM_hat_shared <- numeric(0); eps_M_shared <- numeric(0)
    }
    if (p_M > n_shared) {
      gammaM_true_m_only <- rnorm(p_M - n_shared, mu_M, sd_prior_frac * mu_M)  # 独立先验
      eps_M_m_only <- rnorm(p_M - n_shared, 0, se_M)
      gammaM_hat_m_only <- gammaM_true_m_only + eps_M_m_only
    } else {
      gammaM_hat_m_only <- numeric(0); eps_M_m_only <- numeric(0)
    }
    gammaM_hat_for_step2  <- c(gammaM_hat_shared, gammaM_hat_m_only)
    eps_M_all             <- c(eps_M_shared, eps_M_m_only)

    gammaY_true <- rnorm(p_M, mu_Y, sd_prior_frac * mu_Y)  # 独立先验，不绑定gammaM_true
    eps_Y_all <- rho_MY * (se_Y/se_M) * eps_M_all + sqrt(max(0, 1 - rho_MY^2)) * rnorm(p_M, 0, se_Y)
    gammaY_hat <- gammaY_true + eps_Y_all

    A_beta <- sum(gammaM_hat_for_step2^2 / se_Y^2)
    B_beta <- sum(gammaM_hat_for_step2 * gammaY_hat / se_Y^2)
    beta_hat <- B_beta / A_beta

    c(alpha_hat = alpha_hat, beta_hat = beta_hat)
  }

  res <- t(replicate(n_reps, sim_one()))
  Var_alpha_MC <- var(res[, "alpha_hat"])
  Var_beta_MC  <- var(res[, "beta_hat"])
  Cov_MC       <- cov(res[, "alpha_hat"], res[, "beta_hat"])
  ind_hat      <- res[, "alpha_hat"] * res[, "beta_hat"]
  Var_indirect_MC <- var(ind_hat)

  list(
    Var_alpha_MC = Var_alpha_MC,
    Var_beta_MC  = Var_beta_MC,
    Cov_MC       = Cov_MC,
    Var_indirect_MC = Var_indirect_MC,
    se_indirect_MC  = sqrt(Var_indirect_MC),
    used_placeholder_true_values = used_placeholder,
    n_reps = n_reps
  )
}

# ============================================================
# 自检：用D18已知最差角验证FIXED版是否真的修好了（对照真实ground truth，
# 不再是"MC vs MC"自证——上一版的自检方式本身查不出DGP系统偏差这类问题，
# 这也是本次的一个教训：自检要对照独立的ground truth，不能只互相对照）
# ============================================================
if (sys.nframe() == 0L) {
  cat("=== 自检：FIXED版在D18最差角（F=10,pi_shared=0.7/1.0,rho=0）上对照真实ground truth ===\n")
  gt <- list(list(n_s=14, gt=0.014564341810805), list(n_s=20, gt=0.0121027764374715))
  for (g in gt) {
    r1 <- estimate_var_indirect_MC(se_alpha=0.05, se_beta=0.05, n_shared=g$n_s, p_X=20, p_M=20,
                                     F_stat=10, rho_MY=0, N=50000, n_reps=15000, seed=111)
    r2 <- estimate_var_indirect_MC(se_alpha=0.05, se_beta=0.05, n_shared=g$n_s, p_X=20, p_M=20,
                                     F_stat=10, rho_MY=0, N=50000, n_reps=15000, seed=222)
    avg <- mean(c(r1$Var_indirect_MC, r2$Var_indirect_MC))
    cat(sprintf("n_shared=%d: seed111=%.6f seed222=%.6f 均值=%.6f ground_truth=%.6f 相对误差=%.1f%%\n",
                g$n_s, r1$Var_indirect_MC, r2$Var_indirect_MC, avg, g$gt,
                abs(avg-g$gt)/g$gt*100))
  }
}
