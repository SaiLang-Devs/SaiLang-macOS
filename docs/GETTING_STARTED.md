# Getting Started with SaiLang (Windows 10 and 11)

## 1. Check you have Python

SaiLang's engine is written in Python. You need **Python 3.9 or newer**.

1. Open the Start menu and type `cmd`. Open **Command Prompt**.
2. Type `python --version` and press Enter.
   * If you see `Python 3.x.x`, you are ready.
   * If you see an error, install Python:
     1. Go to https://www.python.org/downloads/ and download the Windows installer.
     2. Run it. Choose **Customize installation** and tick **tcl/tk and IDLE**
        (needed for windows and games).
     3. On the next screen choose **Install for me only**. This does not need
        administrator rights.
     4. Close Command Prompt and open a new one.

## 2. Unpack SaiLang

Right-click `SaiLang-v1.0.0.zip`, choose **Extract All**, and pick a folder such
as `Documents\SaiLang`. Do not run files from inside the ZIP preview.

## 3. Run the hello-world program

1. Open Command Prompt.
2. Go to the SaiLang folder. For example, if you extracted it to Documents:

   ```
   cd %USERPROFILE%\Documents\SaiLang\SaiLang-v1.0.0
   ```

3. Run the example:

   ```
   sai.bat examples\hello.sai
   ```

You should see:

```
Welcome to SaiLang!
Hello, Sai
Score: 10
...
Level complete!
```

## 4. Start the interactive prompt (REPL)

```
sai-repl.bat
```

Type a line and press Enter:

```
sai> make name = "Sai"
sai> say "Hello,", name
Hello, Sai
sai> exit
```

Blocks can span several lines. Type `{` at the end of a line and the prompt
changes to `...>` until you close the block with `}`.

## 5. Write your own program

Create a file called `my_game.sai` in the SaiLang folder with Notepad:

```sai
make lives = 3
say "You have", lives, "lives"
```

Run it with `sai.bat my_game.sai`.

## 6. Desktop windows, images, and games

```
sai.bat examples\desktop_app.sai
sai.bat examples\image_viewer.sai
sai.bat examples\coin_collector_game.sai
```

Close the window to finish the program. See `DESKTOP_APPS.md`.

## 7. Use SaiLang IDLE (the easy way)

Open **SaiLang IDLE** from the Start Menu or the desktop (installed by `SaiLang-Setup-v1.0.0.exe`). Use File > Open to load a
`.sai` file, press F5 to run it, and read the results in the output pane. See
`IDLE.md`. This does not depend on `.bat` files, so it works when Smart App
Control blocks them.

## 8. Check a program without running it

```
sai.bat check examples\hello.sai
```

## Frequently asked questions

**Do I need to be an administrator?** No. The Python installer can install for
just your user account, and SaiLang runs from its own folder.

**Is SaiLang a compiler that makes `.exe` files?** No, not in version 1.0. It
runs `.sai` files directly through the engine. See `LANGUAGE_SPEC.md` and the
README "Limitations" section.

**Why does `python` not work but `py` does?** Some computers have the Python
launcher `py` but not `python` on the path. `sai.bat` tries both.

**Windows opened the Microsoft Store when I typed `python`.** Turn off the
"App execution aliases" for python in Settings > Apps > Advanced app settings,
then install Python from python.org as above.

**Where do my files go?** `read_file`, `write_file`, and the other file
commands use paths relative to the folder you run SaiLang from.

**Can SaiLang open JPEG pictures?** Not in version 1.0. Use PNG or GIF.
