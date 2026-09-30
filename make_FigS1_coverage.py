# -*- coding: utf-8 -*-
"""
make_FigS1_coverage.py
Render Supplementary Figure S1 (coverage + variance calibration) from the
sign-corrected 180-cell coverage grid (M4b_coverage_grid_20260930.csv).

This figure supports the rewritten manuscript Section 3.1: it shows the
strength-dependent coverage regime (naive over-covers at strong instruments,
both intervals under-cover at weak instruments because of IVW attenuation bias)
and the variance-calibration divide (naive SE inflated relative to SD(alpha*beta),
corrected SE tracks it).

Panel A: empirical 95% CI coverage (centred on the true effect) by instrument
          strength F, averaged over n_s, beta, alpha.
Panel B: SE / SD(alpha_hat*beta_hat) by number of shared instruments n_s,
          averaged over F, beta, alpha -- naive vs corrected.

Output: figure/FigS1_simulation.png and .pdf
Log:    log/make_FigS1_coverage.log
"""
import os, csv, logging, collections
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = r"D:\WorkBuddy\两步法MR中介\⑤ 投稿文件_20260904"
SRC_DIR = r"D:\WorkBuddy\两步法MR中介\③ 真实数据应用\temp"
FIGDIR = os.path.join(ROOT, "figure")
LOGDIR = os.path.join(ROOT, "log")
os.makedirs(FIGDIR, exist_ok=True)
os.makedirs(LOGDIR, exist_ok=True)

logging.basicConfig(filename=os.path.join(LOGDIR, "make_FigS1_coverage.log"),
                    level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("make_FigS1_coverage")
log.info("make_FigS1_coverage.py -- Supplementary Fig S1 (coverage, sign-corrected grid)")

CSV = os.path.join(SRC_DIR, "M4b_coverage_grid_20260930.csv")
rows = list(csv.DictReader(open(CSV, encoding="utf-8-sig")))
log.info(f"loaded {len(rows)} cells from {CSV}")

def f(x):
    return float(x)

F_LABELS = [(10, "F\u224810\n(weak)"), (30, "F\u224830"), (90, "F\u224890"), (1000, "F\u22481000\n(strong)")]
NSS = [0, 10, 25, 40, 50]

# ---- group by F (coverage, centred on truth) ----
byF = collections.defaultdict(list)
for r in rows:
    byF[f(r["F"])].append(r)
xF = [lab for lab, _ in F_LABELS]
cov_naive = [np.mean([f(r["cov95_naive"]) for r in byF[F]]) for F, _ in F_LABELS]
cov_corr = [np.mean([f(r["cov95_corr"]) for r in byF[F]]) for F, _ in F_LABELS]
cov_emp  = [np.mean([f(r["cov95_emp"]) for r in byF[F]]) for F, _ in F_LABELS]

# ---- group by n_s (SE / SD) ----
byN = collections.defaultdict(list)
for r in rows:
    byN[f(r["n_s"])].append(r)
rat_naive = [np.mean([f(r["ratio_naive_over_sd"]) for r in byN[n]]) for n in NSS]
rat_corr  = [np.mean([f(r["ratio_corr_over_sd"]) for r in byN[n]]) for n in NSS]

plt.rcParams.update({"font.family": "Times New Roman", "font.size": 9,
                     "axes.labelsize": 10, "axes.titlesize": 10,
                     "mathtext.fontset": "stix"})

fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.8))

# ---------------- Panel A: coverage by F ----------------
ax = axes[0]
xpos = range(len(xF))
ax.plot(xpos, cov_naive, "o-", color="#B2182B", lw=1.6, ms=6, label="naive delta")
ax.plot(xpos, cov_corr, "s-", color="#2166AC", lw=1.6, ms=6, label="corrected")
ax.plot(xpos, cov_emp, "^:", color="#333333", lw=1.2, ms=6, label="empirical SD")
ax.axhline(0.95, color="#888888", lw=1.0, ls="--")
ax.text(0.02, 0.955, "95% target", transform=ax.transAxes, fontsize=7.5, color="#666666")
ax.set_xticks(list(xpos)); ax.set_xticklabels([lab for _, lab in F_LABELS])
ax.set_ylabel("Empirical 95% CI coverage\n(centred on true effect)")
ax.set_ylim(0.0, 1.02)
ax.set_title("A  Coverage: strength-dependent regime", loc="left")
ax.legend(fontsize=7.5, frameon=False, loc="lower right")
ax.grid(alpha=0.25, lw=0.5)
ax.text(0.03, 0.86,
        "weak F (left): both under-cover\nstrong F (right): naive over-covers",
        transform=ax.transAxes, ha="left", va="top", fontsize=7, color="#555555")

# ---------------- Panel B: SE / SD by n_s ----------------
ax = axes[1]
xx = range(len(NSS))
ax.plot(xx, rat_naive, "o-", color="#B2182B", lw=1.6, ms=6, label="naive / SD")
ax.plot(xx, rat_corr, "s-", color="#2166AC", lw=1.6, ms=6, label="corrected / SD")
ax.axhline(1.0, color="#888888", lw=1.0, ls="--")
ax.set_xticks(list(xx)); ax.set_xticklabels([str(n) for n in NSS])
ax.set_xlabel("Number of shared instruments  $n_s$  (of $p=50$ per step)")
ax.set_ylabel(r"SE  /  SD($\hat\alpha\hat\beta$)")
ax.set_ylim(0.9, 1.75)
ax.set_title("B  Variance calibration", loc="left")
ax.legend(fontsize=7.5, frameon=False, loc="upper left")
ax.grid(alpha=0.25, lw=0.5)
ax.annotate("naive inflates the SD by ~41%\non average at full overlap\n(worst single cell ~67%)",
            xy=(4, rat_naive[-1]), xytext=(1.2, 1.62), fontsize=7.5, color="#444444",
            arrowprops=dict(arrowstyle="->", color="#888888", lw=0.8))

fig.suptitle("Supplementary Fig. S1. Coverage and variance calibration across the 180-cell "
             "simulation grid (regime-map DGP; shared-instrument channel, $\\rho_{MY}=0$)",
             fontsize=9.5, y=1.00)
fig.tight_layout(rect=[0, 0, 1, 0.95])

png = os.path.join(FIGDIR, "FigS1_simulation.png")
pdf = os.path.join(FIGDIR, "FigS1_simulation.pdf")
fig.savefig(png, dpi=300, bbox_inches="tight", facecolor="white")
fig.savefig(pdf, bbox_inches="tight", facecolor="white")
log.info(f"saved {png}; {pdf}")
log.info(f"coverage by F (naive): {[round(v,3) for v in cov_naive]}")
log.info(f"coverage by F (corr) : {[round(v,3) for v in cov_corr]}")
log.info(f"SE/SD by n_s (naive): {[round(v,3) for v in rat_naive]}")
log.info(f"SE/SD by n_s (corr) : {[round(v,3) for v in rat_corr]}")
print("saved:", png)
print("saved:", pdf)
