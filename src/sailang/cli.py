"""Command-line entry point: run a file, check a file, or start the REPL."""

import sys

from . import __version__
from .errors import SaiError
from .interpreter import Interpreter
from .parser import parse

USAGE = """SaiLang {version}

Usage:
  sai                    start the interactive prompt (REPL)
  sai FILE.sai           run a SaiLang program
  sai check FILE.sai     check a program for mistakes without running it
  sai idle               open SaiLang IDLE, the editor and runner
  sai --version          show the version
"""


def _read(path):
    with open(path, encoding="utf-8-sig") as handle:  # tolerates Notepad's BOM
        return handle.read()


def run_file(path):
    try:
        source = _read(path)
    except OSError as ex:
        print(f"Could not open '{path}': {ex.strerror or ex}", file=sys.stderr)
        return 1
    try:
        Interpreter().execute(source, path)
    except SaiError as err:
        print(err.format(), file=sys.stderr)
        return 1
    return 0


def check_file(path):
    try:
        source = _read(path)
        parse(source, path)
    except OSError as ex:
        print(f"Could not open '{path}': {ex.strerror or ex}", file=sys.stderr)
        return 1
    except SaiError as err:
        print(err.format(), file=sys.stderr)
        return 1
    print(f"{path}: no problems found")
    return 0


def repl():
    interp = Interpreter()
    print(f"SaiLang {__version__} interactive prompt. Type 'exit' to leave.")
    buffer = []
    while True:
        try:
            line = input("...> " if buffer else "sai> ")
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not buffer and line.strip() in ("exit", "quit"):
            return 0
        buffer.append(line)
        text = "\n".join(buffer)
        if text.count("{") > text.count("}"):
            continue  # a block is still open; keep reading lines
        buffer = []
        if not text.strip():
            continue
        try:
            interp.execute(text, "<prompt>")
        except SaiError as err:
            print(err.format())


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.setrecursionlimit(20000)
    args = sys.argv[1:] if argv is None else list(argv)
    if not args:
        return repl()
    first = args[0]
    if first in ("-h", "--help", "help"):
        print(USAGE.format(version=__version__))
        return 0
    if first in ("-v", "--version", "version"):
        print(f"SaiLang {__version__}")
        return 0
    if first == "check":
        if len(args) != 2:
            print("Usage: sai check FILE.sai", file=sys.stderr)
            return 2
        return check_file(args[1])
    if first == "repl":
        return repl()
    if first == "idle":
        from .idle import main as idle_main
        return idle_main(args[1:])
    return run_file(first)
