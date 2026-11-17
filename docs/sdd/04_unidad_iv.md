# Especificación SDD — Unidad IV

## Propósito y alcance

Aplicar aprendizaje no supervisado descriptivo al conjunto validado de Unidad II mediante K-Means y PCA. Se excluye `NObeyesdad` de todas las matrices de ajuste; la etiqueta sólo puede cruzarse después para describir perfiles. No se interpretan clusters como subtipos clínicos ni como relaciones causales.

## Datos y diseño experimental

- Entrada: `data/processed/obesity_unit_ii.csv`; debe conservar 2,111 observaciones, 17 variables, cero faltantes y 24 duplicados exactos, con SHA-256 documentado por ejecución.
- Predictores numéricos: `Age`, `Height`, `Weight`, `FCVC`, `NCP`, `CH2O`, `FAF`, `TUE`. La selección debe justificarse como variables de edad, medidas físicas, alimentación e indicadores de actividad/uso; `NObeyesdad` queda fuera del ajuste.
- Escalado: `StandardScaler` aplicado al conjunto completo es admisible en este análisis descriptivo no supervisado y debe declararse; no se presenta como evaluación predictiva ni como estimación de generalización.
- K-Means: semilla fija, varias inicializaciones, búsqueda documentada de k con inercia/codo y Silhouette; revisar estabilidad e interpretación, sin asumir que el k de Silhouette es una verdad única.
- PCA: dos componentes con varianza explicada reportada; visualización coloreada por cluster y perfiles en variables originales.
- Conservar duplicados y explicar que tienen peso repetido; documentar el componente sintético del dataset y límites de generalización.

## Entregables previstos

- `notebooks/Aguilar_Solis_David_Rafael_U4_AnalisisNoSupervisado.ipynb`
- `src/unit_iv.py` y `tests/unit_iv/`
- asignaciones derivadas sólo en `data/processed/`
- tablas, figuras y evidencia en `docs/unidad_iv/`; modelos nuevos en `modelos/unidad_iv/`
- informe PDF específico y matriz de cumplimiento del cierre.

## Criterios de aceptación

| ID | Criterio | Evidencia |
|---|---|---|
| AC-IV01 | Contrato y procedencia de datos comprobados; raw intacto. | SHA, dimensiones y pruebas |
| AC-IV02 | Variables elegidas y estandarización justificadas. | Notebook e informe |
| AC-IV03 | K-Means reproduce resultados con semilla fija. | Código, tests y notebook ejecutado |
| AC-IV04 | k se compara mediante codo/inercia y Silhouette. | Tabla y gráfica reales |
| AC-IV05 | Perfiles numéricos/categóricos e interpretación prudente. | Tabla y análisis |
| AC-IV06 | PCA informa varianza explicada y visualización. | Tabla y figura |
| AC-IV07 | `NObeyesdad` no participa en ajuste; sólo resumen posterior. | Código inspeccionado y prueba |
| AC-IV08 | Evidencias y rutas son consistentes y ejecutables. | JSON, pruebas y revisión |
| AC-IV09 | Revisión visual de PDF separada de aceptación académica. | Render por página; docente pendiente |

## Resultado de ejecución — 16/11/2026

La ejecución real sobre el contrato de Unidad II terminó sin errores. `tests/unit_iv/` pasó 2/2; el notebook ejecutó sus 4 celdas de código. Se evaluó k=2…9; Silhouette máximo 0.172636 en k=9, que coincide con el límite superior, por lo que la selección permanece exploratoria. PC1=22.6486%, PC2=18.6579%, acumulado=41.3065%. Se generaron asignaciones derivadas en `data/processed`, tablas/figuras/evidencia en `docs/unidad_iv`, modelos en `modelos/unidad_iv` e informe PDF de 4 páginas renderizado y revisado. Vea `docs/unidad_iv/evidencias/verificacion_unidad_iv.json`.

## Pruebas y límites

Pruebas positivas: hash/esquema/conteo/duplicados, exclusión de etiqueta, reproducibilidad de k, consistencia de salidas y notebook completo. Revisar las figuras y todas las páginas del PDF. Las métricas de clustering son descriptivas; una Silhouette baja/modesta y la sensibilidad a variables/escalas deben reportarse, no ocultarse. La aprobación docente, pertinencia académica final y entrega en Classroom requieren verificación humana.
