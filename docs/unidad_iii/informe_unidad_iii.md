# Unidad III Modelado supervisado evaluación y optimización

**Proyecto:** Análisis de hábitos y condición física asociados con niveles de obesidad
**Estudiante:** David Rafael Aguilar Solis · **Matrícula:** 22300607 · **Grupo:** 10IDGS-G1
**Institución:** Universidad Tecnológica de Tula-Tepeji · **Programa:** Tecnologías de la Información
**Asignatura:** Extracción de Conocimiento en Bases de Datos · **Unidad:** III — Modelado supervisado, evaluación y optimización
**Docente:** pendiente de confirmación · **Corte técnico:** 27 de octubre de 2026

## Resumen

Se implementaron y evaluaron modelos reproducibles para estimar `Weight` y clasificar `NObeyesdad`. La partición final reservó 422 de 2,111 filas y mantuvo juntas las copias exactas; entrenamiento tuvo 1,689 filas. La búsqueda de hiperparámetros utilizó exclusivamente entrenamiento y validación cruzada agrupada. En clasificación se compararon por separado variables antropométricas (A) y hábitos/condición (B). Los resultados son evidencia computacional del conjunto disponible, no demuestran causalidad ni aceptación docente.

## Datos y preparación

Se validó el CSV procesado de Unidad II contra el original UCI: 2,111 registros, 17 columnas, cero faltantes, 24 filas exactas duplicadas, siete categorías y `Weight` numérico. La fuente y derivado se identifican en los manifiestos de Unidad II y III. El SHA-256 de `data/raw/ObesityDataSet_raw_and_data_sinthetic.csv` fue `28b6991062855d3d15642e38b1aa9d1b32fb7abbb5abf5b096f1868cd706154b`; el de `data/processed/obesity_unit_ii.csv` fue `64418dcf666d49d832d07fe53dbfd9415662f2537502fde60e8dbe55b8f5218d`.

Las filas completamente idénticas comparten grupo. Se fijó semilla 42 y se reservó el primer pliegue de `StratifiedGroupKFold(5, shuffle=True)` como test. Ningún grupo aparece a ambos lados de la partición ni entre entrenamiento y validación en los folds. Imputación, escalado y codificación están dentro de `Pipeline`/`ColumnTransformer` para que cada ajuste ocurra en el subconjunto de entrenamiento del pliegue.

## Regresión de Weight

Se excluyeron `Weight`, `NObeyesdad` y variables derivadas del objetivo. Se compararon media Dummy, regresión lineal y Random Forest. Métricas de prueba y CV agrupada de cinco folds:

| Modelo | MAE test | RMSE test | R² test | RMSE CV media ± DE |
|---|---:|---:|---:|---:|
| DummyRegressor media | 21.9245 | 25.8146 | -0.0001 | 26.2825 ± 0.3216 |
| Regresión lineal | 13.4350 | 16.6931 | 0.5818 | 17.2341 ± 0.6279 |
| Random Forest base | 4.7501 | 8.1428 | 0.9005 | 8.9627 ± 1.0288 |

El bosque base obtuvo RMSE de entrenamiento 3.1548 y de test 8.1428; la diferencia de 4.9880 indica una brecha que conviene considerar. La búsqueda seleccionó 150 árboles, profundidad sin límite y hoja mínima 1. Su RMSE CV fue 8.9627 y test RMSE 8.1428, idénticos a los del bosque base con esa configuración.

La optimización usó `GroupKFold(5)` y minimizó RMSE sólo en entrenamiento. El Random Forest seleccionado (150 árboles, profundidad ilimitada y hoja mínima 1) obtuvo RMSE CV de 8.9627; al evaluar una sola vez la configuración fijada en el test reservado, obtuvo MAE de 4.7501, RMSE de 8.1428 y R² de 0.9005. Estas cifras coinciden con las del bosque base, cuya configuración ya tenía esos parámetros.

## Clasificación de NObeyesdad

Se reportan siete categorías y promedios macro. A incluye `Height` y `Weight` y puede reproducir la definición antropométrica de la etiqueta; B excluye ambas y utiliza las demás variables disponibles de hábitos y condición.

| Escenario | Modelo | Accuracy test | Precision macro | Recall macro | F1 macro | F1 macro CV media ± DE |
|---|---|---:|---:|---:|---:|---:|
| A | Dummy prior | 0.1659 | 0.0237 | 0.1429 | 0.0407 | 0.0408 ± 0.0003 |
| A | Regresión logística base | 0.8910 | 0.8891 | 0.8888 | 0.8864 | 0.8729 ± 0.0114 |
| A | Random Forest base | 0.9526 | 0.9524 | 0.9513 | 0.9514 | 0.9311 ± 0.0109 |
| B | Dummy prior | 0.1659 | 0.0237 | 0.1429 | 0.0407 | 0.0408 ± 0.0003 |
| B | Regresión logística base | 0.6398 | 0.6239 | 0.6333 | 0.6105 | 0.5708 ± 0.0134 |
| B | Random Forest base | 0.8697 | 0.8664 | 0.8669 | 0.8666 | 0.8287 ± 0.0135 |

La optimización eligió logística con C=10 para A (F1 macro test 0.9615) y bosque con 100 árboles, profundidad sin límite y hoja mínima 1 (0.9465). Para B eligió logística con C=10 (0.6089) y bosque con 150 árboles, profundidad sin límite y hoja mínima 1 (0.8666). Estas diferencias describen desempeño predictivo observado; no aíslan efectos causales. Los reportes por clase y matrices están en los artefactos acompañantes.

Las búsquedas de clasificación usaron `StratifiedGroupKFold(5)` y maximizaron F1 macro sólo en entrenamiento. Las métricas de test se calcularon después de fijar cada configuración:

| Escenario / modelo optimizado | Parámetros seleccionados | F1 macro CV | Accuracy test | Precision macro test | Recall macro test | F1 macro test |
|---|---|---:|---:|---:|---:|---:|
| A — Regresión logística | C=10 | 0.9310 | 0.9621 | 0.9634 | 0.9613 | 0.9615 |
| A — Random Forest | 100 árboles; profundidad ilimitada; hoja mínima 1 | 0.9326 | 0.9479 | 0.9478 | 0.9463 | 0.9465 |
| B — Regresión logística | C=10 | 0.5791 | 0.6374 | 0.6261 | 0.6308 | 0.6089 |
| B — Random Forest | 150 árboles; profundidad ilimitada; hoja mínima 1 | 0.8287 | 0.8697 | 0.8664 | 0.8669 | 0.8666 |

Las búsquedas y la evaluación se encuentran en `docs/unidad_iii/resultados/optimizacion_metricas_test.csv`; los reportes por clase del experimento base están en `docs/unidad_iii/resultados/clasificacion_reporte_por_clase_base.json`, y sus matrices en `docs/unidad_iii/figuras/clasificacion_matrices_confusion_base.png`. El gráfico de regresión base está en `docs/unidad_iii/figuras/regresion_predicciones_test_base.png`. El CSV de métricas optimizadas tiene SHA-256 registrado en el manifiesto de optimización.

## Validación y reproducibilidad

Ocho pruebas automatizadas de Unidad III pasaron, incluyendo contrato de datos, determinismo, separación de duplicados en test y folds, exclusión de fuga por objetivo, preprocesamiento train-only, finitud de métricas, errores de entrada y serialización. Los tres notebooks (`02_regresion`, `03_clasificacion`, `04_optimizacion`) se ejecutaron sin errores de celda. Cada manifiesto registra semilla, versiones, esquema, índices de partición y hashes; la optimización también confirma que las cinco pipelines serializadas reproducen las predicciones de test.

## Limitaciones y estado académico

El dataset incluye observaciones sintéticas y puede no representar otras poblaciones. Los duplicados exactos se mantienen para trazabilidad, pero se agrupan para evitar contaminación entre particiones. En A existe circularidad potencial con la etiqueta; B reduce esa dependencia a costa de menor desempeño observado. Correlación o capacidad predictiva no implican causalidad. La aceptación docente de Unidad III no está verificada; el nombre del docente continúa pendiente. La verificación de SQL Server de Unidad II permanece fuera de este experimento y no fue necesaria para entrenar sobre el CSV procesado validado.

## Fuentes

- UCI Machine Learning Repository. *Estimation of Obesity Levels Based On Eating Habits and Physical Condition*. https://doi.org/10.24432/C5H31Z
- Mendoza Palechor, F., & de la Hoz Manotas, A. (2019). *Dataset for estimation of obesity levels based on eating habits and physical condition in individuals from Colombia, Peru and Mexico*. Data in Brief, 25, 104344. https://doi.org/10.1016/j.dib.2019.104344
- La descripción de variables y decisiones de preparación se complementa con `docs/unidad_ii/diccionario_datos.md` y `docs/unidad_ii/informe_unidad_ii.md`.
