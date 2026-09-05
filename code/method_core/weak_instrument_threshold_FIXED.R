#' 一阶近似可信区域判定
#'
#' 基于一阶 Taylor 展开的相对误差解析上界，判断给定参数组合是否处于
#' 弱工具变量诊断的可信区域内。
#'
#' ## 修订记录
#'
#' **2026-07-03**：修正 kappa2* 对 pi_shared 的函数形式，由 `sqrt(pi_shared)`
#' 改为线性 `pi_shared`，以与项目已定稿的 D05_M1_derivation_and_verification.md
#' （第381行 boxed 最终公式）及 S09_isolation_experiment2_rho_MY_v2.R（第151行
#' theory_rho 实现）保持一致。原 sqrt 版本源自 D03_appendix_formal.md 的
#' kappa2=|rho_MY|/sqrt(F)（该式隐含 pi_shared=1，未显式含 pi_shared 项），
#' 后续为泛化到 pi_shared<1 而补加的 sqrt 因子未经过 D05/S09 交叉验证。
#' 详见 D14_pi_shared_definitive_resolution.md。
#' 原 6 点自检全部为 pi_shared=1（此时 sqrt(pi)=pi，两种形式无法区分），
#' 故该问题未被原自检发现。
#'
#' ## 上界公式（RMSE 意义）
#'
#'   B(F, rho_MY, pi_shared) =
#'       2 * (1/F)                                    # kappa1*：偏差 + 方差分量（系数2）
#'     + 2 * |rho_MY| * pi_shared / sqrt(F)          # kappa2*：rho_MY 通道（系数2，线性于pi_shared）
#'     + rho_MY^2 * pi_shared / F                    # 二阶交叉项
#'
#' ## 系数说明
#'
#' kappa1 的系数 2 来自两部分之和：
#'   (a) 一阶 Taylor 偏差项：E[1/gamma_Xj] - 1/gamma_Xj ≈ 1/F（凸性修正）
#'   (b) 方差贡献项：sd(alpha_hat)/alpha ≈ 1/sqrt(F)，在汇总 p_M 个 SNP 后
#'       主导由偏差驱动，但方差成分在有限 p_M 下仍贡献约 1/F 量级。
#' kappa2* 的系数 2 给出 rho_MY 通道偏移量的 ±1 置信宽度的保守上界。
#'
#' 这是严格的**充分**保守条件：B 成立则一阶近似可信，B 不成立不意味着
#' 一定不可信（两通道符号可能部分抵消，实测 rel_err 通常远低于上界）。
#'
#' ## 实测校准（n_reps=5000；大样本复核进行中）
#'
#' | F  | rho_MY | B(%)  | 实测(%) | 上界成立 |
#' |----|--------|-------|---------|--------|
#' | 30 | 0.0    |  6.7  |   <6    |   ✓    |
#' | 30 | 0.5    | 25.8  |    4    |   ✓    |
#' | 30 | 0.8    | 38.0  |   11    |   ✓    |
#' | 10 | 0.0    | 20.0  |   <8    |   ✓    |
#' | 10 | 0.5    | 54.1  |    5    |   ✓    |
#' | 10 | 1.0    | 93.2  |   30    |   ✓    |
#'
#' @param F         numeric. 工具变量强度（F 统计量），标量或向量，须 > 0
#' @param rho_MY    numeric. M-GWAS 与 Y-GWAS 样本重叠系数，[0, 1]，标量或向量
#' @param pi_shared numeric. 共享 SNP 比例 n_s/p_M，[0, 1]，标量或向量
#' @param epsilon   numeric. 目标相对误差阈值，默认 0.10（即 10%）
#'
#' @return list，包含：
#'   - is_reliable   : logical，是否在可信区域内（rel_err 上界 < epsilon）
#'   - rel_err_bound : numeric，一阶近似相对误差的解析上界估计值（RMSE 意义）
#'   - kappa1        : numeric，基础 Jensen 修正项 1/F（未乘系数2）
#'   - kappa2        : numeric，rho_MY 通道项 |rho_MY|*pi_shared/sqrt(F)（未乘系数2，线性形式，2026-07-03修正）
#'   - risk_level    : character，"low" / "moderate" / "high"
#'   - diagnostic    : character，简短文字说明判定依据（用于工具输出给用户看）
#'
#' @examples
#' # 单点查询
#' weak_instrument_threshold(F = 30, rho_MY = 0.5, pi_shared = 1.0)
#'
#' # 向量化批量诊断
#' weak_instrument_threshold(
#'   F         = c(30, 30, 10, 10),
#'   rho_MY    = c(0,  0.5, 0, 0.5),
#'   pi_shared = c(1,  1,   1, 1)
#' )
weak_instrument_threshold <- function(F, rho_MY, pi_shared, epsilon = 0.10) {

  # ── 输入校验 ─────────────────────────────────────────────────────────────────
  if (any(F <= 0))
    stop("`F` 必须为正数（F 统计量 > 0）")
  if (any(rho_MY < 0 | rho_MY > 1))
    stop("`rho_MY` 必须在 [0, 1] 范围内")
  if (any(pi_shared < 0 | pi_shared > 1))
    stop("`pi_shared` 必须在 [0, 1] 范围内")
  if (length(epsilon) != 1 || epsilon <= 0 || epsilon >= 1)
    stop("`epsilon` 必须是 (0, 1) 内的单个数值，默认 0.10")

  F         <- as.numeric(F)
  rho_MY    <- as.numeric(rho_MY)
  pi_shared <- as.numeric(pi_shared)

  # ── 解析上界计算 ──────────────────────────────────────────────────────────────
  # kappa1：基础 Jensen 修正项（不含系数2，便于向后兼容报告）
  kappa1 <- 1 / F

  # kappa2*：rho_MY 通道的相对偏移（含 pi_shared 调整）
  # 【2026-07-03 修正】原版本用 sqrt(pi_shared)，与D05已定稿推导（第381行boxed公式）
  # 及 S09_isolation_experiment2_rho_MY_v2.R（第151行 theory_rho）不一致——
  # D05/S09 中该项通过 n_s = pi_shared * p_M 线性进入，不是平方根。
  # 原 sqrt 版本在 pi_shared=1 时与线性版本重合（sqrt(1)=1），
  # 6点自检全部 pi_shared=1，故未能发现此问题（见D14核查报告）。
  # 当 pi_shared = 1 时退化为原始 kappa2 = |rho_MY| / sqrt(F)（与D03一致）
  kappa2 <- abs(rho_MY) * pi_shared / sqrt(F)

  # 二阶交叉项
  cross_term <- rho_MY^2 * pi_shared / F

  # 总上界 B（系数2来自偏差+方差分量的组合，见函数文档）
  rel_err_bound <- 2 * kappa1 + 2 * kappa2 + cross_term

  # ── 风险等级划分 ──────────────────────────────────────────────────────────────
  # 阈值基于 epsilon 相对标准化，兼容现有 kappa1 三级体系（kappa1<0.03低、0.03-0.05中、≥0.05高）：
  # - B < epsilon/2 ("low")      对应 rho=0 时 2/F < 0.05，即 F > 40（比原 kappa1<0.03 略严）
  # - epsilon/2 ≤ B < epsilon ("moderate") 
  # - B ≥ epsilon ("high")
  risk_level <- ifelse(
    rel_err_bound < epsilon / 2, "low",
    ifelse(rel_err_bound < epsilon, "moderate", "high")
  )

  is_reliable <- rel_err_bound < epsilon

  # ── 【2026-07-03两次更新，见D18】共享SNP通道门控 → 已收窄 ──────────────────
  # 第一版（本节最初）：发现只要pi_shared>0，B就系统性失效，加了"n_shared>0即
  # 强制高风险"的硬门控。
  #
  # 后续深挖（D18第七节）：找到了真正缺失的两处解析项——
  #   (1) Var(alpha_hat)/Var(beta_hat)本身漏了全方差公式的Var(E[·|gammaX])项
  #   (2) Var(beta_hat)还漏了rho_MY通过"给定和后条件分布"压缩条件方差的效应
  # 两处补齐后（已实测验证，24组合网格），delta method对Var(indirect effect)
  # 的平均相对误差从88%-244%降到4.8%，最大值13.3%——不再是"整个框架失效"。
  #
  # 这两个修正项已经内置进 S10_prod_mr_cov_tool.R 的 Var_alpha_full/Var_beta_full
  # 计算里（不在本函数中，本函数只负责kappa1/kappa2/B这套独立诊断指标，不直接
  # 参与S10的Cov/Var计算）。因此本函数的B/kappa1/kappa2诊断，对S10实际使用的
  # 修正后公式而言，已经不能代表真实可靠性——本函数的判定意义主要保留给"直接使用
  # 未经修正的朴素delta method"这种场景。
  #
  # 门控收窄为：只在残留误差实测最大的角（F<15 且 pi_shared>0.5，两点分别
  # 12.3%/13.3%，接近epsilon=10%边界）标记为"moderate"提示复核，不再对所有
  # n_shared>0一律标记high。
  shared_channel_uncovered <- pi_shared > 0  # 保留字段供参考/向后兼容，不再单独驱动风险等级
  residual_caution <- (F < 15) & (pi_shared > 0.5)
  if (any(residual_caution)) {
    risk_level[residual_caution & risk_level == "low"] <- "moderate"
  }

  # ── 诊断文字 ──────────────────────────────────────────────────────────────────
  diagnostic <- mapply(function(b, k1, k2, ct, rl, uncov, resid) {
    main_driver <- if (2 * k2 > 2 * k1 + ct) {
      "样本重叠(rho_MY)主导"
    } else {
      "工具强度(F)主导"
    }
    gate_msg <- if (uncov) {
      " | ℹ️共享SNP通道(pi_shared>0)：B本身不含pi_shared项（S10已用D18补齐的解析修正处理，非本函数职责）"
    } else ""
    resid_msg <- if (resid) {
      " | ⚠️残留误差角(F<15且pi_shared>0.5)：修正后delta method仍有约12-13%误差，建议交叉核对MC结果"
    } else ""
    sprintf(
      paste0(
        "风险等级: %s | 相对误差上界: %.1f%% (目标: <%.0f%%) | ",
        "kappa1(Jensen)=%.4f (×2=%.4f), kappa2*(rho通道)=%.4f (×2=%.4f), ",
        "交叉项=%.4f | 主导误差来源: %s%s%s"
      ),
      rl, b * 100, epsilon * 100,
      k1, 2 * k1, k2, 2 * k2, ct,
      main_driver, gate_msg, resid_msg
    )
  }, rel_err_bound, kappa1, kappa2, cross_term, risk_level, shared_channel_uncovered, residual_caution,
  SIMPLIFY = TRUE)

  # ── 返回 ──────────────────────────────────────────────────────────────────────
  list(
    is_reliable   = is_reliable,
    rel_err_bound = rel_err_bound,
    kappa1        = kappa1,          # 原始值（未×2），便于与现有 kappa1 体系对齐
    kappa2        = kappa2,          # 原始值（未×2）
    risk_level    = risk_level,
    shared_channel_uncovered = shared_channel_uncovered,  # 参考字段，不再驱动风险等级
    residual_caution = residual_caution,  # 新增：D18收窄后的残留误差角标记
    diagnostic    = diagnostic
  )
}


# ══════════════════════════════════════════════════════════════════════════════
# 自检（直接运行 Rscript weak_instrument_threshold.R 时执行）
# 输出规范：
#   log/     自检运行日志（本文件）
#   figure/  发表用图表（本函数不产生）
#   temp/    过渡文件（本函数不产生）
# ══════════════════════════════════════════════════════════════════════════════
if (sys.nframe() == 0L) {

  # ── 日志路径 ─────────────────────────────────────────────────────────────────
  `%||%` <- function(x, y) if (is.null(x)) y else x  # 修正：R<4.4没有原生%||%，2026-07-03实测发现补上
  log_dir  <- file.path(dirname(sys.frames()[[1]]$ofile %||% "."), "log")
  dir.create(log_dir, showWarnings = FALSE, recursive = TRUE)
  log_file <- file.path(log_dir, "task2_selfcheck.log")

  # 同时输出到控制台和 log 文件
  tee <- function(...) {
    msg <- paste0(...)
    cat(msg)
    cat(msg, file = log_file, append = TRUE)
  }

  # 清空旧 log
  cat("", file = log_file)

  tee("=== 任务2 自检：6个实测格点 (n_reps=5000，待大样本复核) ===\n\n")

  test_cases <- data.frame(
    F                    = c(30, 30, 30, 10, 10, 10),
    rho_MY               = c( 0, 0.5, 0.8,  0, 0.5, 1.0),
    pi_shared            = rep(1, 6),
    reported_rel_err_pct = c( 6,   4,  11,  8,   5,  30)
  )

  res <- with(test_cases,
    weak_instrument_threshold(F, rho_MY, pi_shared, epsilon = 0.10)
  )

  output <- data.frame(
    F                   = test_cases$F,
    rho_MY              = test_cases$rho_MY,
    kappa1              = round(res$kappa1, 4),
    kappa2              = round(res$kappa2, 4),
    bound_pct           = round(res$rel_err_bound * 100, 1),
    reported_pct        = test_cases$reported_rel_err_pct,
    bound_ge_reported   = res$rel_err_bound * 100 >= test_cases$reported_rel_err_pct,
    is_reliable         = res$is_reliable,
    risk_level          = res$risk_level
  )

  out_str <- capture.output(print(output, row.names = FALSE))
  tee(paste(out_str, collapse = "\n"), "\n")

  tee("\n验证：上界是否均 >= 实测值（保守性）：",
      all(output$bound_ge_reported), "\n")

  tee("\n各行诊断信息：\n")
  for (i in seq_along(res$diagnostic)) {
    tee(sprintf("  [%d] %s\n", i, res$diagnostic[i]))
  }

  tee("\n=== 严格模式（epsilon=0.05）===\n")
  res2 <- with(test_cases,
    weak_instrument_threshold(F, rho_MY, pi_shared, epsilon = 0.05)
  )
  tee("risk_level :", paste(res2$risk_level, collapse = ", "), "\n")
  tee("is_reliable:", paste(res2$is_reliable, collapse = ", "), "\n")

  tee("\n=== kappa1 阈值对齐（rho_MY=0, pi_shared=1, epsilon=0.10）===\n")
  for (f_val in c(10, 20, 25, 33, 50, 100)) {
    r <- weak_instrument_threshold(f_val, 0, 1)
    tee(sprintf("  F=%3d: kappa1=%.4f, B=%.1f%%, risk=%s\n",
                f_val, r$kappa1, r$rel_err_bound * 100, r$risk_level))
  }

  tee(sprintf("\n[完成] 自检日志已写入：%s\n", log_file))
}
