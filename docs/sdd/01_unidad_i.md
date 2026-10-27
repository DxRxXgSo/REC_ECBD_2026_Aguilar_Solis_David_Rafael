# Especificación de Unidad I

## Estado y alcance

- **Estado:** especificación preparada; aceptación pendiente.
- **Unidad:** I, planeación del proyecto (ponderación oficial: 20%).
- **Fecha oficial:** 2 de octubre de 2026, ya transcurrida al 26 de octubre de 2026. No inferir entrega ni cambiar el calendario.
- **En alcance:** revisar y corregir, después de autorizar implementación, los documentos académicos de Unidad I, sus pruebas y evidencia.
- **Fuera de alcance ahora:** modificar documentos académicos, README, dataset o notebook; implementar otras unidades; crear modelos, transformaciones o dashboard; commits o push.

## Contexto y fuentes de trabajo

Proyecto: *Análisis de hábitos y condición física asociados con niveles de obesidad*. Estudiante: David Rafael Aguilar Solis. Asignatura: Extracción de Conocimiento en Bases de Datos. Fuente de datos: UCI *Estimation of Obesity Levels Based on Eating Habits and Physical Condition*.

Archivos que deberán revisarse en una tarea de implementación autorizada:

- `docs/unidad_i/planeacion_unidad_i.md`
- `docs/unidad_i/planeacion_unidad_i.docx`
- `README.md`
- `docs/unidad_i/verificar_unidad_i.py`
- `docs/unidad_i/evidencias/verificacion_unidad_i.json`
- `data/raw/ObesityDataSet_raw_and_data_sinthetic.csv` (sólo lectura)
- `notebooks/00_revision_inicial_dataset.ipynb` (preservar sus resultados guardados)

La especificación no autoriza modificaciones por sí sola. Requiere una instrucción de implementación posterior.

## Requisitos funcionales y editoriales

1. **Identificación y portada:** incluir portada institucional y los datos académicos confirmados: estudiante, asignatura, proyecto, unidad, programa/institución sólo si se verifican en fuente oficial, ciclo/periodo y fecha de entrega. No inventar institución, matrícula, grupo, docente o asesor. Incluir campos pendientes claramente identificados; no consignar un docente sin confirmación oficial.
2. **Contexto y problema:** contextualizar el dataset y el propósito académico; formular un problema preciso, sin presentar correlación o predicción como causalidad ni como diagnóstico clínico.
3. **Pregunta y objetivos:** conservar una pregunta principal coherente con el alcance de todo el proyecto. El objetivo general debe describir el resultado analítico final esperado, no limitarse a “planear”. Incluir al menos tres objetivos específicos observables y alineados.
4. **Alcance y limitaciones:** distinguir Unidad I de actividades posteriores; señalar límites de generalización, origen secundario, datos sintéticos y riesgos interpretativos pertinentes.
5. **Dataset y procedencia:** documentar nombre, repositorio UCI, enlace/DOI, autoría/publicación, descripción de población según fuente, estructura comprobada, variables y etiqueta. Distinguir hechos de la fuente de conteos verificados localmente.
6. **Comparativa conceptual:** comparar IA, Machine Learning, Data Mining y Big Data mediante una matriz sustentada que incluya definición/enfoque, características, beneficios, restricciones, retos, casos de uso y herramientas típicas. Explicar solapamientos y diferencias; no describir Big Data como un algoritmo ni clasificar este CSV como Big Data sin justificar escala/arquitectura.
7. **Tecnologías seleccionadas:** justificar lenguaje, entorno, bibliotecas y herramientas para el trabajo autorizado. Priorizar Python, Pandas, NumPy, scikit-learn, Jupyter y Matplotlib conforme a su uso. Respetar SQL Server para Data Mart y Power BI para dashboard en las unidades correspondientes. No proponer sustitutos a herramientas obligatorias sin justificación y autorización docente.
8. **CRISP-DM:** explicar sus seis fases y mapear su aplicación y productos esperados a las cinco unidades: I comprensión y planeación; II datos y preparación; III modelado/evaluación supervisados; IV modelado/evaluación no supervisados; V comunicación/despliegue. Señalar iteración entre fases y que este mapeo es una organización del proyecto, no evidencia de implementación.
9. **Resultados esperados verificables:** describir artefactos y evidencias futuros medibles (documentación, resultados evaluados, comunicación final), sin inventar métricas ni resultados experimentales.
10. **Cronograma y Actividad 0:** incorporar el calendario global confirmado en `00_reglas_globales.md`, ponderaciones y fechas. Conservar la discrepancia de Actividad 0 entre 25 y 28 de septiembre de 2026; no resolverla por suposición.
11. **Referencias:** usar referencias completas y comprobables para el dataset, artículo, conceptos y metodología; incluir enlaces/DOI y citas en el texto donde corresponda. No inventar bibliografía.
12. **README:** mantener coherencia entre objetivo, datos académicos confirmados, herramientas, fechas, estructura y estado. No marcar Unidad I completada hasta aceptar todos los criterios y evidencias. Preservar cambios previos del README y revisar el diff completo.
13. **Integridad y pruebas:** no modificar el CSV original. Verificar dimensiones, columnas/variables requeridas y hash byte a byte respecto de la línea base; documentar la normalización CRLF/LF sólo como explicación de finales de línea, no como cambio de contenido. Confirmar rutas, referencias, existencia y coherencia documental. Preservar las salidas guardadas del notebook.
14. **Calidad de documentos:** revisar ortografía, estilo académico, consistencia de tablas/citas y renderizar el DOCX final; inspeccionar todas las páginas. Ninguna página final debe quedar casi vacía por un salto evitable. La versión vigente debe renderizarse de nuevo: existe una discrepancia entre el reporte de defecto de cinco páginas casi vacías y la última inspección registrada que mostró cuatro páginas.

## Criterios de aceptación

Los criterios se aceptan con evidencia actual, no con planeación o resultados copiados de una ejecución pasada.

| ID | Criterio de aceptación | Prueba/evidencia requerida | Estado inicial |
|---|---|---|---|
| AC-I01 | Portada institucional completa con sólo datos confirmados; docente ausente mientras no se confirme. | Revisión de portada contra guía oficial y fuentes académicas autorizadas. | Pendiente |
| AC-I02 | Problema, contexto, pregunta y objetivos describen el proyecto analítico final y evitan causalidad no demostrada. | Revisión de trazabilidad pregunta–objetivos–resultados esperados. | Pendiente |
| AC-I03 | Alcance y limitaciones distinguen planeación de las unidades posteriores y registran riesgos de procedencia, duplicados y generalización. | Lista de cotejo documental con fuentes. | Pendiente |
| AC-I04 | Dataset, procedencia, variables, conteos y objetivo están documentados y consisten con el archivo local y fuente citada. | Prueba reproducible del CSV y revisión de referencia UCI/artículo. | Pendiente |
| AC-I05 | Comparativa IA/ML/Data Mining/Big Data cubre todos los aspectos exigidos y usa fuentes comprobables. | Matriz completa y revisión de citas. | Pendiente |
| AC-I06 | Herramientas elegidas tienen justificación y respetan Python/Pandas/NumPy/scikit-learn/Jupyter/Matplotlib, SQL Server y Power BI según el alcance de cada unidad. | Revisión de matriz tecnológica y guía. | Pendiente |
| AC-I07 | CRISP-DM queda explicado y aplicado mediante un mapa explícito a las unidades I–V. | Tabla fase ↔ unidad ↔ producto esperado; sin declarar fases futuras realizadas. | Pendiente |
| AC-I08 | Resultados esperados son artefactos observables; no contienen métricas o resultados inventados. | Revisión del texto y ausencia de valores experimentales no respaldados. | Pendiente |
| AC-I09 | Cronograma coincide con todas las fechas confirmadas y mantiene Actividad 0 como 25/28 de septiembre, sin escoger una. | Comparación automática/manual con `00_reglas_globales.md`. | Pendiente |
| AC-I10 | Referencias y rutas internas existen y apuntan a fuentes verificables. | Verificador de rutas/DOI más comprobación de fuentes citadas. | Pendiente |
| AC-I11 | README concuerda con especificación y estado real sin sobrescribir otros cambios locales. | Diff revisado y lista de estado coherente. | Pendiente |
| AC-I12 | Pruebas del CSV pasan, registran hash y conteos reales, y confirman que el original no cambió. | Ejecución del verificador revisado, salida y evidencia JSON reproducible. | Pendiente; el informe previo 11/0 no se considera validado hasta revisar código y reproducirlo. |
| AC-I13 | Salidas del notebook existente siguen presentes; ninguna se borra o reconstruye como parte de Unidad I. | Hash previo/posterior y revisión de celdas/salidas guardadas. | Pendiente |
| AC-I14 | DOCX final se renderiza y todas sus páginas se inspeccionan; se resuelve el reporte de página casi vacía. | PDF/PNG temporal de la versión final y registro de revisión visual. | Pendiente |

## Pruebas planificadas

- **T-I01 Integridad:** SHA-256 del CSV local frente a la línea base original; registrar bytes y finales de línea. El CSV nunca se modifica durante la prueba.
- **T-I02 Estructura:** parsear CSV con lector estándar, confirmar 2,111 registros, 17 columnas, ancho uniforme y las variables del encabezado.
- **T-I03 Calidad declarada:** recalcular celdas vacías y duplicados exactos; comparar contra la evidencia histórica, explicando cualquier diferencia.
- **T-I04 Documentación:** existencia de Markdown/DOCX/evidencia; comprobar enlaces locales, DOIs, citas y herramientas obligatorias.
- **T-I05 Coherencia:** comparar metadatos, objetivos, alcance, estado y cronograma entre documentación y README.
- **T-I06 Preservación:** verificar hash y salidas del notebook antes/después; inspeccionar `git status` y diff de los archivos protegidos.
- **T-I07 Visual:** renderizar el DOCX final y revisar cada página, saltos, tablas, legibilidad y referencias.

## Evidencias esperadas

- `docs/unidad_i/evidencias/verificacion_unidad_i.json`: salida nueva del verificador revisado, con fecha, entorno, comandos/controles, resultados y hashes.
- Captura o nota de revisión visual con número de páginas de la versión vigente; archivos de render temporales no se mezclan con el documento fuente salvo que se solicite conservar el PDF.
- `git status` y diff final revisados, identificando qué cambios eran preexistentes.

## Bloqueos y riesgos conocidos

- La entrega oficial de Unidad I fue el 2 de octubre de 2026; esa fecha ya pasó. El estado de entrega no está confirmado. Solicitar instrucciones de regularización si es necesario.
- Actividad 0 aparece históricamente con fechas 25 y 28 de septiembre; preservar ambas referencias.
- El README tiene cambios locales preexistentes y contiene matrícula, grupo y docente que no deben tratarse como confirmados hasta verificar fuente oficial.
- El DOCX, Markdown y verificador actuales contienen defectos reportados. Esta especificación los convierte en criterios; no afirma que estén corregidos.
- Ninguna implementación ni commit queda autorizado por la sola existencia de esta especificación.
