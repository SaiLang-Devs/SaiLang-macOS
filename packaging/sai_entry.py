"""Entry point used by PyInstaller to build the SaiLang program.

Double-clicking SaiLang.app (no arguments) opens SaiLang IDLE.
Running it from Terminal with arguments works like the `sai` command:
  SaiLang.app/Contents/MacOS/SaiLang file.sai
"""
import sys

from sailang.cli import main as cli_main
from sailang.idle import main as idle_main

if __name__ == "__main__":
    if len(sys.argv) > 1:
        sys.exit(cli_main())
    else:
        idle_main([])
