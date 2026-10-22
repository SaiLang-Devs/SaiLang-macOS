# The SaiLang Windows installer

The Windows files are built by `installer/build_installer.py` (Windows or Linux, with NSIS installed):

    python installer/build_installer.py

This produces, in `dist/windows/`:

| File | What it does |
|---|---|
| `SaiLang-Setup-v1.0.0.exe` | The setup wizard. Installs SaiLang for the current user. |
| `SaiLang-IDLE.exe` | Opens SaiLang IDLE, using the Python already on the computer. |
| `sai.exe` | Runs `.sai` files or opens the SaiLang prompt in a console window. |

## What the wizard does

1. Checks for Python 3.9 or newer. If it is missing, it offers the python.org download page.
2. Shows the welcome, licence and folder pages. The default folder is `%LOCALAPPDATA%\Programs\SaiLang`.
3. Copies SaiLang, the examples, the documentation and the launchers.
4. Adds Start Menu entries (SaiLang IDLE, SaiLang Prompt, Examples, Uninstall) and a desktop shortcut.
5. Makes `.sai` files open in SaiLang IDLE for the current user.
6. Adds an entry to Installed apps so that SaiLang can be uninstalled.

No administrator rights are needed.

## Testing done

* The three programs compile as 32-bit Windows executables.
* The setup wizard was run silently (`SaiLang-Setup-v1.0.0.exe /S`) under Wine 9.0 on Linux, with a placeholder Python registered. It created the program folder, the Start Menu entries, the desktop shortcut, the file association and the uninstall entry. The uninstaller removed everything.
* The command that `sai.exe` runs was checked against the installed program.

## Not yet tested

* A real Windows 10 or 11 computer with real Python installed.
* Launching SaiLang IDLE through the launcher, because Wine has no Python to run.

## Code signing

The programs are not digitally signed. Smart App Control may block unsigned programs. Signing needs a code-signing certificate from a trusted authority.
