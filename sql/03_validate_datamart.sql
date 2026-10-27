/* Ejecutar después de la carga; las consultas son sólo lectura. */
SELECT COUNT_BIG(*) AS observation_count FROM DM.FactObesityObservation;
SELECT d.ObesityLevel, COUNT_BIG(*) AS observation_count
FROM DM.FactObesityObservation f
JOIN DM.DimObesityLevel d ON d.ObesityLevelKey = f.ObesityLevelKey
GROUP BY d.ObesityLevelKey, d.ObesityLevel
ORDER BY d.ObesityLevelKey;
SELECT COUNT_BIG(*) AS missing_required_fields
FROM DM.FactObesityObservation
WHERE Gender IS NULL OR Age IS NULL OR Height IS NULL OR Weight IS NULL OR ObesityLevelKey IS NULL;
GO
