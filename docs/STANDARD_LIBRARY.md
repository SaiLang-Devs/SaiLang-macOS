# SaiLang Standard Library (version 1.0)

Every command below is always available. Some groups need Tkinter (see
`DESKTOP_APPS.md`). Commands with a fixed number of inputs report an error if
you give a different number.

## Text

| Command                 | Result                                             |
|-------------------------|----------------------------------------------------|
| `length(x)`             | Number of characters or list items                 |
| `upper(s)` / `lower(s)` | Text in capitals or small letters                  |
| `trim(s)`               | Text without spaces at each end                    |
| `split(s)` / `split(s, sep)` | List of parts (split on spaces by default)    |
| `join(list, sep)`       | Text made by joining the items with `sep`          |
| `replace(s, old, new)`  | Text with every `old` swapped for `new`            |
| `text(x)`               | Any value as text                                  |
| `number(x)`             | Text as a number; error if it is not a number      |
| `contains(x, item)`     | `true` if the text or list contains the item       |

## Lists

| Command                 | Result                                             |
|-------------------------|----------------------------------------------------|
| `append(list, value)`   | Adds `value` to the end of the list                |
| `remove_at(list, i)`    | Removes the item at position `i`                   |
| `range(n)`              | `[0, 1, ..., n-1]`                                 |
| `range(a, b)`           | `[a, ..., b-1]`                                    |
| `min(...)` / `max(...)` | Smallest or largest number; takes numbers or one list |

## Maths

| Command                 | Result                                             |
|-------------------------|----------------------------------------------------|
| `abs(x)`                | Absolute value                                     |
| `round(x)` / `round(x, digits)` | Rounded number                             |
| `floor(x)` / `ceil(x)`  | Round down / up to a whole number                  |
| `sqrt(x)`               | Square root (`x` must be zero or more)             |
| `random(low, high)`     | Random whole number from low to high inclusive, or decimal if either is a decimal |
| `now()`                 | Seconds since 1 January 1970                       |

## Types

| Command                 | Result                                             |
|-------------------------|----------------------------------------------------|
| `type_of(x)`            | `"number"`, `"text"`, `"truth value"`, `"nothing"`, `"list"`, `"command"`, or a window type |

## Input and files

| Command                         | Result                                      |
|---------------------------------|---------------------------------------------|
| `ask(prompt)`                   | Asks the user and returns the text they type |
| `read_file(path)`               | The whole file as text                      |
| `write_file(path, text)`        | Creates or replaces the file                |
| `append_file(path, text)`       | Adds text to the end of the file            |
| `file_exists(path)`             | `true` or `false`                           |

File errors are reported with the file name and the reason, such as
"I could not read 'notes.txt': No such file or directory". Catch them with
`try ... on error`.

## Desktop windows (Tkinter)

See `DESKTOP_APPS.md` for examples.

| Command                              | Result                                   |
|--------------------------------------|------------------------------------------|
| `open_window(title, width, height)`  | Opens a window and returns it            |
| `label(window, text)`                | Adds text to a window                    |
| `button(window, text, "command")`    | Adds a button that calls the named command |
| `entry(window)`                      | Adds a single-line text box              |
| `entry_text(entry)`                  | The text in the box                      |
| `set_text(widget, text)`             | Changes a label, button, or text box     |
| `show_image(window, source)`         | Shows a PNG or GIF from a file or http(s) URL |
| `run_app()`                          | Shows the windows and waits until they close |

## Games

| Command                                   | Result                                      |
|-------------------------------------------|---------------------------------------------|
| `open_game(title, width, height)`         | Opens a window with a drawing area          |
| `clear_screen()`                          | Removes everything drawn                    |
| `draw_rect(x, y, w, h, color)`            | Filled rectangle                            |
| `draw_circle(x, y, radius, color)`        | Filled circle                               |
| `draw_text(x, y, text, color)`            | Text at the top left corner of (x, y)       |
| `key_down("left")`                        | `true` while that key is held. Names: `left`, `right`, `up`, `down`, `space`, letters such as `a` |
| `overlaps(x1, y1, w1, h1, x2, y2, w2, h2)`| `true` if two rectangles overlap           |
| `every(milliseconds, "command")`          | Calls the command repeatedly (the game loop) |
| `stop_timer()`                            | Stops the repeating command                 |

Colours can be names such as `"red"`, `"blue"`, `"gold"`, `"green"`, or `"black"`, or
hex codes such as `"#ff8800"`.
