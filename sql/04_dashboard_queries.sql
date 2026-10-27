/* Consultas descriptivas aptas como base para visualizaciones futuras. */
SELECT d.ObesityLevel, COUNT_BIG(*) AS records,
       AVG(f.Age) AS mean_age, AVG(f.Weight) AS mean_weight,
       AVG(f.FCVC) AS mean_vegetable_scale, AVG(f.FAF) AS mean_activity_scale
FROM DM.FactObesityObservation f
JOIN DM.DimObesityLevel d ON d.ObesityLevelKey = f.ObesityLevelKey
GROUP BY d.ObesityLevelKey, d.ObesityLevel
ORDER BY d.ObesityLevelKey;

SELECT d.ObesityLevel, f.MTRANS, COUNT_BIG(*) AS records
FROM DM.FactObesityObservation f
JOIN DM.DimObesityLevel d ON d.ObesityLevelKey = f.ObesityLevelKey
GROUP BY d.ObesityLevelKey, d.ObesityLevel, f.MTRANS
ORDER BY d.ObesityLevelKey, records DESC;
