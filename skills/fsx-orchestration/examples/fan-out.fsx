#!/usr/bin/env -S dotnet fsi
// Pattern: fan-out.
// Apply the same operation across N items, aggregate, return a single structured result.
// The model never sees the per-item intermediate values.

open System
open System.Text.Json

let items = [| "alpha"; "beta"; "gamma"; "delta"; "epsilon" |]

let processOne (name: string) =
    {| name = name
       length = name.Length
       upper = name.ToUpperInvariant() |}

let results = items |> Array.map processOne

let summary =
    {| count = results.Length
       totalLength = results |> Array.sumBy (fun r -> r.length)
       items = results |}

printfn "%s" (JsonSerializer.Serialize(summary, JsonSerializerOptions(WriteIndented = true)))
exit 0
