#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
D61_make_figures.py
Re-render Figure 5 and Figure 6 as 300-dpi PNGs (Times New Roman, all-English,
Figure-numbered titles) so they can be embedded in the submission .docx.

Faithfulness: every value is taken verbatim from the manuscript tables
(Table 1 for Fig 5, Table 3 for Fig 6); nothing is recomputed.

Output: <submission>/figure/Fig5_pisweep.png , Fig6_batch_forest.png
Log   : log/D61_make_figures.log
"""
import os, io, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))          # ⑤ 投稿文件_20260904
ROOT = os.path.dirname(HERE)
FIGDIR = os.path.join(HERE, "figure")
LOGDIR = os.path.join(ROOT, "log")
os.makedirs(FIGDIR, exist_ok=True); os.makedirs(LOGDIR, exist_ok=True)
LOG = os.path.join(LOGDIR, "D61_make_figures.log")

_log = io.StringIO()
def log(m=""):
    print(m); _log.write(str(m) + "\n")

# Times New Roman throughout (matches manuscript font requirement)
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["mathtext.fontset"] = "stix"
plt.rcParams["axes.labelsize"] = 10
plt.rcParams["axes.titlesize"] = 11
plt.rcParams["xtick.labelsize"] = 9
plt.rcParams["ytick.labelsize"] = 9
plt.rcParams["legend.fontsize"] = 9
plt.rcParams["figure.dpi"] = 300

log("=" * 70)
log("D61_make_figures.py — 300-dpi PNG re-render of Figure 5 and Figure 6")
log("=" * 70)
log(f"font family : {plt.rcParams['font.family']}")

# ------------------------------------------------------------------ FIGURE 5
# Table 1 : rho_MY = 0.5, n_reps = 30,000
# (F, pi_shared, emp_cov, theory_total, rel_err)
T1 = [
 (30, 0.1, -0.0003731, -0.0003357, 10.02),
 (30, 0.2, -0.0006333, -0.0006713,  6.01),
 (30, 0.3, -0.0010047, -0.0010070,  0.23),
 (30, 0.7, -0.0023361, -0.0023497,  0.58),
 (30, 0.9, -0.0030894, -0.0030210,  2.21),
 (30, 1.0, -0.0034441, -0.0033567,  2.54),
 (10, 0.1, -0.0002971, -0.0003391, 14.13),
 (10, 0.2, -0.0007604, -0.0006782, 10.81),
 (10, 0.3, -0.0008952, -0.0010173, 13.64),
 (10, 0.7, -0.0022428, -0.0023736,  5.83),
 (10, 0.9, -0.0031135, -0.0030518,  1.98),
 (10, 1.0, -0.0035006, -0.0033909,  3.14),
]
fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.3))
fig.suptitle("Figure 5. Targeted validation sweep at non-degenerate shared-instrument proportions",
             fontsize=11.5, fontweight="bold", y=0.985)

# --- Panel A: empirical (points) vs analytical (lines)
ax = axes[0]
for F, col, mk in ((30, "#1f77b4", "o"), (10, "#d62728", "s")):
    rows = [r for r in T1 if r[0] == F]
    pi   = [r[1] for r in rows]
    emp  = [r[2] * 1e3 for r in rows]
    theo = [r[3] * 1e3 for r in rows]
    ax.plot(pi, theo, "--", color=col, lw=1.4, label=f"analytical, F = {F}")
    ax.plot(pi, emp, mk, color=col, ms=5.5, mfc="white", mew=1.2,
            label=f"empirical, F = {F}")
ax.axhline(0, color="#333", lw=0.8)
ax.set_xlabel(r"$\pi_{shared}$")
ax.set_ylabel(r"Cov($\hat{\alpha}$, $\hat{\beta}$)   ($\times 10^{-3}$)")
ax.set_title("A. Empirical versus analytical covariance", fontsize=10.5, fontweight="bold")
ax.legend(frameon=False, loc="lower left")
ax.grid(alpha=0.25, ls=":", lw=0.6)
for s in ("top", "right"): ax.spines[s].set_visible(False)

# --- Panel B: relative error per validation cell
ax = axes[1]
labels, errs, cols = [], [], []
for F, pi, _e, _t, rel in T1:
    labels.append(f"F={F}\n{pi:g}")
    errs.append(rel)
    cols.append("#1f77b4" if F == 30 else "#d62728")
xpos = range(len(errs))
ax.bar(xpos, errs, color=cols, width=0.62, edgecolor="#333", lw=0.5)
mx = max(errs)
ax.axhline(mx, color="#999", ls="--", lw=1.0)
ax.text(len(errs) - 0.5, mx + 0.5, f"max observed {mx:.1f}%",
        ha="right", fontsize=8.5, color="#666")
ax.set_xticks(list(xpos)); ax.set_xticklabels(labels, fontsize=7.6)
ax.set_ylabel("Relative error (%)")
ax.set_xlabel("Validation cell (F \u00d7 $\\pi_{shared}$)")
ax.set_title("B. Relative error of the analytical covariance", fontsize=10.5, fontweight="bold")
ax.text(0.02, 0.965, "all 12 cells within the conservative bound B (Sec. 2.3)",
        transform=ax.transAxes, fontsize=8.2, color="#666", va="top",
        bbox=dict(facecolor="white", alpha=0.85, edgecolor="none", pad=1.5))
ax.grid(axis="y", alpha=0.25, ls=":", lw=0.6)
for s in ("top", "right"): ax.spines[s].set_visible(False)

fig.tight_layout(rect=[0, 0, 1, 0.94])
p5 = os.path.join(FIGDIR, "Fig5_pisweep.png")
fig.savefig(p5, dpi=300, bbox_inches="tight", facecolor="white")
plt.close(fig)
log(f"[OK] {p5}  ({os.path.getsize(p5)} bytes)")

# ------------------------------------------------------------------ FIGURE 6
# Table 3 : widen_% for the 4 TwoSampleMR-validated overlapping trios
T3 = [("S014", -9.0, 0.0556), ("S273", -0.7, 0.1538),
      ("S137", -5.9, 0.019),  ("S217", -0.1, 0.1111)]
T3 = sorted(T3, key=lambda r: r[1])           # most negative first

fig, ax = plt.subplots(figsize=(7.6, 3.5))
fig.suptitle("Figure 6. Change in indirect-effect SE after S10 correction "
             "(TwoSampleMR-validated batch re-estimation)",
             fontsize=11.5, fontweight="bold", y=0.975)
names = [f"{r[0]}  (\u03c0={r[2]:g})" for r in T3]
vals  = [r[1] for r in T3]
ypos  = range(len(vals))
bars = ax.barh(list(ypos), vals, height=0.55, color="#2b8cbe",
               edgecolor="#1b5f85", lw=0.6, alpha=0.9)
for b, v in zip(bars, vals):
    ax.text(v - 0.22, b.get_y() + b.get_height() / 2, f"{v:.1f}%",
            va="center", ha="right", fontsize=9.5, color="#113")
ax.axvline(0, color="#888", ls=(0, (4, 3)), lw=1.2)
ax.text(0.985, 0.965, "no change", transform=ax.transAxes,
        fontsize=8.5, color="#888", ha="right", va="top",
        bbox=dict(facecolor="white", alpha=0.85, edgecolor="none", pad=1.5))
ax.set_yticks(list(ypos)); ax.set_yticklabels(names, fontsize=10)
ax.invert_yaxis()
ax.set_xlim(-10.4, 0.9)
ax.set_xticks([-10, -8, -6, -4, -2, 0])
ax.set_xlabel("Relative change in SE (%)")
ax.set_title("4 adequately powered published two-step MR mediation studies with "
             "genuine instrument overlap (Table 3)",
             fontsize=9.5, color="#555", pad=8)
ax.grid(axis="x", alpha=0.25, ls=":", lw=0.6)
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.text(0.01, -0.02, "TwoSampleMR-calibrated (cross-validated against the deposited D56 ground "
                      "truth); all values negative = CI narrows; zero-flip conclusion fully validated.",
         fontsize=8, color="#999")

fig.tight_layout(rect=[0, 0.02, 1, 0.93])
p6 = os.path.join(FIGDIR, "Fig6_batch_forest.png")
fig.savefig(p6, dpi=300, bbox_inches="tight", facecolor="white")
plt.close(fig)
log(f"[OK] {p6}  ({os.path.getsize(p6)} bytes)")

log("")
log("Fig 5 source values (Table 1) : 12 cells, max rel_err = "
    f"{max(r[4] for r in T1):.2f}%")
log("Fig 6 source values (Table 3) : " +
    ", ".join(f"{n}={v}%" for n, v, _ in T3))
log("")
log("DONE.")
open(LOG, "w", encoding="utf-8").write(_log.getvalue())
