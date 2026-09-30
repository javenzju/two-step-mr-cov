#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
D61_make_figures.py
Re-render Supplementary Figure S2 (targeted validation sweep) and
Supplementary Figure S4 (batch SE-change forest) as 300-dpi PNGs
(Times New Roman, all-English, Figure-numbered titles) so they can be
embedded in the submission .docx.

Faithfulness: every value is taken verbatim from the manuscript tables
(Supplementary Table S1 for S2, Table 3 for S3); nothing is recomputed.

Output: <submission>/figure/FigS2_pisweep.png , FigS3_batch_forest.png
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
log("D61_make_figures.py — 300-dpi PNG re-render of Supplementary Figures S2 and S3")
log("=" * 70)
log(f"font family : {plt.rcParams['font.family']}")

# ------------------------------------------------------------------ SUPPLEMENTARY FIGURE S2
# Supplementary Table S1 : rho_MY = 0.5, n_reps = 30,000
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
fig.suptitle("Supplementary Figure S2. Targeted validation sweep at non-degenerate shared-instrument proportions",
             fontsize=11.5, fontweight="bold", y=0.965)

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

fig.tight_layout(rect=[0, 0, 1, 0.92])
p5 = os.path.join(FIGDIR, "FigS2_pisweep.png")
fig.savefig(p5, dpi=300, bbox_inches="tight", pad_inches=0.22, facecolor="white")
p5_pdf = os.path.join(FIGDIR, "FigS2_pisweep.pdf")
fig.savefig(p5_pdf, bbox_inches="tight", pad_inches=0.22, facecolor="white")
plt.close(fig)
log(f"[OK] {p5}  ({os.path.getsize(p5)} bytes)")
log(f"[OK] {p5_pdf}  ({os.path.getsize(p5_pdf)} bytes)")

# ------------------------------------------------------------------ SUPPLEMENTARY FIGURE S4
# Dual-pipeline comparison: all-Python batch re-estimation vs TwoSampleMR cross-check
# for the 4 adequately powered overlapping trios.
STUDIES = ["S014", "S137", "S273", "S217"]
PI = {"S014": 0.0556, "S137": 0.019, "S273": 0.1538, "S217": 0.1111}
ALLPY = {"S014": -16.0, "S137": -14.2, "S273": -1.1, "S217": -0.2}
TSMB = {"S014": -9.0, "S137": -5.9, "S273": -0.7, "S217": -0.1}
STUDIES = sorted(STUDIES, key=lambda s: ALLPY[s])   # most negative all-Python first

fig, ax = plt.subplots(figsize=(7.8, 3.6))
fig.suptitle("Supplementary Figure S4. Change in indirect-effect SE after the covariance "
             "correction: all-Python batch vs TwoSampleMR cross-check",
             fontsize=11.5, fontweight="bold", y=0.95)
ypos = list(range(len(STUDIES)))
h = 0.36
ax.barh([y + h/2 for y in ypos], [ALLPY[s] for s in STUDIES], height=h, color="#2b8cbe",
        edgecolor="#1b5f85", lw=0.6, alpha=0.9, label="all-Python")
ax.barh([y - h/2 for y in ypos], [TSMB[s] for s in STUDIES], height=h, color="#d68910",
        edgecolor="#7e4e05", lw=0.6, alpha=0.9, label="TwoSampleMR")
for i, s in enumerate(STUDIES):
    ax.text(ALLPY[s] - 0.25, ypos[i] + h/2, f"{ALLPY[s]:.1f}", va="center", ha="right",
            fontsize=8.5, color="#113")
    ax.text(TSMB[s] - 0.25, ypos[i] - h/2, f"{TSMB[s]:.1f}", va="center", ha="right",
            fontsize=8.5, color="#113")
ax.axvline(0, color="#888", ls=(0, (4, 3)), lw=1.2)
ax.text(0.985, 0.04, "no change", transform=ax.transAxes,
        fontsize=8.5, color="#888", ha="right", va="bottom",
        bbox=dict(facecolor="white", alpha=0.85, edgecolor="none", pad=1.5))
ax.set_yticks(ypos); ax.set_yticklabels([f"{s}  (\u03c0={PI[s]:g})" for s in STUDIES], fontsize=10)
ax.invert_yaxis()
ax.set_xlim(-18, 1.2)
ax.set_xticks([-16, -12, -8, -4, 0])
ax.set_xlabel("Relative change in SE (%)")
ax.set_title("4 adequately powered published two-step MR mediation studies with "
             "genuine instrument overlap (Table 2)",
             fontsize=9.5, color="#555", pad=8)
ax.legend(fontsize=8.5, frameon=False, loc="lower right")
ax.grid(axis="x", alpha=0.25, ls=":", lw=0.6)
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.text(0.01, -0.03, "Both pipelines narrow; TwoSampleMR returns a systematically smaller "
                      "correction (\u22120.1% to \u22129.0%) than the all-Python batch "
                      "(\u22120.2% to \u221216.0%, median \u22121.6%) because the wrappers "
                      "re-harmonise effects differently (e.g., S014 \u03b1\u0302 SE 0.00096 vs 0.00345).",
         fontsize=7.5, color="#666")

fig.tight_layout(rect=[0, 0.04, 1, 0.90])
p6 = os.path.join(FIGDIR, "FigS4_batch_forest.png")
fig.savefig(p6, dpi=300, bbox_inches="tight", pad_inches=0.22, facecolor="white")
p6_pdf = os.path.join(FIGDIR, "FigS4_batch_forest.pdf")
fig.savefig(p6_pdf, bbox_inches="tight", pad_inches=0.22, facecolor="white")
plt.close(fig)
log(f"[OK] {p6}  ({os.path.getsize(p6)} bytes)")
log(f"[OK] {p6_pdf}  ({os.path.getsize(p6_pdf)} bytes)")

log("")
log("Suppl Fig S2 source values (validation sweep, Fig S2) : 12 cells, max rel_err = "
    f"{max(r[4] for r in T1):.2f}%")
log("Suppl Fig S4 source values (dual pipeline) : " +
    ", ".join(f"{s} allPython={ALLPY[s]}% TwoSampleMR={TSMB[s]}%" for s in STUDIES))
log("")
log("DONE.")
open(LOG, "w", encoding="utf-8").write(_log.getvalue())
