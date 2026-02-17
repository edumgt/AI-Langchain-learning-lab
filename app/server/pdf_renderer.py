from __future__ import annotations
import os, re, datetime as dt
from typing import List, Optional, Tuple

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame,
    Paragraph, Spacer, PageBreak,
    ListFlowable, ListItem, Table, TableStyle, Image
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib import colors

from app.server.pdf_theme import get_theme
from app.server.pdf_fonts import try_register_korean_fonts

def _split_md_lines(md_text: str) -> List[str]:
    return (md_text or "").replace("\r\n","\n").split("\n")

def _is_table_block(lines: List[str], i: int) -> bool:
    if i+1 >= len(lines):
        return False
    return ("|" in lines[i]) and re.match(r"^\s*\|?\s*[-:]+", (lines[i+1] or "").strip()) is not None

def _parse_table(lines: List[str], i: int):
    rows = []
    header = [c.strip() for c in lines[i].strip().strip("|").split("|")]
    rows.append(header)
    j = i+2
    while j < len(lines):
        line = lines[j]
        if not line.strip() or "|" not in line:
            break
        rows.append([c.strip() for c in line.strip().strip("|").split("|")])
        j += 1
    return rows, j

def _extract_title(md_text: str) -> str:
    for line in _split_md_lines(md_text):
        if line.startswith("# "):
            return line[2:].strip()
    return "Proposal"

def _header_footer(canvas, doc, theme, meta: dict):
    canvas.saveState()
    w, h = A4

    # header
    canvas.setFillColor(theme.secondary)
    canvas.setFont(theme.font_family, 9)
    header_left = meta.get("header_left") or meta.get("campaign_title") or "ArtBiz Proposal"
    canvas.drawString(18*mm, h - 12*mm, header_left[:80])

    # footer
    canvas.setFillColor(theme.secondary)
    canvas.setFont(theme.font_family, 9)
    canvas.drawString(18*mm, 10*mm, f"{meta.get('sponsor_name','')}"[:60])
    canvas.drawRightString(w - 18*mm, 10*mm, f"Page {doc.page}")
    canvas.restoreState()

class _Doc(BaseDocTemplate):
    def __init__(self, filename: str, theme, meta: dict):
        self.theme = theme
        self.meta = meta
        super().__init__(filename, pagesize=A4,
                         leftMargin=18*mm, rightMargin=18*mm,
                         topMargin=16*mm, bottomMargin=16*mm,
                         title=meta.get("title","Proposal"))

        frame = Frame(self.leftMargin, self.bottomMargin,
                      self.width, self.height,
                      id="normal")

        template = PageTemplate(
            id="with_header_footer",
            frames=[frame],
            onPage=lambda c, d: _header_footer(c, d, theme, meta)
        )
        self.addPageTemplates([template])

def _build_styles(theme, fonts: dict):
    styles = getSampleStyleSheet()
    base_font = fonts.get("regular") or theme.font_family
    bold_font = fonts.get("bold") or theme.font_family_bold

    styles["BodyText"].fontName = base_font
    styles["BodyText"].leading = 14
    styles["BodyText"].spaceAfter = 4

    H1 = ParagraphStyle("H1", parent=styles["Heading1"], fontName=bold_font, textColor=theme.primary, spaceAfter=10)
    H2 = ParagraphStyle("H2", parent=styles["Heading2"], fontName=bold_font, textColor=theme.primary, spaceAfter=8)
    H3 = ParagraphStyle("H3", parent=styles["Heading3"], fontName=bold_font, textColor=theme.primary, spaceAfter=6)

    Small = ParagraphStyle("Small", parent=styles["BodyText"], fontName=base_font, fontSize=9, leading=12, textColor=theme.secondary)
    Mono = ParagraphStyle("Mono", parent=styles["BodyText"], fontName="Courier", fontSize=9, leading=11, backColor=colors.HexColor("#F7F7F7"))

    return {"H1": H1, "H2": H2, "H3": H3, "Body": styles["BodyText"], "Small": Small, "Mono": Mono, "base": base_font, "bold": bold_font}

def _cover_page(story, styles, theme, meta: dict):
    title = meta.get("title") or "후원 제안서"
    sponsor = meta.get("sponsor_name","")
    campaign = meta.get("campaign_title","")
    date = meta.get("date") or dt.date.today().isoformat()
    logo = meta.get("logo_path")

    story.append(Spacer(1, 18*mm))
    if logo and os.path.exists(logo):
        try:
            img = Image(logo)
            img.drawHeight = 18*mm
            img.drawWidth = img.drawHeight * (img.imageWidth / max(img.imageHeight,1))
            story.append(img)
            story.append(Spacer(1, 10*mm))
        except Exception:
            pass

    story.append(Paragraph(title, styles["H1"]))
    story.append(Spacer(1, 6*mm))
    if campaign:
        story.append(Paragraph(f"<b>캠페인</b>: {campaign}", styles["Body"]))
    if sponsor:
        story.append(Paragraph(f"<b>후원사</b>: {sponsor}", styles["Body"]))
    story.append(Paragraph(f"<b>작성일</b>: {date}", styles["Body"]))
    story.append(Spacer(1, 10*mm))

    story.append(Paragraph("본 문서는 학습용 템플릿입니다. 조직/행사 특성에 맞게 수정하세요.", styles["Small"]))
    story.append(PageBreak())

def _toc_page(story, styles):
    story.append(Paragraph("목차", styles["H1"]))
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle(fontName=styles["bold"], name="TOCHeading1", fontSize=11, leftIndent=0, firstLineIndent=0, spaceBefore=5, leading=14),
        ParagraphStyle(fontName=styles["base"], name="TOCHeading2", fontSize=10, leftIndent=12, firstLineIndent=0, spaceBefore=2, leading=12),
    ]
    story.append(toc)
    story.append(PageBreak())
    return toc

def _notify_toc(doc, story, toc, heading_level: int, text: str):
    # attach a callback via doc.afterFlowable in build
    pass

def _parse_markdown_to_story(md_text: str, story, styles, theme, toc_hook):
    lines = _split_md_lines(md_text)
    buf_para = []
    i = 0

    def flush_para():
        nonlocal buf_para
        if buf_para:
            txt = " ".join([re.sub(r"\s+"," ", x).strip() for x in buf_para if x.strip()])
            if txt:
                story.append(Paragraph(txt, styles["Body"]))
            buf_para = []

    while i < len(lines):
        line = lines[i].rstrip()

        if not line.strip():
            flush_para()
            story.append(Spacer(1, 4))
            i += 1
            continue

        if line.startswith("# "):
            flush_para()
            text = line[2:].strip()
            p = Paragraph(text, styles["H1"])
            p._artbiz_toc = (0, text)  # level 0
            story.append(p)
            i += 1
            continue
        if line.startswith("## "):
            flush_para()
            text = line[3:].strip()
            p = Paragraph(text, styles["H2"])
            p._artbiz_toc = (1, text)  # level 1
            story.append(p)
            i += 1
            continue
        if line.startswith("### "):
            flush_para()
            text = line[4:].strip()
            p = Paragraph(text, styles["H3"])
            p._artbiz_toc = (2, text)  # level 2 (not shown by default)
            story.append(p)
            i += 1
            continue

        if _is_table_block(lines, i):
            flush_para()
            rows, j = _parse_table(lines, i)
            t = Table(rows, hAlign="LEFT", repeatRows=1)
            t.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), theme.table_header_bg),
                ("TEXTCOLOR", (0,0), (-1,0), theme.primary),
                ("GRID", (0,0), (-1,-1), 0.5, theme.table_grid),
                ("FONTNAME", (0,0), (-1,0), styles["bold"]),
                ("FONTNAME", (0,1), (-1,-1), styles["base"]),
                ("FONTSIZE", (0,0), (-1,-1), 9.5),
                ("ALIGN", (0,0), (-1,-1), "LEFT"),
                ("VALIGN", (0,0), (-1,-1), "TOP"),
                ("BOTTOMPADDING", (0,0), (-1,0), 6),
                ("TOPPADDING", (0,0), (-1,0), 6),
            ]))
            story.append(t)
            story.append(Spacer(1, 8))
            i = j
            continue

        if re.match(r"^\s*[-*]\s+", line):
            flush_para()
            items = []
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i].rstrip()):
                txt = re.sub(r"^\s*[-*]\s+", "", lines[i].rstrip()).strip()
                items.append(ListItem(Paragraph(txt, styles["Body"])))
                i += 1
            story.append(ListFlowable(items, bulletType="bullet", leftIndent=14))
            story.append(Spacer(1, 6))
            continue

        if line.strip().startswith("```"):
            flush_para()
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i].rstrip())
                i += 1
            if i < len(lines) and lines[i].strip().startswith("```"):
                i += 1
            code_text = "<br/>".join([re.sub(r"&","&amp;", re.sub(r"<","&lt;", l)) for l in code_lines]) or ""
            story.append(Paragraph(code_text, styles["Mono"]))
            story.append(Spacer(1, 6))
            continue

        buf_para.append(line)
        i += 1

    flush_para()

def render_markdown_to_pdf(md_text: str, pdf_path: str, title: Optional[str] = None, meta: Optional[dict] = None):
    """Publication-style PDF renderer.

    meta keys (optional):
      - sponsor_name, campaign_title, date
      - title (cover title)
      - logo_path (optional)
      - header_left (header text)
    """
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    meta = meta or {}
    theme = get_theme()
    fonts = try_register_korean_fonts()
    if fonts:
        theme.font_family = fonts["regular"]
        theme.font_family_bold = fonts["bold"]

    meta.setdefault("title", title or _extract_title(md_text))
    doc = _Doc(pdf_path, theme=theme, meta=meta)
    styles = _build_styles(theme, fonts)

    story = []
    _cover_page(story, styles, theme, meta)
    toc = _toc_page(story, styles)
    _parse_markdown_to_story(md_text, story, styles, theme, toc_hook=True)

    # hook headings into TOC
    def after_flowable(flowable):
        if hasattr(flowable, "_artbiz_toc"):
            level, text = flowable._artbiz_toc
            # only include H1/H2 in TOC
            if level <= 1:
                toc.addEntry(level, text, doc.page)

    doc.afterFlowable = after_flowable
    doc.build(story)
