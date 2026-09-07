#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
make_Fig4_realdata.py
Re-render Figure 4 (BMI -> waist circumference -> CHD indirect-effect CI)
at rho_MY = 0 so the plotted percentages match Table 2 and the main-text legend.

Output: <submission>/figure/Fig4_realdata.png
"""
import os, io, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.join(HERE, "figure")
LOGDIR = os.path.join(os.path.dirname(HERE), "log")
os.makedirs(FIGDIR, exist_ok=True); os.makedirs(LOGDIR, exist_ok=True)
LOG = os.path.join(LOGDIR, "make_Fig4_realdata.log")

_log = io.StringIO()
def log(m=""):
    print(m); _log.write(str(m) + "\n")

plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["mathtext.fontset"] = "stix"
plt.rcParams["axes.labelsize"] = 10
plt.rcParams["axes.titlesize"] = 11
plt.rcParams["xtick.labelsize"] = 9
plt.rcParams["ytick.labelsize"] = 9
plt.rcParams["legend.fontsize"] = 9
plt.rcParams["figure.dpi"] = 300

log("make_Fig4_realdata.py — Figure 4 BMI->waist->CHD CI comparison (rho_MY=0)")

# Table 2, rho_MY = 0 rows
rows = [
    # (label, n_s, indirect, SE_naive, SE_corr, widen_%)
    ("Shared-IV design (n_s=78)", 78, 0.414, 0.0563, 0.0476, -15.5),
    ("Natural overlap (n_s=13)", 13, 0.412, 0.0767, 0.0745, -2.8),
]

fig, ax = plt.subplots(figsize=(7.2, 4.0))

for i, (label, n_s, est, se_n, se_c, widen) in enumerate(rows):
    y = 0.6 - i * 0.45
    ci_n_low = est - 1.96 * se_n
    ci_n_high = est + 1.96 * se_n
    ci_c_low = est - 1.96 * se_c
    ci_c_high = est + 1.96 * se_c

    # naive CI (red, behind)
    ax.plot([ci_n_low, ci_n_high], [y, y], color="#d62728", lw=5.5, solid_capstyle="butt")
    # corrected CI (blue, on top)
    ax.plot([ci_c_low, ci_c_high], [y, y], color="#1f77b4", lw=5.5, solid_capstyle="butt")
    # point estimate
    ax.plot(est, y, "D", color="#1a1a1a", markersize=7, zorder=5)

    # y-axis label
    ax.text(-0.02, y, label, transform=ax.get_yaxis_transform(),
            ha="right", va="center", fontsize=10.5, fontweight="normal")

    # annotation above each bar
    short = "Shared-IV design" if i == 0 else "Natural overlap"
    ax.text(0.02, y + 0.16, f"{short}: corrected SE {widen:.1f}%",
            transform=ax.get_yaxis_transform(), ha="left", va="bottom",
            fontsize=9.5, color="#444")

ax.set_xlim(0.22, 0.55)
ax.set_ylim(0.05, 0.8)
ax.set_yticks([])
ax.spines["left"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["top"].set_visible(False)
ax.set_xlabel(r"Indirect effect ($\hat{\alpha}\hat{\beta}$) with 95% CI", fontsize=11)

# legend / annotation
ax.text(0.98, 0.96, "red = Naive CI (wider); blue = Corrected CI (narrower)",
        transform=ax.transAxes, ha="right", va="top", fontsize=9, color="#555")

fig.suptitle("Figure 4. Indirect effect ($\\hat{\\alpha}\\hat{\\beta}$) and 95% confidence intervals "
             "for the BMI → waist → CHD pathway",
             fontsize=11.5, fontweight="bold", y=0.965)

fig.tight_layout(rect=[0.08, 0, 0.98, 0.92])
p = os.path.join(FIGDIR, "Fig4_realdata.png")
fig.savefig(p, dpi=300, bbox_inches="tight", pad_inches=0.22, facecolor="white")
p_pdf = os.path.join(FIGDIR, "Fig4_realdata.pdf")
fig.savefig(p_pdf, bbox_inches="tight", pad_inches=0.22, facecolor="white")
plt.close(fig)
log(f"[OK] {p}  ({os.path.getsize(p)} bytes)")
log(f"[OK] {p_pdf}  ({os.path.getsize(p_pdf)} bytes)")
log(f"Plotted: shared-IV corrected SE = -15.5%, natural overlap corrected SE = -2.8%")
log("DONE.")
open(LOG, "w", encoding="utf-8").write(_log.getvalue())
