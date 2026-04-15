# Five Principles of Good F# Code

> **Role**: Agent guidance — shapes planning, architecture, and design decisions.
>
> **Source**: [F# Style Guide](https://learn.microsoft.com/en-us/dotnet/fsharp/style-guide/)

These five principles are the foundation for all F# coding decisions. Every other guideline in this repo stems from them.

---

## 1. Good F# code is succinct, expressive, and composable

F# has many features that allow you to express actions in fewer lines of code and reuse generic functionality. Composition of your own functions and those in the F# core library (or other libraries) is a part of routine idiomatic F# programming.

**Agent implication**: When planning code, prefer solutions that:
- Express intent in fewer lines without sacrificing clarity
- Reuse existing FSharp.Core, .NET BCL, or NuGet library functionality
- Compose small, focused functions rather than writing monolithic blocks

```fsharp
// ✔️ Composable — small functions composed via pipeline
let activeUsers =
    users
    |> List.filter isActive
    |> List.sortBy (fun u -> u.LastLogin)
    |> List.take 10

// ❌ Monolithic — hard to reuse or test individual steps
let activeUsers =
    let mutable result = []
    for u in users do
        if u.IsActive then
            result <- u :: result
    result
    |> List.sortBy (fun u -> u.LastLogin)
    |> List.truncate 10
```

---

## 2. Good F# code is interoperable

You should always be thinking about how other code will call into the code you're writing, including if they do so from another language like C#. The [F# Component Design Guidelines](https://learn.microsoft.com/en-us/dotnet/fsharp/style-guide/component-design-guidelines) describe interoperability in detail.

**Agent implication**: When planning APIs, ask:
- Will this be consumed only by F#, or also by C#/VB.NET?
- If cross-language: use .NET conventions (namespaces, `Func<>`, `Task<T>`, tupled args)
- If F#-only: use idiomatic F# (modules, pipelines, `Async<T>`, curried args)

```fsharp
// F#-facing API — idiomatic
module UserService =
    let findActive (users: User list) : User list =
        users |> List.filter (fun u -> u.IsActive)

// .NET-facing API — interoperable
type UserService() =
    member _.FindActive(users: IEnumerable<User>) : IEnumerable<User> =
        users |> Seq.filter (fun u -> u.IsActive)
```

---

## 3. Good F# code makes use of object programming, not object orientation

F# has full support for programming with objects in .NET. For more complicated functional code, such as functions that must be context-aware, objects can easily encapsulate contextual information in ways that functions cannot.

**Agent implication**: When planning architecture:
- Use objects when you need to encapsulate context, state, or configuration
- Use interfaces to define contracts (preferred over records of functions)
- Do NOT default to deep inheritance hierarchies — prefer composition and interfaces
- Use classes for dependency injection and testability

```fsharp
// ✔️ Object programming — encapsulates context
type Transactor(ctx: ITransactionContext, balance: decimal) =
    member _.Execute(txnType) =
        Transactions.doTransaction ctx txnType balance

// ✔️ Interface for contract
type ISerializer =
    abstract Serialize<'T> : value:'T -> string
    abstract Deserialize<'T> : data:string -> 'T

// ❌ Deep inheritance — avoid
type Animal() = ...
type Mammal() = inherit Animal() ...
type Dog() = inherit Mammal() ...
```

---

## 4. Good F# code performs well without exposing mutation

To write high-performance code, you must sometimes use mutation. But avoid exposing mutation to callers. Build a functional interface that hides a mutation-based implementation when performance is critical.

**Agent implication**: When planning for performance:
- Default to immutable data structures
- If mutation is needed for performance, encapsulate it inside a function or class
- Never expose mutable state in public APIs
- Consider `Array` over `List` for performance-critical paths (but return `seq<T>` or `IEnumerable<T>`)

```fsharp
// ✔️ Functional interface hiding mutation
let buildLookup (items: Item list) : Map<string, Item> =
    let dict = System.Collections.Generic.Dictionary()
    for item in items do
        dict[item.Key] <- item
    dict |> Seq.map (fun kv -> kv.Key, kv.Value) |> Map.ofSeq

// ❌ Exposing mutation
type ItemStore() =
    let mutable items = Dictionary<string, Item>()
    member _.Items = items  // Exposes mutable dictionary
    member _.Add(key, item) = items[key] <- item
```

---

## 5. Good F# code is toolable

Write F# code such that it can be used more effectively with F# language tooling. Don't overdo point-free style. Use `let` bindings for intermediate values so they can be inspected in a debugger. Use XML documentation comments.

**Agent implication**: When planning code structure:
- Prefer named `let` bindings over point-free composition for public APIs
- Add XML documentation (`///`) to all public types and members
- Use explicit type annotations on public API boundaries for clarity
- Ensure intermediate values are inspectable during debugging

```fsharp
// ✔️ Toolable — named parameters, inspectable intermediates
let processOrder (order: Order) : Result<Receipt, OrderError> =
    let validated = validateOrder order
    let priced = calculatePrice validated
    let receipt = generateReceipt priced
    Ok receipt

// ❌ Not toolable — point-free, no intermediate values
let processOrder =
    validateOrder >> calculatePrice >> generateReceipt >> Ok
```
