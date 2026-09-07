# -*- coding: utf-8 -*-
"""
make_raster_figure_titles.py
Add (or standardise) the titles of the three figures that have no vector
generator in this repository — Fig 1, Fig 3 and Supplementary Fig S1. These
originate from an earlier R/ggplot pipeline; the pristine 300-dpi renders are
kept in figure/_source/ and are never modified.

Modes
-----
* "replace" (Fig 1 and Fig S1): the existing title occupies the top band and
  is painted over with white before the standard title is drawn in its place.
  The per-figure cover heights were located from the row-wise ink profile of
  the source PNGs (Fig 1: rows 0-180 are safe; Fig S1: rows 0-130 clear the
  old title and its separator line).
* "prepend" (Fig 3): no title exists, so a blank band is added above the
  untouched source image and the standard title is drawn in it.

All sources are composited onto a white background before processing so that
any transparency in the original PNG does not turn black.

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
    # name, mode, cover_px (replace only), title
    ("Fig1_conceptual", "replace", 180,
     "Figure 1. Conceptual diagram of two-step (product-method) MR mediation "
     "with overlapping instruments"),
    ("Fig3_literature", "prepend", 0,
     "Figure 3. Percentage of 333 two-step MR mediation studies at risk of "
     "non-zero covariance under three classification assumptions"),
    ("FigS1_simulation", "replace", 130,
     "Supplementary Figure S1. Relative error of the traditional delta-method "
     "SE and empirical 95% CI coverage from bootstrap validation"),
]


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


def composite_on_white(src_path):
    """Return source as RGB composited on white, preserving anti-aliasing."""
    im = Image.open(src_path)
    if im.mode in ("RGBA", "LA"):
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        return Image.alpha_composite(bg, im.convert("RGBA")).convert("RGB")
    return im.convert("RGB")


def build(name, mode, cover_px, title):
    src = os.path.join(SRCDIR, name + ".png")
    if not os.path.exists(src):
        src = os.path.join(FIGDIR, name + ".png")
    im = composite_on_white(src)
    W, H = im.size
    font = load_font(FONT_SIZE)
    lines = wrap(title, font, W - 2 * SIDE_MARGIN)
    line_h = int(FONT_SIZE * LINE_SPACING)
    band_h = max(150, line_h * len(lines) + 60)

    if mode == "replace":
        band = min(max(band_h, cover_px), 320)
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


for name, mode, cover_px, title in FIGURES:
    build(name, mode, cover_px, title)

log.info("done")
print("\nDone. Run export_figures_pdf.py to refresh the PDFs.")
