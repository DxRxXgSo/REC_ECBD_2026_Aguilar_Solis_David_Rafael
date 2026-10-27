/* Ejecutar con sqlcmd. Ajustar CsvPath al archivo local procesado. */
:setvar CsvPath "C:\Users\rafle\Documents\REC_ECBD_2026_Aguilar_Solis_David_Rafael\data\processed\obesity_unit_ii.csv"
TRUNCATE TABLE DM.StgObesityObservation;
GO

BULK INSERT DM.StgObesityObservation
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

IF NOT EXISTS (SELECT 1 FROM DM.StgObesityObservation)
    THROW 51000, 'La etapa quedó vacía; no se actualizará el hecho.', 1;

IF (SELECT COUNT_BIG(*) FROM DM.StgObesityObservation) <> 2111
    THROW 51002, 'El número de registros de staging no coincide con el archivo fuente validado (2111).', 1;

IF EXISTS (
    SELECT 1 FROM DM.StgObesityObservation
    WHERE Gender IS NULL OR Age IS NULL OR Height IS NULL OR Weight IS NULL
       OR family_history_with_overweight IS NULL OR FAVC IS NULL OR FCVC IS NULL OR NCP IS NULL
       OR CAEC IS NULL OR SMOKE IS NULL OR CH2O IS NULL OR SCC IS NULL OR FAF IS NULL
       OR TUE IS NULL OR CALC IS NULL OR MTRANS IS NULL OR NObeyesdad IS NULL
)
    THROW 51003, 'Hay celdas faltantes en staging.', 1;

IF EXISTS (
    SELECT 1 FROM DM.StgObesityObservation
    WHERE TRY_CONVERT(decimal(12,6), Age) IS NULL
       OR TRY_CONVERT(decimal(12,6), Height) IS NULL
       OR TRY_CONVERT(decimal(12,6), Weight) IS NULL
       OR TRY_CONVERT(decimal(12,6), FCVC) IS NULL
       OR TRY_CONVERT(decimal(12,6), NCP) IS NULL
       OR TRY_CONVERT(decimal(12,6), CH2O) IS NULL
       OR TRY_CONVERT(decimal(12,6), FAF) IS NULL
       OR TRY_CONVERT(decimal(12,6), TUE) IS NULL
       OR NOT EXISTS (SELECT 1 FROM DM.DimObesityLevel d WHERE d.ObesityLevel = NObeyesdad)
)
    THROW 51001, 'Hay valores numéricos o categorías inválidas en staging.', 1;
GO

SET XACT_ABORT ON;
BEGIN TRY
    BEGIN TRANSACTION;
    DELETE FROM DM.FactObesityObservation;
    INSERT INTO DM.FactObesityObservation (
        Gender, Age, Height, Weight, family_history_with_overweight, FAVC, FCVC, NCP,
        CAEC, SMOKE, CH2O, SCC, FAF, TUE, CALC, MTRANS, ObesityLevelKey
    )
    SELECT s.Gender, TRY_CONVERT(decimal(12,6), s.Age), TRY_CONVERT(decimal(12,6), s.Height),
           TRY_CONVERT(decimal(12,6), s.Weight), s.family_history_with_overweight, s.FAVC,
           TRY_CONVERT(decimal(12,6), s.FCVC), TRY_CONVERT(decimal(12,6), s.NCP), s.CAEC,
           s.SMOKE, TRY_CONVERT(decimal(12,6), s.CH2O), s.SCC, TRY_CONVERT(decimal(12,6), s.FAF),
           TRY_CONVERT(decimal(12,6), s.TUE), s.CALC, s.MTRANS, d.ObesityLevelKey
    FROM DM.StgObesityObservation s
    JOIN DM.DimObesityLevel d ON d.ObesityLevel = s.NObeyesdad;
    COMMIT TRANSACTION;
END TRY
BEGIN CATCH
    IF XACT_STATE() <> 0 ROLLBACK TRANSACTION;
    THROW;
END CATCH;
GO
