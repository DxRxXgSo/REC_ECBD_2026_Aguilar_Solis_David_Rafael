# Unidad II — AE2: preparación de datos y Data Mart

**Estudiante:** David Rafael Aguilar Solis · **Matrícula:** 22300607 · **Grupo:** 10IDGS-G1
**Proyecto:** Análisis de hábitos y condición física asociados con niveles de obesidad

## Procedencia y resultado de preparación

La fuente es el archivo UCI `data/raw/ObesityDataSet_raw_and_data_sinthetic.csv`. La salida validada es `data/processed/obesity_unit_ii.csv`. La ejecución previa del ETL y la comprobación fila a fila registran 2,111 filas, 17 columnas, cero exclusiones, cero valores faltantes y 24 duplicados exactos preservados. Los valores interpretados y el orden de columnas coinciden con el origen. La salida no representa una depuración sustantiva: la decisión fue no imputar, recodificar ni eliminar observaciones porque no había una justificación que autorizara cambiar el contenido. La diferencia de archivo es serialización UTF-8/LF, frente al CSV original con CRLF.

Las huellas verificadas durante esta revisión son raw `28b6991062855d3d15642e38b1aa9d1b32fb7abbb5abf5b096f1868cd706154b` y procesado `64418dcf666d49d832d07fe53dbfd9415662f2537502fde60e8dbe55b8f5218d`. No se alteró el archivo original.

## Flujo y Data Mart

El flujo existente documenta extracción, validación, preservación del multiconjunto de filas y carga a SQL Server Express. El Data Mart contiene `DM.StgObesityObservation`, `DM.DimObesityLevel` y `DM.FactObesityObservation`; la dimensión usa clave de categoría y los hechos conservan medidas y atributos de cada observación con llave foránea a la dimensión. El grano de hechos es una fila por observación, incluyendo repeticiones idénticas.

La evidencia de Unidad II ya registrada informa 2,111 filas en staging y hechos, siete categorías, cotejo con el conjunto procesado y segunda carga idempotente. En esta revisión el notebook de AE2 se ejecutó de forma real: leyó ambos CSV y consultó en modo de sólo lectura la instancia `SQLEXPRESS`; no volvió a ejecutar ETL ni DDL. El detalle está en `docs/actividad_u2_ae2/evidencia_validacion.json`. El diagrama se conserva en fuente Mermaid y PNG.

## Interpretación y límites

El dataset contiene registros sintéticos según la procedencia de UCI. Las asociaciones entre hábitos, condición física y etiqueta no son causales; conservar duplicados mantiene la evidencia, aunque las repeticiones pueden afectar análisis posteriores. La equivalencia del archivo procesado y la ejecución técnica no equivalen a entrega o aceptación docente. El notebook ejecutado es `notebooks/Aguilar_Solis_David_Rafael_U2_AE2_ETL.ipynb`.

## Reproducción

Desde la raíz, abrir y ejecutar el notebook con el entorno indicado por el proyecto. Las celdas sólo leen raw, processed, manifiesto y Data Mart. La consulta SQL requiere `sqlcmd`, autenticación integrada y una instancia local disponible. No se incluyen credenciales y el notebook no carga ni modifica filas.
