# Análisis de hábitos y condición física asociados con niveles de obesidad

Proyecto Integrador de Recursamiento 2026 - **Extracción de Conocimiento en Bases de Datos**.

## Datos del proyecto

- **Institución:** Universidad Tecnológica de Tula-Tepeji (UTTT)
- **Programa:** Tecnologías de la Información
- **Estudiante:** David Rafael Aguilar Solis
- **Matrícula:** 22300607
- **Grupo:** 10IDGS-G1
- **Asignatura:** Extracción de Conocimiento en Bases de Datos
- **Docente:** pendiente de confirmación
- **Periodo del proyecto:** 23 de septiembre al 20 de noviembre de 2026

## Objetivo general

Analizar de forma reproducible los patrones asociados con hábitos alimenticios, características personales y condición física en el conjunto **Estimation of Obesity Levels Based On Eating Habits and Physical Condition** mediante preparación de datos, evaluación de modelos supervisados y exploración no supervisada, para comunicar resultados y limitaciones con CRISP-DM sin atribuir causalidad. Las actividades de cada unidad se completarán y documentarán progresivamente; este objetivo no afirma que ya se hayan ejecutado.

## Dataset

- **Fuente:** UCI Machine Learning Repository, dataset 544.
- **Archivo original:** `data/raw/ObesityDataSet_raw_and_data_sinthetic.csv`
- **Registros:** 2111
- **Columnas:** 17 (16 variables predictoras + `NObeyesdad`)
- **Valores faltantes detectados:** 0
- **Duplicados exactos detectados:** 24
- **Ámbito reportado:** México, Perú y Colombia.
- **Composición reportada:** 23% de registros recolectados directamente y 77% generados sintéticamente mediante Weka/SMOTE.
- **DOI del dataset:** https://doi.org/10.24432/C5H31Z

> **Integridad:** el contenido de `data/raw` se conserva sin modificaciones. Toda limpieza o transformación se guardará en `data/processed`.

## Pregunta principal

¿Qué asociaciones descriptivas se observan entre los hábitos alimenticios, las características personales, la condición física y las categorías `NObeyesdad`, y qué límites deben considerarse al evaluar modelos y comunicar esos patrones?

## Líneas de análisis previstas

### Regresión

- **Objetivo:** estimar `Weight`.
- `NObeyesdad` se excluirá como predictor para evitar circularidad.
- Métricas previstas: MAE, RMSE y R².

### Clasificación

- **Objetivo:** clasificar `NObeyesdad` en siete categorías.
- Se compararán configuraciones de variables para controlar el riesgo de fuga de información asociado con `Weight`/`Height`.
- Métricas previstas: accuracy, F1 macro y matriz de confusión.

### Análisis no supervisado

- Clustering para identificar perfiles de hábitos y condición física.
- PCA para reducción de dimensionalidad y visualización.
- `NObeyesdad` no se utilizará para formar clusters; sólo se usará después para describirlos.

## Metodología

El proyecto se organizará con **CRISP-DM**:

1. Comprensión del problema.
2. Comprensión de los datos.
3. Preparación de los datos.
4. Modelado.
5. Evaluación.
6. Despliegue/comunicación.

## Calendario oficial

| Fecha | Hito | Ponderación |
|---|---|---:|
| 25 o 28 de septiembre de 2026 | Actividad 0; discrepancia histórica conservada. | — |
| 2 de octubre de 2026 | Entrega Unidad I. | 20% |
| 9 de octubre de 2026 | Revisión Unidad 2. | — |
| 16 de octubre de 2026 | Entrega Unidad 2. | 15% |
| 23 de octubre de 2026 | Revisión Unidad 3. | — |
| 30 de octubre de 2026 | Entrega Unidad 3. | 25% |
| 6 de noviembre de 2026 | Revisión Unidad 4. | — |
| 13 de noviembre de 2026 | Entrega Unidad 4. | 25% |
| 17 de noviembre de 2026 | Revisión de dashboard y presentación. | — |
| 20 de noviembre de 2026 | Unidad V y cierre. | 15% |

Las fechas transcurridas son hitos del calendario, no evidencia de entregas o revisiones realizadas. El estado de cada entrega se registra sólo cuando existe evidencia independiente.

## Herramientas propuestas

- Python 3.x
- Jupyter Notebook
- Visual Studio Code
- pandas y NumPy
- scikit-learn
- Matplotlib / Seaborn
- SQL Server para Data Mart cuando corresponda, conforme a la guía de la asignatura
- Git y GitHub
- Power BI para el dashboard final, conforme a la guía de la asignatura

## Estructura del repositorio

```text
REC_ECBD_2026_Aguilar_Solis_David_Rafael/
├── data/
│   ├── raw/          # Dataset original sin modificaciones
│   └── processed/    # Datos limpios y transformados
├── notebooks/        # EDA, preparación y experimentos
├── src/              # Código reutilizable
├── sql/              # Scripts del Data Mart
├── modelos/          # Modelos generados
├── dashboard/        # Dashboard y storytelling
├── docs/             # Documentos e informes
└── README.md
```

## Avance actual

- [x] Estructura base del repositorio.
- [x] Dataset original almacenado en `data/raw`.
- [x] Notebook `00_revision_inicial_dataset.ipynb`.
- [x] Revisión inicial: dimensiones, faltantes y duplicados.
- [x] **Unidad I:** documentación terminada y validación técnica interna PASS (12/12 pruebas; 19 verificaciones PASS, 0 FAIL). Véase [planeación de Unidad I](docs/unidad_i/planeacion_unidad_i.md). Entrega y aprobación docente no verificadas.
- [x] **Unidad II:** análisis EDA, diccionario, notebook, ETL y Data Mart ejecutados en SQL Server Express; 2,111 filas cargadas en staging y hechos, segunda carga idempotente, siete clases y cotejo fila a fila con el CSV procesado PASS. Pruebas de cierre: U1 12/12, U2 12/12 y U3 8/8; verificador U1 19/19 PASS. Esto registra validación técnica interna; entrega y aceptación docente no verificadas. Véase [informe](docs/unidad_ii/informe_unidad_ii.md), [guía SQL](docs/unidad_ii/guia_sql_server.md), [diccionario](docs/unidad_ii/diccionario_datos.md), [evidencia](docs/unidad_ii/evidencias/verificacion_unidad_ii.json) y [notebook EDA](notebooks/01_exploracion_datos.ipynb).
- **Actividad U2 AE1 — Exploración, clasificación y diagnóstico:** artefactos integrados y ejecutados internamente. Notebook: [exploración](notebooks/Aguilar_Solis_David_Rafael_U2_AE1_Exploracion.ipynb); PDF: [diagnóstico](docs/Aguilar_Solis_David_Rafael_U2_AE1_Diagnostico.pdf); [matriz de cumplimiento](docs/actividad_u2_ae1/matriz_cumplimiento.md); [evidencia de validación](docs/actividad_u2_ae1/evidencia_validacion.json). El notebook ejecutó sus 20 celdas de código sin errores y el PDF de 11 páginas se renderizó y revisó visualmente. La entrega en Classroom, defensa individual y aceptación del profesor siguen pendientes de verificación.
- [x] **Unidad III:** implementación técnica interna: regresión de `Weight`, clasificación A/B de `NObeyesdad`, validación agrupada, optimización y pruebas. La entrega y aceptación docente no están verificadas. Informe: [Markdown](docs/unidad_iii/informe_unidad_iii.md), [DOCX](docs/unidad_iii/informe_unidad_iii.docx), [PDF](docs/unidad_iii/informe_unidad_iii.pdf); evidencia técnica: [verificación U3](docs/unidad_iii/evidencias/verificacion_unidad_iii.json); especificación: [SDD-U3](docs/sdd/03_unidad_iii.md).
- [ ] **Unidad IV:** clustering y PCA pendientes.
- [ ] **Unidad V:** dashboard, storytelling, documentación final y defensa pendientes.

## Referencias principales

- Mendoza Palechor, F., & de la Hoz Manotas, A. (2019). *Dataset for estimation of obesity levels based on eating habits and physical condition in individuals from Colombia, Peru and Mexico*. Data in Brief, 25, 104344. https://doi.org/10.1016/j.dib.2019.104344
- UCI Machine Learning Repository. (2019). *Estimation of Obesity Levels Based On Eating Habits and Physical Condition* [Dataset]. https://doi.org/10.24432/C5H31Z
