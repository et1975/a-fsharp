# AI-assisted F#

Copilot customization pack for F# development — a set of GitHub Copilot agents, skills, and repository instructions that enforce idiomatic F# coding practices.
Distilled from official F# guidelines, customized with my personal preferences.

## What's Included

- **[copilot-instructions.md](copilot-instructions.md)** — Repository-level instructions that route Copilot to the correct agent/skill based on file type.
- **[agents/fsharp-coding.agent.md](agents/fsharp-coding.agent.md)** — A coding agent with an opinionated F# workflow: types-first domain modelling, purity discipline, single-page domain modelling, railway-oriented error handling, and module organisation conventions.
- **[skills/fsharp-validation/](skills/fsharp-validation/)** — Validation skill for reviewing F# code against naming, formatting, and anti-pattern rules.
- **[skills/fsharp-interop/](skills/fsharp-interop/)** — Opt-in skill for designing .NET-consumer-friendly API façades on top of idiomatic F# internals.

## Usage

Copy or symlink the contents into your home or F# repository. Copilot will automatically pick up the instructions and use the agent/skills when working with `.fs`, `.fsi`, `.fsx`, and `.fsproj` files.

## License

Apache 2.0 — see [LICENSE.md](LICENSE.md).
