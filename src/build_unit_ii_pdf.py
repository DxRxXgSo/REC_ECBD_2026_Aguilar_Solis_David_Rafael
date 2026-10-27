"""Build the Unit II PDF directly from its Markdown source using ReportLab."""

from __future__ import annotations

import re
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


NAVY = colors.HexColor("#17364D")
BLUE = colors.HexColor("#2F6690")
PALE = colors.HexColor("#EAF1F5")
INK = colors.HexColor("#252E36")
PAGE_W, PAGE_H = letter


def register_fonts() -> tuple[str, str]:
    fonts = Path(r"C:\Windows\Fonts")
    regular = fonts / "arial.ttf"
    bold = fonts / "arialbd.ttf"
    italic = fonts / "ariali.ttf"
    bold_italic = fonts / "arialbi.ttf"
    if all(p.is_file() for p in (regular, bold, italic, bold_italic)):
        pdfmetrics.registerFont(TTFont("Arial", str(regular)))
        pdfmetrics.registerFont(TTFont("Arial-Bold", str(bold)))
        pdfmetrics.registerFont(TTFont("Arial-Italic", str(italic)))
        pdfmetrics.registerFont(TTFont("Arial-BoldItalic", str(bold_italic)))
        pdfmetrics.registerFontFamily(
            "Arial", normal="Arial", bold="Arial-Bold", italic="Arial-Italic", boldItalic="Arial-BoldItalic"
        )
        return "Arial", "Arial-Bold"
    return "Helvetica", "Helvetica-Bold"


def inline_markup(text: str) -> str:
    links: list[str] = []

    def preserve_link(match: re.Match[str]) -> str:
        label, url = match.group(1), match.group(2)
        token = f"@@LINK{len(links)}@@"
        links.append(f'<link href="{escape(url, {"\"": "&quot;"})}" color="#2F6690">{escape(label)}</link>')
        return token

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", preserve_link, text)
    text = escape(text)
    text = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", text)
    for index, link in enumerate(links):
        text = text.replace(f"@@LINK{index}@@", link)
    return text


def split_table_row(line: str) -> list[str]:
    return [part.strip() for part in line.strip().strip("|").split("|")]


def add_page_chrome(canvas, document) -> None:
    if document.page == 1:
        return
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D5DEE4"))
    canvas.setLineWidth(0.5)
    canvas.line(0.78 * inch, PAGE_H - 0.48 * inch, PAGE_W - 0.78 * inch, PAGE_H - 0.48 * inch)
    canvas.setFont("Arial", 8)
    canvas.setFillColor(colors.HexColor("#5A6973"))
    canvas.drawRightString(PAGE_W - 0.78 * inch, PAGE_H - 0.39 * inch, "UTTT | EXTRACCIÓN DE CONOCIMIENTO EN BASES DE DATOS")
    canvas.line(0.78 * inch, 0.48 * inch, PAGE_W - 0.78 * inch, 0.48 * inch)
    canvas.drawString(0.78 * inch, 0.31 * inch, "Unidad II | Informe técnico")
    canvas.drawRightString(PAGE_W - 0.78 * inch, 0.31 * inch, f"Página {document.page}")
    canvas.restoreState()


def build(root: Path) -> Path:
    font, bold_font = register_fonts()
    source = root / "docs/unidad_ii/informe_unidad_ii.md"
    output = root / "docs/unidad_ii/informe_unidad_ii.pdf"
    markdown = source.read_text(encoding="utf-8").splitlines()
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("BodyECBD", parent=styles["BodyText"], fontName=font, fontSize=9.4,
                              leading=13.2, textColor=INK, alignment=TA_JUSTIFY, spaceAfter=7))
    styles.add(ParagraphStyle("TitleECBD", parent=styles["Title"], fontName=bold_font, fontSize=24,
                              leading=29, textColor=NAVY, alignment=TA_CENTER, spaceAfter=12))
    styles.add(ParagraphStyle("H1ECBD", parent=styles["Heading1"], fontName=bold_font, fontSize=16,
                              leading=20, textColor=NAVY, spaceBefore=12, spaceAfter=7, keepWithNext=True))
    styles.add(ParagraphStyle("H2ECBD", parent=styles["Heading2"], fontName=bold_font, fontSize=12,
                              leading=15, textColor=BLUE, spaceBefore=9, spaceAfter=5, keepWithNext=True))
    styles.add(ParagraphStyle("CoverECBD", parent=styles["BodyText"], fontName=font, fontSize=11,
                              leading=17, textColor=INK, alignment=TA_CENTER, spaceAfter=6))
    styles.add(ParagraphStyle("CaptionECBD", parent=styles["BodyText"], fontName="Arial-Italic" if font == "Arial" else font,
                              fontSize=8.5, leading=11, textColor=INK, alignment=TA_CENTER, spaceAfter=9))
    styles.add(ParagraphStyle("CodeECBD", parent=styles["Code"], fontName="Courier", fontSize=8,
                              leading=10, leftIndent=8, rightIndent=8, backColor=PALE, borderPadding=6,
                              spaceBefore=3, spaceAfter=7, wordWrap="CJK"))
    styles.add(ParagraphStyle("TableCellECBD", parent=styles["BodyText"], fontName=font, fontSize=8,
                              leading=10, textColor=INK, spaceAfter=0))
    story = []

    story.extend([Spacer(1, 0.95 * inch), Paragraph("UNIVERSIDAD TECNOLÓGICA<br/>DE TULA-TEPEJI", ParagraphStyle(
        "InstitutionECBD", parent=styles["CoverECBD"], fontName=bold_font, fontSize=17,
        leading=22, textColor=NAVY, spaceAfter=16)),
        Paragraph("Tecnologías de la Información", styles["CoverECBD"]),
        Spacer(1, 0.38 * inch),
        Paragraph("PROYECTO INTEGRADOR DE RECURSAMIENTO 2026", ParagraphStyle(
            "ProgramECBD", parent=styles["CoverECBD"], fontName=bold_font, fontSize=11,
            textColor=BLUE, spaceAfter=29)),
        Paragraph("Unidad II", ParagraphStyle("UnitECBD", parent=styles["CoverECBD"],
                  fontName=bold_font, fontSize=24, leading=29, textColor=BLUE, spaceAfter=5)),
        Paragraph("Análisis exploratorio y preparación de datos", ParagraphStyle(
            "SubtitleECBD", parent=styles["CoverECBD"], fontName=bold_font, fontSize=15,
            leading=20, textColor=NAVY, spaceAfter=14)),
        Paragraph("Análisis de hábitos y condición física asociados con niveles de obesidad", styles["CoverECBD"]),
        Spacer(1, 0.3 * inch),
        Paragraph("David Rafael Aguilar Solis · Matrícula 22300607 · Grupo 10IDGS-G1", styles["CoverECBD"]),
        Paragraph("Asignatura: Extracción de Conocimiento en Bases de Datos", styles["CoverECBD"]),
        Paragraph("Docente: pendiente de confirmación", styles["CoverECBD"]),
        Paragraph("Fecha de elaboración: 27 de octubre de 2026", styles["CoverECBD"]),
        Spacer(1, 0.35 * inch),
        Paragraph("Documento de análisis académico y registro técnico reproducible", ParagraphStyle(
            "NoteECBD", parent=styles["CoverECBD"], fontSize=9, textColor=colors.HexColor("#5A6973"))),
        PageBreak()])

    figure_map = {
        "El análisis gráfico incluye conteos de clase": [
            ("distribucion_n_obesidad.png", "Figura 1. Conteos observados por categoría."),
            ("distribuciones_numericas.png", "Figura 2. Distribuciones de variables numéricas y escalas."),
            ("peso_por_categoria.png", "Figura 3. Peso observado por categoría de etiqueta."),
        ]
    }
    start_body = next((i for i, line in enumerate(markdown) if line.startswith("## Alcance y resultado")), None)
    if start_body is None:
        raise ValueError("No se encontró el encabezado 'Alcance y resultado' en el Markdown.")
    i = start_body
    while i < len(markdown):
        raw = markdown[i].strip()
        if not raw:
            i += 1
            continue
        if raw.startswith("# "):
            story.append(Paragraph(inline_markup(raw[2:]), styles["TitleECBD"]))
            i += 1
            continue
        if raw.startswith("## "):
            story.append(Paragraph(inline_markup(raw[3:]), styles["H1ECBD"]))
            i += 1
            continue
        if raw.startswith("### "):
            story.append(Paragraph(inline_markup(raw[4:]), styles["H2ECBD"]))
            i += 1
            continue
        if raw.startswith("```"):
            i += 1
            code_lines = []
            while i < len(markdown) and not markdown[i].strip().startswith("```"):
                code_lines.append(markdown[i].rstrip())
                i += 1
            story.append(Preformatted("\n".join(code_lines), styles["CodeECBD"], maxLineLength=88))
            i += 1
            continue
        if raw.startswith("|"):
            rows = []
            while i < len(markdown) and markdown[i].strip().startswith("|"):
                row = split_table_row(markdown[i])
                if not row or all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in row):
                    i += 1
                    continue
                rows.append([Paragraph(inline_markup(cell), styles["TableCellECBD"]) for cell in row])
                i += 1
            if rows:
                widths = [(PAGE_W - 1.56 * inch) / len(rows[0])] * len(rows[0])
                table = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), bold_font), ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C8D3DA")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5), ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]))
                story.append(table)
                story.append(Spacer(1, 7))
            continue
        if raw.startswith("- "):
            items = []
            while i < len(markdown) and markdown[i].strip().startswith("- "):
                items.append(ListItem(Paragraph(inline_markup(markdown[i].strip()[2:]), styles["BodyECBD"]), leftIndent=12))
                i += 1
            story.append(ListFlowable(items, bulletType="bullet", start="circle", leftIndent=18,
                                      bulletFontName=font, bulletFontSize=7, spaceAfter=5))
            continue
        if raw.startswith("> "):
            story.append(Paragraph(inline_markup(raw[2:]), ParagraphStyle(
                "QuoteECBD", parent=styles["BodyECBD"], leftIndent=14, borderColor=BLUE,
                borderWidth=1, borderPadding=6, backColor=PALE)))
            i += 1
            continue
        if raw == "---":
            i += 1
            continue
        story.append(Paragraph(inline_markup(raw), styles["BodyECBD"]))
        for trigger, figures in figure_map.items():
            if raw.startswith(trigger):
                for filename, caption in figures:
                    path = root / "docs/unidad_ii/figuras" / filename
                    if not path.is_file():
                        raise FileNotFoundError(f"Falta figura requerida: {path}")
                    image = Image(str(path))
                    scale = min((PAGE_W - 1.7 * inch) / image.imageWidth, 3.0 * inch / image.imageHeight)
                    image.drawWidth = image.imageWidth * scale
                    image.drawHeight = image.imageHeight * scale
                    story.append(KeepTogether([image, Paragraph(caption, styles["CaptionECBD"])]))
        i += 1

    doc = SimpleDocTemplate(str(output), pagesize=letter, rightMargin=0.78 * inch, leftMargin=0.78 * inch,
                            topMargin=0.68 * inch, bottomMargin=0.65 * inch,
                            title="Unidad II Análisis exploratorio y preparación de datos",
                            author="David Rafael Aguilar Solis", subject="Extracción de Conocimiento en Bases de Datos")
    doc.build(story, onFirstPage=add_page_chrome, onLaterPages=add_page_chrome)
    return output


if __name__ == "__main__":
    print(build(Path(__file__).resolve().parents[1]))
