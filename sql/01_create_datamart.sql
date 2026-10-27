/* Data Mart de Unidad II. Requiere SQL Server 2017+ para FORMAT='CSV'. */
USE [REC_ECBD_Obesidad_2026];
GO

IF SCHEMA_ID(N'DM') IS NULL EXEC(N'CREATE SCHEMA DM');
GO

IF OBJECT_ID(N'DM.DimObesityLevel', N'U') IS NULL
BEGIN
    CREATE TABLE DM.DimObesityLevel (
        ObesityLevelKey tinyint NOT NULL CONSTRAINT PK_DimObesityLevel PRIMARY KEY,
        ObesityLevel varchar(40) NOT NULL CONSTRAINT UQ_DimObesityLevel_Name UNIQUE
    );
END;
GO

IF OBJECT_ID(N'DM.StgObesityObservation', N'U') IS NULL
BEGIN
    CREATE TABLE DM.StgObesityObservation (
        Gender varchar(20) NULL,
        Age varchar(40) NULL,
        Height varchar(40) NULL,
        Weight varchar(40) NULL,
        family_history_with_overweight varchar(10) NULL,
        FAVC varchar(10) NULL,
        FCVC varchar(40) NULL,
        NCP varchar(40) NULL,
        CAEC varchar(20) NULL,
        SMOKE varchar(10) NULL,
        CH2O varchar(40) NULL,
        SCC varchar(10) NULL,
        FAF varchar(40) NULL,
        TUE varchar(40) NULL,
        CALC varchar(20) NULL,
        MTRANS varchar(40) NULL,
        NObeyesdad varchar(40) NULL
    );
END;
GO

IF OBJECT_ID(N'DM.FactObesityObservation', N'U') IS NULL
BEGIN
    CREATE TABLE DM.FactObesityObservation (
        ObservationKey bigint IDENTITY(1,1) NOT NULL CONSTRAINT PK_FactObesityObservation PRIMARY KEY,
        Gender varchar(20) NOT NULL,
        Age float NOT NULL,
        Height float NOT NULL,
        Weight float NOT NULL,
        family_history_with_overweight varchar(10) NOT NULL,
        FAVC varchar(10) NOT NULL,
        FCVC float NOT NULL,
        NCP float NOT NULL,
        CAEC varchar(20) NOT NULL,
        SMOKE varchar(10) NOT NULL,
        CH2O float NOT NULL,
        SCC varchar(10) NOT NULL,
        FAF float NOT NULL,
        TUE float NOT NULL,
        CALC varchar(20) NOT NULL,
        MTRANS varchar(40) NOT NULL,
        ObesityLevelKey tinyint NOT NULL,
        CONSTRAINT FK_FactObesityObservation_DimObesityLevel
            FOREIGN KEY (ObesityLevelKey) REFERENCES DM.DimObesityLevel(ObesityLevelKey)
    );
END;
GO

/* Migración segura desde la primera DDL decimal: sólo permite cambiar tipos si ambas
   tablas analíticas siguen vacías; nunca redondea datos ya cargados. */
IF EXISTS (
    SELECT 1 FROM sys.columns
    WHERE object_id = OBJECT_ID(N'DM.FactObesityObservation')
      AND name IN (N'Age',N'Height',N'Weight',N'FCVC',N'NCP',N'CH2O',N'FAF',N'TUE')
      AND system_type_id IN (106,108)
)
BEGIN
    IF EXISTS (SELECT 1 FROM DM.FactObesityObservation)
       OR EXISTS (SELECT 1 FROM DM.StgObesityObservation)
        THROW 51010, 'No se cambia la precisión con tablas pobladas; requiere revisión manual.', 1;

    ALTER TABLE DM.FactObesityObservation ALTER COLUMN Age float NOT NULL;
    ALTER TABLE DM.FactObesityObservation ALTER COLUMN Height float NOT NULL;
    ALTER TABLE DM.FactObesityObservation ALTER COLUMN Weight float NOT NULL;
    ALTER TABLE DM.FactObesityObservation ALTER COLUMN FCVC float NOT NULL;
    ALTER TABLE DM.FactObesityObservation ALTER COLUMN NCP float NOT NULL;
    ALTER TABLE DM.FactObesityObservation ALTER COLUMN CH2O float NOT NULL;
    ALTER TABLE DM.FactObesityObservation ALTER COLUMN FAF float NOT NULL;
    ALTER TABLE DM.FactObesityObservation ALTER COLUMN TUE float NOT NULL;
END;
GO

MERGE DM.DimObesityLevel AS target
USING (VALUES
    (1, 'Insufficient_Weight'), (2, 'Normal_Weight'), (3, 'Overweight_Level_I'),
    (4, 'Overweight_Level_II'), (5, 'Obesity_Type_I'), (6, 'Obesity_Type_II'),
    (7, 'Obesity_Type_III')
) AS source(ObesityLevelKey, ObesityLevel)
ON target.ObesityLevelKey = source.ObesityLevelKey
WHEN NOT MATCHED THEN INSERT(ObesityLevelKey, ObesityLevel)
VALUES(source.ObesityLevelKey, source.ObesityLevel);
GO
