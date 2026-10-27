/* Asserts the persisted mart against the validated Unit II contract; read-only. */
USE [REC_ECBD_Obesidad_2026];
GO
SET NOCOUNT ON;

DECLARE @dimension_count bigint = (SELECT COUNT_BIG(*) FROM DM.DimObesityLevel);
DECLARE @staging_count bigint = (SELECT COUNT_BIG(*) FROM DM.StgObesityObservation);
DECLARE @fact_count bigint = (SELECT COUNT_BIG(*) FROM DM.FactObesityObservation);
DECLARE @duplicate_excess bigint = (
    SELECT COALESCE(SUM(copies - 1), 0)
    FROM (
        SELECT COUNT_BIG(*) AS copies
        FROM DM.StgObesityObservation
        GROUP BY Gender, Age, Height, Weight, family_history_with_overweight, FAVC,
                 FCVC, NCP, CAEC, SMOKE, CH2O, SCC, FAF, TUE, CALC, MTRANS, NObeyesdad
        HAVING COUNT_BIG(*) > 1
    ) AS duplicate_groups
);
DECLARE @missing_count bigint = (
    SELECT COUNT_BIG(*) FROM DM.FactObesityObservation
    WHERE Gender IS NULL OR Age IS NULL OR Height IS NULL OR Weight IS NULL
       OR family_history_with_overweight IS NULL OR FAVC IS NULL OR FCVC IS NULL OR NCP IS NULL
       OR CAEC IS NULL OR SMOKE IS NULL OR CH2O IS NULL OR SCC IS NULL OR FAF IS NULL
       OR TUE IS NULL OR CALC IS NULL OR MTRANS IS NULL OR ObesityLevelKey IS NULL
);
DECLARE @orphan_count bigint = (
    SELECT COUNT_BIG(*)
    FROM DM.FactObesityObservation f
    LEFT JOIN DM.DimObesityLevel d ON d.ObesityLevelKey = f.ObesityLevelKey
    WHERE d.ObesityLevelKey IS NULL
);
DECLARE @invalid_numeric_count bigint = (
    SELECT COUNT_BIG(*) FROM DM.FactObesityObservation
    WHERE Age <= 0 OR Height <= 0 OR Weight <= 0
       OR FCVC < 0 OR NCP < 0 OR CH2O < 0 OR FAF < 0 OR TUE < 0
);
DECLARE @fact_class_count bigint = (
    SELECT COUNT_BIG(DISTINCT f.ObesityLevelKey) FROM DM.FactObesityObservation f
);
DECLARE @staging_variable_count bigint = (
    SELECT COUNT_BIG(*) FROM sys.columns
    WHERE object_id = OBJECT_ID(N'DM.StgObesityObservation')
);
DECLARE @fact_variable_count bigint = (
    SELECT COUNT_BIG(*) - 1 FROM sys.columns
    WHERE object_id = OBJECT_ID(N'DM.FactObesityObservation')
);

IF @dimension_count <> 7 THROW 51100, 'Dimensión debe contener siete categorías.', 1;
IF @staging_count <> 2111 THROW 51101, 'Staging no contiene 2,111 filas.', 1;
IF @fact_count <> 2111 THROW 51102, 'Hechos no contiene 2,111 filas.', 1;
IF @duplicate_excess <> 24 THROW 51103, 'El número de duplicados preservados no coincide.', 1;
IF @missing_count <> 0 THROW 51104, 'Hechos contiene valores NULL inesperados.', 1;
IF @orphan_count <> 0 THROW 51105, 'Hechos contiene referencias huérfanas.', 1;
IF @invalid_numeric_count <> 0 THROW 51106, 'Hechos contiene valores numéricos no válidos.', 1;
IF @fact_class_count <> 7 THROW 51107, 'Hechos no representa las siete categorías.', 1;
IF @staging_variable_count <> 17 OR @fact_variable_count <> 17
    THROW 51108, 'El número de variables del Data Mart no coincide con el modelo.', 1;

SELECT N'PASS' AS validation_status, DB_NAME() AS database_name,
       @dimension_count AS dimensions, @staging_count AS staging_rows,
       @fact_count AS fact_rows, @duplicate_excess AS duplicate_rows_preserved,
       @fact_class_count AS fact_categories, @missing_count AS missing_values,
       @orphan_count AS orphaned_rows, @invalid_numeric_count AS invalid_numeric_rows,
       @staging_variable_count AS staging_variables, @fact_variable_count AS fact_variables;
GO
