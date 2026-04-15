# Code Organization

> **Role**: Agent guidance — shapes how code is structured, organized, and initialized.
>
> **Source**: [F# Coding Conventions](https://learn.microsoft.com/en-us/dotnet/fsharp/style-guide/conventions)

---

## Namespaces vs Modules

F# has two primary ways to organize code. The choice affects interoperability:

| Feature | Namespace | Module |
|---------|-----------|--------|
| Compiled as | .NET namespace | Static class |
| Scope | Can span multiple files | Single file only |
| Nesting | Always top level | Can nest within other modules |
| Attributes | — | `[<RequireQualifiedAccess>]`, `[<AutoOpen>]` |
| C# consumption | Natural (`using`) | Requires `using static` |

### Prefer namespaces at the top level

For any publicly consumable code, namespaces are preferential to modules at the top level.

```fsharp
// ✔️ Recommended — consumable from C# naturally
namespace MyCode

type MyClass() =
    member _.DoWork() = ()

// ❌ Avoid for public APIs — seen as static class outside F#
module MyCode

type MyClass() =
    member _.DoWork() = ()
```

### Use modules for grouping related functions

Modules are ideal for grouping related functions, especially collection-like operations:

```fsharp
namespace MyLibrary

module UserOperations =
    let findById id users =
        users |> List.tryFind (fun u -> u.Id = id)

    let filterActive users =
        users |> List.filter (fun u -> u.IsActive)
```

---

## `[<AutoOpen>]` — Use Carefully

`[<AutoOpen>]` pollutes the caller's scope. The answer to "where does this come from?" becomes "magic."

**Use it for**:
- Private helper modules within a public API
- Extension methods at the namespace level
- Expression builders

```fsharp
// ✔️ Good use — private helpers within a public module
module MyAPI =
    [<AutoOpen>]
    module private Helpers =
        let helper1 x y z = x + y + z

    let myFunction1 x =
        let y = 10
        let z = 20
        helper1 x y z
```

**Do NOT use it for**:
- General-purpose modules that pollute global scope
- Anything where the source of a name should be obvious

---

## `[<RequireQualifiedAccess>]` — Use When Names Could Conflict

Forces callers to qualify all access, preventing name collisions and improving readability.

```fsharp
// ✔️ Recommended — prevents name collision with List.parse, etc.
[<RequireQualifiedAccess>]
module StringTokenization =
    let parse s = s |> String.split ','

// Usage: StringTokenization.parse "a,b,c"
```

**Strongly suggested** for custom modules that extend `Seq`, `List`, `Array`, or any module with `[<RequireQualifiedAccess>]`.

---

## Sort `open` Statements Topologically

In F#, the order of `open` statements matters — elements opened later can shadow earlier ones. Reordering can change code meaning.

**Do NOT sort alphabetically.** Sort topologically — by system layer:

```fsharp
namespace Microsoft.FSharp.Compiler.SourceCodeServices

// Layer 1: System
open System
open System.Collections.Generic
open System.IO

// Layer 2: FSharp.Compiler infrastructure
open FSharp.Compiler
open FSharp.Compiler.AbstractIL
open FSharp.Compiler.AbstractIL.IL

// Layer 3: FSharp.Compiler higher-level
open FSharp.Compiler.Ast
open FSharp.Compiler.CompileOps

// Layer 4: Internal utilities
open Internal.Utilities
open Internal.Utilities.Collections
```

Separate topological layers with blank lines. Sort alphabetically *within* each layer.

---

## Side Effects and Initialization — Use Classes, Not Modules

Module-level `let` bindings with side effects cause serious problems:

1. **Configuration baked into code** — `dep1 = File.ReadAllText "/path"`
2. **Thread safety** — statically initialized mutable state is shared
3. **`TypeInitializationException`** — module init failure is cached for the app's lifetime

```fsharp
// ❌ Problematic — side effects at static initialization
module MyApi =
    let dep1 = File.ReadAllText "/config.txt"       // Side effect
    let dep2 = Environment.GetEnvironmentVariable "X" // Side effect
    let private r = Random()
    let dep3() = r.Next()                            // Not thread safe

    let function1 arg = doStuffWith dep1 dep2 dep3 arg

// ✔️ Use a class — dependencies injected, testable, no static side effects
type MyParametricApi(dep1, dep2, dep3) =
    member _.Function1 arg = doStuffWith dep1 dep2 dep3 arg
    member _.Function2 arg = doStuffWith dep1 dep2 dep3 arg
```

**Benefits of the class approach**:
- Dependent state pushed outside the API
- Configuration done externally
- No `TypeInitializationException` risk
- Easier to test (inject mocks)
