# Reglas globales de SDD

## Propósito y flujo

Usar especificaciones persistentes para reducir contexto repetido, acotar cambios y hacer verificable cada avance. Flujo obligatorio: **especificar → dividir en tareas pequeñas → implementar sólo el alcance autorizado → probar → revisar evidencias → solicitar revisión/aceptación → commit únicamente con autorización**.

Antes de cada tarea, revisar el estado de Git, `AGENTS.md`, este archivo y la especificación activa. No cargar especificaciones de unidades futuras mientras no estén activas.

## Restricciones del proyecto

- Conservar sin modificación `data/raw/ObesityDataSet_raw_and_data_sinthetic.csv`. Leerlo en modo de sólo lectura; las transformaciones, copias de trabajo y exportaciones derivadas se guardan exclusivamente en `data/processed`.
- No cambiar de dataset ni sobrescribir, eliminar o reconstruir trabajo existente. Revisar diffs y archivos sin seguimiento antes de tocar una ruta.
- No inventar resultados experimentales, métricas, fuentes, citas, fechas, identidad académica ni hechos sobre el curso. Diferenciar dato observado, resultado de prueba, plan y supuesto; si falta información requerida, registrar bloqueo.
- Documentar las decisiones que afecten alcance, selección de datos, herramientas, métricas o interpretación.
- No instalar dependencias innecesarias ni ejecutar código preexistente sin inspeccionarlo. Mantener pruebas reproducibles y proporcionales a la tarea.
- No hacer commits, push, pull, merge ni reescritura del historial sin autorización explícita del estudiante.
- No marcar criterios o unidades como aceptados hasta cumplir sus pruebas y revisar las evidencias.

## Herramientas

Priorizar Python, Pandas, NumPy, scikit-learn, Jupyter, Matplotlib, SQL Server y Power BI conforme al propósito y a las guías del curso. No sustituir herramientas obligatorias por alternativas sin documentar la razón y obtener autorización docente cuando corresponda. Git y GitHub se usan para trazabilidad; un archivo local no se considera publicado hasta verificarlo en el remoto.

## Estructura del repositorio

- `data/raw/`: fuente original inmutable.
- `data/processed/`: únicamente datos derivados o transformados.
- `notebooks/`: exploración y experimentos reproducibles.
- `src/`: código reutilizable del proyecto.
- `sql/`: artefactos SQL requeridos por la especificación activa.
- `modelos/`: modelos generados cuando una unidad lo autorice.
- `dashboard/`: productos de visualización, incluido Power BI cuando corresponda.
- `docs/unidad_i/`: documentos, scripts y evidencias de Unidad I.
- `docs/sdd/`: reglas globales, especificaciones activas e índice de especificaciones futuras.

No crear entregables de unidades futuras como parte de una tarea de Unidad I.

## Separación y control de calidad

Cada especificación debe separar: requisitos, decisiones, tareas autorizadas, criterios de aceptación, pruebas, evidencias, bloqueos y riesgos. Las pruebas deben registrar comando, fecha/entorno, salida real y ruta de evidencia. Comprobar rutas y referencias, consistencia README/especificación, integridad del CSV y preservación de salidas existentes cuando aplique. Para DOCX, renderizar y revisar todas las páginas; la presencia del archivo por sí sola no prueba calidad visual.

La evidencia se guarda junto a la unidad correspondiente, por ejemplo `docs/unidad_i/evidencias/`. No confundir una salida guardada previamente con una prueba recién ejecutada. Reportar fallas en vez de modificar evidencia para hacerla pasar.

## Calendario confirmado

Estas fechas fueron confirmadas por el estudiante a partir de las guías del curso. Se conservan como fechas oficiales; no deben volver a reportarse como desconocidas.

| Fecha | Hito | Ponderación |
|---|---|---:|
| 25 o 28 de septiembre de 2026 | Actividad 0 | Discrepancia histórica; ambas referencias se conservan sin elegir una. |
| 2 de octubre de 2026 | Entrega Unidad I | 20% |
| 9 de octubre de 2026 | Revisión Unidad II | — |
| 16 de octubre de 2026 | Entrega Unidad II | 15% |
| 23 de octubre de 2026 | Revisión Unidad III | — |
| 30 de octubre de 2026 | Entrega Unidad III | 25% |
| 6 de noviembre de 2026 | Revisión Unidad IV | — |
| 13 de noviembre de 2026 | Entrega Unidad IV | 25% |
| 17 de noviembre de 2026 | Revisión de dashboard y presentación | — |
| 20 de noviembre de 2026 | Unidad V y cierre | 15% |

El 2 de octubre ya pasó según la fecha actual de referencia, 26 de octubre de 2026. No asumir que hubo entrega ni cambiar la fecha: reportar el estado real y pedir instrucciones si la fecha afecta el plan de recuperación.
