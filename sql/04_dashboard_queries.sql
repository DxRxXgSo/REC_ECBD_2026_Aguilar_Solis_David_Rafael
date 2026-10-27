/* Consultas descriptivas aptas como base para visualizaciones futuras. */
USE [REC_ECBD_Obesidad_2026];
GO

SELECT d.ObesityLevel, COUNT_BIG(*) AS records,
       AVG(f.Age) AS mean_age, AVG(f.Height) AS mean_height, AVG(f.Weight) AS mean_weight,
       AVG(f.FCVC) AS mean_vegetable_scale, AVG(f.NCP) AS mean_meals_per_day,
       AVG(f.CH2O) AS mean_water_scale, AVG(f.FAF) AS mean_activity_scale,
       AVG(f.TUE) AS mean_technology_use_scale
FROM DM.FactObesityObservation f
JOIN DM.DimObesityLevel d ON d.ObesityLevelKey = f.ObesityLevelKey
GROUP BY d.ObesityLevelKey, d.ObesityLevel
ORDER BY d.ObesityLevelKey;

SELECT d.ObesityLevel, f.MTRANS, COUNT_BIG(*) AS records
FROM DM.FactObesityObservation f
JOIN DM.DimObesityLevel d ON d.ObesityLevelKey = f.ObesityLevelKey
GROUP BY d.ObesityLevelKey, d.ObesityLevel, f.MTRANS
ORDER BY d.ObesityLevelKey, records DESC;

SELECT d.ObesityLevel, habits.habit_name, habits.habit_value, COUNT_BIG(*) AS records
FROM DM.FactObesityObservation f
JOIN DM.DimObesityLevel d ON d.ObesityLevelKey = f.ObesityLevelKey
CROSS APPLY (VALUES
    ('FAVC', f.FAVC), ('CAEC', f.CAEC), ('SMOKE', f.SMOKE),
    ('SCC', f.SCC), ('CALC', f.CALC)
) AS habits(habit_name, habit_value)
GROUP BY d.ObesityLevelKey, d.ObesityLevel, habits.habit_name, habits.habit_value
ORDER BY d.ObesityLevelKey, habits.habit_name, records DESC;
GO
