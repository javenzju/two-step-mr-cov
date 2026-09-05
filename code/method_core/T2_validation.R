suppressMessages(library(ieugwasr))
suppressMessages(library(TwoSampleMR))
src <- "C:/Users/up201/.workbuddy/m4src/"
source(paste0(src, "S17_unified_dgp_test.R"))
source(paste0(src, "weak_instrument_threshold_FIXED.R"))
options(timeout=300)

# 独立验证集：与原 6 点自检不同的参数网格（覆盖弱/中/强工具 × 无/中/高重叠）
grid <- expand.grid(
  F        = c(10, 20, 30, 50),
  rho_MY   = c(0, 0.2, 0.5, 0.8, 1.0),
  pi_shared = c(0.1, 0.3, 0.5, 0.8, 1.0)
)

rows <- list()
for (i in seq_len(nrow(grid))) {
  g <- grid[i, ]
  emp <- run_grid_point_v2(g$F, g$rho_MY, g$pi_shared, N = 10000, n_reps = 2000, seed = 1000 + i)
  wit <- weak_instrument_threshold(g$F, g$rho_MY, g$pi_shared, epsilon = 0.10)
  B_pct <- wit$rel_err_bound * 100
  rows[[i]] <- data.frame(
    F = g$F, rho_MY = g$rho_MY, pi_shared = g$pi_shared,
    emp_rel_err_v1_pct = round(emp$rel_err_v1_pct, 2),
    B_pct = round(B_pct, 2),
    conservative = B_pct >= emp$rel_err_v1_pct,
    risk_level = wit$risk_level,
    is_reliable = wit$is_reliable
  )
  cat(sprintf("cell %3d/%d  F=%g rho=%g pi=%g  emp=%.1f  B=%.1f  cons=%s\n",
              i, nrow(grid), g$F, g$rho_MY, g$pi_shared,
              emp$rel_err_v1_pct, B_pct, rows[[i]]$conservative))
}
res <- do.call(rbind, rows)
out <- "C:/Users/up201/.workbuddy/m4src/T2_validation.csv"
write.csv(res, out, row.names = FALSE)

cat("\n=== T2 validation summary ===\n")
cat("cells:", nrow(res), "\n")
cat("conservative coverage (B >= emp rel_err_v1):", round(mean(res$conservative) * 100, 1), "%\n")
cat("mean emp rel_err_v1_pct:", round(mean(res$emp_rel_err_v1_pct), 1), "%\n")
cat("mean B_pct:", round(mean(res$B_pct), 1), "%\n")
cat("violations (B < emp):", sum(!res$conservative), "\n")
cat("\nby F (emp% / B% / coverage%):\n")
agg <- aggregate(cbind(emp = emp_rel_err_v1_pct, B = B_pct, cov = conservative) ~ F, res,
                 function(x) if (is.logical(x)) round(mean(x) * 100, 1) else round(mean(x), 1))
print(agg, row.names = FALSE)
cat("\n[done] -> ", out, "\n")
