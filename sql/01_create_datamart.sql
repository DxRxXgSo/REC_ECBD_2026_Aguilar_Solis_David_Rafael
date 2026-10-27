/* Data Mart de Unidad II. Requiere SQL Server 2017+ para FORMAT='CSV'. */
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
        Age decimal(12,6) NOT NULL,
        Height decimal(12,6) NOT NULL,
        Weight decimal(12,6) NOT NULL,
        family_history_with_overweight varchar(10) NOT NULL,
        FAVC varchar(10) NOT NULL,
        FCVC decimal(12,6) NOT NULL,
        NCP decimal(12,6) NOT NULL,
        CAEC varchar(20) NOT NULL,
        SMOKE varchar(10) NOT NULL,
        CH2O decimal(12,6) NOT NULL,
        SCC varchar(10) NOT NULL,
        FAF decimal(12,6) NOT NULL,
        TUE decimal(12,6) NOT NULL,
        CALC varchar(20) NOT NULL,
        MTRANS varchar(40) NOT NULL,
        ObesityLevelKey tinyint NOT NULL,
        CONSTRAINT FK_FactObesityObservation_DimObesityLevel
            FOREIGN KEY (ObesityLevelKey) REFERENCES DM.DimObesityLevel(ObesityLevelKey)
    );
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
