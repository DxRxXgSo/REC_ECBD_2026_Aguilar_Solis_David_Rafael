let
    Source = Sql.Database(SqlInstance, SqlDatabase, [Query="SELECT ObesityLevelKey, ObesityLevel FROM DM.DimObesityLevel"]),
    Typed = Table.TransformColumnTypes(Source, {{"ObesityLevelKey", Int64.Type}, {"ObesityLevel", type text}})
in
    Typed
