# Naming Conventions

> **Role**: Skill enforcement — deterministic rules that validate naming.
>
> **Source**: [F# Component Design Guidelines](https://learn.microsoft.com/en-us/dotnet/fsharp/style-guide/component-design-guidelines#naming-conventions)

---

## Naming Table

| Construct | Case | Part | Examples | Notes |
|-----------|------|------|----------|-------|
| Concrete types | PascalCase | Noun/adjective | `List`, `Double`, `Complex` | Structs, classes, enums, delegates, records, unions |
| DLLs | PascalCase | | `Fabrikam.Core.dll` | |
| Union tags | PascalCase | Noun | `Some`, `Add`, `Success` | No prefix in public APIs. Internal: optionally `TAlpha`, `TBeta` |
| Events | PascalCase | Verb | `ValueChanged`, `ValueChanging` | |
| Exceptions | PascalCase | | `WebException` | **Must** end with `Exception` |
| Fields | PascalCase | Noun | `CurrentName` | |
| Interface types | PascalCase | Noun/adjective | `IDisposable` | **Must** start with `I` |
| Methods | PascalCase | Verb | `ToString` | |
| Namespaces | PascalCase | | `Microsoft.FSharp.Core` | Use `<Org>.<Technology>[.<Sub>]` |
| Parameters | camelCase | Noun | `typeName`, `transform`, `range` | |
| let values (internal) | camelCase or PascalCase | Noun/verb | `getValue`, `myTable` | |
| let values (external) | camelCase or PascalCase | Noun/verb | `List.map`, `Dates.Today` | PascalCase when used from other .NET languages |
| Properties | PascalCase | Noun/adjective | `IsEndOfFile`, `BackColor` | |
| Active Patterns | PascalCase | | `(|Even|Odd|)` | |
| Generic parameters | PascalCase | | `T`, `U`, `Key`, `Value`, `Arg` | Not `TKey` style |

---

## Boolean Properties

### ✔️ RULE: Prefix with `Is` or `Can` (affirmative)

```fsharp
// ✔️ OK — affirmative
member this.IsEndOfFile = ...
member this.CanExecute = ...

// ❌ Not OK — negative
member this.IsNotEndOfFile = ...
```

---

## Abbreviations

### ✔️ RULE: Avoid abbreviations

Use full words. `OnButtonClick` not `OnBtnClick`.

**Exception**: Common abbreviations tolerated in F#-to-F# code:
- `Async` for Asynchronous
- `List.iter` for iterate
- `Seq` for Sequence
- Standard abbreviations in FSharp.Core

### ✔️ RULE: Use well-known acronyms in .NET style

Acronyms like XML are used in uncapitalized form: `Xml` not `XML`.

Only well-known, widely recognized acronyms should be used.

---

## Casing

### ✔️ RULE: Never disambiguate names by casing alone

Some .NET languages (e.g., Visual Basic) are case-insensitive.

```fsharp
// ❌ Not OK — casing collision
type myType = ...
type MyType = ...
```

---

## Public Functions in F# Modules

### ✔️ RULE: Use either PascalCase or camelCase

- **camelCase** for functions designed to be used unqualified (like `invalidArg`) or standard collection functions (`List.map`)
- **PascalCase** for functions used from other .NET languages

In both cases, function names should act like keywords or follow .NET member conventions.

---

## Summary Checklist

A naming skill should validate:

- [ ] Types are PascalCase
- [ ] Parameters are camelCase
- [ ] Interfaces start with `I`
- [ ] Exceptions end with `Exception`
- [ ] Boolean properties start with `Is` or `Can`
- [ ] No abbreviations (except well-known F#/FSharp.Core abbreviations)
- [ ] No casing-only disambiguation
- [ ] Generic parameters are PascalCase single letters or descriptive names
- [ ] Namespaces follow `<Org>.<Technology>[.<Sub>]` pattern
