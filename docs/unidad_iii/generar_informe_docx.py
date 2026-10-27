"""Build the Unit III DOCX from its Markdown source using python-docx."""

from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs/unidad_iii/informe_unidad_iii.md"
OUTPUT = ROOT / "docs/unidad_iii/informe_unidad_iii.docx"


def plain(text: str) -> str:
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", text)
    return text.strip()


def cell_fill(cell, color: str) -> None:
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), color)
    cell._tc.get_or_add_tcPr().append(shading)


def build() -> Path:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.72)
    section.bottom_margin = Inches(0.72)
    section.left_margin = Inches(0.78)
    section.right_margin = Inches(0.78)
    normal = doc.styles["Normal"]
    normal.font.name = "Aptos"
    normal.font.size = Pt(10)
    normal.font.color.rgb = RGBColor(38, 48, 58)
    normal.paragraph_format.space_after = Pt(5)
    normal.paragraph_format.line_spacing = 1.08
    for name, size, color in (("Title", 23, "17324D"), ("Heading 1", 16, "17324D"),
                              ("Heading 2", 12, "176B87")):
        style = doc.styles[name]
        style.font.name = "Aptos Display"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(color)
        style.paragraph_format.space_before = Pt(10 if name != "Title" else 0)
        style.paragraph_format.space_after = Pt(5)
        if name == "Title" and style._element.pPr is not None:
            borders = style._element.pPr.find(qn("w:pBdr"))
            if borders is not None:
                style._element.pPr.remove(borders)

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = footer.add_run("UTTT · Extracción de Conocimiento en Bases de Datos · Unidad III")
    run.font.name = "Aptos"
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor(100, 110, 120)

    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        if line.startswith("|"):
            rows = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                row = [plain(part.strip()) for part in lines[index].strip().strip("|").split("|")]
                if not row or all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in row):
                    index += 1
                    continue
                rows.append(row)
                index += 1
            if rows:
                table = doc.add_table(rows=1, cols=len(rows[0]))
                table.alignment = WD_TABLE_ALIGNMENT.CENTER
                table.style = "Table Grid"
                table.autofit = True
                for row_idx, values in enumerate(rows):
                    cells = table.rows[0].cells if row_idx == 0 else table.add_row().cells
                    for col_idx, value in enumerate(values):
                        cell = cells[col_idx]
                        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
                        cell.text = value
                        for paragraph in cell.paragraphs:
                            paragraph.paragraph_format.space_after = Pt(1)
                            for r in paragraph.runs:
                                r.font.name = "Aptos"
                                r.font.size = Pt(8 if len(rows[0]) > 5 else 9)
                                if row_idx == 0:
                                    r.font.bold = True
                                    r.font.color.rgb = RGBColor(255, 255, 255)
                        if row_idx == 0:
                            cell_fill(cell, "17324D")
                doc.add_paragraph().paragraph_format.space_after = Pt(1)
            continue
        if line.startswith("# "):
            p = doc.add_paragraph(style="Title")
            p.add_run(plain(line[2:]))
        elif line.startswith("## "):
            heading = doc.add_heading(plain(line[3:]), level=1)
            if line[3:].startswith("Clasificación de NObeyesdad"):
                heading.paragraph_format.page_break_before = True
        elif line.startswith("### "):
            doc.add_heading(plain(line[4:]), level=2)
        elif line.startswith("- "):
            p = doc.add_paragraph(style="List Bullet")
            p.add_run(plain(line[2:]))
        else:
            p = doc.add_paragraph(plain(line))
            if index < 7:
                p.paragraph_format.space_after = Pt(2)
        index += 1
    doc.core_properties.title = "Unidad III Modelado supervisado evaluación y optimización"
    doc.core_properties.subject = "Proyecto integrador ECBD 2026"
    doc.core_properties.author = "David Rafael Aguilar Solis"
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUTPUT)
    return OUTPUT


if __name__ == "__main__":
    print(build())
