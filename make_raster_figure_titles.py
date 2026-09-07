# -*- coding: utf-8 -*-
"""
make_raster_figure_titles.py
Add (or standardise) the titles of the three figures that have no vector
generator in this repository — Fig 1, Fig 3 and Supplementary Fig S1. These
originate from an earlier R/ggplot pipeline; the pristine 300-dpi renders are
kept in figure/_source/ and are never modified.

Modes
-----
* "replace" (Fig 1): the existing non-standard title occupies the top band and
  is painted over with white before the standard title is drawn in its place.
  The band height was located from the row-wise ink profile of the source PNG
  (ink rows 65-131 of 1700; rows 0-60 and 135-180 are blank), so covering the
  top 180 px cannot touch figure content.
* "prepend" (Fig 3, Fig S1): no title exists, so a blank band is added above
  the untouched source image and the standard title is drawn in it.

Titles are plain ASCII on purpose: the raster pipeline uses Times New Roman and
must not depend on Greek or combining-diacritic glyph coverage.

Output: figure/<name>.png  (overwritten; re-run export_figures_pdf.py for PDFs)
Log   : log/make_raster_figure_titles.log
"""
import os
import textwrap
import logging

ROOT = r"D:\WorkBuddy\两步法MR中介\⑤ 投稿文件_20260904"
FIGDIR = os.path.join(ROOT, "figure")
SRCDIR = os.path.join(FIGDIR, "_source")
LOGDIR = os.path.join(ROOT, "log")
os.makedirs(LOGDIR, exist_ok=True)
os.makedirs(SRCDIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOGDIR, "make_raster_figure_titles.log"),
    level=logging.INFO,
    format="%(asctime)s %(message)s",
)
log = logging.getLogger("make_raster_figure_titles")
log.info("make_raster_figure_titles.py — standardise titles of raster figures")

from PIL import Image, ImageDraw, ImageFont

FONT_BOLD = r"C:\Windows\Fonts\timesbd.ttf"
FONT_REGULAR = r"C:\Windows\Fonts\times.ttf"
FONT_SIZE = 46          # px at 300 dpi == 11 pt
LINE_SPACING = 1.32
SIDE_MARGIN = 90        # px

FIGURES = [
    # name, mode, title
    ("Fig1_conceptual", "replace",
     "Figure 1. Conceptual diagram of two-step (product-method) MR mediation "
     "with overlapping instruments"),
    ("Fig3_literature", "prepend",
     "Figure 3. Percentage of 333 two-step MR mediation studies at risk of "
     "non-zero covariance under three classification assumptions"),
    ("FigS1_simulation", "prepend",
     "Supplementary Figure S1. Relative error of the traditional delta-method "
     "SE and empirical 95% CI coverage from bootstrap validation"),
]

COVER_PX = 180          # Fig 1: safe top band (ink rows 65-131; blank to 180)


def load_font(size):
    for p in (FONT_BOLD, FONT_REGULAR):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def wrap(title, font, max_width):
    """Greedy word wrap bounded by max_width px."""
    words = title.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if font.getlength(trial) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_title_band(draw, lines, font, width, top, band_h):
    """Centre a block of wrapped lines inside [top, top+band_h]."""
    line_h = int(FONT_SIZE * LINE_SPACING)
    total = line_h * len(lines)
    y = top + (band_h - total) // 2
    for ln in lines:
        w = font.getlength(ln)
        draw.text(((width - w) / 2, y), ln, font=font, fill=(0, 0, 0))
        y += line_h


def build(name, mode, title):
    src = os.path.join(SRCDIR, name + ".png")
    if not os.path.exists(src):
        src = os.path.join(FIGDIR, name + ".png")
    im = Image.open(src).convert("RGB")
    W, H = im.size
    font = load_font(FONT_SIZE)
    lines = wrap(title, font, W - 2 * SIDE_MARGIN)
    line_h = int(FONT_SIZE * LINE_SPACING)
    band_h = max(150, line_h * len(lines) + 60)

    if mode == "replace":
        band = min(max(band_h, COVER_PX), 320)
        out = im.copy()
        d = ImageDraw.Draw(out)
        d.rectangle([0, 0, W, band], fill=(255, 255, 255))
        draw_title_band(d, lines, font, W, 0, band)
    else:  # prepend
        out = Image.new("RGB", (W, H + band_h), (255, 255, 255))
        out.paste(im, (0, band_h))
        d = ImageDraw.Draw(out)
        draw_title_band(d, lines, font, W, 0, band_h)

    dst = os.path.join(FIGDIR, name + ".png")
    out.save(dst, dpi=(300, 300))
    msg = (f"[OK] {name}.png  {out.size[0]}x{out.size[1]} px  "
           f"mode={mode}  lines={len(lines)}  ({os.path.getsize(dst)} bytes)")
    log.info(msg)
    print(msg)
    log.info("     title: " + " ".join(lines))


for name, mode, title in FIGURES:
    build(name, mode, title)

log.info("done")
print("\nDone. Run export_figures_pdf.py to refresh the PDFs.")
