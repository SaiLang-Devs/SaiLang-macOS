# Changelog

## 1.0.0 - first release (language version 1.0)

- Lexer, parser, and tree-walking interpreter for `.sai` files.
- Variables (`make`, `=`), numbers, text, truth values, `nothing`, lists.
- `when` / `otherwise` / `otherwise when`, `repeat ... times`, `while`,
  `for each`, `stop`, `skip`.
- Commands with inputs and results (`command`, `give`), recursion.
- `try ... on error`, errors that name the file and line.
- Modules with `import "file.sai"`.
- Standard library: text, lists, maths, random numbers, files, user input.
- Desktop windows, buttons, text boxes, and PNG/GIF images (Tkinter).
- Game drawing, keyboard state, timers, and collision checks (Tkinter canvas).
- Command line runner, `check` command, and interactive prompt.
- SaiLang IDLE 1.0.0: editor with syntax colours, open/save, run, stop, syntax
  check, program input, and error-line highlighting. Start with
  `SaiLang-IDLE.exe` (installed by the setup wizard) or `python -m sailang idle`.
- Windows setup wizard `SaiLang-Setup-v1.0.0.exe` (installs for the current user, no administrator
  rights needed). Launchers `SaiLang-IDLE.exe` and `sai.exe` replace the `.pyw` launcher.

Not included in 1.0.0: native `.exe` compilation, bytecode compilation, JPEG
images, and an installer.
