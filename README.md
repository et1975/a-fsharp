# AI-assisted F#

Copilot customization pack for F# development — a set of GitHub Copilot agents, skills, and repository instructions that enforce idiomatic F# coding practices.
Distilled from official F# guidelines, customized with my personal preferences.

## What's Included

- **[copilot-instructions.md](copilot-instructions.md)** — Repository-level instructions that route Copilot to the correct agent/skill based on file type, and the *fsx-orchestration* reflex that mandates F# `.fsx` for all orchestration scripts.
- **[agents/fsharp-coding.agent.md](agents/fsharp-coding.agent.md)** — A coding agent with an opinionated F# workflow: types-first domain modelling, purity discipline, single-page domain modelling, railway-oriented error handling, and module organisation conventions.
- **[skills/fsharp-validation/](skills/fsharp-validation/)** — Validation skill for reviewing F# code against naming, formatting, and anti-pattern rules.
- **[skills/fsharp-interop/](skills/fsharp-interop/)** — Opt-in skill for designing .NET-consumer-friendly API façades on top of idiomatic F# internals.
- **[skills/fsx-orchestration/](skills/fsx-orchestration/)** — *Code-as-action* skill: when a plan involves fan-out, multi-tool composition, polling, filtering, or replay, emit a single executable `.fsx` instead of chaining tool calls. Ships with `template.fsx`, three worked `examples/`, and `research.md`.
- **[hooks/fsharp-reflex.{json,py}](hooks/)** — `PreToolUse` audit hook that nags when F# files are edited directly (without delegating to `fsharp-coding`) or when an F# edit isn't followed by `fsharp-validation`. Never blocks; advisory only. Modelled on `palace-reflex` / `fsx-reflex` — wire it up alongside those in `~/.copilot/hooks/`.
- **[hooks/fsx-reflex.{json,py}](hooks/)** — `PreToolUse` audit hook that nags when a scriptable tool (read/grep/fetch/etc.) fires repeatedly in a tight window without any `.fsx` activity, or when a terminal command looks like a loop/pipeline an `.fsx` would express. Never blocks; advisory only.

## Usage

Copy or symlink the contents into your home or F# repository. Copilot will automatically pick up the instructions and use the agent/skills when working with `.fs`, `.fsi`, `.fsx`, and `.fsproj` files.

## License

Apache 2.0 — see [LICENSE.md](LICENSE.md).
