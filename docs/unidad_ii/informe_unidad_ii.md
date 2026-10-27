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

Los scripts diseñan `DM.DimObesityLevel`, staging y `DM.FactObesityObservation`, cuyo grano es un registro fuente; una clave sustituta conserva duplicados sin imponer unicidad falsa. La carga usa `BULK INSERT` CSV UTF-8, valida números y clase y reemplaza el contenido de la tabla de hechos dentro de una transacción. Se incluyen consultas de integridad y resúmenes descriptivos para el futuro dashboard.

La prueba de conexión con `sqlcmd` a `localhost` terminó con código 1 por falta de una instancia accesible. El diseño y los scripts se revisaron estáticamente; la creación/carga real y AC-II11 quedan **NO VERIFICADOS**. El servidor debe tener acceso de lectura al archivo y soportar la opción CSV de SQL Server 2017 o posterior.

## Reproducción

El entorno se fijó en `docs/unidad_ii/requirements.txt`. Desde la raíz del proyecto, con el entorno local activado:

```powershell
python -m unittest discover -s tests/unit_ii -v
python src/unit_ii.py
python src/execute_unit_ii_notebook.py
```

El entorno utilizado y sus versiones, comandos, hashes, conteos y resultados se registran en `docs/unidad_ii/evidencias/verificacion_unidad_ii.json`. Unidad I también se vuelve a probar; sus documentos y el notebook inicial no se editan.

La corrida registrada ejecutó 11 pruebas de Unidad II y 11 pruebas de Unidad I sin fallos; el verificador de Unidad I registró 19/19 PASS. El notebook ejecutó cinco celdas de código sin errores. La conexión local de SQL Server falló con código 1, por lo que creación y carga permanecen NO VERIFICADAS. La aprobación docente y la revisión académica independiente no se sustituyen por estos resultados técnicos.

## Limitaciones y conclusión

La proporción sintética reportada por los autores limita la generalización a personas y contextos no representados. Las respuestas de hábitos son observacionales y no permiten inferir causalidad. Duplicados exactos y muestras sintéticas requieren cuidado al separar datos en Unidad III. Los extremos estadísticos se conservaron; no se dispone de identificador que permita reconstruir qué filas fueron sintéticas. La Unidad II cuenta con análisis y preparación técnica reproducibles, pero la carga en SQL Server y la aprobación académica requieren validación independiente.

## Referencias

- UCI Machine Learning Repository. (2019). *Estimation of Obesity Levels Based On Eating Habits and Physical Condition*. Dataset 544. https://doi.org/10.24432/C5H31Z
- Mendoza Palechor, F., & de la Hoz Manotas, A. (2019). Dataset for estimation of obesity levels based on eating habits and physical condition in individuals from Colombia, Peru and Mexico. *Data in Brief, 25*, 104344. https://doi.org/10.1016/j.dib.2019.104344
