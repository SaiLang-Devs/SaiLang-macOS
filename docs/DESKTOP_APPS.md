# Desktop Apps, Images, and Games

Desktop features use **Tkinter**, the windowing library that comes with the
official Python installer for Windows (tick "tcl/tk and IDLE" during setup).
If it is missing, SaiLang explains how to fix it instead of crashing.

## Your first window

```sai
make clicks = 0
make win = open_window("Counter", 300, 150)
make message = label(win, "You clicked 0 times")

command on_click() {
    clicks = clicks + 1
    set_text(message, "You clicked " + clicks + " times")
}

button(win, "Click me", "on_click")
run_app()
```

Points to remember:

* Buttons call a command **by its name in quotes**, such as `"on_click"`.
* Inside a command, use `clicks = clicks + 1` (not `make`) to change a
  top-level variable. See the scope rules in `LANGUAGE_SPEC.md`.
* `run_app()` must be the last line that creates or runs the window. It stays
  on screen until the user closes the window.

## Images

```sai
make win = open_window("Image Viewer", 420, 320)
show_image(win, "examples/assets/sample.png")
run_app()
```

* Local files and `http://` / `https://` addresses both work.
* Only **PNG and GIF** are supported in version 1.0. JPEG files give a clear error.
* Downloads time out after 10 seconds and are limited to 5 MB.
* An invalid address, a missing file, or a download failure gives a message
  that says what went wrong.

## Games

The coin collector example (`examples/coin_collector_game.sai`) shows the
pattern every game follows:

1. Set up variables for positions and the score.
2. `open_game(...)` creates a drawing area.
3. `every(33, "tick")` calls `tick` about 30 times a second.
4. `tick` reads keys with `key_down`, moves things, checks collisions with
   `overlaps`, clears the screen, and draws the new frame.
5. `stop_timer()` ends the game loop, for example when the player wins.
6. `run_app()` starts the window.

Controls in the example: arrow keys. Collect 5 coins to win.

## Testing without a screen

The automated tests for windows and games are skipped when no display is
available. On a Linux server, `xvfb-run python -m unittest discover -s tests`
runs them against a virtual display.
