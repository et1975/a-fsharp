---
name: fsharp-interop
description: >-
  Use ONLY when user explicitly says 'this targets C# consumers', 'targets
  non-F# .NET consumers', or 'enable interop checks' — opt-in, never
  activated by default.
---

# F# .NET Interop Skill

## Announcement
> Using **fsharp-interop** — applying .NET consumer API rules on top of idiomatic F# defaults.

## When to Activate

This skill is **opt-in only**. The default F# coding and validation skills reason in idiomatic F#. Interop rules apply **only to the .NET-facing façade surface**, not to internal domain code. Only activate when the user explicitly requests it.

## API Surface Rules

| F# Idiom | .NET-Facing Replacement |
|-----------|------------------------|
| `int -> int` (arrow type) | `Func<int, int>` / `Action<T>` |
| `Async<T>` | `Task<T>` (default is already `task{}`; use `Async.StartAsTask` only for legacy `async{}` code) |
| `string list`, `Map<K,V>` | `seq<T>` / `IEnumerable<T>` / `IDictionary<K,V>` |
| `Option<T>` | TryGetValue pattern (`bool` + `byref<T>`) |
| Curried parameters | Tupled parameters |
| F# optional params `?x` | Method overloading |
| F# modules | Static classes (`[<AbstractClass; Sealed>]`) |
| Public DU cases | Private cases + static factory methods |
| F# `Event<T>` | `DelegateEvent<EventHandler<TArgs>>` + `[<CLIEvent>]` |
| `float * float` tuple return | Named record/class type |

## Required Checks (façade surface only)

- [ ] Null checks at all .NET API entry points
- [ ] `Func<>`/`Action<>` for callback parameters (not F# arrow types)
- [ ] `Task<T>` for async returns (not `Async<T>`)
- [ ] `seq<T>`/`IEnumerable<T>` for collection returns (not F# list/map/set)
- [ ] Tupled arguments on all public methods
- [ ] DU cases `private` with static factory methods and member accessors
- [ ] `[<CLIEvent>]` with `DelegateEvent<EventHandler<TArgs>>` for events
- [ ] XML documentation (`///`) on all public types and members
- [ ] No tuples as return values (use named types)
- [ ] TryGetValue pattern instead of `Option` in public API
- [ ] Method overloading instead of F# optional parameters
- [ ] `[<CompiledName>]` where F# and .NET naming conventions diverge

## Design Pattern

Design internally in idiomatic F#, then create a .NET-friendly façade:

```fsharp
// Internal — idiomatic F#
module internal OrderLogic =
    let validate (order: Order) : Result<Order, OrderError> = ...

/// <summary>Order operations for .NET consumers.</summary>
type OrderService(store: IOrderStore) =
    /// <summary>Validates an order.</summary>
    /// <param name="order">The order to validate.</param>
    /// <exception cref="ArgumentNullException">When order is null.</exception>
    /// <exception cref="ValidationException">When validation fails.</exception>
    member _.ValidateAsync(order: Order, cancellationToken: CancellationToken) : Task<Order> =
        if isNull (box order) then nullArg (nameof order)
        task {
            match OrderLogic.validate order with
            | Ok valid -> return valid
            | Error error -> return raise (ValidationException(error.ToDisplayString()))
        }
```

## Cautions

- **Units of measure**: erased at runtime, invisible to C#.
- **Type abbreviations**: invisible to .NET consumers. Wrap in class or DU instead.
