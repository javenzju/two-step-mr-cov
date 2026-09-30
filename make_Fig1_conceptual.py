# -*- coding: utf-8 -*-
"""
make_Fig1_conceptual.py
Redraw Figure 1 (conceptual diagram of two-step MR mediation with overlapping
instruments) as a clean vector figure.

Why: the previous Fig 1 was a raster (figure/_source/Fig1_conceptual.png) from an
old R/ggplot pass with three defects a reviewer would see at a glance:
  1. the red annotation used ASCII maths ("Cov(alpha,beta) != 0 ... n[s] ... rho[MY]")
     while the rest of the figure used proper Greek,
  2. the dashed "total / direct effect" line struck straight through the Mediator box,
     and its label was occluded,
  3. the hats on alpha-hat / beta-hat were offset carets.
This script renders a vector version with mathtext Greek, the direct-effect path
routed as an arc ABOVE the row of boxes (no collision), and a clean symbol set.

Output: figure/Fig1_conceptual.png (300 dpi) and figure/Fig1_conceptual.pdf
Log:    log/make_Fig1_conceptual.log
"""
import os, logging
from datetime import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

ROOT = r"D:\WorkBuddy\两步法MR中介\⑤ 投稿文件_20260904"
FIGDIR = os.path.join(ROOT, "figure")
LOGDIR = os.path.join(ROOT, "log")
os.makedirs(FIGDIR, exist_ok=True)
os.makedirs(LOGDIR, exist_ok=True)

logging.basicConfig(filename=os.path.join(LOGDIR, "make_Fig1_conceptual.log"),
                    level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("make_Fig1_conceptual")
log.info("make_Fig1_conceptual.py — vector redraw of Figure 1")

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "mathtext.fontset": "dejavusans",
    "font.size": 9,
})

# ---- palette (draw.io defaults, matching the rest of the figure set) ----
C_BLUE_F, C_BLUE_E = "#dae8fc", "#6c8ebf"
C_GREEN_F, C_GREEN_E = "#d5e8d4", "#82b366"
C_RED_F, C_RED_E = "#f8cecc", "#b85450"
C_GRAY_F, C_GRAY_E = "#f5f5f5", "#999999"
C_SHARE_F, C_SHARE_E = "#ffe6cc", "#d79b00"
C_SOLID, C_DASH, C_TXT_RED = "#333333", "#666666", "#c00000"

fig, ax = plt.subplots(figsize=(9.2, 5.6))
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

def box(x0, x1, y0, y1, fc, ec, lw=1.4):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, facecolor=fc,
                           edgecolor=ec, linewidth=lw, zorder=2))

def arrow(x0, y0, x1, y1, color=C_SOLID, lw=2.0, ls="-", rad=0.0, zorder=3):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1),
                 arrowstyle="-|>", mutation_scale=16, linewidth=lw,
                 color=color, linestyle=ls, zorder=zorder,
                 connectionstyle=f"arc3,rad={rad}",
                 shrinkA=0, shrinkB=0))

# ---- title ----
ax.text(0.5, 0.978,
        "Figure 1. Conceptual diagram of two-step (product-method) MR mediation "
        "with overlapping instruments",
        ha="center", va="top", fontsize=10.5, fontweight="bold", color="black")

# ---- top row: Exposure -> Mediator -> Outcome ----
YB0, YB1 = 0.615, 0.745           # box bottom / top
YC = 0.680                        # vertical centre
box(0.07, 0.27, YB0, YB1, C_BLUE_F, C_BLUE_E)
box(0.40, 0.60, YB0, YB1, C_GREEN_F, C_GREEN_E)
box(0.73, 0.93, YB0, YB1, C_RED_F, C_RED_E)
ax.text(0.17, YC, "Exposure\nX", ha="center", va="center",
        fontsize=11, fontweight="bold", color="#1f3d63", linespacing=1.25)
ax.text(0.50, YC, "Mediator\nM", ha="center", va="center",
        fontsize=11, fontweight="bold", color="#2d5220", linespacing=1.25)
ax.text(0.83, YC, "Outcome\nY", ha="center", va="center",
        fontsize=11, fontweight="bold", color="#8a2b26", linespacing=1.25)

# step arrows
arrow(0.27, YC, 0.40, YC)
arrow(0.60, YC, 0.73, YC)
ax.text(0.335, YC + 0.042, r"$\hat{\alpha}$", ha="center", va="bottom", fontsize=13)
ax.text(0.665, YC + 0.042, r"$\hat{\beta}$", ha="center", va="bottom", fontsize=13)

# ---- direct effect: arc ABOVE the row (bows up, clears every box) ----
arrow(0.17, YB1, 0.83, YB1, color=C_DASH, lw=1.6, ls=(0, (5, 3)), rad=-0.30)
ax.text(0.50, 0.872, "direct effect", ha="center", va="center",
        fontsize=9, color=C_DASH, style="italic",
        bbox=dict(boxstyle="round,pad=0.18", facecolor="white", edgecolor="none"))

# indirect-effect annotation, placed clear of the Outcome box
ax.text(0.83, 0.585, r"indirect $= \hat{\alpha}\hat{\beta}$",
        ha="center", va="top", fontsize=9, color="#333333")

# ---- bottom: two IV sets with a shared-instrument overlap ----
IY0, IY1 = 0.185, 0.345
IYC = 0.265
box(0.07, 0.55, IY0, IY1, C_GRAY_F, C_GRAY_E)
box(0.45, 0.93, IY0, IY1, C_GRAY_F, C_GRAY_E)
ax.add_patch(Rectangle((0.45, IY0), 0.10, IY1 - IY0, facecolor=C_SHARE_F,
                       edgecolor=C_SHARE_E, linewidth=1.2, zorder=3))
ax.text(0.24, IYC, "Step-1 IV set\n$G_X$", ha="center", va="center",
        fontsize=10, color="#333333", linespacing=1.3)
ax.text(0.76, IYC, "Step-2 IV set\n$G_M$", ha="center", va="center",
        fontsize=10, color="#333333", linespacing=1.3)
ax.text(0.50, IYC, "shared\n$n_s$ SNPs", ha="center", va="center",
        fontsize=6.6, color="#7f4f00", linespacing=1.25, zorder=4)

# arrows from IV sets up to the traits
arrow(0.30, IY1, 0.17, YB0, color=C_BLUE_E, lw=1.8)
arrow(0.70, IY1, 0.50, YB0, color=C_GREEN_E, lw=1.8)

# ---- the punchline ----
ax.text(0.5, 0.072,
        r"$\mathrm{Cov}(\hat{\alpha},\hat{\beta}) \neq 0$"
        r"  whenever  $n_s > 0$  or  $\rho_{MY} \neq 0$",
        ha="center", va="center", fontsize=12, fontweight="bold", color=C_TXT_RED)

png = os.path.join(FIGDIR, "Fig1_conceptual.png")
pdf = os.path.join(FIGDIR, "Fig1_conceptual.pdf")
fig.savefig(png, dpi=300, facecolor="white")
fig.savefig(pdf, facecolor="white")
log.info(f"wrote {png}")
log.info(f"wrote {pdf}")
print("wrote", png)
print("wrote", pdf)
