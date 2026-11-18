let
    Csv = Csv.Document(File.Contents(ProjectRoot & "\data\processed\obesity_unit_ii.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Source = Table.PromoteHeaders(Csv, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Source, {
        {"Gender", type text}, {"Age", type number}, {"Height", type number}, {"Weight", type number},
        {"family_history_with_overweight", type text}, {"FAVC", type text}, {"FCVC", type number},
        {"NCP", type number}, {"CAEC", type text}, {"SMOKE", type text}, {"CH2O", type number},
        {"SCC", type text}, {"FAF", type number}, {"TUE", type number}, {"CALC", type text},
        {"MTRANS", type text}, {"NObeyesdad", type text}
    }, "en-US"),
    AddRowIndex = Table.AddIndexColumn(Typed, "row_index", 0, 1, Int64.Type),
    AssignCsv = Csv.Document(File.Contents(ProjectRoot & "\data\processed\unidad_iv_cluster_assignments.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    AssignHeaders = Table.PromoteHeaders(AssignCsv, [PromoteAllScalars=true]),
    AssignTypes = Table.TransformColumnTypes(AssignHeaders, {{"row_index", Int64.Type}, {"cluster", Int64.Type}, {"PC1", type number}, {"PC2", type number}}, "en-US"),
    Merge = Table.NestedJoin(AddRowIndex, {"row_index"}, AssignTypes, {"row_index"}, "U4", JoinKind.LeftOuter),
    Expand = Table.ExpandTableColumn(Merge, "U4", {"cluster", "PC1", "PC2"}, {"cluster", "PC1", "PC2"}),
    ValidateNoMissing = if Table.RowCount(Expand) <> 2111 or List.NonNullCount(Expand[cluster]) <> 2111 then error "Source rows or cluster assignments differ from the validated 2,111 row contract" else Expand
in
    ValidateNoMissing
