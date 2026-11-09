"""Build the U2 AE1 diagnostic report from the project CSV and notebook metadata."""

from __future__ import annotations

import ast
import hashlib
import io
import json
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data/raw/ObesityDataSet_raw_and_data_sinthetic.csv"
NOTEBOOK = ROOT / "notebooks/Aguilar_Solis_David_Rafael_U2_AE1_Exploracion.ipynb"
OUTPUT = ROOT / "docs/Aguilar_Solis_David_Rafael_U2_AE1_Diagnostico.pdf"
EXPECTED_SHA256 = "28b6991062855d3d15642e38b1aa9d1b32fb7abbb5abf5b096f1868cd706154b"
EXPECTED_COLUMNS = [
    "Gender", "Age", "Height", "Weight", "family_history_with_overweight",
    "FAVC", "FCVC", "NCP", "CAEC", "SMOKE", "CH2O", "SCC", "FAF",
    "TUE", "CALC", "MTRANS", "NObeyesdad",
]
CLASS_ORDER = [
    "Insufficient_Weight", "Normal_Weight", "Overweight_Level_I",
    "Overweight_Level_II", "Obesity_Type_I", "Obesity_Type_II", "Obesity_Type_III",
]
SCALES = ["FCVC", "NCP", "CH2O", "FAF", "TUE"]
NAVY = colors.HexColor("#17324D")
TEAL = colors.HexColor("#147D86")
PALE = colors.HexColor("#F0F5F7")
MID = colors.HexColor("#536B80")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def notebook_dictionary() -> list[tuple[str, ...]]:
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    for cell in notebook.get("cells", []):
        source = "".join(cell.get("source", []))
        if cell.get("cell_type") != "code" or "metadata = [" not in source:
            continue
        tree = ast.parse(source)
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == "metadata" for target in node.targets
            ):
                rows = ast.literal_eval(node.value)
                if len(rows) == 17 and all(len(row) == 6 for row in rows):
                    return rows
    raise ValueError("No se encontró en el notebook el diccionario completo de 17 variables.")


def read_and_validate() -> tuple[pd.DataFrame, dict[str, object]]:
    if not CSV.is_file() or not NOTEBOOK.is_file():
        raise FileNotFoundError(f"Falta el CSV original o el notebook: {CSV}, {NOTEBOOK}")
    observed_hash = sha256(CSV)
    if observed_hash != EXPECTED_SHA256:
        raise ValueError(f"SHA-256 del CSV no coincide: {observed_hash}")
    frame = pd.read_csv(CSV)
    if list(frame.columns) != EXPECTED_COLUMNS or frame.shape != (2111, 17):
        raise ValueError(f"Esquema/dimensiones inesperados: {frame.shape}, {list(frame.columns)}")

    missing = frame.isnull().sum()
    duplicates = int(frame.duplicated().sum())
    numeric_columns = {"Age", "Height", "Weight", "FCVC", "NCP", "CH2O", "FAF", "TUE"}
    categorical_columns = set(frame.columns) - numeric_columns
    unexpected_types = {
        name: str(frame[name].dtype)
        for name in frame.columns
        if (name in numeric_columns and not pd.api.types.is_numeric_dtype(frame[name]))
        or (name in categorical_columns and not (
            pd.api.types.is_object_dtype(frame[name])
            or pd.api.types.is_string_dtype(frame[name])
        ))
    }
    if int(missing.sum()) != 0 or duplicates != 24 or unexpected_types:
        raise ValueError(f"Calidad distinta a las observaciones documentadas: faltantes={int(missing.sum())}, duplicados={duplicates}, tipos={unexpected_types}")

    bounds = {
        "Age": (0, 120), "Height": (0, np.inf), "Weight": (0, np.inf),
        "FCVC": (1, 3), "NCP": (1, 4), "CH2O": (1, 3),
        "FAF": (0, 3), "TUE": (0, 2),
    }
    range_issues = {}
    for name, (lower, upper) in bounds.items():
        values = frame[name]
        invalid = (values <= lower) if name in {"Height", "Weight"} else (values < lower)
        if np.isfinite(upper):
            invalid |= values > upper
        invalid |= ~np.isfinite(values)
        range_issues[name] = int(invalid.sum())
    domains = {
        "Gender": {"Female", "Male"},
        "family_history_with_overweight": {"yes", "no"},
        "FAVC": {"yes", "no"}, "SMOKE": {"yes", "no"}, "SCC": {"yes", "no"},
        "CAEC": {"no", "Sometimes", "Frequently", "Always"},
        "CALC": {"no", "Sometimes", "Frequently", "Always"},
        "MTRANS": {"Automobile", "Motorbike", "Bike", "Public_Transportation", "Walking"},
        "NObeyesdad": set(CLASS_ORDER),
    }
    category_issues = {name: int((~frame[name].isin(values)).sum()) for name, values in domains.items()}
    if any(range_issues.values()) or any(category_issues.values()):
        raise ValueError(f"Los controles de dominio/rango encontraron anomalías: {range_issues}, {category_issues}")

    stats = frame[["Age", "Height", "Weight"]].agg(["mean", "median", "min", "max", "std"]).T
    iqr = {}
    for name in ["Age", "Height", "Weight", "NCP"]:
        q1, q3 = frame[name].quantile([0.25, 0.75])
        spread = q3 - q1
        low, high = q1 - 1.5 * spread, q3 + 1.5 * spread
        iqr[name] = {
            "Q1": float(q1), "Q3": float(q3), "low": float(low), "high": float(high),
            "candidates": int(((frame[name] < low) | (frame[name] > high)).sum()),
        }
    fractional = {name: int(((frame[name] - frame[name].round()).abs() > 1e-9).sum()) for name in SCALES}
    classes = frame["NObeyesdad"].value_counts().reindex(CLASS_ORDER, fill_value=0)
    if int(classes.sum()) != len(frame) or (classes == 0).any():
        raise ValueError("La etiqueta no contiene exactamente las siete clases esperadas.")

    return frame, {
        "sha256": observed_hash,
        "rows": int(frame.shape[0]), "columns": int(frame.shape[1]),
        "missing_by_column": {name: int(value) for name, value in missing.items()},
        "missing_total": int(missing.sum()),
        "duplicate_rows": duplicates,
        "duplicate_percent": 100 * duplicates / len(frame),
        "unexpected_types": unexpected_types,
        "range_issues": range_issues,
        "category_issues": category_issues,
        "statistics": stats,
        "iqr": iqr,
        "fractional": fractional,
        "class_counts": classes,
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
    }


def styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "body": ParagraphStyle("AE1Body", parent=base["BodyText"], fontName="Helvetica", fontSize=8.8, leading=12.1, textColor=NAVY, spaceAfter=5.2, alignment=TA_LEFT, splitLongWords=0),
        "small": ParagraphStyle("AE1Small", parent=base["BodyText"], fontName="Helvetica", fontSize=7.2, leading=9, textColor=NAVY, spaceAfter=2, splitLongWords=0),
        "tiny": ParagraphStyle("AE1Tiny", parent=base["BodyText"], fontName="Helvetica", fontSize=6.9, leading=8.6, textColor=NAVY, spaceAfter=1, splitLongWords=0),
        "h1": ParagraphStyle("AE1H1", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=17, leading=21, textColor=NAVY, spaceBefore=0, spaceAfter=8, keepWithNext=True),
        "h2": ParagraphStyle("AE1H2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=11.3, leading=14, textColor=TEAL, spaceBefore=5, spaceAfter=4, keepWithNext=True),
        "cover_inst": ParagraphStyle("AE1CoverInst", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=16, leading=19, alignment=TA_CENTER, textColor=TEAL, spaceAfter=6),
        "cover_title": ParagraphStyle("AE1CoverTitle", parent=base["Title"], fontName="Helvetica-Bold", fontSize=24, leading=29, alignment=TA_CENTER, textColor=NAVY, spaceAfter=12),
        "cover_sub": ParagraphStyle("AE1CoverSub", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=15, leading=18, alignment=TA_CENTER, textColor=TEAL, spaceAfter=14),
        "cover_body": ParagraphStyle("AE1CoverBody", parent=base["Normal"], fontName="Helvetica", fontSize=10.5, leading=15, alignment=TA_CENTER, textColor=NAVY, spaceAfter=8),
        "center": ParagraphStyle("AE1Center", parent=base["Normal"], fontName="Helvetica", fontSize=8.2, leading=10, alignment=TA_CENTER, textColor=NAVY),
    }


def para(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def cell(text: object, style: ParagraphStyle, *, raw: bool = False) -> Paragraph:
    content = str(text).replace("\n", "<br/>") if raw else escape(str(text)).replace("\n", "<br/>")
    return Paragraph(content, style)


def table(
    data: list[list[object]],
    widths: list[float],
    *,
    small: bool = False,
    header: bool = True,
    cell_style: ParagraphStyle | None = None,
) -> Table:
    st = styles()
    pstyle = cell_style or (st["small"] if small else st["body"])
    header_style = ParagraphStyle(
        "AE1TableHeader", parent=pstyle, fontName="Helvetica-Bold", textColor=colors.white
    )
    converted = []
    for row_index, row in enumerate(data):
        converted_row = []
        for value in row:
            if isinstance(value, Paragraph):
                converted_row.append(value)
            else:
                converted_row.append(cell(value, header_style if header and row_index == 0 else pstyle))
        converted.append(converted_row)
    result = Table(converted, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT", splitByRow=1)
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, -1), (-1, -1), 0.5, colors.HexColor("#B8C8D2")),
    ]
    if header:
        commands.extend([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("TOPPADDING", (0, 0), (-1, 0), 6), ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ])
    start = 1 if header else 0
    for row in range(start, len(data)):
        if (row - start) % 2 == 1:
            commands.append(("BACKGROUND", (0, row), (-1, row), PALE))
    result.setStyle(TableStyle(commands))
    return result


def chart_image(frame: pd.DataFrame, which: str) -> Image:
    buffer = io.BytesIO()
    if which == "classes":
        counts = frame["NObeyesdad"].value_counts().reindex(CLASS_ORDER)
        fig, ax = plt.subplots(figsize=(7.1, 3.1))
        y = np.arange(len(counts))
        ax.barh(y, counts.values, color="#147D86")
        ax.set_yticks(y, counts.index, fontsize=7.5)
        ax.invert_yaxis()
        ax.set(title="Conteos por categoría NObeyesdad", xlabel="Número de registros", ylabel="Nivel de obesidad")
        ax.set_xlim(0, int(counts.max() * 1.15))
        for i, value in enumerate(counts.values):
            ax.text(value + 2, i, str(value), va="center", fontsize=8)
        fig.tight_layout()
        width, height = 7.1 * 72, 3.1 * 72
    elif which == "histograms":
        fig, axes = plt.subplots(1, 3, figsize=(7.1, 2.8))
        for ax, name, unit in zip(axes, ["Age", "Height", "Weight"], ["años", "m", "kg"]):
            ax.hist(frame[name], bins=24, color="#238B92", edgecolor="white")
            ax.set(title=name, xlabel=f"{name} ({unit})", ylabel="Frecuencia")
            ax.tick_params(labelsize=7)
            ax.title.set_fontsize(8)
        fig.suptitle("Distribución de edad, estatura y peso", fontsize=10, fontweight="bold")
        fig.tight_layout(rect=[0, 0, 1, 0.92])
        width, height = 7.1 * 72, 2.8 * 72
    elif which == "boxplots":
        fig, axes = plt.subplots(1, 3, figsize=(7.1, 2.55))
        for ax, name, unit in zip(axes, ["Age", "Height", "Weight"], ["años", "m", "kg"]):
            ax.boxplot(frame[name], patch_artist=True, boxprops={"facecolor": "#DDEFF0"}, medianprops={"color": "#B15B36", "linewidth": 2})
            ax.set(title=name, ylabel=unit, xticks=[])
            ax.tick_params(labelsize=7)
            ax.title.set_fontsize(8)
        fig.suptitle("Valores extremos candidatos según 1.5 × IQR", fontsize=10, fontweight="bold")
        fig.tight_layout(rect=[0, 0, 1, 0.9])
        width, height = 7.1 * 72, 2.55 * 72
    elif which == "scatter":
        fig, ax = plt.subplots(figsize=(7.1, 3.2))
        palette = plt.get_cmap("tab10").colors
        for color, label in zip(palette, CLASS_ORDER):
            subset = frame.loc[frame["NObeyesdad"] == label]
            ax.scatter(subset["Height"], subset["Weight"], s=8, alpha=0.55, label=label, color=color)
        ax.set(title="Estatura y peso por categoría registrada", xlabel="Estatura (m)", ylabel="Peso (kg)")
        ax.legend(fontsize=6.6, ncol=2, loc="upper left", bbox_to_anchor=(1.01, 1))
        fig.tight_layout()
        width, height = 7.1 * 72, 3.2 * 72
    else:
        raise ValueError(which)
    fig.savefig(buffer, format="png", dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buffer.seek(0)
    return Image(buffer, width=width, height=height)


def on_page(canvas, doc) -> None:
    if doc.page == 1:
        canvas.saveState()
        canvas.setFillColor(NAVY)
        canvas.rect(0, A4[1] - 7 * mm, A4[0], 7 * mm, stroke=0, fill=1)
        canvas.setFillColor(TEAL)
        canvas.rect(0, 0, A4[0], 5 * mm, stroke=0, fill=1)
        canvas.restoreState()
        return
    canvas.saveState()
    width, height = A4
    canvas.setFillColor(MID)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(17 * mm, height - 12 * mm, "UTTT  /  EXTRACCIÓN DE CONOCIMIENTO EN BASES DE DATOS")
    canvas.setStrokeColor(colors.HexColor("#B8C8D2"))
    canvas.line(17 * mm, height - 15 * mm, width - 17 * mm, height - 15 * mm)
    canvas.line(17 * mm, 14 * mm, width - 17 * mm, 14 * mm)
    canvas.drawString(17 * mm, 9 * mm, "U2 · Actividad de Evaluación 1  |  Diagnóstico de datos")
    canvas.drawRightString(width - 17 * mm, 9 * mm, f"Página {doc.page}")
    canvas.restoreState()


def build() -> Path:
    frame, result = read_and_validate()
    meta = notebook_dictionary()
    st = styles()
    body, small, tiny = st["body"], st["small"], st["tiny"]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT), pagesize=A4,
        leftMargin=17 * mm, rightMargin=17 * mm,
        topMargin=21 * mm, bottomMargin=19 * mm,
        title="U2 AE1 · Exploración y diagnóstico del conjunto de datos",
        author="David Rafael Aguilar Solis",
        subject="Extracción de Conocimiento en Bases de Datos",
    )
    story: list[object] = []
    usable = A4[0] - 34 * mm

    # Portada.
    story.extend([
        Spacer(1, 23 * mm),
        para("UNIVERSIDAD TECNOLÓGICA<br/>DE TULA-TEPEJI", st["cover_inst"]),
        Spacer(1, 16 * mm),
        para("EXTRACCIÓN DE CONOCIMIENTO<br/>EN BASES DE DATOS", st["cover_title"]),
        para("UNIDAD II · ACTIVIDAD DE EVALUACIÓN 1", st["cover_sub"]),
        para("Exploración, clasificación y diagnóstico<br/>del conjunto de datos", st["cover_body"]),
        Spacer(1, 7 * mm),
        table([
            ["Proyecto integrador", "Análisis de hábitos y condición física asociados con niveles de obesidad"],
            ["Alumno", "David Rafael Aguilar Solis"],
            ["Matrícula / Grupo", "22300607  |  10IDGS-G1"],
            ["Docente", "Ing. Jose Luis Herrera Gallardo, MTI"],
            ["Fecha de elaboración", date.today().strftime("%d de noviembre de %Y")],
        ], [40 * mm, usable - 40 * mm], small=True, header=False),
        Spacer(1, 18 * mm),
        para("Diagnóstico descriptivo, reproducible y sin alteración del dataset original", st["center"]),
        PageBreak(),
    ])

    # Secciones 1 y 2.
    story.extend([
        para("1. Identificación del dataset", st["h1"]),
        para("El proyecto estudia hábitos alimentarios, actividad física y características corporales en el conjunto <i>Estimation of Obesity Levels Based On Eating Habits and Physical Condition</i> del <link href='https://archive.ics.uci.edu/dataset/544/estimation+of+obesity+levels+based+on+eating+habits+and+physical+condition' color='#147D86'>UCI Machine Learning Repository, dataset 544</link>. Se usa el mismo conjunto asignado desde Unidad I. Cada fila representa un registro del archivo y no necesariamente una persona única.", body),
        table([
            ["Propiedad", "Resultado"],
            ["Fuente", "UCI Machine Learning Repository · Dataset 544"],
            ["Formato", "CSV estructurado"],
            ["Dimensiones", f"{result['rows']:,} registros × {result['columns']} variables"],
            ["Predictores / etiqueta", "16 variables descriptivas; NObeyesdad como etiqueta (7 clases)"],
            ["Archivo original", "data/raw/ObesityDataSet_raw_and_data_sinthetic.csv"],
            ["Integridad SHA-256", Paragraph(f"<font name='Courier' size='7'>{result['sha256'][:32]}<br/>{result['sha256'][32:]}</font>", tiny)],
        ], [45 * mm, usable - 45 * mm], small=True),
        Spacer(1, 7),
        para("2. Carga y exploración con Pandas", st["h1"]),
        para("El notebook ejecuta las seis instrucciones solicitadas sobre el archivo original. Cada resultado tiene una interpretación inmediata; las tablas completas quedan guardadas en el cuaderno.", body),
        table([
            ["Instrucción", "Qué muestra / resultado observado"],
            ["df.head()", "Cinco registros de ejemplo y sus campos; no representa todo el conjunto."],
            ["df.shape", "(2,111, 17): cantidad de filas y columnas."],
            ["df.columns", "Nombres exactos de las 17 variables y su orden."],
            ["df.info()", "2,111 entradas no nulas por columna; 8 float64 y 9 object."],
            ["df.dtypes", "Tipo técnico por campo; el tipo no determina por sí solo la escala estadística."],
            ["df.describe()", "Medias, cuartiles, dispersión y extremos de variables numéricas."],
        ], [37 * mm, usable - 37 * mm], small=True),
        para("<b>Interpretación.</b> La lectura produce 2,111 filas, 17 columnas y siete clases. No se observan faltantes; duplicados, escalas y valores extremos se evalúan por separado.", body),
        PageBreak(),
    ])

    # Sección 3, primera parte.
    story.append(para("3. Diccionario de datos · parte 1 de 2", st["h1"]))
    story.append(para("El tipo técnico procede de <font name='Courier'>df.dtypes</font>. La clasificación conceptual distingue variables cuantitativas, cualitativas y escalas codificadas. Los nombres se conservan como aparecen en el CSV.", body))
    headers = ["Nombre", "Descripción", "Python", "Tipo y clasificación", "Unidad", "Utilidad en el proyecto"]
    widths = [77, 101, 46, 125, 58, usable - (77 + 101 + 46 + 125 + 58)]
    dictionary_style = ParagraphStyle(
        "AEDictionary", parent=small, fontSize=8.5, leading=10.2, splitLongWords=0
    )
    first_rows = meta[:9]
    dictionary_data = [headers]
    for name, description, conceptual, classification, unit, utility in first_rows:
        type_class = f"{conceptual}; {classification}" if name != "NCP" else "Cuantitativa; cuenta/escala ordinal"
        if name == "FCVC": type_class = "Cuantitativa codificada; ordinal"
        if name in {"CH2O", "FAF", "TUE"}: type_class = "Cuantitativa codificada; ordinal"
        label = name.replace("family_history_with_overweight", "family_history_<br/>with_overweight")
        dictionary_data.append([label, description, str(frame[name].dtype), type_class, unit, utility])
    story.append(table(
        [[cell(value, dictionary_style, raw=True) if isinstance(value, str) and "<br/>" in value else value for value in row] for row in dictionary_data],
        widths,
        small=True,
        cell_style=dictionary_style,
    ))
    story.extend([
        Spacer(1, 6),
        para("Las escalas de frecuencia permiten analizar orden o cantidad aproximada. Sus fracciones observadas no deben redondearse automáticamente ni tratarse como mediciones clínicas exactas.", body),
        PageBreak(),
    ])

    # Sección 3, segunda parte.
    story.append(para("3. Diccionario de datos · parte 2 de 2", st["h1"]))
    dictionary_data = [headers]
    for name, description, conceptual, classification, unit, utility in meta[9:]:
        type_class = f"{conceptual}; {classification}"
        if name in {"CH2O", "FAF", "TUE"}: type_class = "Cuantitativa codificada; ordinal"
        if name == "NObeyesdad": type_class = "Cualitativa; ordinal"
        unit_display = "Categoría" if name == "NObeyesdad" else unit
        dictionary_data.append([name, description, str(frame[name].dtype), type_class, unit_display, utility])
    story.append(table(dictionary_data, widths, small=True, cell_style=dictionary_style))
    story.extend([
        Spacer(1, 7),
        para("Notas sobre clasificación y posibles usos", st["h2"]),
        para("<b>Nominales</b> representan categorías sin orden intrínseco, como transporte. <b>Ordinales</b> representan respuestas ordenables, como frecuencia. <b>Binarias</b> admiten dos estados registrados. Las escalas codificadas son numéricas en el archivo, pero sus valores representan respuestas ordenadas; algunos decimales son compatibles con la procedencia sintética. <font name='Courier'>NObeyesdad</font> es la etiqueta de clasificación y su orden descriptivo no equivale a distancias constantes.", body),
        PageBreak(),
    ])

    # Secciones 4 y 5.
    story.extend([
        para("4. Tipo y fuente de los datos", st["h1"]),
        para("La documentación de los autores describe un cuestionario en una plataforma web y registros generados sintéticamente con Weka/SMOTE. Reporta 23% recolectado directamente y 77% sintético. El archivo combina respuestas de personas y registros derivados algorítmicamente; no son transacciones ni lecturas directas de sensores. Es estructurado porque organiza filas y campos definidos. No hay una columna que identifique qué observaciones individuales son sintéticas.", body),
        para("5. Diagnóstico de calidad", st["h1"]),
        para("5.1 Valores faltantes", st["h2"]),
        para(f"<font name='Courier'>df.isnull().sum()</font> dio cero en cada una de las 17 variables ({result['missing_total']:,} de {result['rows'] * result['columns']:,} celdas; 0.00%). Columnas revisadas: {escape(', '.join(EXPECTED_COLUMNS))}. No se imputa ningún valor en esta actividad.", body),
        para("5.2 Registros duplicados", st["h2"]),
        para(f"<font name='Courier'>df.duplicated().sum()</font> detectó {result['duplicate_rows']} filas repetidas respecto de filas anteriores, equivalente al {result['duplicate_percent']:.2f}% de las {result['rows']:,} filas. El porcentaje usa la cantidad devuelta por Pandas como numerador; no cuenta dos veces la primera fila de cada grupo. Sin identificador individual, pueden ser coincidencias o reflejar la generación sintética. Se conservaron todas y se recomienda mantener grupos idénticos juntos al particionar.", body),
        para("5.3 Valores incorrectos o inconsistentes", st["h2"]),
        para("Se comprobaron dominios categóricos, valores numéricos finitos, positividad de edad/estatura/peso e intervalos de trabajo de las escalas. Los ocho campos numéricos y nueve categóricos tienen los tipos técnicos esperados; no se convirtieron columnas. No se observaron valores fuera de los dominios comprobados. Estos controles no descartan todos los errores posibles y no constituyen límites clínicos.", body),
        table([
            ["Control", "Resultado observado"],
            ["Dominios categóricos", "0 valores fuera de los dominios esperados"],
            ["Rangos de trabajo", "0 valores fuera de los intervalos revisados"],
            ["Tipos técnicos", "0 columnas con tipo inesperado; no hubo conversiones"],
        ], [44 * mm, usable - 44 * mm], small=True),
        Spacer(1, 6),
        table([["Escala", "Valores con parte decimal", "Tratamiento propuesto"]] + [[name, result["fractional"][name], "Conservar; no redondear sin justificar"] for name in SCALES], [34 * mm, 49 * mm, usable - 83 * mm], small=True),
        para("En etapas posteriores se validará la semántica de las respuestas y las fracciones antes de decidir limpieza. Ningún valor fue eliminado ni modificado.", body),
        PageBreak(),
    ])

    # Secciones 6 y 7.
    story.extend([
        para("6. Análisis estadístico inicial", st["h1"]),
        para("Se seleccionaron Age, Height y Weight. La desviación estándar usa el criterio muestral de Pandas; las cifras describen este archivo.", body),
    ])
    stats = result["statistics"]
    stats_rows = [["Variable", "Media", "Mediana", "Mínimo", "Máximo", "Desv. estándar"]]
    for name in ["Age", "Height", "Weight"]:
        values = stats.loc[name]
        stats_rows.append([name, *[f"{values[key]:.3f}" for key in ["mean", "median", "min", "max", "std"]]])
    story.append(table(stats_rows, [52, 76, 77, 65, 65, usable - 335], small=True))
    story.extend([
        para(f"La edad media es {stats.loc['Age','mean']:.2f} años (rango {stats.loc['Age','min']:.0f}–{stats.loc['Age','max']:.0f}); la estatura media es {stats.loc['Height','mean']:.3f} m y el peso medio {stats.loc['Weight','mean']:.2f} kg. La desviación del peso es {stats.loc['Weight','std']:.2f} kg. Estos valores no estiman la población general.", body),
        para("7. Detección inicial de valores atípicos", st["h1"]),
        para("Se aplicó la regla exploratoria 1.5 × IQR. Los puntos fuera de los límites son candidatos estadísticos, no errores confirmados.", body),
    ])
    iqr = result["iqr"]
    iqr_rows = [["Variable", "Q1", "Q3", "Límite inferior", "Límite superior", "Candidatos"]]
    for name in ["Age", "Height", "Weight", "NCP"]:
        x = iqr[name]
        iqr_rows.append([name, f"{x['Q1']:.3f}", f"{x['Q3']:.3f}", f"{x['low']:.3f}", f"{x['high']:.3f}", x["candidates"]])
    story.extend([
        table(iqr_rows, [48, 58, 58, 86, 86, usable - 336], small=True),
        para("Age presenta candidatos que pueden ser edades válidas dentro del rango observado; Height y Weight requieren contexto, no eliminación automática. NCP tiene muchos candidatos porque sus cuartiles se concentran alrededor de tres comidas y el IQR es poco informativo para una escala codificada. Se conservaron todos los valores.", body),
        PageBreak(),
    ])

    # Sección 8, figuras 1 y 2.
    story.extend([
        para("8. Visualización inicial · análisis descriptivo", st["h1"]),
        chart_image(frame, "classes"),
        para(f"La categoría con mayor conteo es Obesity_Type_I ({int(result['class_counts'].max())}); la menor es Insufficient_Weight ({int(result['class_counts'].min())}). Las siete clases están representadas; estos conteos no son prevalencias poblacionales.", small),
        Spacer(1, 4),
        chart_image(frame, "histograms"),
        para("Los histogramas muestran concentración de edades jóvenes, estaturas próximas a 1.70 m y dispersión más amplia del peso. Son descripciones de la muestra, sin inferencia causal.", small),
        PageBreak(),
    ])

    # Sección 8, figuras 3 y 4; título completo y mantenido junto a los gráficos.
    story.append(KeepTogether([
        para("8. Visualización inicial · extremos y relaciones", st["h1"]),
        chart_image(frame, "boxplots"),
    ]))
    story.extend([
        para(f"Los boxplots muestran {iqr['Age']['candidates']} candidatos en Age, {iqr['Height']['candidates']} en Height y {iqr['Weight']['candidates']} en Weight; ninguno se elimina sin justificación.", small),
        Spacer(1, 5),
        chart_image(frame, "scatter"),
        para("La relación estatura-peso cambia entre las categorías registradas, que se construyeron a partir de medidas antropométricas. El patrón es descriptivo y no demuestra causalidad ni generalización externa.", small),
        PageBreak(),
    ])

    # Sección 9.
    story.extend([
        para("9. Preparación de análisis posteriores", st["h1"]),
        para("<b>Regresión · predecir un valor numérico.</b> Objetivo propuesto: Weight (kg). Entradas candidatas: Age, Height, Gender y variables de hábitos como FCVC, NCP, CH2O, FAF, TUE y consumo de alimentos. Weight no se usaría como entrada de sí misma. Filas idénticas deben permanecer en la misma partición.", body),
        para("<b>Clasificación · predecir una categoría.</b> Objetivo: NObeyesdad, con peso insuficiente, normal, dos grados de sobrepeso y tres tipos de obesidad. Edad, antecedentes y hábitos son entradas candidatas. Se deben comparar escenarios con y sin Weight/Height porque esas medidas se relacionan directamente con las etiquetas y pueden introducir circularidad.", body),
        para("<b>Agrupamiento · descubrir patrones sin etiqueta.</b> Variables candidatas: Age, FCVC, NCP, CH2O, FAF, TUE y, después de codificar, CAEC y MTRANS. No se incluye NObeyesdad para formar clusters. Escalado y codificación se deciden en etapas posteriores.", body),
        para("Las propuestas responden a preguntas distintas: estimar peso, evaluar clasificación de etiquetas y encontrar perfiles de hábitos. Esta actividad no entrena modelos.", body),
        PageBreak(),
    ])

    # Sección 10.
    story.append(para("10. Conclusión del diagnóstico", st["h1"]))
    story.append(para("Respuestas a las diez preguntas de la guía de evaluación.", body))
    answers = [
        ("¿Qué información contiene el dataset?", "2,111 filas y 17 variables sobre características físicas, alimentación, actividad, hábitos y siete etiquetas."),
        ("¿Cuál es su nivel general de calidad?", "Estructura consistente, tipos esperados y ningún faltante; requiere cautela por duplicados, escalas y componente sintético."),
        ("¿Qué problemas se identificaron?", "24 filas duplicadas (1.14%), fracciones en escalas y candidatos IQR; no se hallaron dominios ni tipos técnicos inesperados en los controles."),
        ("¿Qué variables requieren tratamiento?", "Categóricas y escalas requieren codificación y tratamiento semántico al modelar; los duplicados deben controlarse en las particiones."),
        ("¿Existen valores faltantes?", "No: cero en las 17 columnas, 0.00% de las celdas."),
        ("¿Existen registros duplicados?", "Sí: 24 repeticiones posteriores exactas (1.14% de las filas); se conservaron."),
        ("¿Existen valores atípicos?", f"Candidatos IQR: Age {iqr['Age']['candidates']}, Height {iqr['Height']['candidates']}, Weight {iqr['Weight']['candidates']} y NCP {iqr['NCP']['candidates']}; no son errores demostrados."),
        ("¿Qué transformaciones serán necesarias?", "Evaluar codificación, escalado y particiones sin fuga en etapas posteriores; AE1 no transforma datos."),
        ("¿Los datos son adecuados para continuar?", "Sí, para descripción y modelos con validación rigurosa y limitaciones explícitas."),
        ("¿Qué conocimiento podría obtenerse?", "Patrones asociados entre hábitos, condición física y categorías, sin atribuir causalidad ni generalizar automáticamente."),
    ]
    for n, (question, answer) in enumerate(answers, 1):
        story.append(para(f"<b>{n}. {escape(question)}</b> {escape(answer)}", body))
    story.append(PageBreak())

    # Referencias y reproducibilidad.
    story.extend([
        para("Referencias, trazabilidad y revisión", st["h1"]),
        para("<b>Referencias bibliográficas</b>", st["h2"]),
        para("UCI Machine Learning Repository. (2019). <i>Estimation of Obesity Levels Based On Eating Habits and Physical Condition</i> (Dataset 544). <link href='https://doi.org/10.24432/C5H31Z' color='#147D86'>https://doi.org/10.24432/C5H31Z</link>.", body),
        para("Mendoza Palechor, F., &amp; de la Hoz Manotas, A. (2019). Dataset for estimation of obesity levels based on eating habits and physical condition in individuals from Colombia, Peru and Mexico. <i>Data in Brief, 25</i>, 104344. <link href='https://doi.org/10.1016/j.dib.2019.104344' color='#147D86'>https://doi.org/10.1016/j.dib.2019.104344</link>.", body),
        para("Reproducibilidad", st["h2"]),
        para("El notebook se ejecutó desde la carpeta de notebooks y busca el archivo <font name='Courier'>data/raw/ObesityDataSet_raw_and_data_sinthetic.csv</font> por rutas relativas. Conserva código, salidas, tablas, visualizaciones e interpretaciones. No depende de SQL Server ni de acceso a Internet durante su ejecución.", body),
        table([
            ["Control", "Resultado"],
            ["Datos originales", "2,111 filas, 17 columnas; sin modificación"],
            ["Valores faltantes", f"{result['missing_total']} celdas ({100*result['missing_total']/(result['rows']*result['columns']):.2f}%)"],
            ["Duplicados exactos", f"{result['duplicate_rows']} filas ({result['duplicate_percent']:.2f}%; conservadas)"],
            ["Categorías objetivo", "7"],
            ["SHA-256 original", Paragraph(f"<font name='Courier' size='7'>{result['sha256'][:32]}<br/>{result['sha256'][32:]}</font>", tiny)],
            ["Software", "Python 3, Pandas, NumPy y Matplotlib; PDF generado con ReportLab"],
            ["Estado académico", "Revisión docente y defensa individual pendientes"],
        ], [41 * mm, usable - 41 * mm], small=True),
        Spacer(1, 6),
        para("La muestra incluye datos sintéticos; no admite inferencia causal ni generalización automática. Los candidatos IQR requieren revisión contextual. No se alteró el archivo original. La entrega manual en Classroom y la defensa individual deben realizarse por el estudiante.", body),
    ])
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    return OUTPUT


if __name__ == "__main__":
    path = build()
    print(path)
    print("sha256_raw=", sha256(CSV))
    print("pdf_bytes=", path.stat().st_size)
