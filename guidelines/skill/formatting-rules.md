# Formatting Rules

> **Role**: Skill enforcement — deterministic rules that validate code formatting.
>
> **Source**: [F# Code Formatting Guidelines](https://learn.microsoft.com/en-us/dotnet/fsharp/style-guide/formatting)

---

## Tooling

Use [Fantomas](https://github.com/fsprojects/fantomas) as the code formatter. Share its configuration within the team for consistency.

---

## Indentation and Whitespace

### ✔️ RULE: Use spaces, never tabs

Tabs cause compiler errors outside string literals and comments.

### ✔️ RULE: Use 4 spaces per indentation level

Consistent indentation is more important than the exact number, but 4 is recommended.

### ✔️ RULE: Do not align code based on variable/name length

```fsharp
// ✔️ OK
let myLongValueName =
    someExpression
    |> anotherExpression

// ❌ Not OK — alignment breaks on rename
let myLongValueName   = someExpression
                       |> anotherExpression
```

### ✔️ RULE: Avoid extraneous whitespace

Only use extra whitespace where explicitly specified in these rules.

---

## Comments

### ✔️ RULE: Prefer `//` comments over block comments

Use multiple `//`-style lines instead of `(* ... *)` block comments.

---

## Pattern Matching

### ✔️ RULE: `|` at same indentation level as `match`

```fsharp
// ✔️ OK
match l with
| { him = x; her = "Posh" } :: tail -> x
| _ :: tail -> findDavid tail
| [] -> failwith "Couldn't find David"

// ❌ Not OK
match l with
    | { him = x; her = "Posh" } :: tail -> x
    | _ :: tail -> findDavid tail
    | [] -> failwith "Couldn't find David"
```

### ✔️ RULE: No space before opening parenthesis of pattern arguments

```fsharp
// ✔️ OK
match x with
| Some(y) -> y
| None -> 0

// ❌ Not OK
match x with
| Some (y) -> y
| None -> 0
```

### ✔️ RULE: Spaces between curried arguments in patterns

```fsharp
// ✔️ OK
match x with
| Pattern arg (a, b) -> processValues arg a b

// ❌ Not OK
match x with
| Pattern arg(a, b) -> processValues arg a b
```

### ✔️ RULE: Do not align match arrows

```fsharp
// ✔️ OK
match lam with
| Var v -> v.Length
| Abstraction _ -> 2

// ❌ Not OK
match lam with
| Var v         -> v.Length
| Abstraction _ -> 2
```

### ✔️ RULE: Long match expressions — move right-hand side to next line

```fsharp
// ✔️ OK
match lam with
| Var v -> 1
| Abs(x, body) ->
    1 + sizeLambda body
| App(lam1, lam2) ->
    sizeLambda lam1 + sizeLambda lam2
```

---

## Records

### ✔️ RULE: Short records on one line

```fsharp
// ✔️ OK
let point = { X = 1.0; Y = 0.0 }
```

### ✔️ RULE: Multi-line records — use consistent bracket style

Three acceptable styles (Cramped, Aligned, Stroustrup). Pick one and be consistent:

```fsharp
// Cramped (historical default)
let rainbow =
    { Boss = "Jeffrey"
      Lackeys = ["Zippy"; "George"; "Bungle"] }

// Aligned
let rainbow =
    {
        Boss = "Jeffrey"
        Lackeys = ["Zippy"; "George"; "Bungle"]
    }

// Stroustrup
let rainbow = {
    Boss = "Jeffrey"
    Lackeys = ["Zippy"; "George"; "Bungle"]
}
```

---

## Lists and Arrays

### ✔️ RULE: Spaces after `[` and before `]`

```fsharp
// ✔️ OK
let xs = [ 1; 2; 3 ]
let ys = [| 1; 2; 3 |]

// ❌ Not OK
let xs = [1; 2; 3]
```

### ✔️ RULE: Space between distinct brace-like operators

```fsharp
// ✔️ OK — space between [ and {
[ { Ingredient = "Green beans"; Quantity = 250 }
  { Ingredient = "Pine nuts"; Quantity = 250 } ]

// ❌ Not OK
[{ Ingredient = "Green beans"; Quantity = 250 }
 { Ingredient = "Pine nuts"; Quantity = 250 }]
```

### ✔️ RULE: Prefer `->` over `do ... yield`

```fsharp
// ✔️ OK
let squares = [ for x in 1..10 -> x * x ]

// ❌ Not preferred
let squares = [ for x in 1..10 do yield x * x ]
```

### ✔️ RULE: Omit `yield` unless required by language version

```fsharp
// ✔️ OK
let daysOfWeek includeWeekend =
    [
        "Monday"
        "Tuesday"
        if includeWeekend then
            "Saturday"
            "Sunday"
    ]
```

---

## try/with

### ✔️ RULE: Exception patterns at same level as `with`

```fsharp
// ✔️ OK
try
    if System.DateTime.Now.Second % 3 = 0 then
        raise (new System.Exception())
with
| :? System.ApplicationException ->
    printfn "A second that was not a multiple of 3"
| _ ->
    printfn "A second that was a multiple of 3"
```

### ✔️ RULE: Single-clause `with` — no `|`

```fsharp
// ✔️ OK
try
    persistState currentState
with ex ->
    printfn "Something went wrong: %A" ex

// ❌ Not OK
try
    persistState currentState
with
| ex ->
    printfn "Something went wrong: %A" ex
```

---

## Named Arguments

### ✔️ RULE: Spaces around `=` in named arguments

```fsharp
// ✔️ OK
let makeStreamReader x = new System.IO.StreamReader(path = x)

// ❌ Not OK
let makeStreamReader x = new System.IO.StreamReader(path=x)
```

---

## Chained Expressions

### ✔️ RULE: Each chained invocation on its own line, indented one level

```fsharp
// ✔️ OK
Host
    .CreateDefaultBuilder(args)
    .ConfigureWebHostDefaults(fun webBuilder ->
        webBuilder.UseStartup<Startup>())

// ✔️ OK — leading link can combine namespace
Microsoft.Extensions.Hosting.Host
    .CreateDefaultBuilder(args)
    .ConfigureWebHostDefaults(fun webBuilder ->
        webBuilder.UseStartup<Startup>())
```

---

## Index/Slice Expressions

### ✔️ RULE: No spaces around brackets in index expressions

```fsharp
// ✔️ OK
let v = expr[idx]
let y = myList[0..1]

// ❌ Not OK
let v = expr[ idx ]
let y = myList[ 0 .. 1 ]
```

---

## Mutation Expressions

### ✔️ RULE: Long right-hand side on new line

```fsharp
// ✔️ OK
ctx.Response.Headers[HeaderNames.ContentType] <-
    Constants.jsonApiMediaType |> StringValues

// ❌ Not OK
ctx.Response.Headers[HeaderNames.ContentType] <- Constants.jsonApiMediaType
                                                 |> StringValues
```
