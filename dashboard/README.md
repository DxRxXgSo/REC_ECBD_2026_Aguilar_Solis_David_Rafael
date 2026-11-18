# Dashboard Power BI — Unidad V

**Corte de cierre: 18/11/2026.** Se abrió el PBIP existente en Power BI Desktop 2.159.1231.0, se actualizaron las cinco consultas, se aplicaron los cambios y se revisaron las cuatro páginas. No se creó ni sustituyó un PBIX. La conexión fue a `localhost\SQLEXPRESS` / `REC_ECBD_Obesidad_2026` con autenticación integrada de Windows. El error inicial fue de confianza del certificado local; se aplicó `PBI_SQL_TRUSTED_SERVERS=localhost\SQLEXPRESS` sólo al proceso de Desktop. La variable de usuario permanece vacía, no se desactivó el cifrado y no se guardaron credenciales. Microsoft documenta esta excepción limitada para certificados SQL locales autofirmados ([conector SQL Server de Power Query](https://learn.microsoft.com/en-us/power-query/connectors/sqlserver)).

## Fuentes actualizadas y comprobadas

Power Query cargó las cinco tablas sin errores visibles:

| Tabla | Filas cargadas / esperadas |
|---|---:|
| `FactDashboard` | 2,111 |
| `DimObesityLevel` | 7 |
| `ModelMetrics` | 5 |
| `ClusterProfile` | 9 |
| `PcaVariance` | 2 |

La unión U4 por `row_index` tiene 2,111 filas, índices únicos y asignaciones completas en los CSV fuente; el M de `FactDashboard` también impone el contrato de 2,111 filas y cero clusters nulos. Se conservaron las 24 filas exactas duplicadas. Los conteos de clases corresponden a los datos originales. El segmento `Normal_Weight` filtró los KPI a 287 filas y una categoría; al limpiarlo se restauraron 2,111 y siete categorías. Se probó además `ClusterProfile[cluster]=0`: la tabla de perfiles, el conteo de hechos y la dispersión quedaron limitados al cluster 0; el CSV de asignaciones confirma 246 observaciones en ese cluster. Al restaurar el rango completo reaparecieron los nueve grupos. Evidencia separada: `evidencias/cluster_interaction_2026-11-18.png`.

## Páginas y evidencia visual

Las cuatro páginas del PBIP existente muestran datos reales: Panorama general; Modelos supervisados; Clustering y PCA; Hallazgos y conclusiones. El PBIP se cerró, se reabrió y se volvió a actualizar; las cuatro capturas nuevas, exportadas después de reabrir y actualizar, están en [`evidencias/final_powerbi_2026-11-18/`](evidencias/final_powerbi_2026-11-18/). La página de modelos muestra regresión RF (MAE 4.7501, RMSE 8.1428, R² 0.9005), tabla de cuatro resultados de clasificación con cuatro decimales y F1 macro por escenario/modelo; así se evita promediar candidatos. La leyenda del escenario A advierte circularidad por `Height` y `Weight`. La página de clustering presenta nueve grupos, dispersión PC1/PC2 y varianza explicada acumulada de 41.31%, con la advertencia de Silhouette modesto y sensibilidad de k.

La página 2 ya integra la imagen existente de matrices de confusión. El encabezado de la figura identifica “Clasificación base”; por tanto, no se atribuye a los modelos optimizados de la tabla. La relación `ClusterProfile[cluster]` (1) → `FactDashboard[cluster]` (*) está activa y con filtro único; la propagación se probó interactivamente para cluster 0 y se guardó evidencia separada.

## Portabilidad de fuentes

El modelo PBIP declara parámetros Power Query editables `ProjectRoot`, `SqlInstance` y `SqlDatabase`, con valores predeterminados para este equipo (`C:\Users\rafle\Documents\REC_ECBD_2026_Aguilar_Solis_David_Rafael`, `localhost\SQLEXPRESS`, `REC_ECBD_Obesidad_2026`). En otro equipo, abrir **Transformar datos → Administrar parámetros**, actualizar esos tres valores y luego actualizar el modelo. Se requiere Power BI Desktop, acceso a los archivos del repositorio y SQL Server con la base y el esquema `DM` ya creados; las credenciales no se distribuyen ni se incluyen en el PBIP. Mantener cifrado de conexión y usar sólo autenticación autorizada en el equipo destino.

## Archivos y verificación

- Proyecto actual: [`ECBD_Integrador_2026/ECBD_Integrador_2026.pbip`](ECBD_Integrador_2026/ECBD_Integrador_2026.pbip). Se guardó en Desktop después de cargar datos y guardar el PBIR/TMDL actualizado.
- Parámetros PBIP: `ProjectRoot`, `SqlInstance`, `SqlDatabase`; defaults conservan las rutas y servidor usados al actualizar en Desktop.
- PBIX: no creado. En la interfaz, “Guardar como” sólo ofreció PBIP y “Exportar” ofreció plantilla o PDF; no se presentó una conversión PBIX disponible.
- Validación PBIR: cero errores; un aviso porque el CLI no pudo descargar el esquema visual 2.14.0. El esquema faltante de los archivos `.pbip` y `definition.pbir` se restauró después de guardar desde Desktop.
- Suites `unittest` de cierre: dashboard 3/3, U2 12/12, U3 8/8, U4 2/2 PASS; las 25 pruebas se ejecutaron de nuevo el 18/11/2026.
- SHA-256 de `data/raw/ObesityDataSet_raw_and_data_sinthetic.csv`, antes y después: `28b6991062855d3d15642e38b1aa9d1b32fb7abbb5abf5b096f1868cd706154b`.
- `git diff --check`: PASS; Git sólo avisó sobre normalización LF/CRLF en archivos Markdown.

Se consideran componentes funcionales el refresco de fuentes, panorama, modelos supervisados, clustering/PCA y hallazgos, sujetos a la revisión final y pruebas actuales. No se declara PBIX: el formato entregable del proyecto es PBIP. El dashboard no cambia datos originales ni modelos U2–U4. La entrega en Classroom, defensa y aceptación docente sólo se marcan con evidencia independiente.

## Paquete de entrega

El ZIP reproducible se ubica en `dashboard/entrega/ECBD_Entrega_Final_2026-11-20.zip`. Incluye el proyecto PBIP, sus CSV procesados/resultados requeridos, scripts SQL de referencia y sólo las cuatro capturas finales. Para actualizarlo en otro equipo se necesita Power BI Desktop, acceso a esos CSV y SQL Server con la base `REC_ECBD_Obesidad_2026` y esquema `DM`; configurar `ProjectRoot`, `SqlInstance` y `SqlDatabase`. No contiene credenciales ni caché local. La prueba temporal de propagación de cluster se conserva fuera del paquete.
