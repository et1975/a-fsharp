---
name: fsharp-validation
description: >-
  Use immediately after any tool that edits or creates `.fs`, `.fsi`, `.fsx`,
  or `.fsproj` files — and any time the user says 'check', 'lint',
  'validate', or 'review' on F# code, or for PR / code review of F#. Run
  until it reports no findings before handing control back.
---

# F# Validation Skill

## Announcement
> Using **fsharp-validation** to enforce F# coding rules.

> **Scope**: these rules target production `.fs` code. Test modules, `.fsx` scripts, and framework-conventional patterns may follow their ecosystem idioms.

## Naming Guidelines

| Construct | Case | Notes |
|-----------|------|-------|
| Types, records, DUs | PascalCase | |
| DU cases | PascalCase | No prefix in public APIs |
| Interfaces | PascalCase | Must start with `I` per .NET convention, unless existing codebase does not use prefix |
| Exceptions | PascalCase | Must end with `Exception` |
| Namespaces | PascalCase | `<Org>.<Technology>[.<Sub>]`, where <Org> may be omitted |
| Properties | PascalCase | Booleans: prefix `Is` or `Can` |
| Methods | PascalCase | |
| Parameters | camelCase | |
| `let` values/functions | camelCase | Always. PascalCase = violation, unless it's a literal |
| Generic params | PascalCase or match codebase convention | `'T`, `'Key`, `'Value` — not `'TKey`. Existing codebase conventions (e.g. `'msg`) are acceptable |
| Active patterns | PascalCase | `(\|Even\|Odd\|)` |

**Additional rules:**
- No abbreviations (except `Async`, `Seq`, `List.iter`, FSharp.Core standard)
- Never disambiguate names by casing alone
- Acronyms in .NET style: `Xml` not `XML`

## Abstraction Smell: Wrong Decomposition

Flag and refer back to domain modelling. The abstractions need rethinking — noun → module, verb → function.

```fsharp
// ❌ processOrder, handlePayment, doValidation
// ❌ Order.process — equally wrong; the verb must be domain-specific
// ✔️ Order.validate, Order.price, Payment.authorize, Payment.capture
```

## Formatting Guidelines

| Rule | Spec |
|------|------|
| Indentation | 4 spaces, never tabs |
| Line length | 100 chars (120 for type signatures) |
| Function size | Warn at 25 lines |
| Comments | `//` preferred over `(* *)`, don't waste vertical space with superfluous comments |
| Alignment | Never align to name length |

**Pattern matching:**
- `\|` at same indentation as `match`
- Space before constructor argument in patterns: `Some (y)` not `Some(y)`
- Spaces between curried args in patterns: `Pattern arg (a, b)`
- Never align match arrows
- Long RHS → next line, indented

**Records:** Short on one line. Multi-line: pick one style (Cramped/Aligned/Stroustrup), be consistent.

**Lists/Arrays:** Spaces after `[` and before `]`. Space between distinct brace-like operators. Prefer `->` over `do yield`. Omit `yield`.

**Other:**
- Named args: spaces around `=`
- Chained invocations: each on own line, indented
- Index expressions: no spaces around brackets
- Long mutation RHS: new line
- Single-clause `with`: no `|`

## `open` Statement Ordering

Sort from fundamental to most specific.

| Order | Layer | Examples |
|-------|-------|----------|
| 1 | System / BCL | `System`, `System.Collections.Generic`, `System.Threading.Tasks` |
| 2 | FSharp.Core / FSharp libraries | `FSharp.Control`, `FSharp.Collections` |
| 3 | Third-party / Framework | `Newtonsoft.Json`, `Serilog`, `FsToolkit.ErrorHandling` |
| 4 | Application | Project's own namespaces: `MyApp.Domain`, `MyApp.Infrastructure` |
| 5 | Sibling / Internal | Modules within the same project or namespace layer |

- Within a layer, order by dependency (topological), **not** alphabetically
- Flag violations when opens are intermixed across layers

```fsharp
// ❌ Intermixed layers, no grouping
open MyApp.Domain
open System
open FsToolkit.ErrorHandling
open System.Collections.Generic
open MyApp.Infrastructure

// ✔️ Fundamental → most specific
open System
open System.Collections.Generic
open FsToolkit.ErrorHandling
open MyApp.Domain
open MyApp.Infrastructure
```

## Bad Patterns

| Pattern | Alternative |
|---------|-------------|
| `failwith` / `failwithf` in domain module | `Result` with typed DU error (exhaustiveness guard `| _ -> failwith "unreachable"` is acceptable) |
| `failwith` / `failwithf` in IO/boundary | `invalidArg`, `nullArg`, `invalidOp`, specific exception types |
| Exporting partially-applied function as public binding | Explicit parameters (call-site application like `Result.map (f x)` is fine) |
| Point-free in public API | Named `let` bindings |
| Nested `Result<Result<...>>` as return type | Typed DU or exceptions |
| Catch-all `with _ ->` | Catch specific exception types, might be justified in broader context |
| Module-level side effects | Class with DI |
| Non-thread-safe static values | Thread-local or injected, fine if immutable or accessed via `Interlocked` |
| Name-length alignment | Standard indentation |
| `[<AutoOpen>]` on domain/public modules | `[<RequireQualifiedAccess>]` (exception: single internal (ie `Prelude`) or narrow-scoped (`Operators`) module) |
| Public module without `[<RequireQualifiedAccess>]` | Add the attribute (exception: CE builders, extension modules) |
| Implementation inheritance as design tool | Prefer interfaces + composition (CLR-mandated bases like Exception, DbContext, BackgroundService are fine) |
| Record-of-functions as interface substitute | Prefer interface type (framework conventions like Elmish/Remoting config, test doubles are acceptable) |
| `yield` keyword (modern F#) | Implicit yield or `->` |
| noun+verb in function names | Re-model: noun → module, verb → function (exception: framework-conventional names like `perform` in nested modules) |
| Function with 6+ individual parameters | Group into a record or split the function |
| Multiple parameters of same primitive representing different concepts | Wrap each in a zero-cost abstraction (UoM / struct DU / alias) |
| Nested `match` / pyramid of doom | Flatten with a CE (`result`, `asyncResult`) or `Result.bind` pipeline |
| Parameter only passed through to another function call (private/internal code) | Partially apply the inner function instead |
| `Result<'T, string>` as error type | Define a typed DU for domain errors |
| `Option.get` / `.Value` on Option or Result | Pattern match or use `defaultValue`/`Result.defaultWith` |
| `|> ignore` on Result-returning expression | Ensure the error case is intentionally discarded — flag for review in domain code |
| DU wildcard `| _ ->` hiding new cases | Prefer explicit cases in domain logic; wildcards acceptable in message/event handlers where handling a subset is intentional |
| `.Result` / `.Wait()` / `Async.RunSynchronously` | Propagate async; use `task { }` or `async { }` |
| `Task` piped into `ignore` | Unawaited hot task disrupts the .NET task scheduler — always await or return it |
| `Async` piped into `ignore` | No-op — cold async never executes. Start it (`Async.Start`) or await it |

## Opaque Type Discipline

Wrapped primitives (UMX measure types, single-case DUs) are only *opaque* when paired with a `[<RequireQualifiedAccess>]` companion module that owns construction and read-out. Without it, the wrapper is a leaky alias. Flag:

| Pattern | Issue | Fix |
|---------|-------|-----|
| `[<Measure>] type x` + `type X = string<x>` without a `module X` exposing `create`/`value` (or `ofX`/`toX`) | Wrapper exists but callers must reach for `UMX.tag`/`UMX.untag` — type is not opaque | Add `[<RequireQualifiedAccess>] module X` with construction + read-out |
| `UMX.tag<...>`, `UMX.untag`, or the `%foo` shorthand used **outside** the wrapper type's home module | Bypasses validation and leaks the underlying primitive into call sites | Route through `X.create` / `X.value` |
| Single-case DU wrapping a domain primitive with a **public** case constructor | Anyone can fabricate values — invariants unenforceable | Mark the case `private`, expose `create`/`value` from the companion module |
| Direct pattern-match on a single-case DU (`let (ClientId g) = ...`) outside its home module | Same opacity break — the case is in the public surface | Use `ClientId.value` |
| Function parameter typed as the underlying primitive (`string`, `Guid`, `int`) where a domain opaque type exists for that concept | Loses the type safety the wrapper exists to provide | Take the opaque type at the parameter |
| Plain alias (`type CustomerId = string`) used as if it were a domain type | Aliases give zero safety — fully transparent to the compiler | Promote to UMX measure or struct DU with companion module |
| UMX measure tag named `PascalCase` | Convention is lowercase for the phantom tag, PascalCase for the user-facing alias | Rename measure to `lowerCase`, keep alias `PascalCase` |

The canonical leak signal: `UMX.tag` / `UMX.untag` / `%foo` or a raw single-case DU constructor appearing anywhere other than the type's home module.

```fsharp
// ❌ Measure tag PascalCase, no companion module — callers reach for UMX directly
[<Measure>] type OrderId
type OrderId' = string<OrderId>
let publish (raw: string) = sendOrder (UMX.tag<OrderId> raw)   // leaks raw + tag at the call site
```

## Domain Purity Violations

Domain modules must be free of IO, mutable state, and **throwing**. Defensive catching of specific CLR exceptions is OK — never catch-all.

```fsharp
// ❌ IO in domain module
module Order =
    let load id = use conn = new SqlConnection(connStr) ...

// ❌ Mutation in domain module
module Order =
    let mutable lastOrderId = 0

// ❌ Throwing in domain module
module Order =
    let validate order =
        if order.Total <= 0m then failwithf "Invalid: %M" order.Total

// ❌ Raising exceptions in domain module
module Order =
    let validate order =
        if order.Total <= 0m then raise (InvalidOperationException("bad total"))

// ✔️ Pure domain — Result, never throws
module Order =
    let validate (order: Order) : Result<Order, OrderError> =
        if order.Total <= 0m then Error (InvalidTotal order.Total) else Ok order
```

Move IO to IO modules. Domain errors use `Result<'T, DomainError>`. Exceptions are natural at IO boundaries.

## DU Type Qualification

Apply `[<RequireQualifiedAccess>]` to DU types whose case names could collide with common identifiers (e.g., `Status.Active`, `Result.Ok`). Internal types with narrow scope can omit at discretion.
