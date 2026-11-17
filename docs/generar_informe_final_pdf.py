from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "Informe_Final_Integrador_2026.pdf"
CAPTURES = ROOT / "dashboard" / "evidencias" / "final_powerbi_2026-11-16_validado"
FONT = Path(r"C:\Windows\Fonts\arial.ttf")
FONT_BOLD = Path(r"C:\Windows\Fonts\arialbd.ttf")

pdfmetrics.registerFont(TTFont("Arial", str(FONT)))
pdfmetrics.registerFont(TTFont("Arial-Bold", str(FONT_BOLD)))

NAVY = colors.HexColor("#17324D")
TEAL = colors.HexColor("#167D8D")
PALE = colors.HexColor("#EAF2F5")
GRAY = colors.HexColor("#53616D")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TitleECBD", fontName="Arial-Bold", fontSize=24, leading=30,
                          textColor=NAVY, alignment=TA_LEFT, spaceAfter=10))
styles.add(ParagraphStyle(name="SubtitleECBD", fontName="Arial", fontSize=12, leading=17,
                          textColor=GRAY, spaceAfter=14))
styles.add(ParagraphStyle(name="H1ECBD", fontName="Arial-Bold", fontSize=15, leading=19,
                          textColor=NAVY, spaceBefore=10, spaceAfter=6, keepWithNext=True))
styles.add(ParagraphStyle(name="H2ECBD", fontName="Arial-Bold", fontSize=11, leading=14,
                          textColor=TEAL, spaceBefore=5, spaceAfter=3, keepWithNext=True))
styles.add(ParagraphStyle(name="BodyECBD", fontName="Arial", fontSize=9.5, leading=14,
                          textColor=colors.HexColor("#263746"), spaceAfter=6))
styles.add(ParagraphStyle(name="SmallECBD", fontName="Arial", fontSize=8, leading=11,
                          textColor=GRAY, spaceAfter=3))
styles.add(ParagraphStyle(name="CaptureTitle", fontName="Arial-Bold", fontSize=16, leading=20,
                          textColor=NAVY, alignment=TA_CENTER, spaceAfter=9))


def header_footer(canvas, doc):
    canvas.saveState()
    width, height = doc.pagesize
    canvas.setStrokeColor(colors.HexColor("#D7E2E8"))
    canvas.setLineWidth(0.6)
    canvas.line(doc.leftMargin, 1.35 * cm, width - doc.rightMargin, 1.35 * cm)
    canvas.setFont("Arial", 7.5)
    canvas.setFillColor(GRAY)
    canvas.drawString(doc.leftMargin, 0.9 * cm, "ECBD 2026 | Informe integrador - corte tecnico 17/11/2026")
    canvas.drawRightString(width - doc.rightMargin, 0.9 * cm, f"Pagina {doc.page}")
    canvas.restoreState()


portrait = A4
wide = landscape(A4)
doc = BaseDocTemplate(
    str(OUT),
    pagesize=portrait,
    leftMargin=1.8 * cm,
    rightMargin=1.8 * cm,
    topMargin=1.7 * cm,
    bottomMargin=1.8 * cm,
    title="Informe integrador ECBD 2026 - corte tecnico",
    author="David Rafael Aguilar Solis",
)
portrait_frame = Frame(doc.leftMargin, doc.bottomMargin, portrait[0] - doc.leftMargin - doc.rightMargin,
                       portrait[1] - doc.topMargin - doc.bottomMargin, id="portrait")
wide_margin = 1.25 * cm
wide_frame = Frame(wide_margin, 1.65 * cm, wide[0] - 2 * wide_margin,
                   wide[1] - 2.7 * cm, id="wide")
doc.addPageTemplates([
    PageTemplate(id="Portrait", frames=[portrait_frame], onPage=header_footer, pagesize=portrait),
    PageTemplate(id="Landscape", frames=[wide_frame], onPage=header_footer, pagesize=wide),
])

story = [
    Paragraph("Informe integrador", styles["TitleECBD"]),
    Paragraph("Proyecto: An&aacute;lisis de h&aacute;bitos y condici&oacute;n f&iacute;sica asociados con niveles de obesidad<br/>Corte t&eacute;cnico: 17 de noviembre de 2026", styles["SubtitleECBD"]),
    Paragraph("David Rafael Aguilar Solis | Matr&iacute;cula 22300607 | Grupo 10IDGS-G1<br/>Universidad Tecnol&oacute;gica de Tula-Tepeji | Tecnolog&iacute;as de la Informaci&oacute;n<br/>Extracci&oacute;n de Conocimiento en Bases de Datos", styles["BodyECBD"]),
    Paragraph("Estado ejecutivo", styles["H1ECBD"]),
    Paragraph("El proyecto integra preparación de datos y Data Mart, modelos supervisados para Weight y NObeyesdad, análisis exploratorio con K-Means/PCA y un dashboard Power BI de cuatro páginas. Las métricas y conteos se basan en artefactos existentes y verificaciones descritas aquí; no prueban causalidad, utilidad clínica ni generalización poblacional. Classroom, defensa y aprobación docente no están verificadas.", styles["BodyECBD"]),
    Paragraph("Datos y método", styles["H1ECBD"]),
    Paragraph("El dataset UCI contiene 2,111 observaciones y 17 variables; se preservaron 24 filas duplicadas exactas. Se observaron cero valores faltantes en la revisión documentada. El CSV original mantuvo SHA-256 28b6991062855d3d15642e38b1aa9d1b32fb7abbb5abf5b096f1868cd706154b. CRISP-DM organiza comprensión del problema y datos, preparación, modelado, evaluación y comunicación. Las observaciones sintéticas y la procedencia geográfica limitan su representatividad.", styles["BodyECBD"]),
    Paragraph("Resultados supervisados", styles["H1ECBD"]),
]

metrics = [
    ["Experimento", "Accuracy", "Precision macro", "Recall macro", "F1 macro", "MAE", "RMSE", "R2"],
    ["Regresion RF (test)", "-", "-", "-", "-", "4.7501", "8.1428", "0.9005"],
    ["Clasificacion A - Logistica", "0.9621", "0.9634", "0.9613", "0.9615", "-", "-", "-"],
    ["Clasificacion B - Random Forest", "0.8697", "0.8664", "0.8669", "0.8666", "-", "-", "-"],
]
tbl = Table(metrics, colWidths=[4.4 * cm, 1.8 * cm, 2.2 * cm, 2.0 * cm, 1.7 * cm, 1.5 * cm, 1.5 * cm, 1.2 * cm], repeatRows=1)
tbl.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Arial-Bold"), ("FONTNAME", (0, 1), (-1, -1), "Arial"),
    ("FONTSIZE", (0, 0), (-1, -1), 7.4), ("LEADING", (0, 0), (-1, -1), 9),
    ("BACKGROUND", (0, 1), (-1, -1), PALE), ("GRID", (0, 0), (-1, -1), 0.35, colors.white),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ("RIGHTPADDING", (0, 0), (-1, -1), 4), ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
story += [tbl, Spacer(1, 5),
          Paragraph("En clasificacion, el escenario A incluye Height y Weight y tiene riesgo de circularidad frente a NObeyesdad; el escenario B excluye ambas variables. La seleccion se baso en validacion cruzada dentro del entrenamiento. El RMSE de validacion cruzada de regresion fue 8.9627. Las matrices de confusion disponibles corresponden a modelos base y no se integraron como visual al dashboard.", styles["BodyECBD"]),
          Paragraph("Agrupamiento, PCA y dashboard", styles["H1ECBD"]),
          Paragraph("El Silhouette maximo en el rango inicial k=2-9 fue 0.172636 en k=9, limite superior del rango. La sensibilidad ampliada encontro valores superiores para k=10 y k=11; k=9 no se presenta como optimo global. PC1 y PC2 explican 41.31% acumulado. En Power BI Desktop 2.159.1231.0 se actualizaron cinco tablas: FactDashboard (2,111), DimObesityLevel (7), ModelMetrics (5), ClusterProfile (9) y PcaVariance (2). El filtro Normal_Weight cambio el conteo 2,111 a 287 y al limpiarlo restauro 2,111.", styles["BodyECBD"]),
          Paragraph("La conexion local a localhost\\SQLEXPRESS utilizo autenticacion integrada de Windows y una excepcion de confianza limitada al proceso de Power BI Desktop; se mantuvo cifrado. No se guardaron credenciales. El proyecto se guardo como PBIP; la interfaz disponible no ofrecio una salida PBIX. La relacion de perfiles de cluster requiere una prueba interactiva adicional.", styles["BodyECBD"]),
          Paragraph("Verificacion y pendientes", styles["H1ECBD"]),
          Paragraph("Pruebas unittest: dashboard 3/3, Unidad II 12/12, Unidad III 8/8 y Unidad IV 2/2. La validacion PBIR informo cero errores y un aviso por esquema visual remoto inaccesible. El notebook inicial mantiene un cambio local preexistente y queda fuera de esta publicacion. Falta la revision manual final de las matrices, interaccion de cluster, entrega en Classroom, defensa y aceptacion docente.", styles["BodyECBD"]),
          Paragraph("Fuentes", styles["H1ECBD"]),
          Paragraph("UCI Machine Learning Repository, Estimation of Obesity Levels Based On Eating Habits and Physical Condition, https://doi.org/10.24432/C5H31Z.<br/>Mendoza Palechor, F. y de la Hoz Manotas, A. (2019). Dataset for estimation of obesity levels based on eating habits and physical condition in individuals from Colombia, Peru and Mexico. Data in Brief, 25, 104344. https://doi.org/10.1016/j.dib.2019.104344.<br/>Microsoft Learn, Power Query SQL Server connector, https://learn.microsoft.com/en-us/power-query/connectors/sqlserver.", styles["SmallECBD"]),
          __import__("reportlab.platypus", fromlist=["NextPageTemplate"]).NextPageTemplate("Landscape"),
          PageBreak(),
          ]

story.append(Paragraph("Evidencia de las cuatro paginas del dashboard", styles["TitleECBD"]))
story.append(Paragraph("Capturas realizadas despues de reabrir el PBIP y actualizar las fuentes en Power BI Desktop.", styles["SubtitleECBD"]))
for idx, name in enumerate([
    "01 Panorama general.png",
    "02 Modelos supervisados.png",
    "03 Clustering y PCA.png",
    "04 Hallazgos y conclusiones.png",
], start=1):
    image_path = CAPTURES / name
    if not image_path.is_file():
        raise FileNotFoundError(image_path)
    if idx > 1:
        story.append(PageBreak())
    title = name.removeprefix(f"{idx:02d} ").removesuffix(".png")
    story.append(Paragraph(f"{idx}. {title}", styles["CaptureTitle"]))
    img = Image(str(image_path))
    max_w = wide[0] - 2 * wide_margin - 0.5 * cm
    max_h = wide[1] - 4.1 * cm
    img_width, img_height = img.imageWidth, img.imageHeight
    ratio = min(max_w / img_width, max_h / img_height)
    img.drawWidth = img_width * ratio
    img.drawHeight = img_height * ratio
    story.append(img)

doc.build(story)
print(OUT)
