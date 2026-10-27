# Guía de ejecución del Data Mart en SQL Server

Esta guía describe la secuencia reproducible para la base dedicada `REC_ECBD_Obesidad_2026`. Los scripts no abren puertos ni habilitan autenticación SQL; se usa autenticación integrada de Windows. La carga recibe exclusivamente `data/processed/obesity_unit_ii.csv`.

## Requisitos

- SQL Server 2017 o posterior (por la opción `FORMAT = 'CSV'` de `BULK INSERT`).
- Herramienta `sqlcmd` y acceso al motor con la cuenta de Windows.
- El archivo procesado validado en la ruta del parámetro `CsvPath`.
- La cuenta de servicio del motor debe poder leer ese archivo. Si no puede, solicitar al administrador una concesión de lectura limitada a ese archivo y directorio; no cambiar permisos globales.

Compruebe primero la instancia y la base existentes. No ejecute una carga hasta revisar cualquier contenido previo de `DM.StgObesityObservation` y `DM.FactObesityObservation`.

```powershell
Get-Service 'MSSQL$SQLEXPRESS'
# Si está detenida, iníciela desde SQL Server Configuration Manager o Servicios de Windows.
# Iniciar el servicio puede requerir elevación administrativa.
sqlcmd -S .\SQLEXPRESS -E -b -Q "SELECT @@VERSION AS version, @@SERVERNAME AS server_name, DB_NAME() AS current_database;"
sqlcmd -S .\SQLEXPRESS -E -b -Q "SELECT name FROM sys.databases WHERE name = N'REC_ECBD_Obesidad_2026';"
```

## Crear esquema y cargar

Desde la raíz del repositorio, en PowerShell:

```powershell
sqlcmd -S .\SQLEXPRESS -E -b -i .\sql\00_create_database.sql
sqlcmd -S .\SQLEXPRESS -E -b -d REC_ECBD_Obesidad_2026 -i .\sql\01_create_datamart.sql
sqlcmd -S .\SQLEXPRESS -E -b -d REC_ECBD_Obesidad_2026 -i .\sql\02_load_datamart.sql
sqlcmd -S .\SQLEXPRESS -E -b -d REC_ECBD_Obesidad_2026 -i .\sql\02_load_datamart.sql
sqlcmd -S .\SQLEXPRESS -E -b -d REC_ECBD_Obesidad_2026 -i .\sql\03_validate_datamart.sql
sqlcmd -S .\SQLEXPRESS -E -b -d REC_ECBD_Obesidad_2026 -i .\sql\04_dashboard_queries.sql
sqlcmd -S .\SQLEXPRESS -E -b -d REC_ECBD_Obesidad_2026 -i .\sql\05_assert_datamart.sql
```

`00_create_database.sql` conserva una base ya existente. La carga importa primero a una tabla temporal, valida los registros y preserva las tablas permanentes si ya contienen datos. Si staging o hechos difieren del archivo, el script se detiene con error en vez de reemplazarlos. La repetición de una carga idéntica debe dejar los conteos sin cambios.

## Consultas descriptivas

`04_dashboard_queries.sql` devuelve promedios por categoría y distribuciones de hábitos, actividad y transporte. `03_validate_datamart.sql` informa conteos, duplicados, nulos, huérfanos y filas numéricas inválidas. `05_assert_datamart.sql` termina con una fila `PASS` sólo cuando se cumplen las invariantes del proyecto.

## Resultado ejecutado el 27 de octubre de 2026

La conexión integrada a `.\SQLEXPRESS` fue exitosa en SQL Server 2025 RTM 17.0.1000.7 Express. Se verificaron `sysadmin=1`, bases internas `ONLINE`, base del proyecto `ONLINE`, siete filas de dimensión y la relación de hechos. La primera carga ingresó 2,111 filas en staging y 2,111 en hechos. La segunda carga no insertó registros adicionales; el total permaneció en 2,111 y se conservaron 24 repeticiones exactas. Aserciones: 0 faltantes requeridos, 0 huérfanos, 0 errores numéricos y siete categorías. Los promedios de edad, estatura, peso, FCVC y FAF por categoría coincidieron con Pandas dentro de 1e-10.

La conversión inicial decimal rechazó valores de FCVC/FAF/TUE escritos en notación científica; las columnas numéricas del hecho usan ahora `float` y la carga `TRY_CONVERT(float, ...)`. Esta corrección se probó con el conjunto real; conserva la precisión de las columnas float64 del CSV. La consulta de instancia dio `@@SERVERNAME = NULL`, aunque `SERVERPROPERTY('ServerName')` resolvió `LAPTOP-O1T564Q8\SQLEXPRESS`; queda como advertencia local. Los comandos y resultados observados, incluidos códigos de salida, están en `evidencias/verificacion_unidad_ii.json`.

Si una base existente no coincide con el CSV, conserve sus datos y documente el bloqueo; no la elimine ni la sobrescriba. La carga SQL no sustituye la aprobación docente.


## Revalidación final de sólo lectura

La revalidación de AC-II11 se ejecuta con `python src/verify_unit_ii.py --sql-read-only` desde el entorno del proyecto. Consulta la instancia y el esquema, ejecuta únicamente `03_validate_datamart.sql`, `04_dashboard_queries.sql` y `05_assert_datamart.sql`, y compara todas las filas SQL con `data/processed/obesity_unit_ii.csv`. No crea objetos ni vuelve a cargar datos. La evidencia registra fecha, comando, identidad de la instancia, códigos de salida y el cotejo de 2,111 observaciones. La consulta actual confirma `SERVERPROPERTY('ServerName')`; `@@SERVERNAME = NULL` queda documentado como discrepancia local que no afecta la conexión ni las validaciones.
