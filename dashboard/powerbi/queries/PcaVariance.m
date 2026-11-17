let
    ProjectRoot = "C:\Users\rafle\Documents\REC_ECBD_2026_Aguilar_Solis_David_Rafael",
    Csv = Csv.Document(File.Contents(ProjectRoot & "\docs\unidad_iv\resultados\varianza_pca.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Source = Table.PromoteHeaders(Csv, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Source, {{"component", type text}, {"explained_variance_ratio", Percentage.Type}, {"cumulative_variance_ratio", Percentage.Type}}, "en-US")
in
    Typed
