---
name: fsx-orchestration
description: "STOP and emit one F# .fsx instead of chaining tool calls or authoring a script in any other language. Fires when walking a tree with repeated read_file/grep/file_search, same op across 3+ items, multi-tool composition with bulky intermediates, filtering >100 rows to pick a few, polling a condition, replaying anything in ~/.copilot/scripts/, sensitive data, OR about to type `cat > foo.py <<`, `tee foo.sh`, `python3 -c`, `perl -e`, `node -e`. The language gate (F#) is independent of trigger conditions. SKIP for 1-2 tool calls, per-step user judgement, single tool call. Always check `ls ~/.copilot/scripts/` first."
---

# fsx-orchestration

## Overview

Stop narrating tool calls one at a time. When a plan needs the same shape of work repeated, composed, polled, filtered, or replayed, **write a single F# script and run it** — the model emits one `.fsx`, the runtime executes it, and only the final structured result returns. Intermediates never enter context.

This is *code-as-action* (CodeAct). Loops, conditionals, error handling, and state live in the script — not in the conversation. Token-reduction and success-rate numbers in [research.md](research.md).

**Mandate:** every orchestration script is F#, every script is executable.

## Triggers — STOP and write an `.fsx`

| You catch yourself about to… | …write |
|---|---|
| Chain `read_file → grep → read_file → ...` to walk a tree | One script that walks |
| Run the same op against item 1, then 2, then 3 | `Array.map` aggregating to stdout |
| Poll with `sleep` between calls until a condition flips | Bounded `while` loop, hard iteration cap |
| Dump 1000 rows into context to pick out 5 | Filter / sort / truncate before printing |
| Pipe A → B → C where intermediates are uninteresting | Pipeline in script; print only C |
| Repeat a workflow you (or another agent) have done | `ls ~/.copilot/scripts/` → `#load` or copy |
| Handle PII / secrets through tool calls | Script handles raw; returns redacted summary |
| Type `cat > foo.py <<`, `tee foo.sh`, `python3 -c`, `perl -e`, `node -e` | `create` the file as `.fsx` |

## When NOT to use

- 1–2 step tasks (startup cost > savings).
- Per-step user judgement (scripting bypasses the human in the loop).
- Genuine interactive re-planning (exploratory debugging).
- One-shot questions — don't wrap a single `grep` in a script.

## The two independent gates

1. **Trigger gate** (table above) — should you write a script at all?
2. **Language gate** — given you've decided to write one, what language?

These are **not coupled**. Even if no trigger formally fired ("only 2 items", "just a quick parser", "one-off scratch"), if you are about to author an orchestration script of any kind, **it must be `.fsx`**. Python heredocs, shell heredocs, Node one-liners written to files, inline `python3 -c` / `perl -e` / `node -e` — all forbidden, all the time.

### Heredoc & inline-interpreter litmus test

About to type `cat > foo.py <<'PY'`, `tee foo.sh`, `echo … > foo.js`, `python3 -c "..."`, `perl -e "..."`, or `node -e "..."`? **STOP.** Use the `create` tool with a `.fsx` path before any other action. These keystrokes are the most reliable observable signal that the language gate is about to be violated.

### Subprocess is the escape hatch, not the menu

"Python's `pickle` fits this directly." "`pandas` is one import." "`xargs` is simpler than `Array.map`." Almost every "fits better elsewhere" reflex has an F# answer (BCL, FSharp.Core, FSharp.Data, Deedle, MathNet.Numerics, etc.) — reach for the obvious .NET equivalent first. A genuine leaf that lives in another runtime (PyTorch inference, binary-only CLI) is invoked via `System.Diagnostics.Process` from inside the `.fsx`. F# remains the orchestrator.

## The F# mandate

Shebang the script with `#!/usr/bin/env -S dotnet fsi` (the `-S` is required to forward `dotnet`'s subcommand). `chmod +x` so it runs as `./script.fsx`. F# pays back over `.sh` / `.py` on the second edit: types catch errors before side effects run, pipelines (`|>`) and DUs express transformations crisply, `#r "nuget: ..."` pulls dependencies inline.

## Script anatomy

Start from [template.fsx](template.fsx). Non-obvious bits:

- **Args:** `fsi.CommandLineArgs |> Array.skip 1` — first element is the script path, not arg 0.
- **Exceptions propagate.** FSI already prints type + message + stack + line and exits non-zero. Wrapping the top level in `try ... with` just to log `ex.Message` deletes the stack and is strictly worse than nothing. Catch only for cleanup, reformatting, or a specific non-1 exit code.
- **NuGet:** `#r "nuget: Foo, 1.2.3"` — pin versions; first cold-cache fetch is slow.
- **Compose:** `#load "other.fsx"`; resolve sibling paths via `__SOURCE_DIRECTORY__`, not `Environment.CurrentDirectory`.

## Patterns

- **Fan-out** — one script, N items, one aggregated result: [examples/fan-out.fsx](examples/fan-out.fsx).
- **Multi-tool composition** — chain operations where intermediate data is bulky: [examples/multi-tool.fsx](examples/multi-tool.fsx).
- **Data filter / aggregate** — large input, small output: [examples/data-filter.fsx](examples/data-filter.fsx).
- **Polling** — bounded loop with an iteration cap and a non-zero exit on timeout. Never write an unbounded loop.

## Where scripts live

Hybrid library (Voyager-style skill compounding):

- **Per-task / ephemeral:** `./scripts/<name>.fsx` inside the current workspace. Commit if reused; otherwise delete.
- **Shared / reusable:** `~/.copilot/scripts/<category>/<name>.fsx`. Promote on second use or when it generalises beyond one workspace.

**Before scripting from scratch, search the shared library:** `ls ~/.copilot/scripts/` and `grep -rl '<keyword>' ~/.copilot/scripts/`. If a previous solution exists, `#load` it or copy + parameterise.

## Anti-patterns & rationalizations

Every excuse for violating the F# mandate, with its rebuttal:

| Excuse / anti-pattern | Reality |
|---|---|
| Echoing the whole dataset to stdout | Defeats the point — filter before printing |
| Hard-coded paths / secrets | Use `fsi.CommandLineArgs`, env vars, or `__SOURCE_DIRECTORY__` |
| "Only 2 items, below the 3+ trigger, so the language rule doesn't apply" | Trigger gate decides IF to script; language gate decides WHAT LANGUAGE. Independent. The `.fsx` mandate applies whenever you author a script |
| "Python's `pickle` / Node's `fetch` / bash's `xargs` fits this better" | There's an F# answer (BCL or a NuGet). Subprocess is the escape hatch, not the menu |
| "F# would spend effort on parser risk I don't have in Python" | The mandate exists precisely so F# skill compounds in `~/.copilot/scripts/`. Today's "risk" is tomorrow's `#load`. A skill gap to close, not a language-fit argument |
| "I'll be more correct in Python" | Familiarity ≠ correctness. The mandate exists to prevent skill from forking across runtimes |
| "What would change my mind: a proven F# library / 3+ items / existing fsx" | The rule is unconditional. You're describing what would make compliance *easier*, not what would make the rule *apply* |
| "Writing `.sh` because it's simpler" | The simplicity is a mirage; types pay back on the second edit |
