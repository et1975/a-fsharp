# F# Instructions

When **writing or modifying** F# source (`.fs`, `.fsi`, `.fsx`) or project files (`.fsproj`):

- **Delegate the edit to the `fsharp-coding` agent.** Do not edit `.fs`/`.fsi`/`.fsx`/`.fsproj` files directly — dispatch the work via the `task` tool with `agent_type=fsharp-coding`. This applies to every F# edit, not just "architectural" ones. The agent owns the file once delegated. Size of the change is not a reason to skip delegation.
- **After every F# edit** (yours or the agent's), invoke the `/fsharp-validation` skill before returning control to the user. Fix every finding it reports and re-run it until clean. Do not hand back with known violations.
- Invoke the `/fsharp-interop` skill **only** when the user explicitly says the surface targets C#/.NET consumers (`"targets C# consumers"`, `"non-F# .NET consumers"`, `"enable interop checks"`).

Non-F# files (`.ps1`, `.yml`, `.json`, `.md`, etc.) do not require these skills.
