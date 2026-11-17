# Informe integrador — corte técnico del 17 de noviembre de 2026

**Proyecto:** Análisis de hábitos y condición física asociados con niveles de obesidad
**Estudiante:** David Rafael Aguilar Solis · Matrícula 22300607 · Grupo 10IDGS-G1
**Institución:** Universidad Tecnológica de Tula-Tepeji · Tecnologías de la Información
**Asignatura:** Extracción de Conocimiento en Bases de Datos
**Estado:** resultados técnicos documentados; entrega en Classroom, defensa y aceptación académica no verificadas.

## Resumen ejecutivo

El proyecto analiza el dataset UCI de obesidad mediante preparación y Data Mart, modelos supervisados para `Weight` y `NObeyesdad`, y exploración con K-Means/PCA. El archivo contiene 2,111 observaciones y 17 variables; se conservaron 24 filas duplicadas exactas. Las cifras reportadas proceden de resultados reproducibles ya calculados y no demuestran causalidad, utilidad clínica ni generalización poblacional.

## Problema, método y preparación

La pregunta es qué patrones descriptivos aparecen entre hábitos, condición física y las categorías disponibles, y qué límites deben considerarse al comunicarlos. CRISP-DM guía el proyecto: comprensión del problema y los datos, preparación, modelado, evaluación e implementación/comunicación. Unidad II verificó equivalencia por valores entre origen y derivado, mantuvo los duplicados y creó staging, dimensión y hechos en SQL Server. Unidad III utilizó particiones reproducibles agrupadas por duplicados, preprocesamiento dentro de pipelines y evaluación final reservada. Unidad IV ajustó K-Means y PCA sin incluir la etiqueta en el ajuste.

La fuente es el repositorio UCI. Se observaron 2,111 filas, 17 columnas, cero nulos y 24 duplicados exactos. SHA-256 del CSV original: `28b6991062855d3d15642e38b1aa9d1b32fb7abbb5abf5b096f1868cd706154b`. SHA-256 del derivado U2: `64418dcf666d49d832d07fe53dbfd9415662f2537502fde60e8dbe55b8f5218d`. El derivado conserva los valores y normaliza la serialización UTF-8/LF; no se afirma que hubiera filtrado o corrección sustantiva.

## Unidad III — resultados supervisados

El Random Forest optimizado para regresión tuvo MAE de prueba 4.7501, RMSE 8.1428 y R² 0.9005; el RMSE de validación cruzada agrupada fue 8.9627. En clasificación, el escenario A con regresión logística obtuvo accuracy 0.9621, precision macro 0.9634, recall macro 0.9613 y F1 macro 0.9615. El escenario B con Random Forest obtuvo accuracy 0.8697, precision macro 0.8664, recall macro 0.8669 y F1 macro 0.8666. A incluye `Height` y `Weight`, con riesgo de circularidad respecto de `NObeyesdad`; B excluye ambas. La selección se basó en validación cruzada de entrenamiento, no en el conjunto de prueba. Son métricas asociativas sobre este dataset.

## Unidad IV — resultados exploratorios

Se estandarizaron ocho predictores: `Age`, `Height`, `Weight`, `FCVC`, `NCP`, `CH2O`, `FAF` y `TUE`. En el rango inicial k=2–9, el Silhouette máximo fue 0.172636 en k=9, límite superior del rango y señal de separación modesta. El análisis ampliado k=2–12 encontró valores mayores en k=10/11; por ello k=9 no se describe como óptimo global. PC1 y PC2 explicaron 41.31% de la varianza acumulada. La composición sintética, duplicados y posible predominio de variables antropométricas limitan la interpretación.

## Unidad V — dashboard Power BI

Se actualizó el PBIP existente `dashboard/ECBD_Integrador_2026/ECBD_Integrador_2026.pbip` en Power BI Desktop 2.159.1231.0. Power Query cargó `FactDashboard` (2,111 filas), `DimObesityLevel` (7), `ModelMetrics` (5), `ClusterProfile` (9) y `PcaVariance` (2). La conexión fue a `localhost\SQLEXPRESS` y `REC_ECBD_Obesidad_2026` mediante autenticación integrada de Windows. El bloqueo inicial correspondió a la confianza del certificado SQL local. Se utilizó `PBI_SQL_TRUSTED_SERVERS=localhost\SQLEXPRESS` únicamente en el proceso de Desktop, manteniendo cifrado; la variable persistente de usuario permanece vacía y no se guardaron credenciales. Microsoft documenta esta opción para el conector de SQL Server en Power BI Desktop.

La unión fuente por `row_index` conservó 2,111 observaciones y las 24 filas idénticas; las asignaciones U4 del CSV tienen 2,111 índices únicos y completos. El segmentador `Normal_Weight` filtró el modelo a 287 filas y una categoría; al quitarlo regresaron 2,111 filas y siete categorías, lo que verifica la relación dimensional de obesidad con los hechos. No se probó de forma interactiva la relación `ClusterProfile`–`FactDashboard`.

El PBIP se cerró, reabrió y refrescó nuevamente el 17 de noviembre; las cuatro páginas se renderizaron con datos y se revisaron visualmente. Panorama muestra cuatro KPI y distribuciones de categorías, edad, hábitos y medidas físicas. Modelos supervisados incluye la regresión RF, tabla por modelo/escenario con cuatro decimales y F1 macro por escenario/modelo, sin promediar candidatos. Clustering y PCA muestra conteos, perfiles, dispersión PC1/PC2 y 41.31% de varianza acumulada. Hallazgos presenta conclusiones, recomendaciones y límites. La advertencia de página 2 identifica las matrices de confusión disponibles como resultados de modelos base; la imagen de esas matrices todavía no está integrada en el dashboard.

Las capturas revisadas están en `dashboard/evidencias/final_powerbi_2026-11-16_validado/`. El validador PBIR reportó cero errores y un aviso porque no pudo descargar el esquema visual 2.14.0; los esquemas de raíz eliminados por el guardado de Desktop se restauraron. La opción “Guardar como” sólo presentó PBIP y la sección “Exportar” ofreció plantilla/PDF; no se generó un PBIX. Cinco componentes de alto nivel (refresco, panorama, supervisado, clustering/PCA y hallazgos) muestran contenido funcional; esta cuenta no equivale a aceptación completa de cada subcriterio.

## Verificación y límites

Suites ejecutadas con `.venv-unit2\Scripts\python.exe -m unittest discover`: dashboard 3/3, Unidad II 12/12, Unidad III 8/8 y Unidad IV 2/2 PASS. `git diff --check` pasó; Git emitió únicamente avisos de normalización LF/CRLF. El SHA-256 del CSV original antes y después se mantuvo `28b6991062855d3d15642e38b1aa9d1b32fb7abbb5abf5b096f1868cd706154b`. El cambio local preexistente de `notebooks/00_revision_inicial_dataset.ipynb` se conserva sin incluirlo en esta revisión.

Limitaciones: el dataset tiene componente sintético importante y alcance geográfico acotado; las 24 filas duplicadas permanecen y pesan en conteos; las asociaciones no implican causalidad. Los modelos no diagnostican ni predicen prevalencia nacional. Falta revisar la relación de perfiles en Desktop y añadir la imagen de matrices base si la rúbrica solicita verla en la página 2. La interfaz observada no ofreció crear PBIX. Las fechas de revisión integradora difieren entre los programas (17 o 18 de noviembre); el cierre está previsto para el 20 de noviembre. Entrega en Classroom, defensa y aceptación docente no verificadas.

## Fuentes

- UCI Machine Learning Repository. *Estimation of Obesity Levels Based On Eating Habits and Physical Condition*. https://doi.org/10.24432/C5H31Z
- Mendoza Palechor, F., & de la Hoz Manotas, A. (2019). *Dataset for estimation of obesity levels based on eating habits and physical condition in individuals from Colombia, Peru and Mexico*. Data in Brief, 25, 104344. https://doi.org/10.1016/j.dib.2019.104344
- Microsoft Learn. *Power Query SQL Server connector*. https://learn.microsoft.com/en-us/power-query/connectors/sqlserver
