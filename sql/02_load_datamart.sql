/* Ejecutar con sqlcmd. Ajustar CsvPath al archivo local procesado. */
:setvar CsvPath "C:\Users\rafle\Documents\REC_ECBD_2026_Aguilar_Solis_David_Rafael\data\processed\obesity_unit_ii.csv"
USE [REC_ECBD_Obesidad_2026];
GO

/* La importación inicial es temporal para preservar staging/facts existentes hasta validar
   el archivo completo y comparar el contenido. */
SELECT TOP (0) * INTO #IncomingObesityObservation FROM DM.StgObesityObservation;
GO

BULK INSERT #IncomingObesityObservation
FROM '$(CsvPath)'
WITH (
    FIRSTROW = 2,
    FORMAT = 'CSV',
    FIELDQUOTE = '"',
    CODEPAGE = '65001',
    ROWTERMINATOR = '0x0a',
    TABLOCK
);
GO

IF NOT EXISTS (SELECT 1 FROM #IncomingObesityObservation)
    THROW 51000, 'La etapa quedó vacía; no se actualizará el hecho.', 1;

IF (SELECT COUNT_BIG(*) FROM #IncomingObesityObservation) <> 2111
    THROW 51002, 'El número de registros de staging no coincide con el archivo fuente validado (2111).', 1;

IF EXISTS (
    SELECT 1 FROM #IncomingObesityObservation
    WHERE Gender IS NULL OR Age IS NULL OR Height IS NULL OR Weight IS NULL
       OR family_history_with_overweight IS NULL OR FAVC IS NULL OR FCVC IS NULL OR NCP IS NULL
       OR CAEC IS NULL OR SMOKE IS NULL OR CH2O IS NULL OR SCC IS NULL OR FAF IS NULL
       OR TUE IS NULL OR CALC IS NULL OR MTRANS IS NULL OR NObeyesdad IS NULL
)
    THROW 51003, 'Hay celdas faltantes en staging.', 1;

IF EXISTS (
    SELECT 1 FROM #IncomingObesityObservation
    WHERE TRY_CONVERT(float, Age) IS NULL
       OR TRY_CONVERT(float, Height) IS NULL
       OR TRY_CONVERT(float, Weight) IS NULL
       OR TRY_CONVERT(float, FCVC) IS NULL
       OR TRY_CONVERT(float, NCP) IS NULL
       OR TRY_CONVERT(float, CH2O) IS NULL
       OR TRY_CONVERT(float, FAF) IS NULL
       OR TRY_CONVERT(float, TUE) IS NULL
       OR NOT EXISTS (SELECT 1 FROM DM.DimObesityLevel d WHERE d.ObesityLevel = NObeyesdad)
)
    THROW 51001, 'Hay valores numéricos o categorías inválidas en staging.', 1;
GO

SET XACT_ABORT ON;
/* Sólo inserta en staging si está vacía. Si ya existe, exige igualdad de multiconjuntos. */
IF EXISTS (SELECT 1 FROM DM.StgObesityObservation)
BEGIN
    IF EXISTS (
        SELECT Gender, Age, Height, Weight, family_history_with_overweight, FAVC, FCVC, NCP,
               CAEC, SMOKE, CH2O, SCC, FAF, TUE, CALC, MTRANS, NObeyesdad, COUNT_BIG(*) AS copies
        FROM #IncomingObesityObservation
        GROUP BY Gender, Age, Height, Weight, family_history_with_overweight, FAVC, FCVC, NCP,
                 CAEC, SMOKE, CH2O, SCC, FAF, TUE, CALC, MTRANS, NObeyesdad
        EXCEPT
        SELECT Gender, Age, Height, Weight, family_history_with_overweight, FAVC, FCVC, NCP,
               CAEC, SMOKE, CH2O, SCC, FAF, TUE, CALC, MTRANS, NObeyesdad, COUNT_BIG(*)
        FROM DM.StgObesityObservation
        GROUP BY Gender, Age, Height, Weight, family_history_with_overweight, FAVC, FCVC, NCP,
                 CAEC, SMOKE, CH2O, SCC, FAF, TUE, CALC, MTRANS, NObeyesdad
    ) OR EXISTS (
        SELECT Gender, Age, Height, Weight, family_history_with_overweight, FAVC, FCVC, NCP,
               CAEC, SMOKE, CH2O, SCC, FAF, TUE, CALC, MTRANS, NObeyesdad, COUNT_BIG(*) AS copies
        FROM DM.StgObesityObservation
        GROUP BY Gender, Age, Height, Weight, family_history_with_overweight, FAVC, FCVC, NCP,
                 CAEC, SMOKE, CH2O, SCC, FAF, TUE, CALC, MTRANS, NObeyesdad
        EXCEPT
        SELECT Gender, Age, Height, Weight, family_history_with_overweight, FAVC, FCVC, NCP,
               CAEC, SMOKE, CH2O, SCC, FAF, TUE, CALC, MTRANS, NObeyesdad, COUNT_BIG(*)
        FROM #IncomingObesityObservation
        GROUP BY Gender, Age, Height, Weight, family_history_with_overweight, FAVC, FCVC, NCP,
                 CAEC, SMOKE, CH2O, SCC, FAF, TUE, CALC, MTRANS, NObeyesdad
    )
        THROW 51005, 'Staging ya contiene datos distintos; se preservó sin cambios.', 1;
END
ELSE
BEGIN
    INSERT INTO DM.StgObesityObservation
    SELECT * FROM #IncomingObesityObservation;
END;

/* Construye una representación de frecuencias para preservar duplicados y poder reejecutar
   la carga sin borrar tablas de hechos existentes. */
SELECT s.Gender,
       TRY_CONVERT(float, s.Age) AS Age,
       TRY_CONVERT(float, s.Height) AS Height,
       TRY_CONVERT(float, s.Weight) AS Weight,
       s.family_history_with_overweight, s.FAVC,
       TRY_CONVERT(float, s.FCVC) AS FCVC,
       TRY_CONVERT(float, s.NCP) AS NCP,
       s.CAEC, s.SMOKE,
       TRY_CONVERT(float, s.CH2O) AS CH2O,
       s.SCC,
       TRY_CONVERT(float, s.FAF) AS FAF,
       TRY_CONVERT(float, s.TUE) AS TUE,
       s.CALC, s.MTRANS, d.ObesityLevelKey,
       COUNT_BIG(*) AS copies
INTO #SourceCounts
FROM #IncomingObesityObservation s
JOIN DM.DimObesityLevel d ON d.ObesityLevel = s.NObeyesdad
GROUP BY s.Gender, TRY_CONVERT(float, s.Age),
         TRY_CONVERT(float, s.Height), TRY_CONVERT(float, s.Weight),
         s.family_history_with_overweight, s.FAVC,
         TRY_CONVERT(float, s.FCVC), TRY_CONVERT(float, s.NCP),
         s.CAEC, s.SMOKE, TRY_CONVERT(float, s.CH2O), s.SCC,
         TRY_CONVERT(float, s.FAF), TRY_CONVERT(float, s.TUE),
         s.CALC, s.MTRANS, d.ObesityLevelKey;

IF EXISTS (SELECT 1 FROM DM.FactObesityObservation)
BEGIN
    IF EXISTS (
        SELECT Gender, Age, Height, Weight, family_history_with_overweight, FAVC, FCVC, NCP,
               CAEC, SMOKE, CH2O, SCC, FAF, TUE, CALC, MTRANS, ObesityLevelKey, copies
        FROM #SourceCounts
        EXCEPT
        SELECT Gender, Age, Height, Weight, family_history_with_overweight, FAVC, FCVC, NCP,
               CAEC, SMOKE, CH2O, SCC, FAF, TUE, CALC, MTRANS, ObesityLevelKey, COUNT_BIG(*)
        FROM DM.FactObesityObservation
        GROUP BY Gender, Age, Height, Weight, family_history_with_overweight, FAVC, FCVC, NCP,
                 CAEC, SMOKE, CH2O, SCC, FAF, TUE, CALC, MTRANS, ObesityLevelKey
    ) OR EXISTS (
        SELECT Gender, Age, Height, Weight, family_history_with_overweight, FAVC, FCVC, NCP,
               CAEC, SMOKE, CH2O, SCC, FAF, TUE, CALC, MTRANS, ObesityLevelKey, COUNT_BIG(*)
        FROM DM.FactObesityObservation
        GROUP BY Gender, Age, Height, Weight, family_history_with_overweight, FAVC, FCVC, NCP,
                 CAEC, SMOKE, CH2O, SCC, FAF, TUE, CALC, MTRANS, ObesityLevelKey
        EXCEPT
        SELECT Gender, Age, Height, Weight, family_history_with_overweight, FAVC, FCVC, NCP,
               CAEC, SMOKE, CH2O, SCC, FAF, TUE, CALC, MTRANS, ObesityLevelKey, copies
        FROM #SourceCounts
    )
        THROW 51004, 'La tabla de hechos ya contiene datos distintos; se preservó sin cambios.', 1;

    PRINT N'La tabla de hechos ya coincide con staging; no se modificó.';
END
ELSE
BEGIN
    BEGIN TRY
        BEGIN TRANSACTION;
        INSERT INTO DM.FactObesityObservation (
            Gender, Age, Height, Weight, family_history_with_overweight, FAVC, FCVC, NCP,
            CAEC, SMOKE, CH2O, SCC, FAF, TUE, CALC, MTRANS, ObesityLevelKey
        )
        SELECT s.Gender, TRY_CONVERT(float, s.Age), TRY_CONVERT(float, s.Height),
               TRY_CONVERT(float, s.Weight), s.family_history_with_overweight, s.FAVC,
               TRY_CONVERT(float, s.FCVC), TRY_CONVERT(float, s.NCP), s.CAEC,
               s.SMOKE, TRY_CONVERT(float, s.CH2O), s.SCC, TRY_CONVERT(float, s.FAF),
               TRY_CONVERT(float, s.TUE), s.CALC, s.MTRANS, d.ObesityLevelKey
        FROM #IncomingObesityObservation s
        JOIN DM.DimObesityLevel d ON d.ObesityLevel = s.NObeyesdad;
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF XACT_STATE() <> 0 ROLLBACK TRANSACTION;
        THROW;
    END CATCH;
END;
GO
