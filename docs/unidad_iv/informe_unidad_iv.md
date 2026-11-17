# Unidad IV — Clustering y reducción de dimensionalidad

**Estudiante:** David Rafael Aguilar Solis · **Matrícula:** 22300607 · **Grupo:** 10IDGS-G1
**Fecha de ejecución:** 16 de noviembre de 2026

## Datos y método

Se leyó `data/processed/obesity_unit_ii.csv` y se verificó contra el CSV original: 2,111 filas, 17 columnas, mismos valores, cero nulos y 24 filas duplicadas exactas. SHA-256 raw: `28b6991062855d3d15642e38b1aa9d1b32fb7abbb5abf5b096f1868cd706154b`; procesado: `64418dcf666d49d832d07fe53dbfd9415662f2537502fde60e8dbe55b8f5218d`.

K-Means utilizó `Age`, `Height`, `Weight`, `FCVC`, `NCP`, `CH2O`, `FAF` y `TUE`, con `StandardScaler`, `random_state=42`, `n_init=20`, y k de 2 a 9. `NObeyesdad` se excluyó del ajuste, del escalado y de PCA; sólo se usó luego para un cruce descriptivo. El escalado se ajustó a todos los registros porque se trata de segmentación exploratoria sin conjunto de test predictivo. No se presenta el resultado como capacidad de generalización.

## Resultados observados

El valor Silhouette más alto dentro del rango probado fue **0.172636 en k=9**, con inercia **8391.429242**. Dado que k=9 es el límite superior de búsqueda y la Silhouette es modesta, el resultado no prueba que nueve grupos sean una solución natural ni definitiva; conviene contrastar estabilidad, legibilidad e interpretación con el docente. Los tamaños obtenidos fueron: C0 246, C1 206, C2 253, C3 141, C4 247, C5 252, C6 304, C7 295 y C8 167.

PCA explicó **22.65%** con PC1 y **18.66%** con PC2, **41.31% acumulado**. La proyección bidimensional omite la mayor parte de la variación y se usa sólo para visualizar. La tabla de promedios por cluster está en `resultados/perfil_numerico_clusters.csv`; la distribución de la etiqueta calculada post hoc está en `resultados/distribucion_etiqueta_posthoc.csv`. Las gráficas de selección de k, PCA y perfil están bajo `figuras/`.

## Interpretación y límites

Los promedios muestran perfiles distintos en edad, estatura, peso y variables de frecuencia/actividad; sin embargo, las variables antropométricas incluidas pueden dominar distancias incluso después de estandarizar. Las etiquetas se describen después del ajuste y no forman los clusters. Se retuvieron los 24 duplicados, que reciben peso repetido. El conjunto incluye registros sintéticos y no permite afirmar causalidad, subtipos clínicos ni generalización a población externa. La selección actual es exploratoria, sensible a variables, distancia y rango de k.

## Reproducibilidad y estado

Código: `src/unit_iv.py`; notebook: `notebooks/Aguilar_Solis_David_Rafael_U4_AnalisisNoSupervisado.ipynb`; pruebas: `tests/unit_iv/`; evidencia: `evidencias/verificacion_unidad_iv.json`. La ejecución técnica se documenta por separado de la inspección visual y de la aprobación docente. PDF y render están pendientes de completar/revisar en este cierre.
