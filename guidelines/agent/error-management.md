# Error Management

> **Role**: Agent guidance — shapes how errors are modeled and handled in F# code.
>
> **Source**: [F# Coding Conventions](https://learn.microsoft.com/en-us/dotnet/fsharp/style-guide/conventions#error-management)

---

## Decision Framework

| Error type | Approach | Why |
|-----------|----------|-----|
| Known failure modes in your domain | Discriminated Union | Type-safe, exhaustive pattern matching, testable |
| Truly exceptional/unknown failures | Exceptions | .NET ecosystem standard, detailed diagnostics, cross-language |
| Simple present/absent values | `Option<'T>` | Lightweight, no error detail needed |
| Basic success/failure with context | `Result<'S, 'E>` | When error info matters but nesting won't occur |

---

## Represent Error Cases in Discriminated Unions

When you can model the different ways something can **fail** in your domain, use DUs:

```fsharp
type MoneyWithdrawalResult =
    | Success of amount: decimal
    | InsufficientFunds of balance: decimal
    | CardExpired of DateTime
    | UndisclosedFailure

let handleWithdrawal amount =
    let w = withdrawMoney amount
    match w with
    | Success am -> printfn $"Successfully withdrew %f{am}"
    | InsufficientFunds balance -> printfn $"Failed: balance is %f{balance}"
    | CardExpired expiredDate -> printfn $"Failed: card expired on {expiredDate}"
    | UndisclosedFailure -> printfn "Failed: unknown"
```

**Benefits**:
- Error handling is normal program flow, not exceptional
- Compiler enforces exhaustive handling
- Easy to unit test each case
- Maintainable as domain evolves

---

## Use Exceptions for Truly Exceptional Failures

Not all errors can be represented in the domain. Use exceptions for these.

**Exception functions (in order of preference)**:

| Function | Raises | Use when |
|----------|--------|----------|
| `nullArg "name"` | `ArgumentNullException` | Null argument |
| `invalidArg "name" "msg"` | `ArgumentException` | Invalid argument |
| `invalidOp "msg"` | `InvalidOperationException` | Invalid state |
| `raise (ExType("msg"))` | Any specific exception | General purpose |
| ~~`failwith "msg"`~~ | ~~`System.Exception`~~ | ❌ **Avoid** — too generic |
| ~~`failwithf "fmt" args`~~ | ~~`System.Exception`~~ | ❌ **Avoid** — too generic |

```fsharp
// ✔️ Specific exception types
let validateAge age =
    if age < 0 then invalidArg (nameof age) "Age cannot be negative"
    elif age > 150 then invalidArg (nameof age) "Age seems unrealistic"
    else age

// ❌ Avoid — base Exception type
let validateAge age =
    if age < 0 then failwith "Age cannot be negative"
    else age
```

---

## Do NOT Replace Exceptions with Monadic Error Handling

Exceptions are well-understood by the .NET runtime, provide detailed diagnostics, and reduce boilerplate. Don't replace them with `Result` nesting:

```fsharp
// ❌ Leads to fragile, stringly-typed error handling
Result<Result<MyType, string>, string list>

// ❌ Swallows exception context
let tryReadAllText (path: string) =
    try System.IO.File.ReadAllText path |> Some
    with _ -> None   // What went wrong? Who knows.

// ❌ Stringly-typed error matching
match result with
| Error e ->
    if e.Contains "Error string 1" then ...
    elif e.Contains "Error string 2" then ...
    else ...
```

**Instead**: Catch *specific* exceptions and return meaningful values:

```fsharp
// ✔️ Specific exception → meaningful Option
let tryReadAllTextIfPresent (path: string) =
    try System.IO.File.ReadAllText path |> Some
    with :? FileNotFoundException -> None

// ✔️ Use Result for simple, non-nested cases
type ValidationError =
    | TooShort of minLength: int
    | InvalidCharacters of chars: char list

let validateUsername (name: string) : Result<string, ValidationError> =
    if name.Length < 3 then Error (TooShort 3)
    elif name |> Seq.exists (fun c -> not (Char.IsLetterOrDigit c)) then
        Error (InvalidCharacters (name |> Seq.filter (fun c -> not (Char.IsLetterOrDigit c)) |> Seq.toList))
    else Ok name
```

---

## Use Exception-Handling Syntax Idiomatically

```fsharp
// ✔️ Pattern matching on exception types
try
    tryGetFileContents()
with
| :? System.IO.FileNotFoundException as e -> handleMissing e
| :? System.Security.SecurityException as e -> handleSecurity e

// ✔️ Active patterns for extracting exception information
let (|HttpError|_|) (ex: exn) =
    match ex with
    | :? HttpRequestException as e -> Some e.StatusCode
    | _ -> None

try
    callApi()
with
| HttpError (Some code) when int code = 404 -> handleNotFound()
| HttpError _ -> handleApiError()
```

---

## Summary: When to Use What

```
Known failure modes?
    ├── Yes → Discriminated Union
    └── No → Is it truly exceptional?
        ├── Yes → Exception (specific type)
        └── No → Simple present/absent?
            ├── Yes → Option<'T>
            └── No → Result<'S, 'E> (non-nested only)
```
