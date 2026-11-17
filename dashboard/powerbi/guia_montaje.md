# Guía de montaje Power BI — ECBD 2026

**Estado al 17/11/2026:** el PBIP existente se abrió, refrescó, guardó y volvió a abrir en Power BI Desktop 2.159.1231.0. Las cinco tablas cargaron y las cuatro páginas renderizan. La confianza del certificado se limitó al proceso de Desktop mediante `PBI_SQL_TRUSTED_SERVERS=localhost\SQLEXPRESS`, manteniendo cifrado y autenticación integrada. Véanse `../README.md` y `../evidencias/verificacion_powerbi_2026-11-16.json`. No se creó PBIX: la interfaz disponible sólo ofreció guardar PBIP y exportar plantilla/PDF.

## Abrir e importar las fuentes

1. Abrir en Power BI Desktop `dashboard/ECBD_Integrador_2026/ECBD_Integrador_2026.pbip`. El proyecto ya define consultas, tablas, relaciones, medidas y páginas; no recrearlas en paralelo.
2. Si se trabaja desde un PBIX en blanco como recuperación, crear las cinco consultas nombradas con los `.m` homónimos desde `queries/`. Cambiar `ProjectRoot` si cambia la ubicación del repositorio.
3. La consulta SQL es de sólo lectura y usa autenticación integrada. Si el certificado local no es confiable, configurar confianza limitada al host local `localhost\sqlexpress` y conservar cifrado; no aceptar la opción de conexión sin cifrado ni guardar credenciales.
4. Importar sólo `DM.DimObesityLevel` desde SQL. `FactDashboard` se construye desde CSV; no cargar también los hechos de SQL.
5. Confirmar las dos relaciones definidas en `model_relationships.md`, y que las tablas de métricas/PCA permanezcan desconectadas. Probar las medidas según `measures.dax`; una definición presente no prueba que calcule correctamente.

## Página 1 — Panorama general

- Cuatro tarjetas: `Observaciones`, `Categorias`, `Edad promedio`, `Peso promedio (kg)`.
- Barras: eje `DimObesityLevel[ObesityLevel]`, valor conteo de `FactDashboard[row_index]`; ordenar por recuento.
- Columnas/histogramas: edad, peso y estatura; si no existe visual histograma nativo, usar bins desde la interfaz y etiquetarlos.
- Barras/apiladas para `FAVC`, `FCVC`, `NCP`, `CAEC`, `CH2O`, `FAF`, `TUE`, `CALC`, `MTRANS`; usar segmentadores por categoría, género y transporte.
- Aclarar duplicados: 24 filas exactas se conservaron; la frecuencia cuenta observaciones del archivo.

## Página 2 — Modelos predictivos

- Matriz de métricas desde `ModelMetrics`: filas modelo, columnas MAE/RMSE/R² para regresión; accuracy/precision macro/recall macro/F1 macro para clasificación. Filtrar `task`, `scenario`, `model`; no promediar métricas entre candidatos.
- Gráfico comparativo: F1 macro por escenario y modelo; cada combinación corresponde a una fila fuente. Mostrar regresión en visual separado.
- Insertar `docs/unidad_iii/figuras/clasificacion_matrices_confusion_base.png` como imagen sólo si la ruta local se selecciona manualmente; rotular explícitamente “matrices de modelos base”. No presentar como matriz optimizada.
- Cuadro de advertencia visible: “Escenario A incluye Height y Weight, variables directamente relacionadas con la etiqueta antropométrica; su alto desempeño puede reflejar circularidad. Escenario B excluye ambas medidas y es una comparación exploratoria, no evidencia causal ni validación clínica.”

## Página 3 — Agrupamiento y PCA

- Columnas: conteo de `row_index` por `cluster`.
- Dispersión: X=`PC1`, Y=`PC2`, leyenda=`cluster`; detalle=`row_index`, transparencia moderada.
- Barras de `ClusterProfile` para comparar Age, Weight, Height y hábitos; usar selector de variable o visuales separados porque sus escalas difieren.
- Barras `PcaVariance[component]` con `explained_variance_ratio`; mostrar 22.65% PC1 y 18.66% PC2, 41.31% acumulado.
- Advertencia: Silhouette máxima original 0.172636 en k=9 para el rango 2–9, resultado modesto y en límite del rango. Diagnóstico adicional 2–12 encontró valores más altos en k=10/11; k=9 no es óptimo global demostrado. La comparación por semillas de k=9 produjo ARI 0.653–0.939; no afirmar estabilidad fuerte.

## Página 4 — Hallazgos y conclusiones

Usar tarjetas de texto y gráficos enlazados; mantener el lenguaje descriptivo. Al menos tres conclusiones sustentadas: (1) A supera B en los resultados U3, con cautela por circularidad; (2) la proyección PCA PC1+PC2 explica 41.31%; (3) Silhouette modesta y sensibilidad a k/semillas limitan la interpretación de clusters. Dos recomendaciones prudentes: analizar asociaciones con segmentación descriptiva sin inferencia causal; probar sensibilidad adicional y validar externamente antes de recomendaciones poblacionales.

Pie visible en esta página y, en forma breve, en todas: datos UCI con componente sintético; 24 duplicados preservados; asociaciones no causales; no existe validación poblacional/externa; resultados académicos no equivalen a recomendación clínica.

## Revisión y evidencia manual requerida

La actualización de las cinco consultas, las cuatro páginas y el filtro de `DimObesityLevel` ya se verificaron en Desktop. Antes del cierre, el estudiante debe revisar las capturas finales y completar el montaje/visualización de las matrices de confusión base si la guía lo exige en el propio dashboard. Revisar también la relación `ClusterProfile`–`FactDashboard`, reabrir el PBIP para comprobar persistencia y decidir si entrega PBIP o solicita una exportación PBIX por un flujo soportado. Entrega en Classroom y aprobación docente se registran por separado.
