# -*- coding: utf-8 -*-
"""
export_figures_pdf.py
Produce submission-ready PDF versions of the figures that have no vector
generator in this repository (Fig 1, Fig 3, Supplementary Fig S1). These three
originate from an earlier R/ggplot pipeline whose sources are archived; the
300-dpi PNGs are therefore embedded into PDF pages at their native 300 dpi so
the submitted PDF is pixel-identical to the raster used in the manuscript.

Figures produced as TRUE VECTOR PDF are handled by their own generators:
    make_Fig2_PRISMA.py            -> figure/Fig2_PRISMA.pdf
    make_Fig4_realdata.py          -> figure/Fig4_realdata.pdf
    D61_make_figures.py            -> figure/FigS2_pisweep.pdf , FigS4_batch_forest.pdf
    make_FigS3_flip_probability.py -> figure/FigS3_flip_probability.pdf

Output: figure/Fig1_conceptual.pdf , Fig3_literature.pdf , FigS1_simulation.pdf
Log   : log/export_figures_pdf.log
"""
import os
import logging

ROOT = r"D:\WorkBuddy\两步法MR中介\⑤ 投稿文件_20260904"
FIGDIR = os.path.join(ROOT, "figure")
LOGDIR = os.path.join(ROOT, "log")
os.makedirs(LOGDIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOGDIR, "export_figures_pdf.log"),
    level=logging.INFO,
    format="%(asctime)s %(message)s",
)
log = logging.getLogger("export_figures_pdf")
log.info("export_figures_pdf.py — embed 300-dpi raster figures into PDF pages")

from PIL import Image

RASTER_FIGURES = [
    "Fig1_conceptual.png",
    "Fig3_literature.png",
    "FigS1_simulation.png",
]

DPI = 300.0

for fname in RASTER_FIGURES:
    src = os.path.join(FIGDIR, fname)
    if not os.path.exists(src):
        log.warning(f"[SKIP] {fname} not found")
        print(f"[SKIP] {fname} not found")
        continue
    im = Image.open(src)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGB")
    dst = os.path.join(FIGDIR, os.path.splitext(fname)[0] + ".pdf")
    im.save(dst, "PDF", resolution=DPI)
    w_in, h_in = im.size[0] / DPI, im.size[1] / DPI
    msg = f"[OK] {os.path.basename(dst)}  {im.size[0]}x{im.size[1]} px @ {DPI:.0f} dpi " \
          f"= {w_in:.2f} x {h_in:.2f} in  ({os.path.getsize(dst)} bytes)"
    log.info(msg)
    print(msg)

log.info("done")
print("\ndone")
