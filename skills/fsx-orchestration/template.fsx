#!/usr/bin/env -S dotnet fsi
// One-line summary of what this script does.
// #load "lib/Markdown.fsx"   // or Http.fsx, etc. — see ~/.copilot/scripts/lib/
open System

let args = fsi.CommandLineArgs |> Array.skip 1

// stdout: result. stderr: progress (eprintfn). Uncaught exceptions exit non-zero automatically.
