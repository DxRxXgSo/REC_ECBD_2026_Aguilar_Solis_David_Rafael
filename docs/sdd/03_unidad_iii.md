# Especificación SDD — Unidad III

## Estado y dependencia

- **Estado:** especificación activa; contrato de entrada comprobado el 27 de octubre de 2026; implementación en curso.
- **Unidad:** III, modelado supervisado, evaluación y optimización (25%).
- **Revisión prevista:** 23 de octubre de 2026; el calendario no acredita que la revisión haya ocurrido.
- **Entrega oficial:** 30 de octubre de 2026.
- **Proyecto:** estimación de `Weight` y clasificación de `NObeyesdad` en siete clases usando el dataset UCI autorizado.

**Contrato de entrada verificado:** `data/processed/obesity_unit_ii.csv`, SHA-256 `64418dcf666d49d832d07fe53dbfd9415662f2537502fde60e8dbe55b8f5218d`; 2,111 filas y 17 columnas, mismo esquema y mismos valores leídos que la fuente UCI; cero valores faltantes, 24 filas duplicadas exactas conservadas, siete clases y `Weight` numérico. SHA-256 de `data/raw/ObesityDataSet_raw_and_data_sinthetic.csv`: `28b6991062855d3d15642e38b1aa9d1b32fb7abbb5abf5b096f1868cd706154b`. La procedencia, decisiones y huellas están en `data/processed/unit_ii_manifest.json`, con diccionario e informe en `docs/unidad_ii/`. No se requiere SQL Server para entrenar desde el CSV derivado validado. La fuente raw permanece inmutable.

## Alcance y restricciones

Incluye partición reproducible, baselines, regresión, clasificación en dos escenarios, evaluación, validación cruzada, optimización, informe, gráficas, pruebas y artefactos reproducibles. Excluye toda modificación de unidades anteriores, limpieza o transformación directa de `data/raw`, afirmaciones causales, selección de modelos mediante test y publicación remota.

No imponer umbrales arbitrarios de calidad predictiva. Reportar resultados calculados, limitaciones y fallas tal cual. Los registros sintéticos restringen la generalización a poblaciones externas.

## Contrato de entrada obligatorio

Antes de implementar, verificar y registrar:

1. La ruta y versión del conjunto procesado autorizado por Unidad II, su SHA-256, dimensiones y esquema.
2. Su correspondencia con el dataset UCI y el historial reproducible de transformaciones, sin mutar el original.
3. Diccionario de variables, tipos, valores ausentes, codificaciones, etiqueta y decisiones documentadas sobre duplicados.
4. Que `Weight` sea numérico y `NObeyesdad` contenga las siete clases esperadas; no asumir columnas derivadas ni inventar el nombre del archivo.

Si algún punto falla, registrar el bloqueo y detener entrenamiento y métricas. No reconstruir resultados de Unidad II.

## Arquitectura experimental

- `notebooks/02_regresion.ipynb` y `notebooks/03_clasificacion.ipynb`: flujos separados con explicación, ejecución real, tablas y gráficas; conservar salidas que respalden los resultados publicados.
- `src/unit_iii/`: funciones reutilizables para validación de entrada, huellas de filas, particiones, pipelines, búsqueda, métricas y exportación.
- `tests/unit_iii/`: pruebas deterministas con fixtures pequeños y sintéticos sólo para probar el código, nunca para informar resultados del proyecto.
- `modelos/unidad_iii/`: pipelines finales ajustados y manifiesto de versiones, variables, semilla, particiones y huella de entrada.
- `docs/unidad_iii/`: informe Markdown, tablas, interpretación, limitaciones y evidencias; DOCX/PDF sólo tras generarlos y revisar su render.
- `docs/unidad_iii/evidencias/`: reporte JSON real de validación, comandos, fecha, versiones, hashes, diseño de partición, resultados y código de salida.

Los artefactos citados son rutas previstas, no existentes ni completadas. No guardar datos transformados fuera de `data/processed/`.

## Diseño de datos, particiones y fuga

- Fijar `random_state` documentado y guardar índices o huellas de las particiones para poder reproducirlas.
- Construir una llave de grupo determinista a partir de cada fila completa para que copias exactamente duplicadas queden juntas. Asegurar intersección vacía de grupos entre entrenamiento y prueba y entre folds.
- Reservar un test final una sola vez. Optimizar y seleccionar mediante validación cruzada únicamente dentro del entrenamiento.
- Para clasificación, usar partición estratificada y folds estratificados cuando las clases y los grupos lo permitan. Si la restricción de grupos impide una estratificación válida, registrar el desbalance y justificar el método; nunca dividir duplicados para forzar proporciones.
- Ajustar imputación, codificación, escalado y cualquier selección de variables dentro de `Pipeline`/`ColumnTransformer` durante cada fold. El test no ajusta transformadores ni hiperparámetros.
- Registrar versiones de Python, Pandas, NumPy y scikit-learn, semillas, lista y orden de variables por escenario, proporciones/tamaños y conteos de clase.

### Regresión — objetivo `Weight`

Comparar `DummyRegressor` (media), `LinearRegression` y `RandomForestRegressor` (o alternativa justificada). Excluir el objetivo, `NObeyesdad` y cualquier derivación directa de `Weight` según el diccionario de Unidad II. Aplicar escalado a modelos que lo requieran; conservar preprocesamiento en pipeline.

Calcular MAE, RMSE y R² en entrenamiento mediante CV y test reservado, además de la diferencia train/test. Afinar hiperparámetros sólo en folds del entrenamiento y reevaluar el candidato seleccionado una sola vez sobre test.

### Clasificación — objetivo `NObeyesdad`

Usar `DummyClassifier`, `LogisticRegression` y `RandomForestClassifier` (o alternativa justificada). Separar claramente:

- **Escenario A:** variables disponibles, incluyendo `Height` y `Weight`. Interpretar como escenario con posible circularidad porque la etiqueta está estrechamente vinculada con medidas antropométricas; no presentarlo como predicción independiente de ellas.
- **Escenario B:** hábitos y condición física según el diccionario de Unidad II, excluyendo `Height`, `Weight` y cualquier derivación directa de ambos. Registrar explícitamente columnas incluidas/excluidas.

Calcular accuracy, precision/recall/F1 macro, matriz de confusión y métricas por clase en CV de entrenamiento y test reservado. Afinar cada escenario sólo con entrenamiento. Comparar A y B sin fusionar sus métricas ni inferir causalidad.

## Optimización, reproducibilidad y artefactos

Usar `GridSearchCV` o alternativa justificable con folds agrupados (y estratificados para clasificación cuando sea factible). Informar espacio de búsqueda, métrica objetivo, CV, semilla y mejor configuración. Serializar pipelines finales sólo después de seleccionar hiperparámetros; recargarlos y confirmar que reproducen las predicciones guardadas. Guardar tabla de métricas, matrices, reportes por clase, gráficos de predicción/residuales y confusión, además del manifiesto y huellas. No escribir resultados en la fuente procesada.

## Criterios de aceptación

| ID | Criterio | Evidencia requerida | Estado inicial |
|---|---|---|---|
| AC-III01 | Insumos de Unidad II existentes, trazables, validados y con esquema/huella comprobables. | Contrato de entrada y evidencia aprobada de U2. | PASS técnico; aprobación académica de U2 no verificada |
| AC-III02 | Semillas, particiones y versiones permiten reproducir los experimentos. | Manifiesto y segunda ejecución comparable. | No iniciado |
| AC-III03 | Filas completas idénticas no cruzan entrenamiento, test ni folds. | Pruebas de intersección de grupos igual a cero. | No iniciado |
| AC-III04 | Preprocesadores se ajustan sólo dentro de folds de entrenamiento. | Pruebas de pipelines y revisión del código. | No iniciado |
| AC-III05 | Baselines y modelos de regresión requeridos se entrenan y comparan sin incluir etiqueta ni derivados del objetivo. | Pipeline, tabla de MAE/RMSE/R² y evaluación train/CV/test. | No iniciado |
| AC-III06 | Clasificación compara Dummy, logística y bosque aleatorio en A y B por separado. | Variables documentadas, métricas macro/accuracy, matrices y desempeño por clase. | No iniciado |
| AC-III07 | Optimización usa entrenamiento/CV solamente y test se evalúa al final. | Configuración de búsqueda y registro de una evaluación test final. | No iniciado |
| AC-III08 | Resultados e interpretación se derivan de ejecuciones reales y reconocen circularidad, datos sintéticos y límites de generalización. | Informe trazable a métricas y gráficos guardados. | No iniciado |
| AC-III09 | Pruebas cubren entrada inválida, partición reproducible, duplicados, pipelines, métricas y artefactos serializados. | Suite automatizada, salida y código de retorno. | No iniciado |
| AC-III10 | Modelos y documentación se pueden recargar, leer y reproducir sin modificar unidades previas ni `data/raw`. | Checks de artefactos, estado Git y hashes antes/después. | No iniciado |

## Tareas autorizadas por esta especificación

1. Resolver y validar el contrato de entrada de Unidad II.
2. Implementar helpers de datos, grupos duplicados, particiones y pipelines.
3. Implementar regresión con baselines, CV y optimización interna.
4. Implementar clasificación A/B con métricas globales y por clase.
5. Crear pruebas deterministas, notebook e informe conectado a resultados generados.
6. Exportar, validar y revisar DOCX/PDF cuando la herramienta esté disponible.
7. Ejecutar verificadores de unidades anteriores de forma que no sobrescriban sus evidencias; conservar sus salidas originales.
8. Verificar `data/raw` byte por byte antes/después, revisar diffs y evidencia; preparar commits locales separados sólo si todas las validaciones pasan.

Las tareas 2–8 pueden avanzar mientras AC-III01 permanezca PASS técnico; detener el entrenamiento si una comprobación posterior contradice este contrato. La fecha oficial de entrega no cambia y la especificación no presume que la revisión del 23 de octubre haya ocurrido.

## Pruebas y evidencia

Los fixtures sintéticos sólo prueban funciones, no modelan la obesidad ni aportan métricas académicas. Probar: esquema y columnas; ausencia de target/derivados en features; split y CV deterministas; separación de duplicados; estratificación y conteos; ajuste de transformadores con training-only; llamadas de búsqueda sin acceso al test; valores de métricas contra ejemplos manuales; serialización y recarga.

Registrar comando exacto, fecha, versiones, SHA-256 del conjunto procesado y de `data/raw`, random states, semillas, variables, asignaciones de grupo y conteos, hiperparámetros, resultados calculados, pruebas y exit codes. Distinguir checks automáticos, revisión de código y aceptación académica. Ninguna métrica se publica antes de obtenerla con la fuente validada de Unidad II.
