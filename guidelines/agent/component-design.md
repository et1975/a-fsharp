# Component Design

> **Role**: Agent guidance — shapes library design, .NET interop strategy, and API surface decisions.
>
> **Source**: [F# Component Design Guidelines](https://learn.microsoft.com/en-us/dotnet/fsharp/style-guide/component-design-guidelines)

---

## Two Audiences, Two APIs

Every F# library needs to decide its audience:

| Audience | API Style | Key Patterns |
|----------|-----------|-------------|
| F#-facing | Idiomatic F# | Modules, pipelines, `Async<T>`, curried args, DUs |
| .NET-facing (vanilla) | .NET conventions | Classes, `Task<T>`, `Func<>`, tupled args, interfaces |

Most libraries should support both. Design the internal implementation in idiomatic F#, then create a .NET-friendly façade.

---

## General Guidelines

### Learn the .NET Library Design Guidelines

Regardless of the kind of F# coding you are doing, have working knowledge of the [.NET Library Design Guidelines](https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/). Most .NET programmers expect code to conform to them.

### Use XML documentation on all public APIs

```fsharp
/// A class for representing (x,y) coordinates
type Point =
    /// Computes the distance between this point and another
    member DistanceTo: otherPoint:Point -> float
```

Both `/// comment` and `///<summary>comment</summary>` forms are acceptable.

### Follow best practices for strings in .NET

Explicitly state cultural intent in string conversion and comparison where applicable.

---

## F#-Facing Library Design

### Use standard collection function patterns

```fsharp
module OrderCollection =
    let map f orders = ...
    let iter f orders = ...
    let filter predicate orders = ...
```

Follow naming conventions from `FSharp.Core` (e.g., `map`, `filter`, `iter`, `fold`).

### Use `RequireQualifiedAccess` for modules extending core collections

Strongly suggested when extending `Seq`, `List`, `Array`, or any module with `[<RequireQualifiedAccess>]`.

### Use F# extension members for idiomatic wrappers

```fsharp
type System.ServiceModel.Channels.IInputChannel with
    member this.AsyncReceive() =
        Async.FromBeginEnd(this.BeginReceive, this.EndReceive)

type System.Collections.Generic.IDictionary<'Key,'Value> with
    member this.TryGet key =
        let ok, v = this.TryGetValue key
        if ok then Some v else None
```

### Use `[<CompiledName>]` for .NET-friendly names

When you want one name for F# consumers and another for .NET:

```fsharp
type Vector(x: float, y: float) =
    member v.X = x
    member v.Y = y

    [<CompiledName("Create")>]
    static member create x y = Vector(x, y)

// F# usage: Vector.create 5.0 3.0
// C# usage: Vector.Create(5.0, 3.0)
```

---

## Vanilla .NET Library Design

When targeting C#, VB.NET, and other .NET consumers:

### Use namespaces, types, and members as organizational structure

Do NOT use F# modules for public APIs. Use static classes instead:

```fsharp
// ❌ F# module — appears as static class, unfamiliar to C# users
module Fabrikam

module Utilities =
    let Name = "Bob"
    let Add2 x y = x + y

// ✔️ Static class — familiar .NET pattern
namespace Fabrikam

[<AbstractClass; Sealed>]
type Utilities =
    static member Name = "Bob"
    static member Add(x, y) = x + y
    static member Add(x, y, z) = x + y + z  // Overloading works
```

### Use `Func<>` / `Action<>` instead of F# function types

F# function types appear as `FSharpFunc<T,U>` to other languages:

```fsharp
// ❌ F# function type — unfriendly to C#
member this.Transform(f: int -> int) = ...

// ✔️ .NET delegate — natural for C#
member this.Transform(f: Func<int, int>) = ...
```

### Use `IEnumerable<T>` instead of F# collection types

```fsharp
// ❌ F# list — C# sees FSharpList<string>
member this.PrintNames(names: string list) = ...

// ✔️ seq/IEnumerable — natural for .NET
member this.PrintNames(names: seq<string>) = ...
```

### Use TryGetValue pattern instead of F# Option

```fsharp
// ❌ F# Option — unfamiliar to C#
member this.ReturnOption() = Some 3

// ✔️ TryGetValue pattern — standard .NET
member this.ReturnBoolAndOut(outVal: byref<int>) =
    outVal <- 3
    true
```

### Use tupled arguments (not curried)

```fsharp
// ✔️ Tupled — standard .NET calling convention
member this.TupledArguments(str, num) = String.replicate num str
```

### Return `Task<T>` for async operations

```fsharp
type MyType() =
    let compute (x: int) : Async<int> = async { return x * 2 }
    member this.ComputeAsync(x) = compute x |> Async.StartAsTask
    member this.ComputeAsync(x, cancellationToken) =
        Async.StartAsTask(compute x, cancellationToken = cancellationToken)
```

### Use `[<CLIEvent>]` for .NET-compatible events

```fsharp
type MyEventArgs(x: int) =
    inherit System.EventArgs()
    member this.X = x

type MyGoodType() =
    let myEv = new DelegateEvent<EventHandler<MyEventArgs>>()

    [<CLIEvent>]
    member this.MyEvent = myEv.Publish
```

### Check for null at API boundaries

```fsharp
// ✔️ Null check at boundary
let checkNonNull argName (arg: obj) =
    match arg with
    | null -> nullArg argName
    | _ -> ()

// F# 9+: leverage null annotation syntax
let checkNonNull argName (arg: obj | null) =
    match arg with
    | null -> nullArg argName
    | _ -> ()
```

### Hide F# union types in vanilla APIs

```fsharp
type PropLogic =
    private
    | And of PropLogic * PropLogic
    | Not of PropLogic
    | True

    member x.Evaluate =
        match x with
        | And(a, b) -> a.Evaluate && b.Evaluate
        | Not a -> not a.Evaluate
        | True -> true

    static member CreateAnd(a, b) = And(a, b)
```

---

## Units of Measure

Use carefully. Additional typing information is **erased** when viewed by other .NET languages. C# consumers see `float` not `float<kg>`.

## Type Abbreviations

Use carefully. Abbreviated names are **not visible** to .NET consumers. Significant usage can make a domain appear more complex. Consider wrapping in a class or single-case DU instead.

```fsharp
// ❌ Type abbreviation — invisible to C#, leaks representation
type MultiMap<'Key,'Value> = Map<'Key,'Value list>

// ✔️ Wrapped type — proper abstraction
type MultiMap<'Key,'Value>(inner: Map<'Key,'Value list>) =
    member _.TryFind(key) = inner |> Map.tryFind key |> Option.defaultValue []
    member _.Add(key, value) = ...
```
