# Dashboard Power BI — Unidad V

**Corte técnico: 16/11/2026; reapertura verificada: 17/11/2026.** Se abrió, actualizó, guardó, cerró y reabrió el PBIP existente en Power BI Desktop 2.159.1231.0. La conexión fue a `localhost\SQLEXPRESS` / `REC_ECBD_Obesidad_2026` con autenticación integrada de Windows. El error inicial fue de confianza del certificado local; se aplicó `PBI_SQL_TRUSTED_SERVERS=localhost\SQLEXPRESS` sólo al proceso de Desktop. La variable de usuario permanece vacía, no se desactivó el cifrado y no se guardaron credenciales. Microsoft documenta esta excepción limitada para certificados SQL locales autofirmados ([conector SQL Server de Power Query](https://learn.microsoft.com/en-us/power-query/connectors/sqlserver)).

## Fuentes actualizadas y comprobadas

Power Query cargó las cinco tablas sin errores visibles:

| Tabla | Filas cargadas / esperadas |
|---|---:|
| `FactDashboard` | 2,111 |
| `DimObesityLevel` | 7 |
| `ModelMetrics` | 5 |
| `ClusterProfile` | 9 |
| `PcaVariance` | 2 |

La unión U4 por `row_index` tiene 2,111 filas, índices únicos y asignaciones completas en los CSV fuente; el M de `FactDashboard` también impone el contrato de 2,111 filas y cero clusters nulos. Se conservaron las 24 filas exactas duplicadas. Los conteos de clases corresponden a los datos originales. El segmento `Normal_Weight` filtró los KPI a 287 filas y una categoría; al limpiar el filtro se restauraron 2,111 y siete categorías. La relación de la dimensión de obesidad con la tabla de hechos queda probada por este filtro. La relación de perfiles de cluster no se probó mediante interacción.

## Páginas y evidencia visual

Las cuatro páginas del PBIP existente muestran datos reales: Panorama general; Modelos supervisados; Clustering y PCA; Hallazgos y conclusiones. El PBIP se cerró, se reabrió y se volvió a actualizar; las capturas verificadas están en [`evidencias/final_powerbi_2026-11-16_validado/`](evidencias/final_powerbi_2026-11-16_validado/). La página de modelos muestra regresión RF (MAE 4.7501, RMSE 8.1428, R² 0.9005), tabla de cuatro resultados de clasificación con cuatro decimales y F1 macro por escenario/modelo; así se evita promediar candidatos. La leyenda del escenario A advierte circularidad por `Height` y `Weight`. La página de clustering presenta nueve grupos, dispersión PC1/PC2 y varianza explicada acumulada de 41.31%, con la advertencia de Silhouette modesto y sensibilidad de k.

**Límite visible:** el dashboard menciona que las matrices de confusión disponibles corresponden a modelos base, pero no incrusta la imagen de esas matrices. No se atribuyen matrices base a los resultados optimizados. Requiere revisión antes de considerar esta subparte completa.

## Archivos y verificación

- Proyecto actual: [`ECBD_Integrador_2026/ECBD_Integrador_2026.pbip`](ECBD_Integrador_2026/ECBD_Integrador_2026.pbip). Se guardó en Desktop después de cargar datos y guardar el PBIR/TMDL actualizado.
- PBIX: no creado. En la interfaz, “Guardar como” sólo ofreció PBIP y “Exportar” ofreció plantilla o PDF; no se presentó una conversión PBIX disponible.
- Validación PBIR: cero errores; un aviso porque el CLI no pudo descargar el esquema visual 2.14.0. El esquema faltante de los archivos `.pbip` y `definition.pbir` se restauró después de guardar desde Desktop.
- Suites `unittest`: dashboard 3/3, U2 12/12, U3 8/8, U4 2/2 PASS.
- SHA-256 de `data/raw/ObesityDataSet_raw_and_data_sinthetic.csv`, antes y después: `28b6991062855d3d15642e38b1aa9d1b32fb7abbb5abf5b096f1868cd706154b`.
- `git diff --check`: PASS; Git sólo avisó sobre normalización LF/CRLF en archivos Markdown.

Se consideran funcionales cinco componentes de alto nivel: refresco de fuentes, panorama, modelos supervisados, clustering/PCA y hallazgos. Esto no equivale a aceptación académica ni cierre completo: faltan la matriz de confusión en la página, un PBIX exportable, cierre de revisión visual por el estudiante, entrega en Classroom y aprobación docente. No se realizaron cambios en datos originales ni modelos U2–U4.
