# Guion breve de defensa individual

## Apertura (60–90 segundos)

“Mi proyecto analiza los hábitos alimenticios y la condición física asociados con niveles de obesidad usando el dataset UCI. Conservé el CSV original y documenté la preparación: 2,111 registros, 17 variables, cero faltantes y 24 filas duplicadas retenidas. En Unidad II preparé un Data Mart en SQL Server con staging, una dimensión de siete categorías y una tabla de hechos. En Unidad III comparé regresión para estimar Weight y clasificación de NObeyesdad con dos escenarios: uno que usa Height y Weight y otro que los excluye. El segundo evita depender directamente de medidas antropométricas y tiene desempeño menor en estos datos. En Unidad IV apliqué K-Means a variables estandarizadas sin usar la etiqueta para formar grupos y utilicé PCA para visualizar. Los resultados son exploratorios: el dataset tiene componente sintético, los duplicados se mantienen y ninguna asociación se interpreta como causal. El dashboard Power BI aún es un pendiente técnico en este entorno; no afirmo que esté terminado ni que las entregas hayan sido aceptadas.”

## Preguntas probables

**¿Por qué no eliminaste los 24 duplicados?** Para conservar todas las observaciones fuente y evitar una decisión de limpieza no justificada; en U3 agrupé duplicados al dividir datos para impedir contaminación entre train/test.

**¿Por qué el escenario A tiene mejores métricas?** Usa Height y Weight, relacionados estrechamente con la definición de la etiqueta; por eso existe riesgo de circularidad y no representa predicción independiente de antropometría.

**¿Qué significa el mejor k?** Dentro del rango k=2–9, k=9 tuvo el Silhouette máximo 0.1726; es modesto y coincide con el límite probado, por lo que no demuestra un número natural o definitivo de clusters.

**¿Qué representa PCA?** PC1 y PC2 explicaron 41.31% acumulado; la gráfica resume parcialmente ocho variables estandarizadas y pierde el resto de variación.

**¿El análisis prueba que un hábito cause obesidad?** No. Son asociaciones descriptivas/predictivas sobre este conjunto, con observaciones sintéticas y límites de generalización.

**¿Qué falta para cerrar?** Terminar y probar el dashboard en Power BI conforme a la guía; entregar manualmente en Classroom y obtener revisión/aceptación del docente.
