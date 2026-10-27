![Logotipo institucional de la Universidad Tecnológica de Tula-Tepeji](https://www.uttt.edu.mx/img/about/logouttt.png)

# Universidad Tecnológica de Tula-Tepeji

## Tecnologías de la Información

### Proyecto Integrador de Recursamiento 2026

**Proyecto:** Análisis de hábitos y condición física asociados con niveles de obesidad  
**Asignatura:** Extracción de Conocimiento en Bases de Datos  
**Estudiante:** David Rafael Aguilar Solis  
**Matrícula:** 22300607  
**Grupo:** 10IDGS-G1  
**Unidad:** I — Planeación  
**Docente:** Pendiente de confirmación  
**Fecha oficial de entrega:** 2 de octubre de 2026  
**Actualización del documento:** 26 de octubre de 2026

<div style="page-break-after: always;"></div>

# Planeación del proyecto — Unidad I

**Proyecto:** Análisis de hábitos y condición física asociados con niveles de obesidad  
**Asignatura:** Extracción de Conocimiento en Bases de Datos  
**Estudiante:** David Rafael Aguilar Solis  
**Unidad:** I — Planeación  
**Versión de trabajo:** 26 de octubre de 2026

## Resumen

Este proyecto académico propone estudiar patrones asociados con hábitos alimenticios, características personales, condición física y niveles de obesidad en el conjunto de UCI *Estimation of Obesity Levels Based on Eating Habits and Physical Condition*. A lo largo de cinco unidades se documentarán los datos, se prepararán para análisis, se evaluarán métodos supervisados y no supervisados y se comunicarán hallazgos mediante los productos solicitados por el curso. El análisis será descriptivo y predictivo; no permitirá concluir causalidad ni emitir diagnósticos clínicos. Esta planeación no presenta resultados experimentales.

## 1. Contexto y planteamiento del problema

El conjunto contiene atributos demográficos, antropométricos y de hábitos, junto con la etiqueta `NObeyesdad`. Su análisis requiere documentar procedencia y calidad, distinguir asociación de causalidad y controlar el riesgo de que variables corporales estrechamente relacionadas con la etiqueta hagan que una evaluación predictiva parezca más favorable de lo que es. Los autores informan que el conjunto combina datos recolectados directamente y registros sintéticos generados para balancear clases; por ello sus patrones no deben generalizarse automáticamente a poblaciones completas (Mendoza-Palechor & de la Hoz-Manotas, 2019).

**Problema:** establecer un proceso reproducible para describir y modelar relaciones presentes en estos datos, explicando sus límites de procedencia, representatividad e interpretación.

**Pregunta principal:** ¿Qué asociaciones descriptivas se observan entre los hábitos alimenticios, las características personales, la condición física y las categorías `NObeyesdad`, y qué límites deben considerarse al evaluar modelos y comunicar esos patrones?

## 2. Objetivos

**Objetivo general.** Analizar de forma reproducible los patrones asociados con hábitos alimenticios, características personales y condición física en el conjunto UCI mediante preparación de datos, evaluación de modelos supervisados y exploración no supervisada, para comunicar resultados y limitaciones con CRISP-DM sin atribuir causalidad.

**Objetivos específicos.**

1. Documentar procedencia, estructura, variables, calidad y limitaciones de la fuente con un inventario verificable.
2. Preparar un conjunto derivado y un flujo ETL reproducible, preservando el original y documentando su carga al Data Mart de SQL Server cuando corresponda.
3. Implementar y evaluar en Unidad III al menos una tarea de regresión y una de clasificación con partición y preprocesamiento adecuados, métricas pertinentes y controles de fuga de información.
4. Aplicar y evaluar en Unidad IV clustering y PCA, documentando criterios de selección e interpretación de perfiles.
5. Comunicar en Unidad V los hallazgos sustentados, sus límites y su contexto mediante el dashboard Power BI, documentación final y materiales para la defensa.

## 3. Alcance y limitaciones

La Unidad I define problema, objetivos, decisiones metodológicas y productos esperados. La exploración y preparación corresponden a Unidad II; los modelos supervisados a Unidad III; clustering y PCA a Unidad IV; y dashboard, narrativa y defensa a Unidad V. Las actividades futuras aquí descritas son planes, no trabajo concluido.

El CSV local tiene 2,111 registros y 17 columnas según las comprobaciones reproducibles del proyecto; el artículo describe población de Colombia, Perú y México y reporta una proporción de registros sintéticos. El archivo no acredita muestreo probabilístico ni representatividad poblacional. La presencia local de duplicados exactos debe considerarse al decidir particiones y validación; su tratamiento se justificará en la preparación, no se presupone aquí. Las asociaciones no son efectos causales y `NObeyesdad` no equivale a diagnóstico clínico individual.

## 4. Dataset y variables

Fuente: UCI Machine Learning Repository, dataset 544, *Estimation of Obesity Levels Based on Eating Habits and Physical Condition* (UCI Machine Learning Repository, 2019). La publicación asociada describe participantes de México, Perú y Colombia y la composición sintética del conjunto (Mendoza-Palechor & de la Hoz-Manotas, 2019). Los conteos locales que se comprobarán son 2,111 filas de datos, 17 columnas, 16 atributos y la etiqueta `NObeyesdad`.

| Grupo | Variables | Consideración |
|---|---|---|
| Características y medidas | `Gender`, `Age`, `Height`, `Weight` | Verificar unidades y codificaciones en la ficha fuente. |
| Antecedentes y alimentación | `family_history_with_overweight`, `FAVC`, `FCVC`, `NCP`, `CAEC`, `CALC` | Interpretar abreviaturas conforme a la descripción UCI. |
| Hidratación, actividad y tecnología | `CH2O`, `FAF`, `TUE`, `SMOKE`, `SCC` | No asumir unidades físicas para valores codificados. |
| Transporte | `MTRANS` | Categoría de medio de transporte habitual. |
| Etiqueta | `NObeyesdad` | Categoría registrada, no diagnóstico clínico. |

## 5. Comparación conceptual

Los cuatro conceptos se relacionan, pero no son equivalentes. IA es el campo amplio; ML agrupa métodos que aprenden de datos; Data Mining organiza la búsqueda y validación de patrones; Big Data describe propiedades y necesidades de infraestructura. Las herramientas de la tabla son ejemplos representativos, no todas se adoptarán en este proyecto (Russell & Norvig, 2021; Mitchell, 1997; Han et al., 2022; Chang et al., 2018).

| Concepto y características | Beneficios y casos de uso | Restricciones y retos | Herramientas típicas |
|---|---|---|---|
| **Inteligencia Artificial (IA):** campo que diseña sistemas para tareas como percepción, razonamiento, búsqueda y decisión; puede usar reglas, conocimiento o aprendizaje. | Automatizar tareas y apoyar decisiones complejas; asistentes, reconocimiento de imágenes y sistemas de recomendación. | El desempeño depende del problema y los datos; riesgos de sesgo, opacidad, privacidad y seguridad. Reto: establecer objetivos, supervisión y evaluación responsables. | Python, bibliotecas de IA/ML, motores de reglas y plataformas de cómputo. |
| **Machine Learning (ML):** métodos que ajustan modelos a ejemplos; incluye aprendizaje supervisado, no supervisado y por refuerzo. | Generalizar patrones para predicción o agrupamiento; clasificación, regresión, detección de anomalías y segmentación. | Sobreajuste, sesgo, deriva y dependencia de los datos; reto de diseñar partición, validación, métricas y controles de fuga. | scikit-learn, TensorFlow, PyTorch, Python y Jupyter. |
| **Data Mining:** proceso iterativo de seleccionar, preparar, explorar y evaluar datos para extraer patrones útiles, combinando estadística, bases de datos, ML y visualización. | Convierte datos disponibles en conocimiento evaluable; segmentación, asociaciones, tendencias y anomalías. | Calidad insuficiente, patrones espurios, privacidad y dificultad de interpretación; reto de integrar contexto del dominio y validar hallazgos. | Python, Pandas, NumPy, scikit-learn, SQL Server y herramientas de visualización. |
| **Big Data:** datos o flujos cuyas propiedades (por ejemplo, volumen, velocidad, variedad y variabilidad) pueden exigir arquitecturas escalables; no es un algoritmo. | Procesar fuentes grandes, diversas o de alta velocidad; telemetría, registros, sensores y análisis de flujos. | Coste, gobernanza, seguridad, latencia e integración; reto de mantener calidad y operación distribuida. La elección depende de requisitos de escala (Chang et al., 2018). | Hadoop y Spark son ejemplos de ecosistema distribuido; se citan sólo como referencia, no como herramientas seleccionadas. |

El CSV tabular de 2,111 registros no se clasifica como Big Data por usar ML: no hay evidencia de volumen, velocidad o arquitectura que lo requiera.

## 6. Tecnologías seleccionadas

| Herramienta | Uso y justificación |
|---|---|
| Python | Lenguaje para análisis reproducible y automatización. |
| Pandas y NumPy | Lectura, manipulación tabular y operaciones numéricas. |
| scikit-learn | Preprocesamiento, modelos y evaluación en las unidades correspondientes. |
| Jupyter y Matplotlib | Registro reproducible de análisis y visualización exploratoria. |
| SQL Server | Plataforma indicada para el Data Mart cuando corresponda. |
| Power BI | Herramienta indicada para dashboard final y comunicación visual. |
| Git y GitHub | Trazabilidad de cambios y respaldo del código y documentos. |

No se fijan versiones de dependencias en esta planeación ni se afirma que los modelos o el dashboard ya existan.

## 7. Metodología CRISP-DM

CRISP-DM contempla seis fases iterativas: comprensión del negocio, comprensión de los datos, preparación, modelado, evaluación y despliegue. La evaluación puede llevar a revisar fases anteriores (Chapman et al., 2000).

| Fase | Aplicación por unidad | Producto esperado |
|---|---|---|
| Comprensión del negocio | I: problema, objetivos, alcance y criterios de éxito. | Planeación y preguntas delimitadas. |
| Comprensión de los datos | I–II: procedencia en I; exploración y calidad en II. | Inventario, diccionario y reporte exploratorio. |
| Preparación | II: limpieza justificada, transformaciones y ETL; datos derivados separados del original; Data Mart SQL Server cuando aplique. | Flujo reproducible y conjunto preparado. |
| Modelado | III: regresión y clasificación; IV: clustering y PCA. | Implementaciones configuradas para las preguntas. |
| Evaluación | III–IV: validación, métricas, interpretación y revisión de límites; volver a objetivos si hace falta. | Resultados calculados e interpretación sustentada. |
| Despliegue y comunicación | V: dashboard Power BI, documentación y defensa. | Productos finales según la guía. |

Este mapa distribuye el trabajo futuro y no afirma que las fases posteriores estén realizadas.

## 8. Resultados esperados verificables

- Documentación de problema, alcance, fuentes y variables.
- Inventario y proceso de preparación reproducibles, con datos derivados identificados.
- Implementaciones supervisadas con particiones, métricas, validación y análisis de limitaciones registrados.
- Evaluaciones de clustering y PCA con criterios explícitos e interpretación de perfiles.
- Dashboard Power BI y narrativa final que distingan asociaciones de causalidad y expliquen límites de los datos.

No se anticipan métricas, resultados de modelos ni conclusiones empíricas.

## 9. Cronograma oficial

| Fecha | Hito oficial | Ponderación |
|---|---|---:|
| 25 o 28 de septiembre de 2026 | Actividad 0; la discrepancia histórica se conserva. | — |
| 2 de octubre de 2026 | Entrega Unidad I. | 20% |
| 9 de octubre de 2026 | Revisión Unidad II. | — |
| 16 de octubre de 2026 | Entrega Unidad II. | 15% |
| 23 de octubre de 2026 | Revisión Unidad III. | — |
| 30 de octubre de 2026 | Entrega Unidad III. | 25% |
| 6 de noviembre de 2026 | Revisión Unidad IV. | — |
| 13 de noviembre de 2026 | Entrega Unidad IV. | 25% |
| 17 de noviembre de 2026 | Revisión de dashboard y presentación. | — |
| 20 de noviembre de 2026 | Unidad V y cierre. | 15% |

Las fechas son hitos oficiales confirmados. Al 26 de octubre de 2026, las fechas anteriores ya transcurrieron; el calendario por sí solo no acredita entregas o revisiones realizadas, cuyo estado requiere evidencia independiente.

## 10. Referencias

Chang, W., Grady, N., & NIST Big Data Public Working Group. (2018). *NIST Big Data Interoperability Framework: Volume 1, Big Data Definitions* (NIST SP 1500-1, Version 2). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.SP.1500-1r1

Chapman, P., Clinton, J., Kerber, R., Khabaza, T., Reinartz, T., Shearer, C., & Wirth, R. (2000). *CRISP-DM 1.0: Step-by-step data mining guide*. CRISP-DM Consortium. https://kddlab.com/files/CRISPWP-0800.pdf

Han, J., Pei, J., & Tong, H. (2022). *Data mining: Concepts and techniques* (4th ed.). Morgan Kaufmann.

Mendoza-Palechor, F., & de la Hoz-Manotas, A. (2019). Dataset for estimation of obesity levels based on eating habits and physical condition in individuals from Colombia, Peru and Mexico. *Data in Brief, 25*, 104344. https://doi.org/10.1016/j.dib.2019.104344

Mitchell, T. M. (1997). *Machine learning*. McGraw-Hill.

Russell, S. J., & Norvig, P. (2021). *Artificial intelligence: A modern approach* (4th ed.). Pearson.

UCI Machine Learning Repository. (2019). *Estimation of Obesity Levels Based on Eating Habits and Physical Condition* (Dataset 544). https://doi.org/10.24432/C5H31Z
