# SaiLang Language Specification (version 1.0)

This document describes every rule of SaiLang 1.0. Anything not described here
is not part of the language.

## 1. Source files

* Source files end in `.sai` and are plain text in UTF-8.
* Each statement sits on its own line.
* `#` starts a comment that runs to the end of the line.
* Blocks are wrapped in `{` and `}`. The opening `{` must be on the same line
  as the statement it belongs to.

## 2. Values

| Type         | Examples                       | Notes                                   |
|--------------|--------------------------------|-----------------------------------------|
| number       | `42`, `3.5`, `-7`              | Whole numbers and decimals              |
| text         | `"Hello"`                      | Escapes: `\n`, `\t`, `\"`, `\\`         |
| truth value  | `true`, `false`                | Used by conditions                      |
| nothing      | `nothing`                      | The empty value                         |
| list         | `[1, "two", true]`             | Ordered, may mix types, may span lines  |
| command      | created by `command`           | Can be passed around by name only       |

## 3. Variables

```sai
make name = "Sai"      # creates name, or updates it if it already exists here
name = "Alex"          # updates an existing name; error if it does not exist
```

Scope rules:

* The top level of a file has one scope. Blocks (`when`, `repeat`, `while`,
  `for each`, `try`) do **not** create a new scope.
* Each command call has its own scope. Inside a command, `make` creates a
  local variable. It never changes a top-level variable of the same name.
* Inside a command, a plain `name = value` changes the nearest existing
  variable, including top-level variables. Use this to update a score or
  counter from inside a command.
* A command can read top-level variables but cannot see the caller's local
  variables.
* Loop variables from `for each` stay available after the loop.

## 4. Operators

| Operators                 | Meaning                                                   |
|---------------------------|-----------------------------------------------------------|
| `+`                       | Adds numbers; joins text (a number is turned into text); joins two lists |
| `-` `*` `/` `%`           | Subtract, multiply, divide, remainder (numbers only)      |
| `==` `!=`                 | Equal / not equal. `true` is never equal to `1`.          |
| `<` `<=` `>` `>=`         | Compare two numbers or two texts                          |
| `and` `or` `not`          | Logic on truth values. `and` / `or` stop early when possible. |
| `-x`                      | Negate a number                                           |
| `list[i]`                 | Read item `i` (starts at 0) of a list or character of text |

Division of two whole numbers gives a whole number when the result is exact
(`8 / 2` is `4`); otherwise it gives a decimal (`7 / 2` is `3.5`). Dividing by
zero is an error.

Precedence, from tightest to loosest binding:

1. Negation `-x` and list positions `list[i]`
2. `*` `/` `%`
3. `+` `-`
4. Comparisons `==` `!=` `<` `<=` `>` `>=` (these do not chain: write
   `a < b and b < c`, not `a < b < c`)
5. `not`
6. `and`
7. `or`

Use brackets whenever you are unsure.

## 5. Output and input

```sai
say "Hello", name, 5        # prints the parts separated by spaces
make answer = ask("Your name? ")
```

`say` with no parts prints an empty line.

## 6. Conditions

```sai
when score >= 50 {
    say "Level complete!"
} otherwise when score >= 20 {
    say "Halfway"
} otherwise {
    say "Keep going"
}
```

A condition must be `true` or `false`. Anything else is an error, so
`when "yes" { }` does not work.

## 7. Loops

```sai
repeat 5 times { say "hi" }          # the count must be a whole number, 0 or more
while count > 0 { count = count - 1 }
for each item in items { say item }  # works on lists and text
```

Inside any loop:

* `stop` leaves the loop.
* `skip` jumps to the next pass of the loop.

## 8. Commands

```sai
command add(a, b) {
    give a + b
}
say add(2, 3)            # 5
```

* `give value` returns a value and leaves the command. `give` with no value
  returns `nothing`. A command that never gives anything returns `nothing`.
* A call must have exactly as many inputs as the command has parameters.
* Commands may call themselves. Very deep recursion stops with an error.
* A command must be defined before it is called. Programs run from top to
  bottom, so a `command` block must come above the first line that calls it.
  Commands defined in an imported file are available once the `import` line has run.

## 9. Errors and try

```sai
try {
    say 10 / 0
} on error {
    say "Problem:", error_message
}
```

Inside `on error`, the variable `error_message` holds the message text.
Errors raised outside a `try` stop the program and print:

```
file.sai:12: I don't know a variable called 'scroe'
```

Syntax errors use the same format and appear before the program runs.
`sai check file.sai` reports them without running the file.

## 10. Modules

```sai
import "lib/mathtools.sai"
```

The path is relative to the file that contains the `import`. Each file is
loaded once, even if imported twice. Everything the imported file defines
becomes available at the top level of the importing program.

## 11. Grammar summary

```
program    := { statement NEWLINE }
statement  := make | assign | setindex | say | when | repeat | while | for
            | stop | skip | command | give | import | try | call
make       := "make" NAME "=" expr
assign     := NAME "=" expr
setindex   := index "=" expr
say        := "say" [ expr { "," expr } ]
when       := "when" expr block { "otherwise" "when" expr block } [ "otherwise" block ]
repeat     := "repeat" expr "times" block
while      := "while" expr block
for        := "for" "each" NAME "in" expr block
stop       := "stop"            skip := "skip"
command    := "command" NAME "(" [ NAME { "," NAME } ] ")" block
give       := "give" [ expr ]
import     := "import" TEXT
try        := "try" block "on" "error" block
call       := NAME "(" [ expr { "," expr } ] ")"
block      := "{" { statement NEWLINE } "}"
expr       := or-expression, using the operators in section 4
```

## 12. Reserved words

`make say when otherwise repeat times while for each in stop skip command give
import try on error true false nothing and or not`

Words such as `length`, `text`, `number`, and `label` are standard library
commands. You may use them as variable names, but then they hide the command of
the same name.
