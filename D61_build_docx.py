# -*- coding: utf-8 -*-
"""
Build submission-ready .docx from D61_论文终稿_20260906.md
- Times New Roman throughout (body 12pt)
- Body paragraphs: justified, first-line indent (2 chars ~ 24pt)
- Citations [n] rendered as superscript, in order, before period (already in source)
- Display equations inserted as native Word OMML (editable, not raster images)
- figures are supplied as SEPARATE files; only their legends appear here, at
  the end of the manuscript (no image is embedded)
- every table is rendered as a classic three-line (booktabs) table: solid top
  and bottom rules plus a solid rule under the header, no vertical rules
"""
import re, os
# (display equations are native OMML; matplotlib no longer needed)
from docx import Document
from docx.shared import Pt, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement, parse_xml

ROOT = r"D:\WorkBuddy\两步法MR中介\⑤ 投稿文件_20260904"
SRC = os.path.join(ROOT, "D61_论文终稿_20260906.md")
FIGDIR = os.path.join(ROOT, "figure")
OUT = os.path.join(ROOT, "D61_论文终稿_20260906.docx")
EQDIR = os.path.join(ROOT, "figure")
os.makedirs(EQDIR, exist_ok=True)

# ---------- 1. native Word (OMML) display equations ----------
NS_M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'

def _mr(txt, plain=False):
    sty = '<m:rPr><m:sty m:val="p"/></m:rPr>' if plain else ''
    return f'<m:r>{sty}<m:t>{txt}</m:t></m:r>'

def _acc(base):
    return (f'<m:acc><m:accPr><m:chr m:val="^"/></m:accPr>'
            f'<m:e>{base}</m:e></m:acc>')

def _sup(base, sup):
    return f'<m:sSup><m:e>{base}</m:e><m:sup>{sup}</m:sup></m:sSup>'

def _sub(base, sub):
    return f'<m:sSub><m:e>{base}</m:e><m:sub>{sub}</m:sub></m:sSub>'

def _frac(num, den):
    return f'<m:f><m:num>{num}</m:num><m:den>{den}</m:den></m:f>'

def _rad(base):
    return (f'<m:rad><m:radPr/><m:deg><m:r><m:t>2</m:t></m:r></m:deg>'
            f'<m:e>{base}</m:e></m:rad>')

def _delim(content):
    return (f'<m:d><m:dPr><m:begChr m:val="|"/><m:endChr m:val="|"/></m:dPr>'
            f'<m:e>{content}</m:e></m:d>')

# shared tokens (Greek letters render as math-italic; function/label words upright)
_A = _mr('\u03b1'); _B = _mr('\u03b2'); _R = _mr('\u03c1'); _P = _mr('\u03c0'); _F = _mr('F')
_AH = _acc(_A); _BH = _acc(_B)
_VAR = _mr('Var', plain=True); _COV = _mr('Cov', plain=True); _TWO = _mr('2', plain=True)
_LP = _mr('('); _RP = _mr(')'); _CM = _mr(','); _AP = _mr('\u2248'); _PL = _mr('+'); _EQ = _mr('=')
_shared = _mr('shared', plain=True); _MY = _mr('MY', plain=True); _ovlp = _mr('overlap', plain=True)

_OMML = [
    # 1. Var(ab) ~= b^2 Var(a) + a^2 Var(b)
    (_VAR + _LP + _AH + _BH + _RP + _AP
     + _sup(_BH, _TWO) + _VAR + _LP + _AH + _RP
     + _PL + _sup(_AH, _TWO) + _VAR + _LP + _BH + _RP),
    # 2. Cov(a,b) = Cov_shared + Cov_overlap
    (_COV + _LP + _AH + _CM + _BH + _RP + _EQ
     + _sub(_COV, _shared) + _PL + _sub(_COV, _ovlp)),
    # 3. Var(ab) ~= b^2 Var(a) + a^2 Var(b) + 2ab Cov(a,b)
    (_VAR + _LP + _AH + _BH + _RP + _AP
     + _sup(_BH, _TWO) + _VAR + _LP + _AH + _RP
     + _PL + _sup(_AH, _TWO) + _VAR + _LP + _BH + _RP
     + _PL + _TWO + _AH + _BH + _COV + _LP + _AH + _CM + _BH + _RP),
    # 4. B(F,rho_MY,pi_shared) = 2/F + 2|rho_MY|pi_shared/sqrt(F) + rho_MY^2 pi_shared/F
    (_mr('B', plain=True) + _LP + _F + _CM
     + _sub(_R, _MY) + _CM + _sub(_P, _shared) + _RP + _EQ
     + _frac(_TWO, _F)
     + _PL + _frac(_TWO + _delim(_sub(_R, _MY)) + _sub(_P, _shared), _rad(_F))
     + _PL + _frac(_sup(_sub(_R, _MY), _TWO) + _sub(_P, _shared), _F)),
]

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
    elif level == 2:
        run.font.size = Pt(12)
    else:
        run.font.size = Pt(11.5)
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
    # Journal style: the reference list is justified with a two-character
    # first-line indent (no hanging indent), matching the body-text convention.
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Pt(20)   # 2 chars at the 10 pt ref size
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    add_inline(p, text, base_size=10)
    return p

def add_equation(idx):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)
    xml = f'<m:oMath xmlns:m="{NS_M}">{_OMML[idx-1]}</m:oMath>'
    p._p.append(parse_xml(xml))
    return p

def _set_three_line_borders(tbl):
    """Classic three-line (booktabs) table style.

    A solid rule on the top, a solid rule under the header row, and a solid
    rule at the bottom. No vertical rules, no side borders and no interior
    horizontal rules between data rows.
    """
    tblPr = tbl._tbl.tblPr
    borders = OxmlElement('w:tblBorders')
    spec = [('top', 'single', 12), ('left', 'none', 0), ('bottom', 'single', 12),
            ('right', 'none', 0), ('insideH', 'none', 0), ('insideV', 'none', 0)]
    for edge, val, sz in spec:
        e = OxmlElement('w:' + edge)
        e.set(qn('w:val'), val)
        e.set(qn('w:sz'), str(sz))
        e.set(qn('w:space'), '0')
        e.set(qn('w:color'), 'auto')
        borders.append(e)
    tblPr.append(borders)
    # solid rule under the header row
    for cell in tbl.rows[0].cells:
        tcPr = cell._tc.get_or_add_tcPr()
        tcB = OxmlElement('w:tcBorders')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), '6')
        bottom.set(qn('w:space'), '0')
        bottom.set(qn('w:color'), 'auto')
        tcB.append(bottom)
        tcPr.append(tcB)


def add_table(rows, is_caption_preceding=None):
    # rows: list of list of str; first is header
    ncol = max(len(r) for r in rows)
    tbl = doc.add_table(rows=1, cols=ncol)
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
    _set_three_line_borders(tbl)
    return tbl

def shade_header(tbl):
    pass

# ---------- 5. parse markdown ----------
def _table_sep_below(lines, idx):
    """True if a markdown table separator is at idx, skipping blank lines."""
    k = idx
    while k < len(lines) and not lines[k].strip():
        k += 1
    return k < len(lines) and re.match(r'^\s*\|[\s:|-]+\|\s*$', lines[k]) is not None



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
        # Figure legends section. The figures themselves are supplied as
        # SEPARATE files (this journal requires figures and manuscript to be
        # separate), so nothing is embedded here: the manuscript keeps only the
        # legend text, collected at the end of the manuscript.
        if htext.lower().startswith('figure legends'):
            add_heading('Figure legends', 1)
            add_body('Figures are provided as separate electronic files '
                     '(Fig. 1-4 and Supplementary Fig. S1-S4).', indent=False)
            i += 1
            while i < len(lines):
                line = lines[i]
                if line.startswith('## ') or line.strip() == '---':
                    break
                if line.strip():
                    add_body(line, indent=False)
                i += 1
            continue
        add_heading(htext, 1)
        if htext.lower() == 'references':
            in_references = True
        i += 1
        continue

    if raw.startswith('#### '):
        add_heading(raw[5:].strip(), 3)
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
    if raw.strip().startswith('|') and _table_sep_below(lines, i+1):
        # caption: previous non-empty line starting with '**Table' or 'Table'
        # parse rows, tolerating blank lines inside the table block
        tbl_rows = []
        j = i
        while j < len(lines):
            if lines[j].strip().startswith('|'):
                cells = [c.strip() for c in lines[j].strip().strip('|').split('|')]
                tbl_rows.append(cells)
                j += 1
            elif not lines[j].strip() and j+1 < len(lines) and lines[j+1].strip().startswith('|'):
                j += 1
            else:
                break
        i = j
        # tbl_rows[1] is separator
        header = tbl_rows[0]
        data = tbl_rows[2:]
        # caption: look back - we stored caption text in preceding **Table N.** line
        add_table([header] + data)
        if pending_table_caption:
            cap = doc.add_paragraph()
            cap.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
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
def _force_times(document):
    """Guarantee Times New Roman on EVERY run (ascii / hAnsi / eastAsia / cs),
    so the whole manuscript is typographically uniform regardless of which
    paragraph style happens to be in force (List Bullet, List Number, ...)."""
    def _fix(runs):
        for r in runs:
            r.font.name = 'Times New Roman'
            rPr = r._element.get_or_add_rPr()
            rf = rPr.get_or_add_rFonts()
            for attr in ('w:ascii', 'w:hAnsi', 'w:eastAsia', 'w:cs'):
                rf.set(qn(attr), 'Times New Roman')
    for p in document.paragraphs:
        _fix(p.runs)
    for t in document.tables:
        for row in t.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    _fix(p.runs)

_force_times(doc)

doc.core_properties.title = "Correcting for instrument overlap in two-step summary-data Mendelian randomization mediation"
doc.core_properties.author = "Yan Chen, Jianfeng Wang"

doc.save(OUT)
print("SAVED:", OUT)
