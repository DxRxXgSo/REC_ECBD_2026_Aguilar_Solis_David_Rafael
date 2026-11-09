# Matriz de cumplimiento — Actividad U2 AE1

**Actividad:** Actividad de Evaluación 1 – Exploración, clasificación y diagnóstico del conjunto de datos.
**Fuente de criterios:** guía oficial de cinco páginas proporcionada para la actividad.
**Estado técnico:** validación local ejecutada el 8 de noviembre de 2026.
**Alcance:** notebook exploratorio y diagnóstico PDF. No se entrenaron modelos.

| Requisito de la guía | Estado | Evidencia / observación |
|---|---|---|
| Identificación del proyecto, dataset, UCI 544, CSV, dimensiones, procedencia y limitaciones | PASS | Notebook, apartado 1; PDF, página 2. CSV leído: 2,111 registros y 17 variables. |
| Explicar `df.head()`, `df.shape`, `df.columns`, `df.info()`, `df.dtypes` y `df.describe()` | PASS | Notebook, apartado de exploración; salida e interpretación para cada comando. PDF, página 2. |
| Diccionario de las 17 variables con nombre, descripción, tipo Python/Pandas, tipo conceptual, unidad y utilidad | PASS | Notebook y PDF, páginas 3–4. Se distinguen variables continuas de escalas codificadas y categorías nominales/ordinales/binarias. |
| Procedencia, datos de personas, estructura tabular y componente sintético (~77%) | PASS | Notebook y PDF, página 5; fuente y artículo citados. |
| Faltantes por columna y porcentaje, duplicados y porcentaje | PASS | Ejecución actual: cero faltantes y 24 duplicados exactos (1.14% de filas), conservados. Salidas del notebook; PDF, página 5. |
| Revisar dominios, rangos, tipos inesperados y conversiones sospechosas | PASS | Controles ejecutados sobre las variables: cero incidencias en dominios/rangos y cero tipos técnicos inesperados; no se convierten ni alteran datos. PDF, página 5. |
| Proponer tratamientos futuros sin aplicarlos | PASS | Notebook y PDF, páginas 5 y 9; se difiere cualquier tratamiento a etapas posteriores y se preservan registros. |
| Estadística descriptiva de Age, Height y Weight (media, mediana, mínimo, máximo, desviación estándar) | PASS | Valores calculados sobre el CSV original y presentados con unidades e interpretación. PDF, página 6. |
| Examinar valores extremos de las tres variables, distinguir candidato atípico de error y proponer tratamiento | PASS | Método IQR 1.5 y boxplots; candidatos no se declaran errores ni se eliminan. PDF, páginas 6 y 8. |
| Al menos tres visualizaciones distintas, generadas por código y con interpretación | PASS | Cuatro salidas verificadas: barras por clase, histogramas, boxplots y dispersión estatura-peso. PDF, páginas 7–8. |
| Proponer regresión, clasificación de siete clases y agrupamiento sin usar la etiqueta para formar grupos | PASS | Notebook y PDF, página 9. Sólo son propuestas: no se entrenan modelos en esta actividad. |
| Responder las diez preguntas de conclusión de la guía | PASS | Respuestas numeradas 1–10 en el notebook y PDF, página 10. |
| Portada: UTTT, estudiante, matrícula, grupo, profesor, materia y actividad | PASS | PDF, página 1; incluye al Ing. Jose Luis Herrera Gallardo, MTI, según la guía de esta actividad. |
| Referencias verificables y reproducción local con rutas relativas | PASS | Notebook y PDF, página 11; UCI y artículo DOI. Entorno y comando registrados en evidencia JSON. |
| Notebook ejecutable con salidas guardadas y sin dependencia de SQL Server o Internet | PASS | `nbclient`: 20/20 celdas de código ejecutadas, cero errores; cuatro salidas gráficas. |
| PDF paginado, legible y revisado visualmente | PASS | 11 páginas A4 renderizadas localmente; revisión de todas las páginas. Se corrigieron encabezados de tablas que no se distinguían en el primer render. |
| Notebook y PDF en las rutas requeridas | PASS | `notebooks/Aguilar_Solis_David_Rafael_U2_AE1_Exploracion.ipynb` y `docs/Aguilar_Solis_David_Rafael_U2_AE1_Diagnostico.pdf`. |
| Pruebas de regresión de Unidades I y II | PASS | 12/12 pruebas de Unidad I y 12/12 de Unidad II. Verificador integral U1: 19 PASS, 0 FAIL, exit code 0; evidencia oficial previa preservada. |
| Pruebas de regresión de Unidad III | NO VERIFICADO | La suite no pudo importar `scikit-learn`: Windows Application Control bloqueó `_sgd_fast`; ninguna prueba de Unidad III llegó a ejecutarse. No se alteraron modelos ni métricas. |
| Publicación en GitHub de notebook y PDF | PASS | Verificado en `main` tras el push: [notebook](https://github.com/DxRxXgSo/REC_ECBD_2026_Aguilar_Solis_David_Rafael/blob/main/notebooks/Aguilar_Solis_David_Rafael_U2_AE1_Exploracion.ipynb) (blob `f4e333aea6d65093cd362bd46213a6cd2b2ad67f`) y [PDF](https://github.com/DxRxXgSo/REC_ECBD_2026_Aguilar_Solis_David_Rafael/blob/main/docs/Aguilar_Solis_David_Rafael_U2_AE1_Diagnostico.pdf) (blob `9512484b0182943101e9a3fbf941bdbd79524e5d`); coinciden con el árbol del commit publicado. |
| Entrega manual en Classroom | NO VERIFICADO | Requiere acción del estudiante. No se afirma entrega. |
| Defensa/revisión individual y aceptación docente | NO VERIFICADO | La elaboración del artefacto no acredita evaluación ni aprobación. |

## Interpretación

Los criterios de contenido, ejecución, archivo y revisión visual de esta actividad tienen evidencia local PASS. Los estados pendientes se limitan a publicación/entrega externa, revisión humana y al bloqueo de importación de la suite U3. Esta matriz no sustituye la calificación del profesor.
