# -*- coding: utf-8 -*-
"""
make_FigS4_flip_probability.py
Render Supplementary Figure S4 from the pre-computed 200-cell flip-probability
surface (T2_flip_prob_20260906.csv). The plotted panels match the manuscript
caption: Panel A = concordant mediation (sgn=+1, rho_MY=0, F=10); Panel B =
discordant mediation / full sample overlap (sgn=-1, rho_MY=1, F=10).
Output: figure/FigS4_flip_probability.png
Log: log/make_FigS4_flip_probability.log
"""
import os, csv, logging
from datetime import datetime

ROOT = r"D:\WorkBuddy\两步法MR中介\⑤ 投稿文件_20260904"
FIGDIR = os.path.join(ROOT, "figure")
LOGDIR = os.path.join(ROOT, "log")
os.makedirs(LOGDIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOGDIR, "make_FigS4_flip_probability.log"),
    level=logging.INFO,
    format="%(asctime)s %(message)s"
)
log = logging.getLogger("make_FigS4_flip_probability")
log.info("make_FigS4_flip_probability.py — Supplementary Fig S4 flip probability")

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False

# Load the pre-computed flip-probability surface
CSV = r"C:\Users\up201\.workbuddy\m4src\T2_flip_prob_20260906.csv"
rows = []
with open(CSV, newline='') as f:
    for r in csv.DictReader(f):
        rows.append({k: float(v) for k, v in r.items()})

def subset(sgn, rho, F):
    return [r for r in rows if r['sgn'] == sgn and r['rho_MY'] == rho and r['F'] == F]

def plot_panel(ax, data, title, ylabel=False):
    pi_vals = sorted({r['pi_shared'] for r in data})
    colors = plt.cm.viridis(np.linspace(0.15, 0.85, len(pi_vals)))
    for pi, c in zip(pi_vals, colors):
        sub = sorted([r for r in data if r['pi_shared'] == pi], key=lambda x: x['lambda'])
        lam = [r['lambda'] for r in sub]
        fp = [100 * r['flip_prob'] for r in sub]
        ax.plot(lam, fp, color=c, marker='o', markersize=3, linewidth=1.5,
                label=f"$\\pi_{{\\mathrm{{shared}}}}={pi:.1f}$")
    ax.axvline(1.96, color='#999999', linestyle='--', linewidth=1.0, label='$\\lambda=1.96$')
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 12)
    ax.set_xlabel('True indirect-effect non-centrality  $\\lambda=\\delta/\\sigma_{\\mathrm{naive}}$')
    if ylabel:
        ax.set_ylabel('Flip probability (%)')
    ax.set_title(title, fontsize=11, fontweight='bold')
    ax.legend(loc='upper left', frameon=False, fontsize=8, handlelength=1.3)
    # Report panel maxima as annotations
    m = max(data, key=lambda r: r['flip_prob'])
    ax.text(0.98, 0.97, f"max {100*m['flip_prob']:.1f}%\n($\\pi$={m['pi_shared']:.1f}, $\\lambda$={m['lambda']:.2f})",
            transform=ax.transAxes, ha='right', va='top', fontsize=9,
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='gray'))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.3), sharey=True)
fig.suptitle('Figure S4. Flip probability as a function of true indirect-effect non-centrality',
             fontsize=12, fontweight='bold', y=0.98)

panelA = subset(sgn=1, rho=0, F=10)
panelB = subset(sgn=-1, rho=1, F=10)
plot_panel(ax1, panelA, 'Panel A. Concordant mediation ($\\rho_{MY}=0$, $F=10$)', ylabel=True)
plot_panel(ax2, panelB, 'Panel B. Discordant mediation / full overlap ($\\rho_{MY}=1$, $F=10$)')

fig.tight_layout(rect=[0, 0, 1, 0.94])
out = os.path.join(FIGDIR, 'FigS4_flip_probability.png')
fig.savefig(out, dpi=300, bbox_inches='tight', facecolor='white')
plt.close(fig)
log.info(f"[OK] {out} ({os.path.getsize(out)} bytes)")
print(f"[OK] {out} ({os.path.getsize(out)} bytes)")
