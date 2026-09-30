# -*- coding: utf-8 -*-
"""
make_FigS3_regime_map.py
Render Supplementary Figure S3 (regime map) from the sign-corrected simulation grid
(M4b_regime_map_20260930.csv).

Replaces the earlier Fig. S3 (flip-probability surface), which was computed with the
sign error documented in Supplementary Methods S2.5 (Remark S2.5a) and therefore showed
a "flip-loss" regime that is structurally impossible.

Channels are kept separate: everything plotted here is the SHARED-INSTRUMENT channel
with rho_MY = 0 (the rho_MY channel is treated separately in Remark S2.5b).

Panel A: dSE% (percentage change in the indirect-effect SE) vs n_s — all negative.
Panel B: variance calibration, SE/SD(alpha_hat*beta_hat), for naive vs corrected.

Output: figure/FigS3_regime_map.png and .pdf
Log:    log/make_FigS3_regime_map.log
"""
import os, csv, logging
from datetime import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = r"D:\WorkBuddy\两步法MR中介\⑤ 投稿文件_20260904"
SRC_DIR = r"D:\WorkBuddy\两步法MR中介\③ 真实数据应用\temp"
FIGDIR = os.path.join(ROOT, "figure")
LOGDIR = os.path.join(ROOT, "log")
os.makedirs(FIGDIR, exist_ok=True)
os.makedirs(LOGDIR, exist_ok=True)

logging.basicConfig(filename=os.path.join(LOGDIR, "make_FigS3_regime_map.log"),
                    level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("make_FigS3_regime_map")
log.info("make_FigS3_regime_map.py — Supplementary Fig S3 (regime map, sign-corrected)")

CSV = os.path.join(SRC_DIR, "M4b_regime_map_20260930.csv")
rows = list(csv.DictReader(open(CSV, encoding="utf-8-sig")))
log.info(f"loaded {len(rows)} cells from {CSV}")


def fnum(x, d=float("nan")):
    try:
        return float(x)
    except Exception:
        return d


plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9,
                     "axes.labelsize": 10, "axes.titlesize": 10})

fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.7))

# ---------------- Panel A: dSE% vs n_s ----------------
ax = axes[0]
styles = {("v.strong F~1000", 1.0):   ("o", "#B2182B", "same-sign, |ab|=0.50"),
          ("v.strong F~1000", -1.0):  ("s", "#2166AC", "opposite-sign, |ab|=0.50"),
          ("v.strong F~1000", 0.5):   ("^", "#E08214", "same-sign, |ab|=0.25"),
          ("v.strong F~1000", -0.5):  ("v", "#5AAE61", "opposite-sign, |ab|=0.25")}
for (strength, beta), (mk, col, lab) in styles.items():
    sel = [r for r in rows if r["strength"] == strength and abs(fnum(r["beta"]) - beta) < 1e-9]
    sel.sort(key=lambda r: fnum(r["n_shared"]))
    xs = [fnum(r["n_shared"]) for r in sel]
    ys = [fnum(r["dSE_pct"]) for r in sel]
    ax.plot(xs, ys, marker=mk, color=col, label=lab, lw=1.4, ms=5)

ax.axhline(0, color="black", lw=0.9, ls="--")
ax.set_xlabel("Number of shared instruments  $n_s$  (of $p=50$ per step)")
ax.set_ylabel(r"$\Delta$SE  (%)")
ax.set_title("A  Correction always narrows the interval", loc="left")
ax.legend(fontsize=7.5, frameon=False, loc="upper right")
ax.set_xticks([0, 10, 25, 50])
ax.grid(alpha=0.25, lw=0.5)
ax.text(0.02, 0.04, "$n_s=0$: covariance $\\equiv 0$ (scatter = MC noise)",
        transform=ax.transAxes, fontsize=7, color="#555555")
ax.text(0.02, 0.10, "all points for $n_s>0$ are $\\leq 0$: the naive SE is\nnever smaller than the corrected SE",
        transform=ax.transAxes, fontsize=7, color="#555555")

# ---------------- Panel B: variance calibration ----------------
ax = axes[1]
for strength, mk in [("strong F~90", "o"), ("v.strong F~1000", "s")]:
    sel = [r for r in rows if r["strength"] == strength]
    byn = {}
    for r in sel:
        byn.setdefault(fnum(r["n_shared"]), []).append(r)
    xs = sorted(byn)
    rn = [sum(fnum(r["ratio_naive_over_sd"]) for r in byn[x]) / len(byn[x]) for x in xs]
    rc = [sum(fnum(r["ratio_corr_over_sd"]) for r in byn[x]) / len(byn[x]) for x in xs]
    tag = "F≈90" if mk == "o" else "F≈1000"
    ax.plot(xs, rn, marker=mk, color="#B2182B", lw=1.4, ms=5, label=f"naive ({tag})")
    ax.plot(xs, rc, marker=mk, color="#2166AC", lw=1.4, ms=5, ls="--", label=f"corrected ({tag})")
ax.axhline(1.0, color="black", lw=0.9, ls=":")
ax.set_xlabel("Number of shared instruments  $n_s$")
ax.set_ylabel(r"SE  /  SD($\hat\alpha\hat\beta$)")
ax.set_title("B  Variance calibration", loc="left")
ax.legend(fontsize=7.5, frameon=False, loc="upper left")
ax.set_xticks([0, 10, 25, 50])
ax.grid(alpha=0.25, lw=0.5)
ax.annotate("naive overstates the true SD\nby up to ~65% at full overlap",
            xy=(50, 1.62), xytext=(12, 1.75), fontsize=7.5, color="#444444",
            arrowprops=dict(arrowstyle="->", color="#888888", lw=0.8))

fig.suptitle("Supplementary Fig. S3 — Regime map for the covariance correction "
             "(shared-instrument channel, $\\rho_{MY}=0$)",
             fontsize=9.5, y=1.00)
fig.tight_layout(rect=[0, 0, 1, 0.96])

png = os.path.join(FIGDIR, "FigS3_regime_map.png")
pdf = os.path.join(FIGDIR, "FigS3_regime_map.pdf")
fig.savefig(png, dpi=300)
fig.savefig(pdf)
log.info(f"saved {png}; {pdf}")
print("saved:", png)
print("saved:", pdf)
