# -*- coding: utf-8 -*-
"""
Build submission-ready .docx from D61_论文终稿_20260906.md
- Times New Roman throughout (body 12pt)
- Body paragraphs: justified, first-line indent (2 chars ~ 24pt)
- Citations [n] rendered as superscript, in order, before period (already in source)
- Display equations rendered offline via matplotlib mathtext (stix -> Times-like)
- 6 figures embedded (centered) in a Figures section; 4 tables inline
"""
import re, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from docx import Document
from docx.shared import Pt, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = r"D:\WorkBuddy\两步法MR中介\⑤ 投稿文件_20260904"
SRC = os.path.join(ROOT, "D61_论文终稿_20260906.md")
FIGDIR = os.path.join(ROOT, "figure")
OUT = os.path.join(ROOT, "D61_论文终稿_20260906.docx")
EQDIR = os.path.join(ROOT, "figure")
os.makedirs(EQDIR, exist_ok=True)

# ---------- 1. render display equations to PNG ----------
import glob as _glob
_times_candidates = [
    r'C:\Windows\Fonts\times.ttf', r'C:\Windows\Fonts\timesbd.ttf',
    r'C:\Windows\Fonts\timesi.ttf', r'C:\Windows\Fonts\TIMES.TTF',
]
_times_found = [p for p in _times_candidates if os.path.exists(p)]
if _times_found:
    for p in _times_found:
        try: font_manager.fontManager.addfont(p)
        except Exception: pass
    plt.rcParams['mathtext.fontset'] = 'custom'
    plt.rcParams['mathtext.rm'] = 'Times New Roman'
    plt.rcParams['mathtext.it'] = 'Times New Roman'
    plt.rcParams['mathtext.bf'] = 'Times New Roman'
    plt.rcParams['mathtext.cal'] = 'Times New Roman'
    plt.rcParams['mathtext.sf'] = 'Times New Roman'
    plt.rcParams['mathtext.tt'] = 'Times New Roman'
    plt.rcParams['font.family'] = 'Times New Roman'
else:
    plt.rcParams['mathtext.fontset'] = 'stix'
EQUATIONS = [
    r"\mathrm{Var}(\hat{\alpha}\hat{\beta}) \approx \hat{\beta}^{2}\,\mathrm{Var}(\hat{\alpha}) + \hat{\alpha}^{2}\,\mathrm{Var}(\hat{\beta})",
    r"\mathrm{Cov}(\hat{\alpha},\hat{\beta}) = \mathrm{Cov}_{\mathrm{shared}} + \mathrm{Cov}_{\mathrm{overlap}}",
    r"\mathrm{Var}(\hat{\alpha}\hat{\beta}) \approx \hat{\beta}^{2}\,\mathrm{Var}(\hat{\alpha}) + \hat{\alpha}^{2}\,\mathrm{Var}(\hat{\beta}) + 2\hat{\alpha}\hat{\beta}\,\mathrm{Cov}(\hat{\alpha},\hat{\beta})",
    r"B(F,\rho_{MY},\pi_{\mathrm{shared}}) = \frac{2}{F} + \frac{2|\rho_{MY}|\pi_{\mathrm{shared}}}{\sqrt{F}} + \frac{\rho_{MY}^{2}\pi_{\mathrm{shared}}}{F}",
]
eq_paths = []
for i, tex in enumerate(EQUATIONS, 1):
    p = os.path.join(EQDIR, f"eq{i}.png")
    fig = plt.figure(figsize=(6.6, 0.7))
    fig.text(0.5, 0.5, f"${tex}$", ha='center', va='center', fontsize=14)
    fig.savefig(p, dpi=300, bbox_inches='tight', transparent=True)
    plt.close(fig)
    eq_paths.append(p)
print("equations rendered:", len(eq_paths))

# ---------- 2. read source ----------
lines = open(SRC, encoding='utf-8').read().split('\n')

# ---------- 3. docx styling ----------
doc = Document()
# default Normal style -> Times New Roman 12pt
normal = doc.styles['Normal']
normal.font.name = 'Times New Roman'
normal.font.size = Pt(12)
normal.element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')

def set_first_line_indent(p, pts=24):
    p.paragraph_format.first_line_indent = Pt(pts)

def justify(p):
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

# ---------- 4. inline parser (handles **bold**, *italic* and [n] citations) ----------
def add_inline(parent, text, bold=False, base_size=12, clip=False):
    """Add runs to parent paragraph handling **bold** and [n] (superscript)."""
    pat = re.compile(r'(\*\*[^*]+\*\*|\*[^*]+\*|\[\d+\])')
    pos = 0
    for m in pat.finditer(text):
        if pos < m.start():
            r = parent.add_run(text[pos:m.start()])
            r.font.name = 'Times New Roman'; r.font.size = Pt(base_size)
            r.bold = bold
        tok = m.group(0)
        if tok.startswith('**'):
            r = parent.add_run(tok[2:-2]); r.bold = True
            r.font.name = 'Times New Roman'; r.font.size = Pt(base_size)
        elif tok.startswith('*'):   # single-asterisk italic
            r = parent.add_run(tok[1:-1]); r.italic = True
            r.font.name = 'Times New Roman'; r.font.size = Pt(base_size)
            r.bold = bold
        else:  # [n]
            r = parent.add_run(tok[1:-1])
            r.font.name = 'Times New Roman'; r.font.size = Pt(base_size)
            r.font.superscript = True
            r.bold = bold
        pos = m.end()
    if pos < len(text):
        r = parent.add_run(text[pos:])
        r.font.name = 'Times New Roman'; r.font.size = Pt(base_size)
        r.bold = bold

def add_body(text, indent=True, base_size=12):
    p = doc.add_paragraph()
    justify(p)
    if indent:
        set_first_line_indent(p, 24)
    add_inline(p, text, base_size=base_size)
    return p

def add_heading(text, level=1):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.bold = True
    if level == 1:
        run.font.size = Pt(13)
    else:
        run.font.size = Pt(12)
    return p

def add_centered(text, size=11, bold=False, italic=False):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    r.font.name = 'Times New Roman'; r.font.size = Pt(size)
    r.bold = bold; r.italic = italic
    return p

def add_bullet(text, numbered=False):
    p = doc.add_paragraph(style='List Number' if numbered else 'List Bullet')
    justify(p)
    # strip leading "N. " if numbered (style adds it)
    t = text
    if numbered:
        t = re.sub(r'^\d+\.\s+', '', text)
    add_inline(p, t)
    return p

def add_ref_paragraph(text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.74)
    p.paragraph_format.first_line_indent = Cm(-0.74)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    add_inline(p, text, base_size=10)
    return p

def add_equation(idx):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)
    p.add_run().add_picture(eq_paths[idx-1], width=Inches(5.6))
    return p

def add_table(rows, is_caption_preceding=None):
    # rows: list of list of str; first is header
    ncol = max(len(r) for r in rows)
    tbl = doc.add_table(rows=1, cols=ncol)
    tbl.style = 'Table Grid'
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = tbl.rows[0].cells
    for j, v in enumerate(rows[0]):
        hdr[j].text = ''
        rp = hdr[j].paragraphs[0].add_run(v)
        rp.bold = True; rp.font.name='Times New Roman'; rp.font.size = Pt(9.5)
    for r in rows[1:]:
        cells = tbl.add_row().cells
        for j in range(ncol):
            val = r[j] if j < len(r) else ''
            cells[j].text = ''
            rp = cells[j].paragraphs[0].add_run(val)
            rp.font.name='Times New Roman'; rp.font.size = Pt(9.5)
    return tbl

def shade_header(tbl):
    pass

# ---------- 5. parse markdown ----------
i = 0
state = 'body'
fig_legend_texts = {}  # N -> legend paragraph text
pending_table_caption = None
eq_counter = 0
in_references = False

while i < len(lines):
    line = lines[i]
    raw = line.rstrip('\n')

    # blank
    if raw.strip() == '':
        i += 1
        continue

    # horizontal rule (section break)
    if re.match(r'^-{3,}$|^={3,}$', raw.strip()):
        i += 1
        continue

    # close references block when a non-numbered line appears
    if in_references and not re.match(r'^\d+\.\s+', raw):
        in_references = False

    # title
    if raw.startswith('# '):
        add_centered(raw[2:].strip(), size=16, bold=True)
        i += 1
        continue

    # headings
    if raw.startswith('## '):
        htext = raw[3:].strip()
        # Special: Figure legends section -> embed each figure directly above its legend,
        # matching the markdown order and supporting both main (Fig 1-4) and
        # supplementary (Fig S1-S4) labels.
        if htext.lower().startswith('figure legends'):
            add_heading('Figures', 1)
            import glob
            i += 1
            while i < len(lines):
                line = lines[i]
                if line.startswith('## ') or line.strip() == '---':
                    break
                fm = re.match(r'^\*\*(?:Supplementary\s+)?Figure\s+(S?\d+)\.\*\*(.*)$', line, re.I)
                if fm:
                    label = fm.group(1).strip()            # e.g. "1" or "S1"
                    fn_pat = f"Fig{label.upper()}_*.png"   # Fig1_*.png or FigS1_*.png
                    matches = glob.glob(os.path.join(FIGDIR, fn_pat))
                    if matches:
                        pp = doc.add_paragraph()
                        pp.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        pp.add_run().add_picture(matches[0], width=Inches(6.0))
                    else:
                        print(f"[WARN] no image for Figure {label} (pattern {fn_pat})")
                    add_body(line, indent=False)
                elif line.strip():
                    add_body(line, indent=False)
                i += 1
            continue
        add_heading(htext, 1)
        if htext.lower() == 'references':
            in_references = True
        i += 1
        continue

    if raw.startswith('### '):
        add_heading(raw[4:].strip(), 2)
        i += 1
        continue

    # display equation block
    if raw.strip().startswith('$$'):
        # collect until closing $$
        buf = []
        if raw.strip() != '$$':
            buf.append(raw.strip().lstrip('$').rstrip('$'))
        i += 1
        while i < len(lines) and not lines[i].strip().startswith('$$'):
            buf.append(lines[i].strip())
            i += 1
        i += 1  # skip closing $$
        eq_counter += 1
        add_equation(eq_counter)
        continue

    # table detection
    if raw.strip().startswith('|') and i+1 < len(lines) and re.match(r'^\s*\|[\s:|-]+\|\s*$', lines[i+1]):
        # caption: previous non-empty line starting with '**Table' or 'Table'
        # parse rows
        tbl_rows = []
        while i < len(lines) and lines[i].strip().startswith('|'):
            cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
            tbl_rows.append(cells)
            i += 1
        # tbl_rows[1] is separator
        header = tbl_rows[0]
        data = tbl_rows[2:]
        # caption: look back - we stored caption text in preceding **Table N.** line
        add_table([header] + data)
        if pending_table_caption:
            cap = doc.add_paragraph()
            cap.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
            add_inline(cap, pending_table_caption, base_size=10)
            cap.runs[0].italic = True
            pending_table_caption = None
        continue

    # table caption line (preceding a table): "**Table N.** ..."
    if re.match(r'^\*\*Table', raw) or re.match(r'^Table \d', raw):
        pending_table_caption = raw
        i += 1
        continue

    # figure legend capture (in body **Figure N.** paragraphs) -- also embed inline? keep inline text, store legend
    fm = re.match(r'^\*\*Figure (\d+)\.\*\*(.*)$', raw)
    if fm:
        n = int(fm.group(1))
        fig_legend_texts[n] = raw  # store full legend for Figures section
        # also render inline in body (as bold description)
        add_body(raw, indent=False)
        i += 1
        continue

    # bullet list
    if re.match(r'^-\s+', raw):
        add_bullet(raw[2:].strip())
        i += 1
        continue

    # numbered list (1. ...) -- references use plain hanging-indent paragraphs
    if re.match(r'^\d+\.\s+', raw):
        if in_references:
            add_ref_paragraph(raw)
        else:
            add_bullet(raw, numbered=True)
        i += 1
        continue

    # author / affiliation / correspondence (centered, not justified)
    if raw.startswith('**Authors:**') or raw.startswith('**Affiliations:**') or raw.startswith('**Correspondence:**'):
        _p = doc.add_paragraph()
        _p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_inline(_p, raw, base_size=11)
        i += 1
        continue

    # Abstract / Keywords special handling
    if raw.strip() == '**Keywords:**' or raw.startswith('**Keywords:**'):
        p = doc.add_paragraph(); justify(p)
        add_inline(p, raw, base_size=11)
        i += 1
        continue

    # generic paragraph
    # detect if it is the Abstract heading (a standalone **Abstract**)
    if raw.strip() == '**Abstract**':
        add_heading('Abstract', 1)
        i += 1
        continue

    add_body(raw, indent=True)
    i += 1

# ---------- 6. finalize ----------
doc.core_properties.title = "Correcting for instrument overlap in two-step summary-data Mendelian randomization mediation"
doc.core_properties.author = "Yan Chen, Jianfeng Wang"

doc.save(OUT)
print("SAVED:", OUT)
