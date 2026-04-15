# F# Coding Guidelines — Agent/Skill Architecture

## Philosophy

This repo captures official Microsoft F# guidelines, categorized by the **agent/skill architecture** described in `question.md`.

The core insight:

> **Planning-level coding guidance belongs in agents.**
> **Policy-level coding guidance belongs in skills.**

| Concern | Representation | Question it answers |
|---------|---------------|-------------------|
| Intent planning | Agent | *How should I do this?* |
| Domain heuristics | Agent | *What's the idiomatic approach?* |
| Code style bias | Agent | *What patterns should I prefer?* |
| Correctness | Skill | *Is this allowed?* |
| Naming policy | Skill | *Does this follow conventions?* |
| Forbidden patterns | Skill | *Should this be rejected?* |
| API boundary safety | Skill | *Is this safe for consumers?* |

## Source Material

All guidelines are derived from official Microsoft documentation:

1. **[F# Style Guide](https://learn.microsoft.com/en-us/dotnet/fsharp/style-guide/)** — Five principles of good F# code
2. **[F# Coding Conventions](https://learn.microsoft.com/en-us/dotnet/fsharp/style-guide/conventions)** — Organization, errors, partial application, performance
3. **[F# Code Formatting Guidelines](https://learn.microsoft.com/en-us/dotnet/fsharp/style-guide/formatting)** — Whitespace, indentation, bracket styles
4. **[F# Component Design Guidelines](https://learn.microsoft.com/en-us/dotnet/fsharp/style-guide/component-design-guidelines)** — Naming, types, API design, .NET interop

## File Map

### Agent Guidelines (`agent/`) — Planning-Time Reasoning

These documents shape **how** the agent reasons about architecture, decomposition, and implementation strategy *before* code generation:

| File | Purpose |
|------|---------|
| `fsharp-principles.md` | Five principles of good F# code — the foundation for all decisions |
| `code-organization.md` | Namespaces vs modules, open statement ordering, side-effect management |
| `error-management.md` | DU-based error modeling vs exceptions — decision framework |
| `type-and-api-design.md` | Object programming, class/interface/DU design, API shape decisions |
| `component-design.md` | Library design, .NET interop strategy, F#-facing vs vanilla .NET APIs |

### Skill Guidelines (`skill/`) — Enforcement-Time Validation

These documents define **deterministic rules** that validate correctness after code generation:

| File | Purpose |
|------|---------|
| `formatting-rules.md` | Indentation, spacing, bracket styles — enforceable formatting rules |
| `naming-conventions.md` | PascalCase/camelCase rules, abbreviation policy, naming table |
| `forbidden-patterns.md` | Anti-patterns that must be rejected with alternatives |
| `api-boundary-checks.md` | Null checks, .NET interop requirements, type exposure rules |

## How These Become Agents and Skills

### Agents (Future)

Each `agent/` document becomes part of an agent's **system prompt** or **reasoning context**. The agent uses these guidelines to:
- Plan architecture before generating code
- Choose between design alternatives (e.g., DU vs exception, namespace vs module)
- Decompose problems using idiomatic F# patterns
- Make tradeoff decisions informed by the five principles

### Skills (Future)

Each `skill/` document becomes a **validation function** or **linting rule**. Skills:
- Run deterministically against generated code
- Return pass/fail with specific violation details
- Can be composed into a validation pipeline
- Gate execution (code that violates skill rules is rejected and rewritten)

### The Canonical Flow

```
User Goal
    → F# Agent (plans using agent/ guidelines)
        → Code Generation
            → F# Skills (validate using skill/ guidelines)
                → Pass: proceed to commit
                → Fail: return to agent with violations
```

## Review Process

**You are here** → Review these guidelines and add your own before any agent or skill implementation begins.

Feel free to:
- Edit any guideline file to add project-specific rules
- Add new files for domain-specific guidance
- Annotate guidelines with priority (must-have vs nice-to-have)
- Remove guidelines that don't apply to your context
