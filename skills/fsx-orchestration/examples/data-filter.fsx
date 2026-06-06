#!/usr/bin/env -S dotnet fsi
// Pattern: data filter / aggregate.
// Start from a large raw dataset; return only the handful of items that matter.
// The model never sees the 1000 raw rows — only the top-N summary.

open System
open System.Text.Json

// Synthesise 1000 rows. In a real script: query a DB, scan a log, fetch an API.
let rng = Random 42
let rows =
    Array.init 1000 (fun i ->
        {| id = i
           score = rng.NextDouble()
           bucket = if i % 7 = 0 then "hot" else "cold" |})

eprintfn "loaded %d rows" rows.Length

// Filter: only "hot" rows with score > 0.8, take top 5 by score.
let top =
    rows
    |> Array.filter (fun r -> r.bucket = "hot" && r.score > 0.8)
    |> Array.sortByDescending (fun r -> r.score)
    |> Array.truncate 5

eprintfn "filtered to %d row(s)" top.Length

let result =
    {| scannedRows = rows.Length
       matched = top.Length
       top = top |}

printfn "%s" (JsonSerializer.Serialize(result, JsonSerializerOptions(WriteIndented = true)))
exit 0
