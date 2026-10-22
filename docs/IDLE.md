# SaiLang IDLE 1.0.0

SaiLang IDLE is an editor and runner for `.sai` programs, in the same spirit as
Python's IDLE. It is a Python program, so it works on computers where Smart
App Control blocks `.bat` files.

## Starting it

Any one of these works:

* Open **SaiLang IDLE** from the Start Menu or desktop. The setup wizard installs it.
* Double-click `SaiLang-IDLE.exe` in the SaiLang folder.
* Right-click a `.sai` file, choose **Open with > Choose another app**, pick
  **Python** (or `pythonw.exe` from your Python folder), and tick **Always use
  this app**. Then double-clicking `.sai` files opens them in IDLE.
* In Command Prompt, from the SaiLang folder: `python -m sailang idle hello.sai`

Requirements are the same as SaiLang itself: Python 3.9+ with "tcl/tk and IDLE"
ticked during installation.

## Using it

| Action | Menu | Key |
|---|---|---|
| New file | File > New | Ctrl+N |
| Open | File > Open | Ctrl+O |
| Save / Save As | File | Ctrl+S / Ctrl+Shift+S |
| Undo / Redo | Edit | Ctrl+Z / Ctrl+Y |
| Run the program | Run > Run Program | F5 |
| Check syntax without running | Run > Check Syntax | F6 |
| Stop a running program | Run > Stop Program | Esc |

* The output pane below the editor shows what the program prints.
* When a program asks a question with `ask(...)`, type the answer in the
  **Program input** box and press Enter.
* When a program has an error, IDLE highlights the line in red and moves the
  cursor there.
* Syntax colours: keywords blue, built-in commands teal, text green, numbers
  orange, comments grey.
* Pressing Enter keeps the indentation of the line above, and Tab inserts four spaces.
* The status bar shows the file name, the cursor position, and whether a
  program is running.

## How programs run

IDLE saves the file first, then runs it in a separate Python process
(`python -m sailang yourfile.sai`). Consequences:

* A program that opens windows (`open_window`, `run_app`) shows them as separate
  windows. Closing them ends the program.
* Stopping a program or closing IDLE ends its process.
* Relative file names in a program (such as `read_file("notes.txt")`) are
  relative to the folder the `.sai` file is in.
