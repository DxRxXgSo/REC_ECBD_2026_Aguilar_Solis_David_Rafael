let
    ProjectRoot = "C:\Users\rafle\Documents\REC_ECBD_2026_Aguilar_Solis_David_Rafael",
    Csv = Csv.Document(File.Contents(ProjectRoot & "\docs\unidad_iv\resultados\perfil_numerico_clusters.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Source = Table.PromoteHeaders(Csv, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Source, {{"cluster", Int64.Type}, {"Age", type number}, {"Height", type number}, {"Weight", type number}, {"FCVC", type number}, {"NCP", type number}, {"CH2O", type number}, {"FAF", type number}, {"TUE", type number}}, "en-US")
in
    Typed
