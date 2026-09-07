# -*- coding: utf-8 -*-
"""
canonicalize_figure_names.py
Rename and clean figure/ so PNG filenames strictly match the order in which they
appear in the Figure legends section of the manuscript.

Target mapping:
  Figure 1  -> Fig1_conceptual.png (keep)
  Figure 2  -> Fig2_PRISMA.png (generated separately)
  Supplementary Figure S1 -> FigS1_simulation.png (was Fig2_simulation.png)
  Figure 3  -> Fig3_literature.png (was Fig4_literature.png)
  Figure 4  -> Fig4_realdata.png (keep; supersedes Fig3_realdatavforest.png)
  Supplementary Figure S2 -> FigS2_pisweep.png (keep)
  Supplementary Figure S3 -> FigS3_batch_forest.png (keep)
  Supplementary Figure S4 -> FigS4_flip_probability.png (generated separately)

Files removed to avoid glob collisions:
  Fig3_realdatavforest.png, Fig5_pisweep.png, Fig6_batch_forest.png
SVG source files are preserved.

Log: log/canonicalize_figure_names.log
"""
import os, logging, shutil

ROOT = r"D:\WorkBuddy\两步法MR中介\⑤ 投稿文件_20260904"
FIGDIR = os.path.join(ROOT, "figure")
LOGDIR = os.path.join(ROOT, "log")
os.makedirs(LOGDIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOGDIR, "canonicalize_figure_names.log"),
    level=logging.INFO,
    format="%(asctime)s %(message)s"
)
log = logging.getLogger("canonicalize_figure_names")
log.info("canonicalize_figure_names.py — align figure filenames with legend order")

# Renames: (old, new)
renames = [
    ("Fig4_literature.png", "Fig3_literature.png"),
    ("Fig2_simulation.png", "FigS1_simulation.png"),
]

# Files that are superseded or would match wrong legend glob pattern
remove = [
    "Fig3_realdatavforest.png",
    "Fig5_pisweep.png",
    "Fig6_batch_forest.png",
]

for old, new in renames:
    oldp = os.path.join(FIGDIR, old)
    newp = os.path.join(FIGDIR, new)
    if os.path.exists(oldp):
        if os.path.exists(newp):
            log.warning(f"target {new} already exists; removing old {old} without rename")
            os.remove(oldp)
            print(f"[WARN] {old} removed (target {new} already exists)")
        else:
            os.rename(oldp, newp)
            log.info(f"[RENAME] {old} -> {new}")
            print(f"[RENAME] {old} -> {new}")
    else:
        log.info(f"[SKIP rename] {old} does not exist")
        print(f"[SKIP rename] {old} does not exist")

for fname in remove:
    p = os.path.join(FIGDIR, fname)
    if os.path.exists(p):
        os.remove(p)
        log.info(f"[REMOVE] {fname}")
        print(f"[REMOVE] {fname}")
    else:
        log.info(f"[SKIP remove] {fname} does not exist")
        print(f"[SKIP remove] {fname} does not exist")

# Final check: list all PNGs in legend order
print("\n=== final PNG files ===")
for pat in ["Fig1_*.png", "Fig2_*.png", "FigS1_*.png", "Fig3_*.png",
            "Fig4_*.png", "FigS2_*.png", "FigS3_*.png", "FigS4_*.png"]:
    matches = [f for f in os.listdir(FIGDIR) if f.lower().endswith('.png')
               and f.startswith(pat.split('*')[0])]
    status = matches[0] if matches else "MISSING"
    print(f"  {pat}: {status}")

log.info("canonicalization complete")
print("\ncanonicalization complete")
