# Forbidden Patterns

> **Role**: Skill enforcement — patterns that must be detected and rejected.
>
> **Source**: [F# Coding Conventions](https://learn.microsoft.com/en-us/dotnet/fsharp/style-guide/conventions), [F# Formatting Guidelines](https://learn.microsoft.com/en-us/dotnet/fsharp/style-guide/formatting), [F# Component Design Guidelines](https://learn.microsoft.com/en-us/dotnet/fsharp/style-guide/component-design-guidelines)

---

## Public API Anti-Patterns

### ❌ Partial application in public APIs

```fsharp
// ❌ FORBIDDEN — confusing for consumers
module PublicApi =
    let add x = fun y -> x + y  // Returns function value, not a value

// ✔️ ALTERNATIVE
module PublicApi =
    let add x y = x + y
```

### ❌ Point-free style in public APIs

```fsharp
// ❌ FORBIDDEN — no parameter names in tooling, not debuggable
let processAll = List.map transform >> List.filter isValid

// ✔️ ALTERNATIVE — explicit parameters, inspectable
let processAll items =
    items
    |> List.map transform
    |> List.filter isValid
```

### ❌ Custom symbolic operators in public APIs

```fsharp
// ❌ FORBIDDEN — hard to document, search, and discover
let (<!>) x f = Option.map f x

// ✔️ ALTERNATIVE — named function as primary API
let mapOption f x = Option.map f x
// Operators OK additionally for convenience, not as sole API
```

---

## Error Handling Anti-Patterns

### ❌ `failwith` / `failwithf` for raising exceptions

```fsharp
// ❌ FORBIDDEN — raises base System.Exception
let validate x =
    if x < 0 then failwith "Cannot be negative"
    x

// ✔️ ALTERNATIVE — specific exception type
let validate x =
    if x < 0 then invalidArg (nameof x) "Cannot be negative"
    x
```

### ❌ Monadic error handling as exception replacement

```fsharp
// ❌ FORBIDDEN — nested Result types
Result<Result<MyType, string>, string list>

// ❌ FORBIDDEN — stringly-typed error matching
match result with
| Error e ->
    if e.Contains "Error string 1" then ...
    elif e.Contains "Error string 2" then ...
    else ...

// ✔️ ALTERNATIVE — typed error DU or specific exceptions
type ApiError =
    | NotFound of resource: string
    | Unauthorized
    | ValidationFailed of errors: string list
```

### ❌ Catch-all exception swallowing

```fsharp
// ❌ FORBIDDEN — discards all error context
let tryReadAllText (path: string) =
    try System.IO.File.ReadAllText path |> Some
    with _ -> None

// ✔️ ALTERNATIVE — catch specific exceptions
let tryReadAllTextIfPresent (path: string) =
    try System.IO.File.ReadAllText path |> Some
    with :? FileNotFoundException -> None
```

---

## Module Initialization Anti-Patterns

### ❌ Module-level static initialization with side effects

```fsharp
// ❌ FORBIDDEN
module MyApi =
    let config = File.ReadAllText "/config.txt"        // Side effect at init
    let envVar = Environment.GetEnvironmentVariable "X" // Side effect at init

// ✔️ ALTERNATIVE — use class with dependency injection
type MyApi(config: string, envVar: string) =
    member _.Config = config
    member _.EnvVar = envVar
```

### ❌ Non-thread-safe statically initialized values

```fsharp
// ❌ FORBIDDEN
module MyApi =
    let private r = Random()
    let getNext() = r.Next()  // Not thread safe

// ✔️ ALTERNATIVE — thread-local or injected
type MyApi(rng: Random) =
    member _.GetNext() = lock rng (fun () -> rng.Next())
```

---

## Formatting Anti-Patterns

### ❌ Tabs for indentation

Tabs cause compiler errors outside string literals and comments. Always use spaces.

### ❌ Aligning code to name length

```fsharp
// ❌ FORBIDDEN — breaks on rename
let myLongValueName   = someExpression
                       |> anotherExpression

// ✔️ ALTERNATIVE
let myLongValueName =
    someExpression
    |> anotherExpression
```

### ❌ `yield` keyword when not required

```fsharp
// ❌ FORBIDDEN (modern F#)
let items = [ for x in 1..10 do yield x * x ]

// ✔️ ALTERNATIVE
let items = [ for x in 1..10 -> x * x ]
```

---

## Type Design Anti-Patterns

### ❌ Implementation inheritance for polymorphism

```fsharp
// ❌ FORBIDDEN
type Animal() =
    abstract member Speak: unit -> string

type Dog() =
    inherit Animal()
    override _.Speak() = "Woof"

// ✔️ ALTERNATIVE — interface-based polymorphism
type IAnimal =
    abstract Speak: unit -> string

type Dog() =
    interface IAnimal with
        member _.Speak() = "Woof"
```

### ❌ Indiscriminate `[<AutoOpen>]` usage

```fsharp
// ❌ FORBIDDEN — pollutes global scope
[<AutoOpen>]
module EverythingEverywhere =
    let helper1 x = x + 1
    let helper2 x = x * 2
    type MyType = { X: int }

// ✔️ ALTERNATIVE — qualified access or targeted AutoOpen
[<RequireQualifiedAccess>]
module Helpers =
    let helper1 x = x + 1
    let helper2 x = x * 2
```

---

## .NET Interop Anti-Patterns

### ❌ Exposing F# function types in .NET-facing APIs

```fsharp
// ❌ FORBIDDEN — C# sees FSharpFunc<int, int>
member this.Transform(f: int -> int) = ...

// ✔️ ALTERNATIVE
member this.Transform(f: Func<int, int>) = ...
```

### ❌ Returning F# lists/maps in .NET-facing APIs

```fsharp
// ❌ FORBIDDEN — C# sees FSharpList<string>
member this.GetNames() : string list = ...

// ✔️ ALTERNATIVE
member this.GetNames() : seq<string> = ...
```

### ❌ Exposing F# union types in .NET-facing APIs

```fsharp
// ❌ FORBIDDEN — unfamiliar to C# consumers
type Result =
    | Success of int
    | Failure of string

// ✔️ ALTERNATIVE — hide with private, expose methods
type Result =
    private
    | Success of int
    | Failure of string

    member x.IsSuccess = match x with Success _ -> true | _ -> false
    member x.Value = match x with Success v -> v | _ -> invalidOp "No value"
```

---

## Quick Reference

| Pattern | Verdict | Alternative |
|---------|---------|-------------|
| Partial application in public API | ❌ | Explicit parameters |
| Point-free in public API | ❌ | Named let bindings |
| `failwith` / `failwithf` | ❌ | `invalidArg`, `nullArg`, `invalidOp`, `raise` |
| Nested `Result<Result<...>>` | ❌ | Typed DU or exceptions |
| Catch-all `with _ ->` | ❌ | Catch specific exceptions |
| Module-level side effects | ❌ | Class with DI |
| Tabs | ❌ | 4 spaces |
| Name-length alignment | ❌ | Standard indentation |
| `[<AutoOpen>]` on public modules | ❌ | `[<RequireQualifiedAccess>]` |
| F# function types in .NET APIs | ❌ | `Func<>` / `Action<>` |
| F# lists in .NET APIs | ❌ | `seq<T>` / `IEnumerable<T>` |
| Implementation inheritance | ❌ | Interfaces |
