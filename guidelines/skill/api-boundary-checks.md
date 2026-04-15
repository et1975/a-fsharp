# API Boundary Checks

> **Role**: Skill enforcement — validation rules for API boundaries, especially .NET interop.
>
> **Source**: [F# Component Design Guidelines](https://learn.microsoft.com/en-us/dotnet/fsharp/style-guide/component-design-guidelines)

---

## Null Safety

### ✔️ CHECK: Null validation at .NET API boundaries

F# code tends to have fewer null values due to immutable design. But other .NET languages use null frequently. Check parameters at the API boundary.

```fsharp
// ✔️ Required — null check at boundary
let checkNonNull argName (arg: obj) =
    match arg with
    | null -> nullArg argName
    | _ -> ()

// Alternative using isNull
let checkNonNull' argName (arg: obj) =
    if isNull arg then nullArg argName

// F# 9+: compiler-assisted null checking
let checkNonNull argName (arg: obj | null) =
    match arg with
    | null -> nullArg argName
    | _ -> ()
```

### ✔️ CHECK: Handle nullable return values from .NET APIs

```fsharp
// ✔️ Pattern match on null from .NET APIs
let readLineFromStream (sr: System.IO.StreamReader) =
    let line = sr.ReadLine()  // May return null
    match line with
    | null -> None
    | s -> Some s
```

---

## Return Type Validation

### ✔️ CHECK: .NET-facing methods return `IEnumerable<T>` or `IDictionary<K,V>`

Not F# lists, maps, or sets.

```fsharp
// ✔️ Correct — seq is alias for IEnumerable<T>
member this.GetItems() : seq<Item> = ...

// ❌ Violation — F# list visible to C#
member this.GetItems() : Item list = ...

// ❌ Violation — F# Map visible to C#
member this.GetLookup() : Map<string, Item> = ...
```

### ✔️ CHECK: .NET-facing methods return `Task<T>` for async

Not `Async<T>`.

```fsharp
// ✔️ Correct
member this.ComputeAsync(x) : Task<int> =
    compute x |> Async.StartAsTask

// ❌ Violation
member this.ComputeAsync(x) : Async<int> =
    compute x
```

### ✔️ CHECK: Avoid tuples as return values in .NET-facing APIs

Use named types instead.

```fsharp
// ❌ Violation — tuple return
member this.GetCoordinates() : float * float = (x, y)

// ✔️ Correct — named type
type Coordinates = { X: float; Y: float }
member this.GetCoordinates() : Coordinates = { X = x; Y = y }
```

---

## Parameter Type Validation

### ✔️ CHECK: .NET-facing methods use `Func<>` / `Action<>` for callbacks

Not F# function types.

```fsharp
// ✔️ Correct
member this.Transform(f: Func<int, int>) = ...
member this.ForEach(action: Action<Item>) = ...

// ❌ Violation — F# function type visible as FSharpFunc
member this.Transform(f: int -> int) = ...
```

### ✔️ CHECK: .NET-facing methods use tupled arguments

Not curried.

```fsharp
// ✔️ Correct
member this.Add(x: int, y: int) = x + y

// ❌ Violation — curried parameters
member this.Add (x: int) (y: int) = x + y
```

### ✔️ CHECK: Use TryGetValue pattern instead of F# Option in .NET-facing APIs

```fsharp
// ✔️ Correct — standard .NET pattern
member this.TryGetValue(key, [<Out>] value: byref<'T>) : bool = ...

// ❌ Violation — F# Option unfamiliar to C#
member this.TryGetValue(key) : 'T option = ...
```

### ✔️ CHECK: Use method overloading instead of F# optional parameters

```fsharp
// ✔️ Correct
member this.Log(message: string) = ...
member this.Log(message: string, retryPolicy: RetryPolicy) = ...

// ❌ Violation — F# optional parameter
member this.Log(message: string, ?retryPolicy: RetryPolicy) = ...
```

---

## Event Validation

### ✔️ CHECK: Events use `[<CLIEvent>]` with `DelegateEvent<EventHandler<TArgs>>`

```fsharp
// ✔️ Correct — .NET compatible event
type MyEventArgs(x: int) =
    inherit System.EventArgs()
    member this.X = x

type MyGoodType() =
    let myEv = new DelegateEvent<EventHandler<MyEventArgs>>()

    [<CLIEvent>]
    member this.MyEvent = myEv.Publish

// ❌ Violation — F# Event type, not .NET compatible
type MyBadType() =
    let myEv = new Event<int>()

    [<CLIEvent>]
    member this.MyEvent = myEv.Publish
```

---

## Documentation Validation

### ✔️ CHECK: XML documentation on all public APIs

```fsharp
// ✔️ Correct
/// A class for representing (x,y) coordinates
type Point =
    /// Computes the distance between this point and another
    member DistanceTo: otherPoint:Point -> float

// ❌ Violation — no documentation on public type/member
type Point =
    member DistanceTo: otherPoint:Point -> float
```

---

## Unit Type Usage

### ✔️ CHECK: Unit type only as input/return for zero-arg/void methods

```fsharp
// ✔️ Correct
member this.NoArguments() = 3
member this.ReturnVoid(x: int) = ()

// ❌ Violation — unit as a parameter alongside others
member this.WrongUnit(x: unit, z: int) = ((), ())
```

---

## Summary Checklist

A skill validating API boundaries should check:

- [ ] Null checks present at all .NET API entry points
- [ ] Return types use `seq<T>` / `IEnumerable<T>` (not F# list/map/set) for .NET consumers
- [ ] Async operations return `Task<T>` for .NET consumers
- [ ] Callback parameters use `Func<>` / `Action<>` (not F# arrow types) for .NET consumers
- [ ] Methods use tupled arguments (not curried) for .NET consumers
- [ ] F# union types are hidden (`private`) in .NET-facing APIs
- [ ] Events use `[<CLIEvent>]` with `DelegateEvent<EventHandler<TArgs>>`
- [ ] All public types and members have XML documentation (`///`)
- [ ] No tuples as return values in .NET-facing APIs (use named types)
- [ ] TryGetValue pattern used instead of F# Option for .NET consumers
- [ ] Method overloading preferred over F# optional parameters for .NET consumers
- [ ] Unit type not used as a regular parameter
