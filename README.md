# SaiLang 1.0.0

SaiLang is a general-purpose programming language with easy, English-like
commands. It is designed for beginners and for experienced developers who want
a small, readable language for scripts, desktop windows, and simple games.

```sai
make player = "Sai"
make score = 0

say "Welcome to SaiLang!"

command greet(name) {
    say "Hello,", name
}

greet(player)

repeat 5 times {
    make score = score + 10
    say "Score:", score
}

when score >= 50 {
    say "Level complete!"
} otherwise {
    say "Keep playing!"
}
```

## What is included

* Variables, numbers, text, truth values, `nothing`, and lists
* `when` / `otherwise`, `repeat ... times`, `while`, `for each`, `stop`, `skip`
* Commands with inputs and results, recursion
* `try ... on error`, with errors that show the file and line
* Modules with `import`
* Standard library for text, lists, maths, files, and user input
* Desktop windows, buttons, text boxes, and PNG/GIF images
* Game drawing, keyboard input, a game loop, and collision checks
* A command-line runner, a `check` command, and an interactive prompt
* SaiLang IDLE: an editor with syntax colours, a run button, and error highlighting

## Requirements

* Windows 10 or Windows 11
* Python 3.9 or newer, from https://www.python.org/downloads/. No administrator
  rights are needed. Tick "tcl/tk and IDLE" for windows and games.

## SaiLang IDLE (editor and runner)

Run `SaiLang-Setup-v1.0.0.exe` to install it, then open **SaiLang IDLE** from the Start Menu or desktop (or use `python -m sailang idle`). You can open,
edit, save, check, and run `.sai` files from one window. See `docs/IDLE.md`.
This is the easiest way to use SaiLang on a computer where Smart App Control
blocks `.bat` files.

## Quick start (Windows)

Open Command Prompt in the SaiLang folder and run:

```
sai.bat examples\hello.sai          run a program
sai-repl.bat                        start the interactive prompt
sai.bat check examples\hello.sai    check a program without running it
sai.bat examples\desktop_app.sai    desktop window demo
sai.bat examples\image_viewer.sai   image viewer demo
sai.bat examples\coin_collector_game.sai   playable game (arrow keys)
```

On Linux or macOS, use `python3 -m sailang examples/hello.sai` with
`PYTHONPATH=src` set. A full beginner guide is in `docs/GETTING_STARTED.md`.

## Documentation

| File | Contents |
|------|----------|
| `docs/GETTING_STARTED.md` | Setup, first programs, and FAQ |
| `docs/LANGUAGE_SPEC.md` | Every language rule, with grammar |
| `docs/STANDARD_LIBRARY.md` | Every built-in command |
| `docs/DESKTOP_APPS.md` | Windows, images, and games |
| `docs/IDLE.md` | The SaiLang IDLE editor |
| `docs/PUBLISHING.md` | GitHub release and Windows distribution |

## Testing

```
python -m unittest discover -s tests -v
```

GUI tests run only when a display is available. See `docs/DESKTOP_APPS.md`.

## Limitations in version 1.0.0

* SaiLang runs `.sai` files through a Python engine. It does **not** compile
  to native `.exe` files or bytecode yet.
* Images: PNG and GIF only. JPEG is not supported without extra libraries.
* Desktop windows and games use Tkinter, so Python's "tcl/tk" option must be installed.
* The `.bat` launchers were written for Windows but could not be run on Windows
  while preparing this release. The same commands were tested on Linux. Please
  report any problem with the launchers.
* No Windows installer is included. The download is a portable ZIP.
* No classes, dictionaries, or user-defined types yet.

## Licence

MIT. See `LICENSE`.
