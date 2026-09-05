# ============================================================
# S10_prod_mr_cov_tool.R
# 两步法乘积MR：Cov(α̂, β̂) 诊断与估计工具
#
# 任务1（cov估计）+ 任务2（weak_instrument_threshold弱工具变量判定）整合版
# 2026-07-03 正式合并：按D01最初设计意图，任务1不再用自己内部的简化
# .reliability_check()，改为直接调用已验收的任务2 weak_instrument_threshold()
# 做风险判定（D11第八节：任务2 ✅ 验收，任务6 ✅ 验收，本次一并整合）
#
# 输入：论文可报告的 summary 统计量
# 输出：Cov(α̂, β̂) 的解析估计、weak_instrument_threshold()风险评级、精度警告
#
# 依赖：weak_instrument_threshold_FIXED.R（需与本文件放在同一 scripts/ 目录下）
#
# 【2026-07-03 补充，见D02"已知的坑"】原版 .this_dir 只用 sys.frame(1)$ofile
# 探测路径，这只在 `Rscript S10_prod_mr_cov_tool.R`（命令行）方式运行时有效；
# 用户在RStudio点"Source"按钮运行时该值为空，会静默退化到错误的工作目录。
# 本项目在S03/S06/S07/S09/S11已确立"rstudioapi fallback"的标准做法，本文件
# 补上同样的三层探测，避免用户被迫手动硬编码绝对路径（后者在换机器/换人跑
# 时会直接失效）。若项目里已有统一的 .get_script_path() 辅助函数，建议直接
# 复用那个以保持一致，而不是用下面这套独立实现。
.get_this_script_dir <- function() {
  # 第一层：Rscript 命令行运行 —— 正确做法是解析 commandArgs 里的 --file=
  # （sys.frame(1)$ofile 只在 source() 调用链里才会被设置，Rscript顶层执行
  #  根本不会填这个值——上一版想当然以为它对Rscript有效，实测直接报错，
  #  这里改用真正对Rscript生效的commandArgs方式）
  cmd_args <- commandArgs(trailingOnly = FALSE)
  file_arg <- grep("^--file=", cmd_args, value = TRUE)
  if (length(file_arg) > 0) return(dirname(normalizePath(sub("^--file=", "", file_arg[1]))))
  # 第二层：RStudio 内 source() 运行，用 rstudioapi 取当前编辑器文件路径
  if (requireNamespace("rstudioapi", quietly = TRUE) &&
      rstudioapi::isAvailable() && rstudioapi::hasFun("getSourceEditorContext")) {
    ctx_path <- tryCatch(rstudioapi::getSourceEditorContext()$path, error = function(e) "")
    if (nzchar(ctx_path)) return(dirname(ctx_path))
  }
  # 第三层：都探测不到，退化到当前工作目录（与本项目weak_instrument_threshold.R
  # 自检部分`%||% "."`的既有降级习惯保持一致），同时给出提示而非静默出错
  message("[提示] 无法自动探测脚本路径，按当前工作目录寻找 weak_instrument_threshold_FIXED.R；",
          "若报错找不到文件，请先 setwd() 到scripts目录，或设置 options(S10_script_dir=...)")
  "."
}
.this_dir <- getOption("S10_script_dir", .get_this_script_dir())
source(file.path(.this_dir, "weak_instrument_threshold_FIXED.R"))
source(file.path(.this_dir, "S16_bootstrap_fallback_indirect_var_FIXED.R"))

# ---- 目录规范（2026-07-06按用户实际部署方式调整）--------------------------
# 【与S03/S11等脚本的差异说明】那些脚本放在 scripts/ 子目录下，proj_root要
# 往上退两层（dirname(dirname(...)))。本脚本连同两个依赖文件直接放在项目
# 根目录 D:\数据分析\科研选题\两步法MR中介\ 下（用户明确的部署方案），
# 所以 proj_root 就是 .this_dir 本身，只退一层会退过头。
proj_root <- .this_dir
log_dir   <- file.path(proj_root, "log")
temp_dir  <- file.path(proj_root, "temp")
figure_dir<- file.path(proj_root, "figure")
dir.create(log_dir,    showWarnings = FALSE, recursive = TRUE)
dir.create(temp_dir,   showWarnings = FALSE, recursive = TRUE)
dir.create(figure_dir, showWarnings = FALSE, recursive = TRUE)
# 【说明】本脚本目前只产生log，不产生temp/figure文件（estimate_cov_prod_mr()
# 和batch_evaluate_cov()都只返回R对象，不落盘）；temp_dir/figure_dir先按统一
# 规范建好，供后续如需导出批量评估结果CSV或诊断图时直接复用，不必另起路径逻辑。

LOG_FILE <- file.path(log_dir, paste0("S10_prod_mr_cov_tool_",
                                       format(Sys.time(), "%Y%m%d_%H%M%S"), ".log"))

.log <- function(...) {
  msg <- paste0("[", format(Sys.time(), "%H:%M:%S"), "] ", paste0(..., collapse = ""))
  cat(msg, "\n", file = LOG_FILE, append = TRUE)
}

# ============================================================
# 内部辅助：MC估计 Cov(γ̂_Mj, β̂) ——共享SNP通道的核心参数
# 依赖 summary 统计量，无需个体数据
# ============================================================
.compute_cov_gM_beta_mc <- function(mu_M, mu_Y, se_M, se_Y, p_M,
                                     sd_prior_frac = 0.3,
                                     n_mc = 100000) {
  .log(sprintf("  MC估计 Cov(gM_j,beta): mu_M=%.4e mu_Y=%.4e se_M=%.4e se_Y=%.4e p_M=%d n_mc=%d",
               mu_M, mu_Y, se_M, se_Y, p_M, n_mc))
  # Z = gM_hat_j（单个共享SNP的M效应估计）
  Z <- rnorm(n_mc, mu_M, mu_M * sd_prior_frac) + rnorm(n_mc, 0, se_M)
  # C = A_{-j}（其余 p_M-1 个SNP的A_beta贡献，与Z独立）
  gM_oth <- matrix(rnorm(n_mc * (p_M - 1), mu_M, mu_M * sd_prior_frac),
                   n_mc, p_M - 1) +
            matrix(rnorm(n_mc * (p_M - 1), 0, se_M), n_mc, p_M - 1)
  C <- rowSums(gM_oth^2 / se_Y^2)
  # W = gY_hat_j（独立，ρ_MY=0基线）
  W <- rnorm(n_mc, mu_Y, mu_Y * sd_prior_frac) + rnorm(n_mc, 0, se_Y)
  E_Bp   <- (p_M - 1) * mu_M * mu_Y / se_Y^2
  A_beta <- Z^2 / se_Y^2 + C
  beta_h <- (Z * W / se_Y^2 + E_Bp) / A_beta
  result <- as.numeric(cov(Z, beta_h))   # cov()作用于两个向量时直接返回标量，无需索引
  .log(sprintf("  Cov(gM_j,beta) = %.4e", result))
  result
}

# ============================================================
# 【2026-07-03移除】原内部 .reliability_check()/.build_warn() 已删除，
# 精度可靠性诊断改为直接调用任务2已验收的 weak_instrument_threshold()
# （见 estimate_cov_prod_mr() 主函数内的调用），不再维护重复的简化版逻辑。

# ============================================================
# 主函数：estimate_cov_prod_mr()
# ============================================================
#' 估计两步乘积MR的 Cov(α̂, β̂) 并给出风险评级
#'
#' @param se_alpha   SE(α̂)：从论文中读取的第一步效应估计标准误
#' @param se_beta    SE(β̂)：从论文中读取的第二步效应估计标准误
#' @param n_shared   共享SNP数量（G'_X ∩ G'_M 的大小）
#' @param p_X        第一步工具变量总数
#' @param p_M        第二步工具变量总数
#' @param F_stat     第一步F统计量（工具变量强度，来自论文报告）
#' @param rho_MY     M-GWAS与Y-GWAS样本重叠比例（0=完全独立）
#' @param N          GWAS样本量（如三步用同一N则统一填写）
#' @param sd_prior_frac  效应量先验变异系数（默认0.3，与模拟一致）
#' @param n_mc       MC估计的样本量（精度与速度的权衡，默认100000）
#' @param seed       随机种子，NULL(默认)不固定（结果有5.7%-9.9%波动，见D21 3.2节）
#' @param verbose    是否打印详细信息
#'
#' @return list，包含：
#'   cov_shared     共享SNP通道估计值
#'   cov_rho        样本重叠通道估计值
#'   cov_total      总Cov估计值
#'   risk_score     协方差风险评分（数值）
#'   risk_level     风险等级（"低"/"中"/"高"）
#'   warning_msg    精度警告文字
#'   se_indirect_corrected  修正后的间接效应SE（如提供alpha_hat和beta_hat）
estimate_cov_prod_mr <- function(
    se_alpha,
    se_beta,
    n_shared,
    p_X,
    p_M,
    F_stat,
    rho_MY    = 0,
    N         = NULL,
    N_X       = N, N_M = N, N_Y = N,
    sd_prior_frac = 0.3,
    n_mc      = 100000,
    alpha_hat_obs = NULL,   # 【2026-07-03新增，D18兜底】论文报告的alpha点估计，供MC兜底用作模拟锚点
    beta_hat_obs  = NULL,   # 同上，beta点估计；两者都不提供时MC兜底用1,1占位（见S16说明）
    run_mc_fallback = TRUE, # 触发条件已收窄为residual_caution(F<15且pi_shared>0.5)，见D18第七节
    n_reps_mc = 10000,      # MC兜底重复次数，默认与D18最终确认档位一致
    seed      = NULL,       # 【2026-07-06新增，D21 3.2节】固定MC估计的随机种子以保证结果可复现；
                            # NULL(默认)保持原行为（每次调用结果有5.7%-9.9%波动，见D21）
    verbose   = TRUE
) {
  if (!is.null(seed)) set.seed(seed)
  # ---- 输入校验 --------------------------------------------------
  stopifnot(
    "se_alpha 必须为正数" = se_alpha > 0,
    "se_beta 必须为正数"  = se_beta  > 0,
    "n_shared 必须为非负整数" = n_shared >= 0 && n_shared == round(n_shared),
    "n_shared 不能超过 min(p_X, p_M)" = n_shared <= min(p_X, p_M),
    "|rho_MY| 必须 ≤ 1" = abs(rho_MY) <= 1
  )

  # ---- 从 SE 反推量级参数 ----------------------------------------
  # 【2026-07-03 两轮修正，见 D17_prod_mr_cov_tool_summary_stat_fix.md 完整过程】
  #
  # 第一轮尝试（"固定效应SE假设"，E_inv_Aa<-se_alpha^2）已被证伪：
  # 用D05表2 ground truth（F=30,pi_shared=0.5,n_s=10 => theory=-2.01e-3）实测对照，
  # 算出cov_shared=-7.43e-3，偏离3.7倍，且仍违反Cauchy-Schwarz。
  # 原因：D05模拟里SNP间效应量异质性(0.3μ)是数据生成过程本身自带的，
  # Var(α̂|γ_X)=v_M/(σ_M²·A_α) 恒成立（v_M含异质性项），不是"论文报告哪种SE"
  # 的选择问题，无法通过重新诠释se_alpha的含义来绕开。
  #
  # 【当前做法，已实测对齐D05 ground truth】E[1/A_α]、E[1/A_β] 完全由 F/N/p_X
  # 通过理论公式计算（E[A]=p·(μ²+v)/σ²，v=(0.3μ)²+σ²），不使用用户输入的
  # se_alpha/se_beta。se_alpha/se_beta 仅用于：
  #   (a) 下方Cauchy-Schwarz合理性校验
  #   (b) 与理论隐含se_alpha的交叉校验提示（偏离过大说明该论文结构超出本工具假设）
  #   (c) 最终Var(αβ)修正公式的展示（那里必须用论文真实报告的SE，不能用理论值）

  if (!is.null(N_M)) {
    if (is.null(N_X)) N_X <- N_M
    se_M <- 1 / sqrt(N_M)
    se_Y <- 1 / sqrt(N_Y)
    mu_X <- sqrt(F_stat / N_X)
    mu_M <- sqrt(F_stat / N_M)
    mu_Y <- sqrt(F_stat / N_Y)
  } else {
    N_M_est <- round(1 / (p_X * F_stat * se_alpha^2))
    N_Y_est <- round(1 / (p_M * F_stat * se_beta^2))
    se_M    <- 1 / sqrt(N_M_est)
    se_Y    <- 1 / sqrt(N_Y_est)
    mu_X    <- sqrt(F_stat / N_M_est)
    mu_M    <- sqrt(F_stat / N_M_est)
    mu_Y    <- sqrt(F_stat / N_Y_est)
    if (verbose) cat(sprintf(
      "[信息] N未提供，从se_alpha反推：N_M≈%.0f，N_Y≈%.0f\n", N_M_est, N_Y_est))
  }

  v_X <- (sd_prior_frac * mu_X)^2 + se_M^2
  v_M <- (sd_prior_frac * mu_M)^2 + se_M^2
  v_Y <- (sd_prior_frac * mu_Y)^2 + se_Y^2
  E_A_alpha <- p_X * (mu_X^2 + v_X) / se_M^2
  E_A_beta  <- p_M * (mu_M^2 + v_M) / se_Y^2
  E_inv_Aa <- 1 / E_A_alpha
  E_inv_Ab <- 1 / E_A_beta

  # 【2026-07-03新增，见D18续篇】Var(alpha_hat)/Var(beta_hat)的完整解析式：
  # 全方差公式 Var(alpha_hat) = E[Var(alpha_hat|gammaX)] + Var(E[alpha_hat|gammaX])。
  # E_inv_Aa*（v_M/se_M^2）只是第一项；第二项此前完全没人算过，实测发现量级上
  # 跟第一项相当（不是可忽略的小修正），是B之前被验证"不成立"的真正主因
  # （不是共享SNP通道缺项，是Var(alpha_hat)/Var(beta_hat)本身被系统性低估）。
  # 已用"固定gammaX只重随机化gammaM"的条件模拟验证条件方差部分（比值1.03），
  # 用delta method展开S1=Σγ_X,hat、S2=Σγ_X,hat²的比值解析推出第二项（比值0.98）。
  .var_ratio_est_full <- function(mu, v, p, se) {
    Q <- mu^2 + v
    E_A <- p * Q / se^2
    term_cond <- (v / se^2) * (1 / E_A)
    t1 <- v/Q^2; t2 <- 4*mu^2*v/Q^3; t3 <- mu^2*(4*mu^2*v+2*v^2)/Q^4
    term_uncond <- mu^2 * (t1 - t2 + t3) / p
    term_cond + term_uncond
  }
  Var_alpha_full <- .var_ratio_est_full(mu_X, v_X, p_X, se_M)
  # alpha不受rho_MY影响：Step1回归不涉及Y-GWAS，gammaX与gammaY无直接关联

  # 【2026-07-03再追加，见D18第七节ρ_MY残留项】Var(beta_hat)本身还依赖rho_MY：
  # gammaY_hat的测量噪声与gammaM_hat的测量噪声相关(rho_MY)，条件在gammaM_hat已知时，
  # 用"两个独立正态变量给定和后的条件分布"标准结果，gammaY_hat的条件方差被压缩为
  # v_Y - rho^2*se_Y^2*se_M^2/v_M（而非原本的v_Y），条件均值的线性系数也相应改变。
  # 已验证：n_s=0隔离场景下，旧公式（无rho项）比值从rho=0的1.02一路掉到rho=1的0.78，
  # 新公式（含rho修正）三个rho值下比值都稳定在1.02附近。
  .var_beta_with_rho <- function(mu_M, mu_Y, v_M, v_Y, p_M, se_M, se_Y, rho_MY) {
    E_A_beta <- p_M * (mu_M^2 + v_M) / se_Y^2
    v_Y_cond <- v_Y - rho_MY^2 * se_Y^2 * se_M^2 / v_M
    term_cond <- (v_Y_cond / se_Y^2) * (1 / E_A_beta)
    Q_M <- mu_M^2 + v_M
    t1 <- v_M/Q_M^2; t2 <- 4*mu_M^2*v_M/Q_M^3; t3 <- mu_M^2*(4*mu_M^2*v_M+2*v_M^2)/Q_M^4
    Var_R <- (t1 - t2 + t3) / p_M
    coef <- mu_Y - rho_MY * se_M * se_Y * mu_M / v_M
    term_cond + coef^2 * Var_R
  }
  Var_beta_full <- .var_beta_with_rho(mu_M, mu_Y, v_M, v_Y, p_M, se_M, se_Y, rho_MY)

  # ---- 交叉校验：理论隐含的se_alpha/se_beta vs 用户报告值 -----------
  se_alpha_theo <- sqrt(Var_alpha_full)  # 修正：用含二阶项的完整式，不再用(v_M/se_M^2)*E_inv_Aa这个只含一半的近似
  se_beta_theo  <- sqrt(Var_beta_full)
  ratio_alpha <- se_alpha / se_alpha_theo
  ratio_beta  <- se_beta  / se_beta_theo
  consistency_msg <- if (ratio_alpha < 0.5 || ratio_alpha > 2 ||
                          ratio_beta  < 0.5 || ratio_beta  > 2) {
    sprintf("输入se_alpha/se_beta与F/N/p_X隐含的理论值偏离较大（se_alpha实测/理论=%.2f，se_beta实测/理论=%.2f）：该论文的工具变量结构或效应异质性程度可能偏离本工具的0.3先验假设，结果仅供参考",
            ratio_alpha, ratio_beta)
  } else {
    NULL
  }

  .log(sprintf("参数: n_s=%.0f p_X=%.0f p_M=%.0f F=%g rho=%.2f",
               n_shared, p_X, p_M, F_stat, rho_MY))
  .log(sprintf("推算: se_M=%.4e se_Y=%.4e mu_M=%.4e", se_M, se_Y, mu_M))
  .log(sprintf("推算: E[1/Aa]=%.4e E[1/Ab]=%.4e", E_inv_Aa, E_inv_Ab))

  # ---- 精度可靠性诊断：调用任务2已验收的 weak_instrument_threshold() ------
  # 2026-07-03整合：不再用本文件内部的简化 .reliability_check()，改为直接调用
  # D11/D16已验收（含D14/D15的sqrt->线性修正）的正式判定函数，pi_shared按其
  # 文档定义（n_s/p_M，共享SNP比例）传入。
  pi_shared_val <- n_shared / p_M
  mc_fallback <- NULL
  if (n_shared == 0) {
    rel <- list(risk_overall = "低", warn_msg =
      "n_shared=0：两条通道均不活跃，Cov(α̂,β̂)=0（代数精确），无精度问题")
  } else {
    wit <- weak_instrument_threshold(F = F_stat, rho_MY = rho_MY,
                                      pi_shared = pi_shared_val, epsilon = 0.10)
    risk_cn <- c(low = "低", moderate = "中", high = "高")[wit$risk_level]
    rel <- list(risk_overall = unname(risk_cn), warn_msg = wit$diagnostic,
                rel_err_bound = wit$rel_err_bound, is_reliable = wit$is_reliable)

    # 【2026-07-03新增，D18第五节建议1】共享SNP通道门控触发时，delta method的
    # Var(indirect effect)已知不可信（哪怕是正数也可能大幅低估），自动跑MC兜底
    if (isTRUE(wit$residual_caution) && run_mc_fallback) {
      N_for_mc <- if (!is.null(N_M)) N_M else round(1/(p_X*F_stat*se_alpha^2))
      mc_fallback <- estimate_var_indirect_MC(
        se_alpha = se_alpha, se_beta = se_beta, n_shared = n_shared,
        p_X = p_X, p_M = p_M, F_stat = F_stat, rho_MY = rho_MY, N = N_for_mc,
        alpha_hat_obs = alpha_hat_obs, beta_hat_obs = beta_hat_obs,
        n_reps = n_reps_mc)
      if (verbose) .log(sprintf(
        "MC兜底(D18门控触发): Var_indirect_MC=%.4e se_indirect_MC=%.4e 用占位真值=%s",
        mc_fallback$Var_indirect_MC, mc_fallback$se_indirect_MC,
        mc_fallback$used_placeholder_true_values))
    }
  }

  # ---- 共享SNP通道 -----------------------------------------------
  if (n_shared == 0) {
    cov_shared <- 0
    .log("n_shared=0，共享SNP通道 Cov=0（代数精确）")
  } else {
    Cov_Z_beta <- .compute_cov_gM_beta_mc(
      mu_M, mu_Y, se_M, se_Y, p_M, sd_prior_frac, n_mc)
    cov_shared <- n_shared * (mu_X / se_M^2) * E_inv_Aa * Cov_Z_beta
    .log(sprintf("共享SNP通道: n_s*(mu_X/se_M^2)*E_inv_Aa*CovZb = %.4e", cov_shared))
  }

  # ---- ρ_MY 通道 -------------------------------------------------
  if (rho_MY == 0 || n_shared == 0) {
    cov_rho <- 0
    .log("rho_MY=0 或 n_shared=0，ρ_MY通道 Cov=0")
  } else {
    cov_rho <- n_shared * rho_MY * mu_X * mu_M / (se_M * se_Y) * E_inv_Aa * E_inv_Ab
    .log(sprintf("ρ_MY通道: n_s*rho*mu_X*mu_M/(se_M*se_Y)*E[1/Aa]*E[1/Ab] = %.4e", cov_rho))
  }

  cov_total <- cov_shared + cov_rho

  # ---- Cauchy-Schwarz 合理性校验（新增，2026-07-03）------------------
  # |Cov(alpha_hat,beta_hat)| <= SD(alpha_hat)*SD(beta_hat) = se_alpha*se_beta
  # 恒成立，这是任意两个有限方差随机变量协方差的数学硬约束，与近似公式是否
  # 精确无关。若违反，说明输入参数（尤其se_alpha/se_beta与F/N/p_X的组合）已经
  # 超出本工具简化模型的适用范围，不应静默返回一个数学上不可能的数字。
  cs_bound <- se_alpha * se_beta
  cs_violated <- abs(cov_total) > cs_bound
  cov_total_raw <- cov_total
  if (cs_violated) {
    cov_total <- sign(cov_total) * cs_bound * 0.999  # 截断到理论上界内，仅作保守展示
    cov_shared_frac <- cov_shared / cov_total_raw
    cov_total <- cov_total  # cap后的值用于后续风险评分和展示
  }

  # ---- 风险评分（连续值） ----------------------------------------
  # 基于 |Cov_total| / (se_alpha * se_beta) 的标准化量
  risk_score <- abs(cov_total) / (se_alpha * se_beta)

  # ---- SE修正 ----------------------------------------------------
  # Var(α̂β̂) = β²*Var(α̂) + α²*Var(β̂) + 2αβ*Cov(α̂,β̂)（忽略高阶项）
  # 但我们没有 α, β 的真值，只有 SE，所以提供 Cov 本身供用户代入
  # 如果用户提供了 alpha_hat 和 beta_hat，可以给出修正的 SE

  combined_warn_parts <- c(
    rel$warn_msg,
    if (cs_violated) sprintf(
      "🚨 Cauchy-Schwarz上界被违反：|Cov_raw|=%.4e > se_alpha*se_beta=%.4e，已截断展示为%.4e，说明输入参数组合超出本工具适用范围（很可能是se_alpha/se_beta与F/N/p_X不自洽，或n_shared/p_X比例过高），不建议直接采用此结果",
      abs(cov_total_raw), cs_bound, cov_total) else NULL,
    consistency_msg
  )
  combined_warn_msg <- paste(combined_warn_parts[!vapply(combined_warn_parts, is.null, logical(1))],
                              collapse = "；\n  ")

  result <- list(
    # 核心估计
    cov_shared   = cov_shared,
    cov_rho      = cov_rho,
    cov_total    = cov_total,
    cov_total_raw = cov_total_raw,
    cs_violated  = cs_violated,
    # 诊断
    risk_score   = risk_score,
    risk_level   = rel$risk_overall,
    rel_err_bound = rel$rel_err_bound,
    is_reliable   = rel$is_reliable,
    warning_msg  = combined_warn_msg,
    se_alpha_theo = se_alpha_theo,
    se_beta_theo  = se_beta_theo,
    # 【2026-07-03新增，D18门控】MC兜底结果（门控触发且run_mc_fallback=TRUE时非空）
    mc_fallback  = mc_fallback,
    # 中间量（供调试和论文引用）
    E_inv_A_alpha = E_inv_Aa,
    E_inv_A_beta  = E_inv_Ab,
    mu_X = mu_X, mu_M = mu_M, mu_Y = mu_Y,
    se_M = se_M, se_Y = se_Y
  )

  if (verbose) .print_result(result, se_alpha, se_beta, n_shared, p_X, p_M,
                              F_stat, rho_MY)
  invisible(result)
}

# ---- 格式化输出 ---------------------------------------------------
.print_result <- function(r, se_alpha, se_beta, n_shared, p_X, p_M, F_stat, rho_MY) {
  risk_icon <- c("低" = "✅", "中" = "⚠️ ", "高" = "🚨")
  cat("\n", strrep("=", 60), "\n")
  cat(" 两步法乘积MR协方差诊断报告\n")
  cat(strrep("=", 60), "\n")
  cat(sprintf(" 输入参数：n_shared=%.0f  p_X=%.0f  p_M=%.0f  F=%.0f  ρ_MY=%.2f\n",
              n_shared, p_X, p_M, F_stat, rho_MY))
  cat(strrep("-", 60), "\n")
  cat(sprintf(" Cov(α̂,β̂) 估计\n"))
  cat(sprintf("   共享SNP通道：  %+.4e\n", r$cov_shared))
  cat(sprintf("   样本重叠通道： %+.4e\n", r$cov_rho))
  cat(sprintf("   合计：         %+.4e\n", r$cov_total))
  cat(strrep("-", 60), "\n")
  cat(sprintf(" 风险评级：%s %s（协方差风险评分 = %.3f）\n",
              risk_icon[r$risk_level], r$risk_level, r$risk_score))
  if (!is.null(r$rel_err_bound)) {
    cat(sprintf("   weak_instrument_threshold(): 相对误差上界=%.1f%%  is_reliable=%s\n",
                r$rel_err_bound * 100, r$is_reliable))
  }
  cat(strrep("-", 60), "\n")
  cat(" 精度提示：\n  ", r$warning_msg, "\n")
  cat(strrep("-", 60), "\n")
  if (!is.null(r$mc_fallback)) {
    mc <- r$mc_fallback
    cat(" 🔧 MC兜底估计（D18门控触发，delta method的Var(indirect effect)不可信）：\n")
    cat(sprintf("   Var(indirect effect)_MC = %.4e   SE_MC = %.4e\n",
                mc$Var_indirect_MC, mc$se_indirect_MC))
    if (mc$used_placeholder_true_values) {
      cat("   ⚠️ 未提供alpha_hat_obs/beta_hat_obs，模拟锚点用了1,1占位——建议提供论文真实\n")
      cat("      点估计后重跑，当前MC结果的相对误差量级可参考，绝对量级不建议直接采信\n")
    }
    cat("   建议：优先采用此MC估计而非下方delta method公式算出的cov_total\n")
    cat(strrep("-", 60), "\n")
  }
  cat(sprintf(" 间接效应SE修正参考：\n"))
  cat(sprintf("   传统SE(αβ) 计算忽略此 Cov 项，相当于假设 Cov=0\n"))
  cat(sprintf("   修正公式：Var(αβ) = β²·SE(α)² + α²·SE(β)² + 2αβ·Cov(α̂,β̂)\n"))
  cat(sprintf("   使用说明：将 cov_total=%.4e 代入上式计算修正后Var\n", r$cov_total))
  if (!is.null(r$mc_fallback)) {
    cat("   （本场景下更建议直接用上方MC兜底给出的Var(indirect effect)_MC，而非此式）\n")
  }
  cat(strrep("=", 60), "\n\n")
}

# ============================================================
# 辅助函数：批量评估（供文献库重新评估使用）
# ============================================================
#' 对一批已发表论文做批量协方差诊断
#'
#' @param df  data.frame，每行一篇论文，列名需包含：
#'            se_alpha, se_beta, n_shared, p_X, p_M, F_stat
#'            可选：rho_MY（默认0），N_M, N_Y
#' @param n_mc  每次MC的样本量（批量时建议用小值10000节省时间）
batch_evaluate_cov <- function(df, n_mc = 10000, verbose = FALSE) {
  .log(sprintf("批量评估：%d 篇论文", nrow(df)))

  results <- lapply(seq_len(nrow(df)), function(i) {
    row <- df[i, ]
    tryCatch({
      r <- estimate_cov_prod_mr(
        se_alpha  = as.numeric(row$se_alpha),
        se_beta   = as.numeric(row$se_beta),
        n_shared  = as.integer(row$n_shared),
        p_X       = as.integer(row$p_X),
        p_M       = as.integer(row$p_M),
        F_stat    = as.numeric(row$F_stat),
        rho_MY    = if ("rho_MY" %in% names(row)) as.numeric(row$rho_MY) else 0,
        N_M       = if ("N_M" %in% names(row)) as.numeric(row$N_M) else NULL,
        N_Y       = if ("N_Y" %in% names(row)) as.numeric(row$N_Y) else NULL,
        n_mc      = n_mc,
        verbose   = verbose
      )
      data.frame(
        row_id      = i,
        cov_total   = r$cov_total,
        cov_shared  = r$cov_shared,
        cov_rho     = r$cov_rho,
        risk_score  = r$risk_score,
        risk_level  = r$risk_level,
        warning_msg = r$warning_msg,
        stringsAsFactors = FALSE
      )
    }, error = function(e) {
      .log(sprintf("  第%.0f行出错: %s", i, e$message))
      data.frame(row_id=i, cov_total=NA, cov_shared=NA, cov_rho=NA,
                 risk_score=NA, risk_level="错误", warning_msg=e$message,
                 stringsAsFactors=FALSE)
    })
  })

  result_df <- do.call(rbind, results)
  .log(sprintf("批量评估完成：高风险=%.0f  中风险=%.0f  低风险=%.0f",
               sum(result_df$risk_level=="高", na.rm=TRUE),
               sum(result_df$risk_level=="中", na.rm=TRUE),
               sum(result_df$risk_level=="低", na.rm=TRUE)))
  result_df
}

# ============================================================
# 使用示例（source后自动运行，按需注释掉）
# ============================================================
if (interactive() || !exists(".tool_loaded")) {
  .tool_loaded <- TRUE
  cat("\n===== prod_mr_cov_tool.R 加载完毕 =====\n")
  cat("主函数：estimate_cov_prod_mr()\n")
  cat("批量函数：batch_evaluate_cov(df)\n\n")

  cat("--- 示例1：典型两步MR论文（中度共享，无样本重叠）---\n")
  ex1 <- estimate_cov_prod_mr(
    se_alpha = 0.05,   # SE(α̂)，来自论文Table
    se_beta  = 0.04,   # SE(β̂)，来自论文Table
    n_shared = 10,     # 共享SNP数量
    p_X = 20, p_M = 20,
    F_stat = 30,       # 第一步F统计量
    rho_MY = 0,        # 无样本重叠
    N_M = 50000, N_Y = 50000
  )

  cat("--- 示例2：高共享比例 + 样本重叠（高风险场景）---\n")
  ex2 <- estimate_cov_prod_mr(
    se_alpha = 0.05,
    se_beta  = 0.04,
    n_shared = 20,
    p_X = 20, p_M = 20,
    F_stat = 15,       # 弱工具变量
    rho_MY = 0.5,      # 中度样本重叠
    N_M = 50000, N_Y = 50000
  )

  cat("--- 示例3：π_shared=0（无共享SNP，Cov应精确为0）---\n")
  ex3 <- estimate_cov_prod_mr(
    se_alpha = 0.05,
    se_beta  = 0.04,
    n_shared = 0,      # 完全不重叠
    p_X = 20, p_M = 20,
    F_stat = 30,
    rho_MY = 0.8,
    N_M = 50000, N_Y = 50000
  )

  cat("--- 示例4：批量评估（文献库）---\n")
  literature_batch <- data.frame(
    study_id  = c("Smith2021", "Jones2022", "Wang2023"),
    se_alpha  = c(0.05, 0.08, 0.03),
    se_beta   = c(0.04, 0.06, 0.05),
    n_shared  = c(15,   8,    20),
    p_X       = c(20,   15,   25),
    p_M       = c(20,   15,   25),
    F_stat    = c(30,   12,   45),
    rho_MY    = c(0,    0.3,  0),
    N_M       = c(50000, 30000, 80000),
    N_Y       = c(50000, 30000, 80000)
  )
  batch_results <- batch_evaluate_cov(literature_batch, n_mc = 20000)
  cat("\n批量评估结果：\n")
  print(batch_results[, c("row_id","cov_total","risk_score","risk_level")])

  cat("\n工具运行完毕。log文件：", LOG_FILE, "\n")
}
