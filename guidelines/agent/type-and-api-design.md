# Type and API Design

> **Role**: Agent guidance — shapes type design, API shape, and architectural patterns.
>
> **Source**: [F# Coding Conventions](https://learn.microsoft.com/en-us/dotnet/fsharp/style-guide/conventions) and [Component Design Guidelines](https://learn.microsoft.com/en-us/dotnet/fsharp/style-guide/component-design-guidelines)

---

## Object and Type Design

### Use methods and properties for operations intrinsic to object types

```fsharp
// ✔️ Methods and properties on the type
type HardwareDevice() =
    member this.ID = ...
    member this.SupportedProtocols = ...

type HashTable<'Key,'Value>(comparer: IEqualityComparer<'Key>) =
    member this.Add(key, value) = ...
    member this.ContainsKey(key) = ...
    member this.ContainsValue(value) = ...
```

### Use classes to encapsulate mutable state

Only when state isn't already encapsulated by closures, sequences, or async computations:

```fsharp
// ✔️ Class encapsulates mutable state
type Counter() =
    let mutable count = 0
    member this.Next() =
        count <- count + 1
        count
```

### Use interfaces to represent sets of operations

Preferred over records of functions or tuples of functions:

```fsharp
// ✔️ Interface — first-class .NET concept, supports existential types
type ISerializer =
    abstract Serialize<'T> : preserveRefEq:bool -> value:'T -> string
    abstract Deserialize<'T> : preserveRefEq:bool -> pickle:string -> 'T

// ❌ Record of functions — less flexible, no existential types
type Serializer<'T> = {
    Serialize: bool -> 'T -> string
    Deserialize: bool -> string -> 'T
}
```

### Use modules to group functions that act on collections

Follow the `CollectionType.map`, `CollectionType.iter` pattern:

```fsharp
module OrderCollection =
    let map f orders = orders |> List.map f
    let filter predicate orders = orders |> List.filter predicate
    let tryFind id orders = orders |> List.tryFind (fun o -> o.Id = id)
```

---

## Discriminated Unions

### Use DUs instead of class hierarchies for tree-structured data

```fsharp
// ✔️ Elegant with DUs
type BST<'T> =
    | Empty
    | Node of 'T * BST<'T> * BST<'T>

// ❌ Awkward with inheritance
type BSTBase<'T>() = ...
type EmptyBST<'T>() = inherit BSTBase<'T>() ...
type NodeBST<'T>(value, left, right) = inherit BSTBase<'T>() ...
```

### Use `[<RequireQualifiedAccess>]` on DUs with non-unique case names

```fsharp
[<RequireQualifiedAccess>]
type Color =
    | Red
    | Green
    | Blue

// Usage: Color.Red (not just Red)
```

### Hide DU representations for evolving APIs

If the design is likely to change, use `private` cases and provide active patterns or member methods:

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

## Avoid Implementation Inheritance

Inheritance hierarchies are complex and difficult to change. Prefer:
- Interface implementation for polymorphism
- Composition over inheritance
- DUs for variant types

---

## Partial Application and Point-Free

### Avoid in public APIs

Partial application in public APIs confuses consumers. Point-free code loses argument names in tooling.

```fsharp
// ✔️ Explicit parameters — tooling shows names
let func name age =
    printfn $"My name is {name} and I am %d{age} years old!"
// Tooltip: val func : name:string -> age:int -> unit

// ❌ Point-free — no parameter names in tooling
let funcWithApplication =
    printfn "My name is %s and I am %d years old!"
// Tooltip: val funcWithApplication : (string -> int -> unit)
```

### Use internally for reducing boilerplate

Partial application is excellent for internal code and testing:

```fsharp
module TransactionsTestable =
    let getTestableTransactionRoutine mockContext =
        Transactions.doTransaction mockContext

// In tests — no need to construct mock context each time
let transactionRoutine = getTestableTransactionRoutine testableContext

[<Fact>]
let ``Test withdrawal with 0.0 balance``() =
    let actual = transactionRoutine TransactionType.Withdraw 0.0
    Assert.Equal(expected, actual)
```

---

## Async and Task

### Use `Async<T>` at F# API boundaries

```fsharp
type SomeType =
    member this.Compute(x: int) : int = ...
    member this.AsyncCompute(x: int) : Async<int> = ...
```

### Use `Task<T>` for .NET consumers

```fsharp
type MyType() =
    let compute (x: int) : Async<int> = async { return x * 2 }
    member this.ComputeAsync(x) = compute x |> Async.StartAsTask
    member this.ComputeAsync(x, cancellationToken) =
        Async.StartAsTask(compute x, cancellationToken = cancellationToken)
```

---

## Signature Files (.fsi)

Consider explicit signature files for stable library APIs:
- Provides succinct summary of public API surface
- Clean separation between public docs and internal implementation
- Adds friction to public API changes (good for stability)
- Only introduce when API has solidified

---

## Operator Definitions

Avoid defining custom symbolic operators in public APIs:
- Hard to document
- Hard to search for
- Confusing for new users

Publish functionality as named functions/members. Additionally expose operators only if notational benefits clearly outweigh cognitive cost.

```fsharp
// ✔️ Named function (primary API)
type Vector(x: float) =
    member v.X = x
    member v.Scale(scalar) = Vector(v.X * scalar)
    member v.Add(other: Vector) = Vector(v.X + other.X)

    // Additional operators for mathematical convenience
    static member (*) (vector: Vector, scalar: float) = vector.Scale(scalar)
    static member (+) (v1: Vector, v2: Vector) = v1.Add(v2)
```
