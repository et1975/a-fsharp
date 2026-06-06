#!/usr/bin/env -S dotnet fsi
// Pattern: multi-tool composition.
// Output of step A feeds step B feeds step C. The model never sees A or B —
// only the final structured result from C.
//
// Toy version: load lines → transform → aggregate. In a real script each step
// would call a tool / API / MCP server; the principle is identical.

open System
open System.IO
open System.Text.Json

// Step A: load (here, synthesise; in a real script: read a file, hit an API)
let load () =
    [| "2026-05-01,login,alice"
       "2026-05-01,login,bob"
       "2026-05-02,logout,alice"
       "2026-05-02,login,carol"
       "2026-05-03,login,alice" |]

// Step B: transform (parse CSV-ish lines into structured records)
let parse (line: string) =
    let parts = line.Split(',')
    {| date = parts.[0]; action = parts.[1]; user = parts.[2] |}

// Step C: aggregate (group + count). Only this leaves the script.
let summarise (records: {| date: string; action: string; user: string |}[]) =
    records
    |> Array.groupBy (fun r -> r.user)
    |> Array.map (fun (user, rs) ->
        {| user = user
           events = rs.Length
           actions = rs |> Array.map (fun r -> r.action) |> Array.distinct |})

let result =
    load ()
    |> Array.map parse
    |> summarise

printfn "%s" (JsonSerializer.Serialize(result, JsonSerializerOptions(WriteIndented = true)))
exit 0
