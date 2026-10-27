# Especificación de Unidad II

## Objetivo y alcance

Desarrollar una comprensión descriptiva del conjunto UCI de obesidad y un flujo reproducible de extracción, validación, transformación y preparación para análisis posteriores. Incluye diccionario de datos, notebook EDA, código ETL, datos derivados, diseño de Data Mart para SQL Server, documentación y evidencia técnica. No incluye modelos de Unidad III ni dashboard final de Unidad V.

El dataset de entrada es `data/raw/ObesityDataSet_raw_and_data_sinthetic.csv` (se conserva con ese nombre observado). Sólo las salidas derivadas se guardan bajo `data/processed/`. La ruta canónica escrita en reglas globales tiene una diferencia ortográfica; se registra aquí para evitar cambios o copias incorrectas.

## Calendario

La guía del curso fija revisión de Unidad II el 9 de octubre de 2026 y entrega el 16 de octubre de 2026, con ponderación de 15%. A la fecha de esta ejecución (27 de octubre de 2026), ambos hitos ya transcurrieron. Se conservan las fechas oficiales y no se afirma que la revisión o entrega hayan ocurrido; la evidencia del repositorio sólo permite fechar las actividades técnicas actuales.

## Requisitos

- RF-II01: perfilar las 17 variables, tipos, dominios/categorías, distribuciones, faltantes, duplicados, anomalías y relaciones descriptivas.
- RF-II02: entregar diccionario sustentado en la fuente UCI, distinguiendo definiciones documentadas de inferencias sobre códigos.
- RF-II03: documentar procedencia, proporción sintética reportada y límites de generalización.
- RF-II04: implementar ETL determinista, idempotente, con validación de entrada/salida, manejo de errores, conteos de conservados/excluidos y trazabilidad criptográfica.
- RF-II05: preservar filas y valores por defecto. Cualquier deduplicación, imputación, recodificación o exclusión requiere justificación; el proceso no debe aprender imputación, escalado, codificación ni balanceo sobre el conjunto completo.
- RF-II06: diseñar Data Mart SQL Server sencillo con claves, relaciones, carga, validación y consultas analíticas.
- RF-II07: preparar documentación reproducible en Markdown, DOCX y PDF cuando la herramienta disponible lo permita.
- RNF-II01: usar rutas relativas, semillas cuando sean pertinentes, codificación UTF-8 y registro de versiones/fecha real.
- RNF-II02: ningún resultado se declara si no se calculó; ninguna asociación se presenta como causalidad.
- RNF-II03: conservar intactos raw, Unidad I, notebook previo y especificación no seguida de Unidad III.

## Diseño y decisiones

EDA: lectura del CSV con Pandas en modo lectura; resumen de esquema y estadística descriptiva, balance de etiqueta, frecuencias de variables categóricas, rangos y posibles valores inusuales. Los hallazgos son descriptivos y no inferenciales. Se conservarán los 24 duplicados exactos identificados inicialmente: eliminar duplicados cambiaría el material y puede introducir decisiones no justificadas; su impacto y riesgo para particiones futuras se documentarán.

ETL: extracción del raw; validación estricta de encabezados, anchura, tipos y dominios; transformación conservadora (normalización de representación CSV y tipos sólo cuando sean semánticamente equivalentes); carga a un CSV derivado y manifiesto JSON con SHA-256 de origen/salida, conteos, versiones, decisiones y comando. No se crean variables objetivo derivadas ni se eliminan outliers automáticamente.

Data Mart: esquema relacional analítico apto para SQL Server, con dimensión de categoría de obesidad y tabla de observaciones/persona-análisis. La carga recibirá el archivo derivado y será repetible. El diseño estático no equivale a una carga ejecutada; toda indisponibilidad del motor se registra como NO VERIFICADO.

## Criterios de aceptación

| ID | Criterio | Evidencia requerida |
|---|---|---|
| AC-II01 | Fuente UCI, archivo local y huella documentados; raw inalterado. | hash antes/después y manifiesto |
| AC-II02 | CSV válido: 2,111 filas, 17 columnas, esquema esperado y lectura completa. | salida de validación y prueba |
| AC-II03 | Diccionario cubre las 17 variables, tipo, significado, dominios/códigos y limitaciones. | Markdown y referencias |
| AC-II04 | EDA calcula nulos, duplicados, estadísticas y distribuciones reales. | notebook ejecutado y reporte |
| AC-II05 | Gráficos y conclusiones descriptivas están ligados a resultados observados. | figuras y notebook |
| AC-II06 | Faltantes, 24 duplicados, extremos y decisiones de limpieza están tratados explícitamente. | informe y ETL |
| AC-II07 | ETL conserva entrada, reporta filas y rechaza entradas inválidas sin excepciones sin controlar. | pruebas positivas/negativas |
| AC-II08 | ETL es determinista e idempotente y registra hashes/versiones. | ejecución repetida/manifiesto |
| AC-II09 | Salida procesada existe sólo en `data/processed`, tiene esquema utilizable para Unidad III y no altera raw. | CSV derivado, lector y hashes |
| AC-II10 | Data Mart tiene DDL, claves/relaciones, carga, consultas de validación y consultas analíticas útiles. | scripts SQL y revisión estática |
| AC-II11 | Carga y consultas ejecutadas en SQL Server o se informan NO VERIFICADO si no hay instancia. | evidencia de conexión/ejecución |
| AC-II12 | Informe Markdown/DOCX/PDF describe EDA, limpieza, ETL, Mart, límites y reproducción. | entregables y revisión visual |
| AC-II13 | Pruebas de Unidad I y II terminan sin regresiones. | salidas reales y códigos de salida |
| AC-II14 | README enlaza artefactos y declara sólo estados demostrados; aprobación académica queda separada. | diff y verificación |

## Pruebas

Casos positivos: esquema, conteos, lectura de todas las filas, determinismo, idempotencia, salida y hash estable, compatibilidad de siete clases, integridad del raw. Casos negativos en temporales: archivo ausente, columnas omitidas/extra, fila de ancho incorrecto, archivo corrupto y valor fuera de dominio. SQL: conexión de sólo lectura a una instancia disponible; revisión estática y delimitación de scripts si no existe motor.

No son automatizables por completo: validez conceptual del diccionario, pertinencia académica de conclusiones, calidad visual, aceptación del docente y aprobación de rúbrica. Se reportan aparte.

## Tareas

1. Especificar criterios y preservar estado previo.
2. Calcular EDA y documentar diccionario.
3. Implementar/validar ETL y generar el derivado.
4. Diseñar y validar scripts SQL Server.
5. Crear informe, pruebas y evidencia; revisar el render DOCX/PDF.
6. Actualizar README y ejecutar regresión completa.

## Dependencias con Unidad III

La salida derivada conserva etiqueta, predictores, categorías y registros para regresión/clasificación. Los 24 duplicados deben agruparse al particionar para evitar que copias idénticas crucen train/test. Los pipelines de imputación, escalado, codificación, selección y balanceo pertenecen a Unidad III y se ajustarán sólo en entrenamiento.

## DoD

Todos los criterios aplicables tienen PASS/FAIL/NO VERIFICADO con evidencia reproducible. Un servidor SQL inexistente puede dejar AC-II11 como NO VERIFICADO, pero nunca simulado. La revisión académica y visual se declara por separado. La unidad no se declara aprobada por pruebas automáticas; commits locales separados requieren autorización explícita vigente en la tarea.
