"""Build the final academic report PDF from validated project artifacts."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image, KeepTogether, NextPageTemplate, PageBreak, PageTemplate,
    Paragraph, Spacer, Table, TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "Informe_Final_Integrador_2026.pdf"
CAPTURES = ROOT / "dashboard" / "evidencias" / "final_powerbi_2026-11-18"
FONT = Path(r"C:\Windows\Fonts\arial.ttf")
FONT_BOLD = Path(r"C:\Windows\Fonts\arialbd.ttf")

pdfmetrics.registerFont(TTFont("Arial", str(FONT)))
pdfmetrics.registerFont(TTFont("Arial-Bold", str(FONT_BOLD)))

NAVY = colors.HexColor("#17324D")
TEAL = colors.HexColor("#167D8D")
PALE = colors.HexColor("#EAF2F5")
GRAY = colors.HexColor("#53616D")
INK = colors.HexColor("#263746")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverTitle", fontName="Arial-Bold", fontSize=22, leading=29,
                          textColor=NAVY, alignment=TA_CENTER, spaceAfter=14))
styles.add(ParagraphStyle(name="CoverSub", fontName="Arial", fontSize=13, leading=20,
                          textColor=GRAY, alignment=TA_CENTER, spaceAfter=8))
styles.add(ParagraphStyle(name="H1Final", fontName="Arial-Bold", fontSize=15, leading=19,
                          textColor=NAVY, spaceBefore=9, spaceAfter=5, keepWithNext=True))
styles.add(ParagraphStyle(name="H2Final", fontName="Arial-Bold", fontSize=11.5, leading=15,
                          textColor=TEAL, spaceBefore=5, spaceAfter=3, keepWithNext=True))
styles.add(ParagraphStyle(name="BodyFinal", fontName="Arial", fontSize=10.5, leading=15,
                          textColor=INK, spaceAfter=6))
styles.add(ParagraphStyle(name="SmallFinal", fontName="Arial", fontSize=8.5, leading=12,
                          textColor=GRAY, spaceAfter=4))
styles.add(ParagraphStyle(name="CaptureTitle", fontName="Arial-Bold", fontSize=16, leading=21,
                          textColor=NAVY, alignment=TA_CENTER, spaceAfter=10))
styles.add(ParagraphStyle(name="CoverMeta", fontName="Arial", fontSize=12, leading=20,
                          textColor=INK, alignment=TA_CENTER, spaceAfter=6))
styles.add(ParagraphStyle(name="TableHead", fontName="Arial-Bold", fontSize=8.5, leading=10,
                          textColor=colors.white))


def header_footer(canvas, doc):
    canvas.saveState()
    width = doc.pagesize[0]
    canvas.setStrokeColor(colors.HexColor("#D7E2E8"))
    canvas.setLineWidth(0.5)
    canvas.line(doc.leftMargin, 1.25 * cm, width - doc.rightMargin, 1.25 * cm)
    canvas.setFont("Arial", 8)
    canvas.setFillColor(GRAY)
    canvas.drawString(doc.leftMargin, 0.82 * cm, "ECBD 2026 | Informe final integrador")
    canvas.drawRightString(width - doc.rightMargin, 0.82 * cm, f"Página {doc.page}")
    canvas.restoreState()


PORTRAIT = A4
WIDE = landscape(A4)
doc = BaseDocTemplate(
    str(OUT), pagesize=PORTRAIT, leftMargin=1.8*cm, rightMargin=1.8*cm,
    topMargin=1.7*cm, bottomMargin=1.7*cm,
    title="Informe Final Integrador ECBD 2026",
    author="David Rafael Aguilar Solis",
)
portrait_frame = Frame(doc.leftMargin, doc.bottomMargin,
                       PORTRAIT[0]-doc.leftMargin-doc.rightMargin,
                       PORTRAIT[1]-doc.topMargin-doc.bottomMargin, id="portrait")
wide_margin = 1.1*cm
wide_frame = Frame(wide_margin, 1.55*cm, WIDE[0]-2*wide_margin,
                   WIDE[1]-2.65*cm, id="wide")
cover_frame = Frame(2*cm, 2*cm, PORTRAIT[0]-4*cm, PORTRAIT[1]-4*cm, id="cover")
doc.addPageTemplates([
    PageTemplate(id="Cover", frames=[cover_frame], pagesize=PORTRAIT),
    PageTemplate(id="Portrait", frames=[portrait_frame], onPage=header_footer, pagesize=PORTRAIT),
    PageTemplate(id="Landscape", frames=[wide_frame], onPage=header_footer, pagesize=WIDE),
])


def para(text, style="BodyFinal"):
    return Paragraph(text, styles[style])


def table(rows, widths, font=9.2):
    wrapped = [[para(str(cell), "TableHead" if row_index == 0 else "SmallFinal")
                for cell in row] for row_index, row in enumerate(rows)]
    t = Table(wrapped, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Arial-Bold"),
        ("BACKGROUND", (0, 1), (-1, -1), PALE),
        ("GRID", (0, 0), (-1, -1), 0.45, colors.white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


story = [
    para("UNIVERSIDAD TECNOLÓGICA<br/>DE TULA-TEPEJI", "CoverTitle"),
    Spacer(1, 0.5*cm),
    para("Tecnologías de la Información", "CoverSub"),
    para("Extracción de Conocimiento en Bases de Datos", "CoverSub"),
    Spacer(1, 1.1*cm),
    para("INFORME FINAL<br/>PROYECTO INTEGRADOR", "CoverTitle"),
    para("Análisis de hábitos y condición física asociados<br/>con niveles de obesidad", "CoverSub"),
    Spacer(1, 1.0*cm),
    para("David Rafael Aguilar Solis<br/>Matrícula 22300607 · Grupo 10IDGS-G1", "CoverMeta"),
    para("Docente: pendiente de confirmación documental", "CoverMeta"),
    Spacer(1, 1.0*cm),
    para("Cierre académico · 20 de noviembre de 2026", "CoverMeta"),
    NextPageTemplate("Portrait"), PageBreak(),

    para("Resumen ejecutivo", "H1Final"),
    para("El proyecto integra exploración y preparación del dataset UCI de obesidad, un Data Mart SQL Server, modelos supervisados para Weight y NObeyesdad, clustering con K-Means, PCA y un dashboard Power BI de cuatro páginas. El CSV contiene 2,111 observaciones y 17 variables; se mantuvieron 24 filas idénticas. Las conclusiones describen este conjunto y no implican causalidad, diagnóstico ni validez poblacional."),
    para("Introducción y problema", "H1Final"),
    para("Los hábitos, la actividad física y las medidas antropométricas aparecen conjuntamente en el conjunto analizado. El problema de extracción de conocimiento es preparar datos trazables, comparar modelos sin fuga y presentar patrones con límites explícitos. NObeyesdad se relaciona con Height y Weight, de modo que el escenario que las incluye puede reproducir parte de la definición de la etiqueta."),
    para("Pregunta principal", "H2Final"),
    para("¿Qué patrones descriptivos y de desempeño predictivo se observan entre hábitos, condición física y las categorías registradas, y cuáles son los límites metodológicos de interpretarlos?"),
    para("Objetivos", "H1Final"),
    para("<b>General.</b> Integrar extracción de conocimiento desde preparación y exploración hasta modelado, análisis no supervisado y comunicación en Power BI, documentando reproducibilidad y límites.<br/><b>Específicos.</b> (1) Verificar fuente, estructura y calidad sin alterar el original; (2) preparar un derivado y estructurar un Data Mart SQL Server; (3) comparar regresión/clasificación con particiones agrupadas, pipelines y métricas; (4) explorar agrupamientos y PCA sin usar la etiqueta en el ajuste; (5) comunicar resultados mediante cuatro páginas Power BI."),
    para("Alcance y metodología", "H1Final"),
    para("CRISP-DM organiza la comprensión del problema y los datos, preparación, modelado, evaluación y comunicación. Las cinco unidades aplican estas fases en secuencia iterativa: planeación, EDA/ETL/Data Mart, modelos supervisados, clustering/PCA y dashboard. El proyecto no estima prevalencia ni efectos causales; una prueba técnica no acredita entrega o aceptación académica."),
    NextPageTemplate("Portrait"), PageBreak(),

    para("Dataset, exploración y preparación", "H1Final"),
    para("La fuente es UCI Machine Learning Repository, dataset 544: Estimation of Obesity Levels Based On Eating Habits and Physical Condition, con observaciones descritas para México, Perú y Colombia. UCI señala una mezcla de registros recolectados en plataforma web y datos sintéticos generados con Weka/SMOTE. Esta procedencia y el alcance geográfico limitan la generalización."),
    table([
        ["Control", "Resultado verificado"],
        ["Filas / variables", "2,111 / 17 (16 entradas y NObeyesdad)"],
        ["Faltantes / duplicados exactos", "0 / 24; duplicados conservados"],
        ["Categorías", "7 en NObeyesdad"],
        ["Edad / estatura / peso", "14–61 (media 24.31); 1.45–1.98 m (1.70); 39–173 kg (86.59)"],
        ["SHA-256 CSV raw", "28b6991062855d3d15642e38b1aa9d1b32fb7abbb5abf5b096f1868cd706154b"],
    ], [4.4*cm, 11.7*cm]),
    Spacer(1, 0.25*cm),
    para("El análisis exploratorio resume distribuciones y frecuencias; los rangos observados no son umbrales clínicos. La regla 1.5×IQR marcó candidatos, en especial NCP; no se eliminaron ni recortaron valores. Algunas escalas contienen fracciones compatibles con la composición sintética. El derivado UTF-8/LF conserva esquema, orden y valores del origen; las transformaciones se guardan en data/processed/."),
    para("ETL y Data Mart", "H1Final"),
    para("El ETL valida encabezados, tipos, finitud, dominios y conteos. SQL Server organiza categorías en DM.DimObesityLevel y observaciones en DM.FactObesityObservation, con staging para validar la carga, claves y restricciones referenciales. El dashboard consulta sólo la dimensión SQL; FactDashboard se basa en CSV U2 unido con asignaciones U4 por row_index, evitando duplicar los hechos."),
]
diagram = ROOT / "docs" / "unidad_ii" / "figuras" / "diagrama_datamart_ae2.png"
img = Image(str(diagram))
max_w, max_h = 16.1*cm, 8.4*cm
scale = min(max_w/img.imageWidth, max_h/img.imageHeight)
img.drawWidth, img.drawHeight = img.imageWidth*scale, img.imageHeight*scale
story += [img, para("Figura 1. Esquema del Data Mart de Unidad II.", "SmallFinal"),
          KeepTogether([
              para("Regresión de Weight", "H1Final"),
              para("Se compararon DummyRegressor, regresión lineal y Random Forest. Se excluyeron Weight, NObeyesdad y variables derivadas del objetivo. Partición agrupada: 1,689 entrenamiento y 422 test; los duplicados exactos permanecen juntos. La imputación, codificación y escalado se ajustan dentro de pipelines y folds de entrenamiento. La búsqueda de hiperparámetros no usó test."),
              table([
                  ["Modelo", "MAE test", "RMSE test", "R² test", "RMSE CV"],
                  ["DummyRegressor (media)", "21.9245", "25.8146", "-0.0001", "26.2825"],
                  ["Regresión lineal", "13.4350", "16.6931", "0.5818", "17.2341"],
                  ["Random Forest optimizado", "4.7501", "8.1428", "0.9005", "8.9627"],
              ], [5.0*cm, 2.4*cm, 2.6*cm, 2.0*cm, 2.4*cm]),
              para("El Random Forest seleccionado tiene 150 árboles, profundidad ilimitada y hoja mínima 1. La brecha entre RMSE de entrenamiento (3.1548) y prueba (8.1428) debe considerarse al interpretar el ajuste.")
          ])]

story += [NextPageTemplate("Portrait"),
          para("Clasificación y evaluación", "H1Final"),
          para("La etiqueta contiene siete categorías. Escenario A incorpora Height y Weight, por lo que existe riesgo de circularidad; B excluye ambas medidas. La tabla muestra métricas de modelos optimizados; las matrices de confusión adjuntas al dashboard corresponden a modelos base y no se atribuyen a estos modelos optimizados."),
          table([
              ["Escenario / modelo optimizado", "Acc.", "Prec. macro", "Recall macro", "F1 macro", "F1 CV"],
              ["A · Regresión logística, C=10", "0.9621", "0.9634", "0.9613", "0.9615", "0.9310"],
              ["A · Random Forest, 100 árboles", "0.9479", "0.9478", "0.9463", "0.9465", "0.9326"],
              ["B · Regresión logística, C=10", "0.6374", "0.6261", "0.6308", "0.6089", "0.5791"],
              ["B · Random Forest, 150 árboles", "0.8697", "0.8664", "0.8669", "0.8666", "0.8287"],
          ], [5.4*cm, 1.7*cm, 2.3*cm, 2.2*cm, 1.7*cm, 1.7*cm]),
          para("Las búsquedas optimizaron F1 macro mediante validación cruzada estratificada y agrupada sólo en entrenamiento. La diferencia A/B refleja capacidad predictiva en estas particiones, no efecto causal ni utilidad clínica."),
          para("Clustering y PCA", "H1Final"),
          para("K-Means usó Age, Height, Weight, FCVC, NCP, CH2O, FAF y TUE con StandardScaler, random_state=42 y n_init=20. NObeyesdad no participó en el ajuste. En el rango inicial k=2–9 el máximo Silhouette fue 0.172636 en k=9; el análisis ampliado halló valores mayores para k=10 y k=11. k=9 no se describe como óptimo global."),
          table([["Componente", "Varianza", "Acumulada"], ["PC1", "22.65%", "22.65%"], ["PC2", "18.66%", "41.31%"]], [5.0*cm, 5.0*cm, 5.0*cm]),
          para("PC1 y PC2 omiten 58.69% de la variación. Variables antropométricas pueden dominar distancias; los grupos son exploratorios, no subtipos clínicos."),
          para("Dashboard e integración", "H1Final"),
          para("El PBIP organiza panorama, resultados supervisados, clustering/PCA y conclusiones. FactDashboard contiene 2,111 filas y se enriquece con asignaciones U4 completas mediante row_index. Se conservan duplicados. La dimensión de obesidad filtró Normal_Weight a 287 observaciones y, al limpiar el filtro, restauró 2,111. Las métricas y perfiles vienen de resultados U3/U4 ya calculados; no se reentrenaron modelos."),
          para("En Power BI Desktop se verificó interactivamente ClusterProfile → FactDashboard: al filtrar cluster 0, el gráfico de hechos y el dispersograma mostraron únicamente ese grupo; el CSV de asignaciones U4 confirma 246 observaciones. Al restaurar el rango completo reaparecieron los nueve clusters. En una prueba separada, Normal_Weight redujo el KPI a 287 observaciones y al quitar la selección regresó a 2,111."),
          para("La evidencia visual de interacción se conserva separada en dashboard/evidencias/cluster_interaction_2026-11-18.png.")]

story += [NextPageTemplate("Portrait"),
          para("Conclusiones, recomendaciones y limitaciones", "H1Final"),
          para("Conclusiones sustentadas", "H2Final"),
          para("1. El Random Forest redujo MAE desde 21.9245 del baseline constante hasta 4.7501 en test; R²=0.9005 describe ajuste dentro de la muestra reservada y debe leerse con la brecha entrenamiento/prueba.<br/>2. La regresión logística optimizada de A obtuvo F1 macro 0.9615; el Random Forest optimizado de B obtuvo 0.8666. Son algoritmos distintos. Comparando Random Forest entre escenarios, A obtuvo 0.9465 frente a 0.8666 en B. El escenario A incluye medidas relacionadas con la etiqueta, por lo que no demuestra causalidad.<br/>3. PC1 y PC2 acumulan 41.31% de varianza, por lo que la vista bidimensional no captura la mayor parte de la variación.<br/>4. Silhouette modesta y valores mayores en k=10/11 impiden sostener que k=9 sea óptimo global."),
          para("Recomendaciones prudentes", "H2Final"),
          para("1. Utilizar el dashboard para describir y explorar este archivo; no convertir asociaciones o predicciones internas en diagnóstico, prevalencia o recomendación clínica.<br/>2. Antes de generalizar modelos o segmentos, validar con datos externos representativos y revisar sensibilidad a variables, duplicados y configuración de clusters bajo supervisión académica."),
          para("Limitaciones", "H2Final"),
          para("La fuente combina datos recolectados y sintéticos, conserva duplicados y no dispone de identificadores individuales. El alcance geográfico y la generación limitan la representatividad. Los modelos se evaluaron sobre particiones del mismo dataset; clustering es exploratorio; no hay inferencia causal ni validación poblacional. La operación técnica no acredita entrega en Classroom, defensa ni aceptación docente."),
          para("Referencias", "H2Final"),
          para("UCI Machine Learning Repository. (2019). <i>Estimation of Obesity Levels Based On Eating Habits and Physical Condition</i> (Dataset 544). https://doi.org/10.24432/C5H31Z<br/>Mendoza Palechor, F., &amp; de la Hoz Manotas, A. (2019). Dataset for estimation of obesity levels based on eating habits and physical condition in individuals from Colombia, Peru and Mexico. <i>Data in Brief, 25</i>, 104344. https://doi.org/10.1016/j.dib.2019.104344<br/>Microsoft. (s. f.). <i>Power Query SQL Server connector</i>. https://learn.microsoft.com/en-us/power-query/connectors/sqlserver<br/>Microsoft. (s. f.). <i>Tabular Model Definition Language</i>. https://learn.microsoft.com/en-us/analysis-services/tmdl/tmdl-overview?view=sql-analysis-services-2025", "SmallFinal"),
          NextPageTemplate("Landscape"), PageBreak(),
          para("Matriz de confusión — clasificadores base", "CaptureTitle"),
          para("Fuente: docs/unidad_iii/figuras/clasificacion_matrices_confusion_base.png. Son resultados base del test reservado; no corresponden a las métricas de los modelos optimizados presentadas en la tabla anterior.", "SmallFinal")]

def append_figure(path, caption, next_page=False):
    if next_page:
        story.extend([NextPageTemplate("Landscape"), PageBreak()])
    if not path.is_file():
        raise FileNotFoundError(path)
    figure = Image(str(path))
    max_w, max_h = WIDE[0]-2*wide_margin, WIDE[1]-6.5*cm
    ratio = min(max_w/figure.imageWidth, max_h/figure.imageHeight)
    figure.drawWidth, figure.drawHeight = figure.imageWidth*ratio, figure.imageHeight*ratio
    story.extend([figure, Spacer(1, 0.25*cm), para(caption, "SmallFinal")])

append_figure(ROOT / "docs" / "unidad_iii" / "figuras" / "clasificacion_matrices_confusion_base.png",
              "Figura 2. Clasificación base en escenario A (antropométrico) y B (hábitos).")
append_figure(ROOT / "docs" / "unidad_iv" / "figuras" / "perfil_clusters.png",
              "Figura 3. Perfiles numéricos descriptivos de los nueve clusters exploratorios.", next_page=True)
append_figure(ROOT / "docs" / "unidad_iv" / "figuras" / "pca_clusters.png",
              "Figura 4. Proyección PCA bidimensional; PC1 y PC2 acumulan 41.31% de varianza.", next_page=True)

for idx, (filename, caption) in enumerate([
    ("pagina_01_panorama.png", "Captura final de Power BI: página 1, Panorama general."),
    ("pagina_02_modelos.png", "Captura final de Power BI: página 2, Modelos supervisados. La matriz corresponde a clasificadores base."),
    ("pagina_03_clustering_pca.png", "Captura final de Power BI: página 3, Clustering y PCA."),
    ("pagina_04_conclusiones.png", "Captura final de Power BI: página 4, Hallazgos y conclusiones."),
]):
    append_figure(CAPTURES / filename, caption, next_page=True)

doc.build(story)
print(OUT)
