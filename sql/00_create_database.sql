/* Crea la base dedicada sólo si no existe; nunca elimina ni reemplaza datos. */
IF DB_ID(N'REC_ECBD_Obesidad_2026') IS NULL
BEGIN
    CREATE DATABASE [REC_ECBD_Obesidad_2026];
END;
GO

USE [REC_ECBD_Obesidad_2026];
GO

SELECT DB_NAME() AS database_name;
GO
