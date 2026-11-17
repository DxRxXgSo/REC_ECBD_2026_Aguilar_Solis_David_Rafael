# Modelo de datos para Power BI

## Tablas y grano

- `FactDashboard`: CSV procesado de U2 más asignación U4 mediante `row_index` creado en orden físico de lectura. Una fila por observación fuente; no deduplicar. Las 24 observaciones idénticas se conservan como filas distintas.
- `DimObesityLevel`: lectura SQL de `DM.DimObesityLevel` (7 niveles), sólo dimensión. No importar también la tabla de hechos SQL para evitar contar dos veces las observaciones.
- `ModelMetrics`: 5 filas: una regresión y cuatro resultados de clasificación (A/B por dos modelos); cada fila es una combinación de tarea/escenario/modelo.
- `ClusterProfile`: una fila por cluster, medias en escala original.
- `PcaVariance`: PC1 y PC2 con cociente decimal y acumulado.

## Relaciones

1. `DimObesityLevel[ObesityLevel]` 1 → * `FactDashboard[NObeyesdad]`, dirección de filtro única desde dimensión.
2. `ClusterProfile[cluster]` 1 → * `FactDashboard[cluster]`, dirección de filtro única. Confirmar unicidad de las 9 filas de perfil antes de aplicar.
3. `ModelMetrics` y `PcaVariance` desconectadas: se filtran por sus columnas categóricas/componente dentro de cada visual. No crear relaciones artificiales.

## Tipos y seguridad

`row_index`, `cluster`, `ObesityLevelKey` enteros; `PC1`, `PC2`, métricas y variables numéricas como decimal; variables categóricas como texto. Conectar SQL Server como `localhost\SQLEXPRESS` / `REC_ECBD_Obesidad_2026` usando autenticación de Windows. La consulta selecciona exclusivamente la dimensión; no escribe en la base. La ruta local de Power Query es específica de este equipo y se debe cambiar si se mueve el repositorio.

Las fórmulas de `measures.dax` se deben crear como medidas, no columnas calculadas. Aplicar filtro por `task`, `scenario` y `model` para mostrar cada valor de U3; no promediar métricas entre modelos. En las matrices de confusión existentes, señalar que son de modelos base y no atribuirlas a las filas optimizadas.
