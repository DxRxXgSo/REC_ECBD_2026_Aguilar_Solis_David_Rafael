"""Build the editable Unit II report from its Markdown and generated figures."""

from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


def clean(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", text)
    return text.replace("**", "").replace("`", "").replace("*", "").strip()


def build(root: Path) -> Path:
    markdown = (root / "docs/unidad_ii/informe_unidad_ii.md").read_text(encoding="utf-8")
    output = root / "docs/unidad_ii/informe_unidad_ii.docx"
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.72)
    section.bottom_margin = Inches(0.72)
    section.left_margin = Inches(0.85)
    section.right_margin = Inches(0.85)
    normal = doc.styles["Normal"]
    normal.font.name = "Aptos"
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = RGBColor(37, 46, 54)
    normal.paragraph_format.space_after = Pt(5)
    for name, size, color in [
        ("Title", 26, (23, 54, 77)), ("Heading 1", 17, (23, 54, 77)),
        ("Heading 2", 13, (47, 102, 144)), ("Heading 3", 11, (47, 102, 144)),
    ]:
        style = doc.styles[name]
        style.font.name = "Aptos Display"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor(*color)
        style.paragraph_format.space_before = Pt(12)
        style.paragraph_format.space_after = Pt(5)

    header = section.header.paragraphs[0]
    header.text = "UTTT  |  EXTRACCIÓN DE CONOCIMIENTO EN BASES DE DATOS"
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    for run in header.runs:
        run.font.size = Pt(8)
        run.font.color.rgb = RGBColor(90, 105, 115)
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.add_run("Unidad II  ·  ")
    page = OxmlElement("w:fldSimple")
    page.set(qn("w:instr"), "PAGE")
    footer._p.append(page)

    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_before = Pt(48)
    run = paragraph.add_run("UNIVERSIDAD TECNOLÓGICA\nDE TULA-TEPEJI")
    run.bold = True
    run.font.size = Pt(17)
    run.font.color.rgb = RGBColor(23, 54, 77)
    cover = [
        ("Tecnologías de la Información", 11, 4),
        ("PROYECTO INTEGRADOR DE RECURSAMIENTO 2026", 11, 48),
        ("Unidad II", 25, 2),
        ("Análisis exploratorio y preparación de datos", 16, 9),
        ("Análisis de hábitos y condición física asociados con niveles de obesidad", 11, 8),
        ("David Rafael Aguilar Solis  ·  Matrícula 22300607  ·  Grupo 10IDGS-G1", 10, 4),
        ("Asignatura: Extracción de Conocimiento en Bases de Datos", 10, 4),
        ("Docente: pendiente de confirmación", 10, 4),
        ("Fecha de elaboración: 27 de octubre de 2026", 10, 45),
        ("Documento de análisis académico y registro técnico reproducible", 10, 0),
    ]
    for text, size, space in cover:
        paragraph = doc.add_paragraph(text)
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragraph.paragraph_format.space_before = Pt(space)
        paragraph.runs[0].font.size = Pt(size)
        if text == "Unidad II":
            paragraph.runs[0].bold = True
            paragraph.runs[0].font.color.rgb = RGBColor(47, 102, 144)
        if text.startswith("Análisis exploratorio"):
            paragraph.runs[0].font.color.rgb = RGBColor(23, 54, 77)
    doc.add_page_break()

    started = False
    skip_title = True
    add_figures = False
    figures = [
        ("distribucion_n_obesidad.png", "Figura 1. Conteos observados por categoría."),
        ("distribuciones_numericas.png", "Figura 2. Distribuciones de variables numéricas y escalas."),
        ("peso_por_categoria.png", "Figura 3. Peso observado por categoría de etiqueta."),
    ]
    for raw in markdown.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("# "):
            if skip_title:
                skip_title = False
                continue
            doc.add_heading(clean(line[2:]), level=1)
            continue
        if line.startswith("## "):
            heading = clean(line[3:])
            paragraph = doc.add_heading(heading, level=2)
            paragraph.paragraph_format.keep_with_next = True
            started = started or heading == "Alcance y resultado"
            add_figures = heading == "Exploración"
            continue
        if not started:
            continue
        if line.startswith("### "):
            doc.add_heading(clean(line[4:]), level=3)
            continue
        if line.startswith("- "):
            doc.add_paragraph(clean(line[2:]), style="List Bullet")
            continue
        if line.startswith("> "):
            doc.add_paragraph(clean(line[2:]))
            continue
        if line.startswith("|") or line == "---" or line.startswith("```"):
            continue
        paragraph = doc.add_paragraph(clean(line))
        if line.startswith("El entorno se fijó") or line in {
            "python -m unittest discover -s tests/unit_ii -v",
            "python src/unit_ii.py",
        }:
            paragraph.paragraph_format.keep_with_next = True
        if add_figures and line.startswith("El análisis gráfico"):
            for filename, caption in figures:
                paragraph = doc.add_paragraph()
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                paragraph.add_run().add_picture(
                    str(root / "docs/unidad_ii/figuras" / filename), width=Inches(6.0)
                )
                paragraph = doc.add_paragraph(caption)
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in paragraph.runs:
                    run.italic = True
                    run.font.size = Pt(9)
    doc.core_properties.title = "Unidad II Análisis exploratorio y preparación de datos"
    doc.core_properties.author = "David Rafael Aguilar Solis"
    doc.core_properties.subject = "Extracción de Conocimiento en Bases de Datos"
    doc.save(output)
    return output


if __name__ == "__main__":
    print(build(Path(__file__).resolve().parents[1]))
