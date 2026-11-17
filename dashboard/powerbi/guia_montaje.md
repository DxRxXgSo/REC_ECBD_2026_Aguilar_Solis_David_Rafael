# Guía de montaje Power BI — ECBD 2026

**Estado:** paquete de importación y diseño listo para montar. No se creó ni probó un PBIX porque Power BI Desktop no está instalado/disponible en este entorno. No hay capturas ni páginas funcionales verificadas.

## Importar las fuentes

1. Abrir Power BI Desktop y elegir **Obtener datos > Consulta en blanco > Editor avanzado**.
2. Crear consultas nombradas `FactDashboard`, `DimObesityLevel`, `ModelMetrics`, `ClusterProfile` y `PcaVariance`, copiando el archivo `.m` homónimo desde `queries/`. Cambiar la raíz de proyecto en las cuatro consultas CSV si se mueve la carpeta. La consulta SQL usa autenticación Windows local.
3. Deshabilitar carga para consultas auxiliares sólo si se agregan; conservar las cinco tablas anteriores.
4. Configurar relaciones conforme a `model_relationships.md`; importar únicamente la dimensión desde SQL, no los hechos SQL.
5. Crear las medidas incluidas en `measures.dax`. Confirmar que las métricas filtren exactamente una fila y que `PcaVariance` use porcentaje decimal.

## Página 1 — Panorama general

- Cuatro tarjetas: `Observaciones`, `Categorias`, `Edad promedio`, `Peso promedio (kg)`.
- Barras: eje `DimObesityLevel[ObesityLevel]`, valor conteo de `FactDashboard[row_index]`; ordenar por recuento.
- Columnas/histogramas: edad, peso y estatura; si no existe visual histograma nativo, usar bins desde la interfaz y etiquetarlos.
- Barras/apiladas para `FAVC`, `FCVC`, `NCP`, `CAEC`, `CH2O`, `FAF`, `TUE`, `CALC`, `MTRANS`; usar segmentadores por categoría, género y transporte.
- Aclarar duplicados: 24 filas exactas se conservaron; la frecuencia cuenta observaciones del archivo.

## Página 2 — Modelos predictivos

- Matriz de métricas desde `ModelMetrics`: filas modelo, columnas MAE/RMSE/R² para regresión; accuracy/precision macro/recall macro/F1 macro para clasificación. Filtrar `task`, `scenario`, `model`; no mezclar escenarios.
- Gráfico comparativo A/B: columnas agrupadas para Accuracy y F1 macro con dos series por escenario y leyenda de modelo. Mostrar regresión en visual separado.
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

Al disponer de Power BI Desktop, guardar el PBIX en `dashboard/`, refrescar todas las consultas, comprobar 2,111 filas y 7 categorías, navegar cada página y revisar títulos, filtros, interacciones y legibilidad. Exportar capturas completas de las cuatro páginas a `dashboard/evidencias/` y registrar versión, fecha, PBIX y resultados de comprobación. Sólo entonces actualizar el avance funcional; fuentes y guía por sí solas no son componentes funcionales.
