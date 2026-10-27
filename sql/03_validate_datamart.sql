/* Ejecutar después de la carga; las consultas son sólo lectura. */
USE [REC_ECBD_Obesidad_2026];
GO

SELECT DB_NAME() AS database_name;
SELECT COUNT_BIG(*) AS dimension_count FROM DM.DimObesityLevel;
SELECT COUNT_BIG(*) AS staging_observation_count FROM DM.StgObesityObservation;
SELECT COUNT_BIG(*) AS observation_count FROM DM.FactObesityObservation;
SELECT COALESCE(SUM(copies - 1), 0) AS duplicate_source_rows_preserved
FROM (
    SELECT COUNT_BIG(*) AS copies
    FROM DM.StgObesityObservation
    GROUP BY Gender, Age, Height, Weight, family_history_with_overweight, FAVC,
             FCVC, NCP, CAEC, SMOKE, CH2O, SCC, FAF, TUE, CALC, MTRANS, NObeyesdad
    HAVING COUNT_BIG(*) > 1
) AS duplicate_groups;
SELECT d.ObesityLevel, COUNT_BIG(*) AS observation_count
FROM DM.FactObesityObservation f
JOIN DM.DimObesityLevel d ON d.ObesityLevelKey = f.ObesityLevelKey
GROUP BY d.ObesityLevelKey, d.ObesityLevel
ORDER BY d.ObesityLevelKey;
SELECT COUNT_BIG(*) AS missing_required_fields
FROM DM.FactObesityObservation
WHERE Gender IS NULL OR Age IS NULL OR Height IS NULL OR Weight IS NULL OR ObesityLevelKey IS NULL;
SELECT COUNT_BIG(*) AS orphaned_fact_rows
FROM DM.FactObesityObservation f
LEFT JOIN DM.DimObesityLevel d ON d.ObesityLevelKey = f.ObesityLevelKey
WHERE d.ObesityLevelKey IS NULL;
SELECT COUNT_BIG(*) AS invalid_numeric_rows
FROM DM.FactObesityObservation
WHERE Age <= 0 OR Height <= 0 OR Weight <= 0
   OR FCVC < 0 OR NCP < 0 OR CH2O < 0 OR FAF < 0 OR TUE < 0;
GO
GO
