# -*- coding: utf-8 -*-
"""
make_Fig2_PRISMA.py
Render PRISMA 2020 flow diagram for the literature audit as a 300-dpi PNG.
Numbers are taken verbatim from the manuscript legend and Methods section.
Output: figure/Fig2_PRISMA.png
Log: log/make_Fig2_PRISMA.log
"""
import os, sys, logging
from datetime import datetime

ROOT = r"D:\WorkBuddy\两步法MR中介\⑤ 投稿文件_20260904"
FIGDIR = os.path.join(ROOT, "figure")
LOGDIR = os.path.join(ROOT, "log")
os.makedirs(LOGDIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOGDIR, "make_Fig2_PRISMA.log"),
    level=logging.INFO,
    format="%(asctime)s %(message)s"
)
log = logging.getLogger("make_Fig2_PRISMA")
log.info("make_Fig2_PRISMA.py — PRISMA 2020 flow diagram (300 dpi)")

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.size'] = 11
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.spines.left'] = False
plt.rcParams['axes.spines.bottom'] = False
plt.rcParams['xtick.bottom'] = False
plt.rcParams['ytick.left'] = False

fig, ax = plt.subplots(figsize=(10, 8))
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.set_aspect('equal')
ax.axis('off')

def box(x, y, w, h, text, color='#e6f2ff', edge='#333333', fontsize=10):
    rect = FancyBboxPatch((x - w/2, y - h/2), w, h,
                          boxstyle="round,pad=0.02,rounding_size=0.15",
                          facecolor=color, edgecolor=edge, linewidth=1.2)
    ax.add_patch(rect)
    ax.text(x, y, text, ha='center', va='center', fontsize=fontsize,
            wrap=True, linespacing=1.15)

def arrow(x1, y1, x2, y2):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color='#333333', lw=1.2))

def side_label(x, y, text, fontsize=10, color='#333333'):
    ax.text(x, y, text, ha='center', va='center', fontsize=fontsize, color=color,
            bbox=dict(boxstyle='round,pad=0.2', facecolor='#fff8dc', edgecolor='#d4a017', linewidth=0.8))

# Title
ax.text(5, 9.55, 'Figure 2. PRISMA 2020 flow diagram of the literature audit',
        ha='center', va='center', fontsize=13, fontweight='bold')

# Identification
box(2.5, 8.6, 4.0, 0.75,
    'Identification\nNine PubMed query strings identified\n695 primary records', '#d9ead3')

# Screening box
box(2.5, 7.3, 4.0, 0.85,
    'Screening\n695 records screened\n362 excluded (not two-step MR mediation)', '#f4cccc')
arrow(2.5, 8.225, 2.5, 7.725)

# Included reports
box(7.5, 7.3, 4.0, 0.85,
    '333 two-step MR mediation reports\nincluded for design coding', '#c9daf8')
arrow(4.5, 7.3, 5.5, 7.3)

# Re-estimation eligibility
box(7.5, 5.9, 4.0, 0.85,
    'Assessed for real-data re-estimation\n113 trios could be resolved to\npublic GWAS accessions', '#c9daf8')
arrow(7.5, 6.875, 7.5, 6.325)
side_label(3.8, 5.9, '220 excluded:\nno resolvable EUR-clumped\nexposure→mediator→outcome\naccessions', fontsize=9)

# Valid trios after errors
box(7.5, 4.5, 4.0, 0.85,
    'Re-estimated trios\n108 valid after 5 accession/\nnetwork errors', '#c9daf8')
arrow(7.5, 5.475, 7.5, 4.925)

# Overlap result
box(7.5, 3.1, 4.0, 0.85,
    'Genuine instrument overlap\n7 trios (6.5%; 95% CI 3.2–12.8%)\nwith shared step-1 / step-2 SNPs', '#d9ead3')
arrow(7.5, 4.075, 7.5, 3.525)

# Excluded-error detail
side_label(3.8, 4.5, '5 trios excluded:\naccession/network errors', fontsize=9)

# Bottom note
ax.text(5, 0.7, 'The audit was confined to PubMed and is described fully in the Methods and Supplementary Table S3.',
        ha='center', va='center', fontsize=9, style='italic')

fig.tight_layout()
out = os.path.join(FIGDIR, 'Fig2_PRISMA.png')
fig.savefig(out, dpi=300, bbox_inches='tight', facecolor='white')
plt.close(fig)
log.info(f"[OK] {out} ({os.path.getsize(out)} bytes)")
print(f"[OK] {out} ({os.path.getsize(out)} bytes)")
