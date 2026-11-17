# Matriz integradora de cumplimiento ECBD 2026

**Corte técnico:** 17 de noviembre de 2026. **Docente:** Ing. Jose Luis Herrera Gallardo, MTI (identidad indicada por el estudiante; aceptación de entregables pendiente).
Estados separados: **Desarrollado** (artefacto existe), **Probado** (ejecución técnica), **Documentado**, **Publicado** (verificado en remoto) y **Aceptación docente/Classroom** (no inferida).

## Calendario y fuentes

Los programas oficiales señalan U2 AE2 el 13/11 (9 puntos), U3 el 16/11 (25), U4 el 18/11 a las 12:00 (25), correcciones el 19/11, U5/cierre el 20/11 (15). La revisión integradora aparece como 17/11 en el programa continuo y 18/11 en el programa de cierre; se conserva la discrepancia y se prepara para el 17/11. El cierre exige dashboard en avance de 50–70% o 70% según guía; se adopta el mínimo conservador de 70% funcional. Las fechas oficiales previas de Unidad I y Unidad II se conservan históricamente; no prueban que las entregas ocurrieran.

## Matriz por unidad

| Unidad / requisito | Desarrollado | Probado | Documentado | Publicado | Aceptación |
|---|---|---|---|---|---|
| Actividad 0 | Informe/notebook previos presentes | evidencia previa 12/12 U1 y verificador 19/19 | `docs/unidad_i/` | confirmar rutas con remoto al publicar esta tanda | No verificada |
| U1 planeación | Markdown/DOCX/PDF existentes; docente pendiente | pruebas/verificador previos PASS | Planeación y SDD-U1 | presencia remota deberá comprobarse tras push | No verificada |
| U1: identidad institucional y planteamiento | Documento académico existente | Revisión técnica anterior; aceptación humana no replicada aquí | Planeación U1 | previo; confirmar remoto | No verificada |
| U1: objetivos, alcance, dataset, comparativa IA/ML/Data Mining/Big Data, herramientas, CRISP-DM y resultados esperados | Planeación existente | Verificador automatiza sólo parte; criterio académico requiere lectura | Markdown/DOCX/PDF U1 | previo; confirmar remoto | No verificada |
| U1: cronograma oficial, fuentes y README coherentes | Planeación histórica y calendario de cierre nuevo | Verificador actual valida parte del README/calendario; AC-I13 falla por hash del notebook local protegido | README/planeación/reglas globales | cambios de calendario publicados en `main` | No verificada |
| U2 AE1 | Notebook y PDF de 11 páginas | ejecución histórica 20/20; PDF revisado | matriz/evidencia AE1 | publicado en GitHub antes de este corte | Classroom/defensa no verificadas |
| U2 AE2 — comparación y transformación | Notebook, informe PDF/MD, diagrama; derivado equivalente sin cambio de valores | notebook ejecutado; 2,111×17, 0 nulos, 24 duplicados, hashes y query SQL de lectura PASS | `informe_ae2.md`, SQL y JSON AE2 | publicado en `main`; [notebook](https://github.com/DxRxXgSo/REC_ECBD_2026_Aguilar_Solis_David_Rafael/blob/main/notebooks/Aguilar_Solis_David_Rafael_U2_AE2_ETL.ipynb) y [PDF](https://github.com/DxRxXgSo/REC_ECBD_2026_Aguilar_Solis_David_Rafael/blob/main/docs/Aguilar_Solis_David_Rafael_U2_AE2_PreparacionDatos.pdf) verificados | Entrega 13/11 ya pasó; Classroom y aceptación no verificadas |
| U2 Data Mart | Staging, dimensión, hechos, claves y scripts existentes | consulta real observó 2,111 staging/hechos y siete clases; evidencia anterior documenta segunda carga idempotente | guía SQL, informe y diagrama | scripts y documentos AE2 publicados en `main` | No verificada |
| U3 regresión | Dummy, lineal y Random Forest; modelos guardados | tests U3 actuales 8/8 PASS; notebook consolidado ejecutado | informe MD/DOCX/PDF y métricas reales | [notebook](https://github.com/DxRxXgSo/REC_ECBD_2026_Aguilar_Solis_David_Rafael/blob/main/notebooks/Aguilar_Solis_David_Rafael_U3_AnalisisSupervisado.ipynb) y [PDF](https://github.com/DxRxXgSo/REC_ECBD_2026_Aguilar_Solis_David_Rafael/blob/main/docs/Aguilar_Solis_David_Rafael_U3_Informe.pdf) verificados en `main` | No verificada |
| U3 clasificación | Dummy/logística/RF en escenarios A/B, optimización y reportes base por clase | 8/8 tests; notebook de lectura ejecutado | métricas de CSV reales, informe y matrices base | entregables específicos verificados en `main` | No verificada |
| U4 selección/justificación | K-Means sobre 8 predictores escalados; sin etiqueta durante ajuste | tests 2/2; notebook ejecutado; k=2–9 comparados | SDD, informe, tablas, figuras y JSON | [notebook](https://github.com/DxRxXgSo/REC_ECBD_2026_Aguilar_Solis_David_Rafael/blob/main/notebooks/Aguilar_Solis_David_Rafael_U4_AnalisisNoSupervisado.ipynb) y [PDF](https://github.com/DxRxXgSo/REC_ECBD_2026_Aguilar_Solis_David_Rafael/blob/main/docs/Aguilar_Solis_David_Rafael_U4_Informe.pdf) verificados en `main` | Revisión académica pendiente; plazo 18/11 12:00 |
| U4 PCA e interpretación | PCA 2 componentes; etiqueta sólo post hoc | ejecución real, varianza PC1+PC2 41.31% | informe/notebook/evidencia | artefactos publicados en `main` | No verificada |
| U5 dashboard Power BI | PBIP original actualizado; cinco tablas cargadas y cuatro páginas con datos | Refresh Desktop: FactDashboard 2,111; dimensión 7; métricas 5; perfiles 9; PCA 2. Filtro dimensional 2,111→287→2,111. Suites 3/3,12/12,8/8,2/2. PBIR: 0 errores, 1 aviso de esquema no descargable | `dashboard/ECBD_Integrador_2026/`, capturas `dashboard/evidencias/final_powerbi_2026-11-16_validado/` y evidencia JSON | 5/5 componentes de alto nivel con datos; esta cuenta no equivale a aceptación de todos los subcriterios | Parcial: matrices base no están incrustadas, relación de clusters requiere prueba visual, PBIX no ofrecido por Desktop; revisión/entrega/aprobación pendientes |
| U5 informe final | Informe técnico actualizado con capturas y resultados U2–U4/U5 verificados | Fuentes y valores contrastados; límites del PBIP/PBIX y matrices reportados sin inferir cierre académico | `docs/Informe_Final_Borrador.md` y PDF asociado | PDF se registra después de renderizar/revisar todas las páginas | Classroom, defensa y aceptación docente no verificadas |
| U5 storytelling/defensa | Guion y preguntas preparadas | revisión interna solamente | `docs/cierre_2026/guion_defensa.md` | guion publicado en `main` | defensa individual no verificada |

## Evidencias actuales y límites

- Raw: SHA-256 esperado y confirmado antes/después: `28b6991062855d3d15642e38b1aa9d1b32fb7abbb5abf5b096f1868cd706154b`.
- Procesado: SHA-256 `64418dcf666d49d832d07fe53dbfd9415662f2537502fde60e8dbe55b8f5218d`.
- U3 optimizado: regresión RF test MAE 4.7501, RMSE 8.1428, R² 0.9005; clasificación A logística accuracy 0.9621/F1 macro 0.9615 y B RF accuracy 0.8697/F1 macro 0.8666. Fuente: `docs/unidad_iii/resultados/optimizacion_metricas_test.csv`; no son inferencias causales.
- U4: máximo Silhouette del rango probado 0.172636 en k=9 (límite superior); PCA dos componentes 41.31% acumulado; interpretación exploratoria.
- U3 tuvo un bloqueo `_sgd_fast` reportado anteriormente; en esta revisión no se reprodujo y las pruebas pasaron 8/8. No se desactivó seguridad.
- El notebook inicial `00_revision_inicial_dataset.ipynb` ya tenía una modificación local de usuario antes de la misión; se conserva sin staging ni commit.
- Se verificaron en GitHub los seis notebooks/PDF específicos AE2, U3 y U4; cada SHA de blob remoto coincide con `git hash-object` local. La publicación confirma disponibilidad en el repositorio, no entrega en Classroom ni aceptación docente.

## Verificación requisito a requisito de los programas de cierre

| Programa / producto exigido | Estado de avance al corte | Evidencia / pendiente concreto |
|---|---|---|
| U2 AE2: notebook `Apellido_Nombre_U2_AE2_ETL.ipynb` | Confirmado, ejecutado | Ruta local específica; 3 celdas de código, cero errores; actualiza evidencia tras consulta SQL de lectura. Classroom no verificado. |
| U2 AE2: PDF `Apellido_Nombre_U2_AE2_PreparacionDatos.pdf` | Confirmado, revisado | 4 páginas renderizadas/revisadas. |
| U2 AE2: datos procesados/limpios | Confirmado como equivalente validado | Raw vs procesado iguales por valores; sin limpieza sustantiva fingida; 24 duplicados preservados. |
| U2 AE2: comparación original/procesado y transformación justificada | Confirmado | Notebook, informe y manifiesto: serialización UTF-8/LF; cero exclusiones/recodificaciones/imputaciones. |
| U2 AE2: script SQL de Data Mart, dimensión, relaciones y medidas | Confirmado | `sql/01_create_datamart.sql`, `sql/02_load_datamart.sql`, diagrama Mermaid/PNG; PK/FK e inspección SQL real. |
| U2 AE2: verificación de carga y clases | Confirmado | Consulta real de sólo lectura: staging=2,111; hechos=2,111; categorías y conteos en JSON. Idempotencia proviene de evidencia previa; no se repitió escritura en este cierre. |
| U3: notebook con nombre específico | Confirmado, ejecutado | `notebooks/Aguilar_Solis_David_Rafael_U3_AnalisisSupervisado.ipynb`; lee resultados/modelos existentes, no reentrena. |
| U3: informe PDF con nombre específico | Confirmado, revisado | `docs/Aguilar_Solis_David_Rafael_U3_Informe.pdf`, 4 páginas; integra tablas y matriz base existente. |
| U3: regresión con MAE y métrica complementaria | Confirmado | MAE/RMSE/R² de test y RMSE CV en informe/notebook. |
| U3: clasificación accuracy, precision, recall, F1 y matriz de confusión | Confirmado | Métricas de test A/B optimizadas y matrices existentes de modelos base, claramente diferenciadas. |
| U3: optimización/interpretación, guardado de modelos, fuga | Confirmado | CSV de optimización, pipelines guardadas y tests U3 8/8; test no selecciona hiperparámetros. |
| U4: K-Means, variables justificadas y estandarización | Confirmado, ejecutado | Ocho predictores documentados; etiqueta excluida; StandardScaler. |
| U4: elección k, codo/Silhouette e interpretación | Parcial | Tabla/gráfica real k=2–9; máximo 0.172636 en k=9, límite del rango; decisión exploratoria requiere discusión humana/sensibilidad. |
| U4: PCA, varianza explicada y gráfica | Confirmado, ejecutado | PC1+PC2=41.3065%; PDF/notebook/figuras revisados. |
| U5: KPI y mínimo tres visualizaciones descriptivas en Power BI | No verificado | La página Panorama contiene definiciones de visuales, pero no se cargaron datos; los valores visibles están vacíos. 0/5 componentes funcionales. |
| U5: fuentes, relaciones, medidas e instrucciones de montaje | Parcial, definición creada | Cinco tablas, dos relaciones y medidas definidas en PBIP/TMDL; refresh SQL bloqueado, por tanto no verificados en ejecución. |
| U5: resultados de modelos y clustering/PCA integrados en dashboard | No verificado funcionalmente | Hay definiciones de página y fuentes esperadas; el modelo no confirmó datos ni coincidencia con salidas U3/U4 dentro de Power BI. |
| U5: storytelling, interpretación visible y limitaciones | Parcial, definiciones creadas | Existe página PBIR con textos y visuales previstos; revisión de contenido final, legibilidad e interacciones pendiente. |
| U5: informe final y preparación de presentación/defensa | Parcial | Borrador U1–U4 y guion existentes; cerrar la sección de dashboard tras validación; entrega y aceptación no verificadas. |

## Actualización técnica de Unidad V — 17/11/2026

> Esta actualización sustituye los estados iniciales de U5 registrados arriba; conserva las unidades previas sin cambios.

| Componente | Resultado observado | Estado y límite |
|---|---|---|
| Fuentes Power Query | FactDashboard 2,111; DimObesityLevel 7; ModelMetrics 5; ClusterProfile 9; PcaVariance 2 | Actualización real en Power BI Desktop 2.159.1231.0, autenticación integrada de Windows. |
| Integridad e interacción | 2,111 índices U4 únicos; 24 duplicados conservados. Filtro Normal_Weight: 2,111→287→2,111 | Relación de obesidad/hechos probada; interacción de perfil/cluster pendiente. |
| Páginas | Panorama, modelos, clustering/PCA y conclusiones muestran datos | Cinco componentes de alto nivel funcionales; matrices base aún no están incrustadas en la página 2. |
| Calidad | Tests dashboard 3/3, U2 12/12, U3 8/8, U4 2/2; SHA raw igual; PBIR 0 errores/1 aviso de esquema no descargable | La interfaz sólo ofreció PBIP y exportación de plantilla/PDF; no hay PBIX. El notebook inicial modificado sigue local y sin incluirse. |
| Informe y publicación | PDF técnico de seis páginas revisado y capturas finales reales en carpeta `final_powerbi_2026-11-16_validado` | Classroom, defensa y aprobación docente no verificadas. |
