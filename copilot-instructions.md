# F# Instructions

When **writing or modifying** F# source (`.fs`, `.fsi`, `.fsx`) or project files (`.fsproj`):

- **Delegate the edit to the `fsharp-coding` agent.** Do not edit `.fs`/`.fsi`/`.fsx`/`.fsproj` files directly — dispatch the work via the `task` tool with `agent_type=fsharp-coding`. This applies to every F# edit, not just "architectural" ones. The agent owns the file once delegated. Size of the change is not a reason to skip delegation.
- **After every F# edit** (yours or the agent's), invoke the `/fsharp-validation` skill, including its *Consistency with Neighbours* check against the changed files, before returning control to the user. Fix every finding it reports and re-run it until clean. Do not hand back with known violations.
- Invoke the `/fsharp-interop` skill **only** when the user explicitly says the surface targets C#/.NET consumers (`"targets C# consumers"`, `"non-F# .NET consumers"`, `"enable interop checks"`).

Non-F# files (`.ps1`, `.yml`, `.json`, `.md`, etc.) do not require these skills.

### Delegation brief

A `task` prompt to `fsharp-coding` is built from these parts, in order:

1. **Goal** — the F# part of the user's request, in the user's words and attributed to them. Non-F# steps such as opening a PR stay with the parent.
2. **Decisions** — decisions the user approved, each in the user's words and attributed to them.
3. **Scope** — working directory, the files or projects the agent may change, and the repository's build/test command (a repository fact, not a requirement).
4. **Context** — paths to the relevant code and docs. Say which of them are agent-drafted designs, specs or saved decision records that the user has not approved.
5. **Acceptance** — one line per observable behaviour, each traced to what the user said.
6. **Execution boundary** — what the agent returns, e.g. "edit and build only; report back, no commits".
7. The line: `Survey local precedent first and mirror it for representation.`

Representation (wrapper style, failure idiom, new files or modules) is the agent's Phase 1 output. When its report lists `Conflicts`, show them to the user.

# fsx-orchestration — code-as-action reflex

When a plan involves repeated, composed, polled, filtered, or previously-solved work, **emit one executable F# `.fsx` and run it** instead of chaining step→AI→step tool calls. The model writes the script, the runtime runs it, only the final structured result re-enters context. Full skill: [`skills/fsx-orchestration/SKILL.md`](skills/fsx-orchestration/SKILL.md).

## Fire when ANY of these is in the plan

- **Fan-out** — same operation across 3+ items.
- **Tree walk / composition** — chained `view → grep → view → …` or output of A feeds B feeds C, intermediates uninteresting.
- **Data filter / aggregate** — large raw result (>100 rows), small needed answer.
- **Polling** — bounded loop with a clear termination condition.
- **Replay** — the workflow has been done before; check `.copilot/scripts/` first, then `~/.copilot/scripts/` and `#load` or copy + parameterise.
- **Sensitive data** — PII / secrets should not enter model context.

## Do NOT fire

- 1–2-step tasks (script startup cost > savings).
- Per-step user judgement required.
- Genuine interactive re-planning between steps (exploratory debugging).
- A single tool call.

## Language gate (independent of trigger gate)

The triggers above decide IF to write a script. The "Hard rules" below decide WHAT LANGUAGE. These gates are **independent** — if you decide to author any orchestration script at all (even one-off, even for 2 items, even if no trigger above fired), it MUST be `.fsx`. No `cat > foo.py <<`, no `tee foo.sh`, no Node one-liner saved to a file. Ecosystem-fit ("Python's `pickle` fits this", "`xargs` is one line") is not an exemption — call foreign runtimes as subprocesses from inside the `.fsx`. If you are about to type a heredoc whose target file isn't `.fsx`, STOP.

## Hard rules for any script produced

1. `.fsx` extension. F# only — no Python/bash fallback.
2. First line: `#!/usr/bin/env -S dotnet fsi`.
3. `chmod +x` always. Invoke as `./script.fsx`, never `dotnet fsi script.fsx`.
4. stdout = structured result (JSON for non-trivial). stderr = progress.
5. Let exceptions propagate — FSI prints full type/message/stack/line and exits non-zero. Only add a top-level `try ... with` for cleanup, reformatting, or a specific non-1 exit code; never just to log `ex.Message` (it deletes the stack).
6. Iteration / polling caps. No unbounded loops.
7. Args via `fsi.CommandLineArgs |> Array.skip 1`. No hard-coded paths or secrets.

A `PreToolUse` audit hook ([`hooks/fsx-reflex.json`](hooks/fsx-reflex.json) → [`hooks/fsx-reflex.py`](hooks/fsx-reflex.py)) reinforces this rule: when a scriptable tool fires its 3rd time in the recent window — or a terminal command looks like a loop/pipeline — without any `.fsx` activity in the window, the hook injects a one-line reminder via `additionalContext`. The hook never blocks — it's an audit trail, not a gate.
