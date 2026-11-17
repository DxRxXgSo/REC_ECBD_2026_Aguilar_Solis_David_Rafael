let
    Source = Sql.Database("localhost\SQLEXPRESS", "REC_ECBD_Obesidad_2026", [Query="SELECT ObesityLevelKey, ObesityLevel FROM DM.DimObesityLevel"]),
    Typed = Table.TransformColumnTypes(Source, {{"ObesityLevelKey", Int64.Type}, {"ObesityLevel", type text}})
in
    Typed
