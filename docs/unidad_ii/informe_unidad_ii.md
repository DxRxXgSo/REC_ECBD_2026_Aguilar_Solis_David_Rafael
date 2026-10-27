# Unidad II Análisis exploratorio y preparación de datos

- **Institución:** Universidad Tecnológica de Tula-Tepeji
- **Programa:** Tecnologías de la Información
- **Proyecto Integrador de Recursamiento 2026:** Extracción de Conocimiento en Bases de Datos
- **Estudiante:** David Rafael Aguilar Solis · **Matrícula:** 22300607 · **Grupo:** 10IDGS-G1
- **Docente:** pendiente de confirmación
- **Proyecto:** Análisis de hábitos y condición física asociados con niveles de obesidad

## Alcance y resultado

Este informe documenta el análisis descriptivo, la preparación conservadora y el diseño de Data Mart de Unidad II. El CSV fuente se leyó sin modificar. Se creó un derivado que conserva el esquema y todas las filas para análisis posteriores. La exploración no establece causas y los resultados no representan prevalencias poblacionales. La fecha de ejecución registrada es 27 de octubre de 2026; no se infiere que la revisión o entrega del 9/16 de octubre se haya realizado.

La guía asigna 15% a Unidad II, con revisión el 9 de octubre y entrega el 16 de octubre de 2026. Ambas fechas ya pasaron; este informe no afirma que esos hitos académicos se hayan cumplido.

## Fuente y calidad observada

La fuente es el dataset 544 del UCI Machine Learning Repository: 2,111 filas y 17 columnas (16 predictores y la clase `NObeyesdad`), descritas para personas de México, Perú y Colombia. UCI informa que el 23% fue recolectado mediante plataforma web y 77% generado sintéticamente con Weka/SMOTE. La lectura del archivo local encontró cero faltantes y 24 filas exactamente duplicadas. Los duplicados se conservaron porque no hay una llave para distinguir individuos ni evidencia que justifique borrarlos; en evaluación futura deberán permanecer en una sola partición para evitar contaminación.

La huella SHA-256 del archivo fuente se registra en `data/processed/unit_ii_manifest.json` y en la evidencia de ejecución. La lectura fue de sólo lectura; el ETL escribió exclusivamente bajo `data/processed/`.

## Exploración

La edad observada va de 14 a 61 años (media 24.31); estatura de 1.45 a 1.98 m (media 1.70); peso de 39 a 173 kg (media 86.59). La variable de clase contiene siete categorías: Obesity Type I (351), Obesity Type III (324), Obesity Type II (297), Overweight Level I (290), Overweight Level II (290), Normal Weight (287) e Insufficient Weight (272). Los conteos pertenecen a este conjunto, no a una población.

El análisis gráfico incluye conteos de clase, distribuciones numéricas y peso por clase. El diagrama de cajas muestra diferencias de peso entre etiquetas, pero la etiqueta se relaciona con medidas antropométricas; no es una relación predictiva independiente ni causal. Las tablas de frecuencias categóricas y el perfil completo se guardan como salidas del notebook `notebooks/01_exploracion_datos.ipynb`.

Una detección exploratoria por la regla 1.5×IQR marca candidatos en Age (168), Height (1), Weight (1) y NCP (579), y ninguno en FCVC, CH2O, FAF o TUE. NCP y varias escalas contienen fracciones y la muestra incluye datos sintéticos; estos conteos no prueban errores. No se eliminó ni recortó ningún valor.

## Diccionario y preparación

El diccionario de datos documenta las 17 columnas, significado, tipo inferido, categorías/rangos observados y limitaciones. Se preservan las fracciones observadas en FCVC, NCP, CH2O, FAF y TUE; redondearlas alteraría valores. La definición de `NObeyesdad` se mantiene como publicada por UCI.

El ETL de `src/unit_ii.py` verifica encabezados y orden, tipos numéricos, valores finitos, dominios categóricos, faltantes y número de registros. Serializa a UTF-8/LF, sin filtrar filas ni recodificar variables. Las 2,111 filas y 17 columnas se conservaron, incluyendo 24 duplicados; las lecturas de fuente y derivado coinciden exactamente en valores y tipos. La salida es determinista; el manifiesto incluye fecha real y por ello cambia entre ejecuciones.

No se ajustan imputadores, escaladores, codificadores, selección de variables ni balanceo en Unidad II. Esas operaciones deben ajustarse dentro de pipelines de entrenamiento en Unidad III.

## Data Mart SQL Server

Los scripts crean la base `REC_ECBD_Obesidad_2026`, el esquema `DM`, `DM.DimObesityLevel`, staging y `DM.FactObesityObservation`; el grano del hecho es una fila fuente y su clave sustituta conserva repeticiones sin imponer unicidad falsa. La conexión real se hizo por autenticación integrada a `LAPTOP-O1T564Q8\SQLEXPRESS`, SQL Server 2025 RTM 17.0.1000.7 Express, con `sysadmin=1`. La base quedó `ONLINE`; la dimensión contiene siete categorías y la clave foránea está habilitada y confiable. `@@SERVERNAME` devolvió NULL, aunque `SERVERPROPERTY('ServerName')` identificó la instancia; esto se conserva como advertencia de configuración del nombre local, no se modificó metadato del servidor.

La primera ejecución de `sql/02_load_datamart.sql` cargó 2,111 observaciones en staging y hechos. La segunda ejecución fue idempotente: detectó multiconjuntos iguales y no insertó de nuevo. Ambos conteos finales son 2,111 y se conservan las 24 repeticiones exactas. La aserción de `sql/05_assert_datamart.sql` pasó: 7 categorías, 0 faltantes requeridos, 0 hechos huérfanos, 0 filas numéricas inválidas y 17 variables de origen cotejadas. Los conteos y promedios por categoría de Age, Height, Weight, FCVC y FAF coincidieron con Pandas con tolerancias absolutas y relativas de 1e-10; las consultas descriptivas también cubren NCP, CH2O, TUE, transporte y hábitos.

La primera carga reveló que `TUE` y `FAF` contienen valores en notación científica, por ejemplo `7.3e-05` y `9.6e-05`; convertirlos a `decimal(12,6)` los volvía nulos y detenía la validación. Se corrigió la representación de medidas a `float`, compatible con los valores float64 del CSV y Pandas. La migración de un esquema previo se restringió a tablas vacías; no se alteró contenido poblado. SQL Server leyó el CSV procesado directamente mediante `BULK INSERT`; no se cambiaron permisos globales. La evidencia de conexión, comandos, códigos de salida, resultados y cotejo se conserva en `docs/unidad_ii/evidencias/verificacion_unidad_ii.json`.

La ejecución técnica de AC-II11 queda **PASS**: la revalidación actual confirmó conexión, esquema, conteos, siete categorías, integridad referencial, aserciones y coincidencia fila a fila con el CSV procesado. La primera y segunda carga reales registradas conservaron 2,111 observaciones y demostraron idempotencia. Esto no equivale a aprobación docente ni aceptación académica. La fecha de ejecución fue el 27 de octubre de 2026; no se afirma que las fechas oficiales de revisión o entrega ya transcurridas se hayan cumplido. La revalidación final fue de sólo lectura y no repitió la carga.

## Reproducción

El entorno se fijó en `docs/unidad_ii/requirements.txt`. Desde la raíz del proyecto, con el entorno local activado:

```powershell
python -m unittest discover -s tests/unit_ii -v
python src/unit_ii.py
python src/execute_unit_ii_notebook.py
python src/verify_unit_ii.py --sql-read-only
python src/verify_unit_ii.py --closure-read-only
python src/build_unit_ii_report.py
python src/build_unit_ii_pdf.py
```

El primer comando SQL de carga se ejecutó dos veces durante la carga real inicial. La opción `--sql-read-only` sólo consulta la instancia y no crea objetos ni vuelve a cargar filas. `--closure-read-only` ejecuta pruebas de regresión, el verificador de Unidad I y consultas SQL, sin correr ETL, cargas o notebooks. El DOCX se genera desde este Markdown con `python-docx`; el PDF se construye directamente desde el mismo Markdown con ReportLab 4.4.9, no se presenta como exportación de Word. Las versiones requeridas están en `docs/unidad_ii/requirements.txt`. El entorno utilizado y sus versiones, comandos, hashes, conteos y resultados se registran en `docs/unidad_ii/evidencias/verificacion_unidad_ii.json`. Unidad I también se vuelve a probar; sus documentos y el notebook inicial no se editan.

La corrida de cierre ejecutó 12 pruebas de Unidad I, 12 de Unidad II y 8 de Unidad III sin fallos; el verificador integral de Unidad I registró 19/19 PASS. En esta revalidación, el notebook se ejecutó en una copia temporal del proyecto con cinco celdas de código y generó las tres figuras; la copia temporal se descartó. Los hashes del notebook original, CSV raw y CSV procesado permanecieron idénticos. La revalidación SQL de sólo lectura terminó con código 0 y cotejó las 2,111 filas y sus 17 variables con el CSV procesado. La aprobación docente y la revisión académica independiente no se sustituyen por estos resultados técnicos.

## Limitaciones y conclusión

La proporción sintética reportada por los autores limita la generalización a personas y contextos no representados. Las respuestas de hábitos son observacionales y no permiten inferir causalidad. Duplicados exactos y muestras sintéticas requieren cuidado al separar datos en Unidad III. Los extremos estadísticos se conservaron; no se dispone de identificador que permita reconstruir qué filas fueron sintéticas. La carga y las consultas del Data Mart quedaron verificadas técnicamente en SQL Server; la aprobación docente y la aceptación académica requieren revisión independiente.

## Referencias

- UCI Machine Learning Repository. (2019). *Estimation of Obesity Levels Based On Eating Habits and Physical Condition*. Dataset 544. https://doi.org/10.24432/C5H31Z
- Mendoza Palechor, F., & de la Hoz Manotas, A. (2019). Dataset for estimation of obesity levels based on eating habits and physical condition in individuals from Colombia, Peru and Mexico. *Data in Brief, 25*, 104344. https://doi.org/10.1016/j.dib.2019.104344
