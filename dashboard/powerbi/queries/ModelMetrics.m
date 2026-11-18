let
    Csv = Csv.Document(File.Contents(ProjectRoot & "\docs\unidad_iii\resultados\optimizacion_metricas_test.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Source = Table.PromoteHeaders(Csv, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Source, {{"task", type text}, {"scenario", type text}, {"model", type text}, {"cv_best_score", type number}, {"test_mae", type number}, {"test_rmse", type number}, {"test_r2", type number}, {"test_accuracy", type number}, {"test_precision_macro", type number}, {"test_recall_macro", type number}, {"test_f1_macro", type number}}, "en-US")
in
    Typed
