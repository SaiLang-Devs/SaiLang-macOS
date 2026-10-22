"""Run every code example in the book through SaiLang.

For each example:
  * the program must parse,
  * programs without a window must run, and their transcript must match the
    expected 'out' text (ask() prompts and answers are included in the transcript),
  * examples with an 'error' key must fail with that text,
  * window examples are started under a display and must not crash.

The book builder uses the transcripts produced here, so the book always shows
what SaiLang really prints.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(HERE, "content"))

from sailang.errors import SaiError  # noqa: E402
from sailang.interpreter import Interpreter  # noqa: E402
from sailang.parser import parse  # noqa: E402


# The same token pattern the SaiLang IDLE uses for colouring (see sailang/idle.py).
TOKEN_RE = re.compile(
    r'#[^\n]*'
    r'|"(?:\\.|[^"\\\n])*"?'
    r'|\b\d+(?:\.\d+)?\b'
    r'|[A-Za-z_][A-Za-z_0-9]*'
)


def all_blocks(chapters):
    for chapter in chapters:
        for block in chapter["blocks"]:
            if block["type"] == "code":
                yield chapter, block


def run_program(block, folder):
    """Run a non-window example. Returns (transcript, error_message_or_None)."""
    transcript = []
    answers = list(block.get("input", []))

    def say(text):
        transcript.append(text + "\n")

    def ask(prompt):
        answer = answers.pop(0) if answers else ""
        transcript.append(prompt + answer + "\n")
        return answer

    for name, content in block.get("files", {}).items():
        path = os.path.join(folder, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content)
    main_path = os.path.join(folder, "program.sai")
    interp = Interpreter(out=say, input_fn=ask)
    previous = os.getcwd()
    os.chdir(folder)
    try:
        interp.execute(block["src"], main_path)
        return "".join(transcript), None
    except SaiError as err:
        return "".join(transcript), err.format()
    finally:
        os.chdir(previous)


def normalise(text):
    return "\n".join(line.rstrip() for line in text.rstrip().split("\n"))


def check_block(chapter, block):
    """Returns a list of problem strings (empty when the example is fine)."""
    problems = []
    label = f"chapter {chapter['num']}: {block['src'][:40]!r}"
    try:
        parse(block["src"], "program.sai")
    except SaiError as err:
        if "error" in block and block["error"] in err.format():
            return problems  # a deliberate syntax error, with the expected text
        return [f"{label}: does not parse: {err.format()}"]
    if "error" in block and block.get("fragment") is None and not block.get("gui"):
        pass  # runtime errors are checked below
    if block.get("fragment"):
        return problems
    if block.get("gui"):
        return problems  # started under a display by run_windows()
    folder = tempfile.mkdtemp(prefix="sai-book-")
    try:
        transcript, error = run_program(block, folder)
    finally:
        shutil.rmtree(folder, ignore_errors=True)
    if "error" in block:
        if error is None or block["error"] not in error:
            problems.append(f"{label}: expected error containing {block['error']!r}, got {error!r}")
        elif "out" in block and normalise(transcript) != normalise(block["out"]):
            problems.append(f"{label}: output before error differs: {transcript!r}")
    else:
        if error is not None:
            problems.append(f"{label}: unexpected error {error}")
        elif "out" in block and normalise(transcript) != normalise(block["out"]):
            problems.append(f"{label}: expected {block['out']!r}\n      got      {transcript!r}")
    return problems


def run_window(chapter, block):
    """Start a window example for a few seconds. It must not print a Python traceback."""
    folder = tempfile.mkdtemp(prefix="sai-gui-")
    try:
        for name in block.get("assets", []):
            shutil.copy(os.path.join(ROOT, "examples", "assets", name), os.path.join(folder, name))
        path = os.path.join(folder, "program.sai")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(block["src"])
        env = dict(os.environ, PYTHONPATH=os.path.join(ROOT, "src"), PYTHONUNBUFFERED="1")
        proc = subprocess.Popen([sys.executable, "-m", "sailang", path], cwd=folder, env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            _out, err = proc.communicate(timeout=4)   # still open after 4 seconds: good
        except subprocess.TimeoutExpired:
            proc.kill()
            _out, err = proc.communicate()
        if "Traceback" in err or "SaiRuntimeError" in err or "SaiSyntaxError" in err:
            return [f"chapter {chapter['num']} window example failed: {err[-400:]}"]
        return []
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def run_all(chapters, windows=True):
    problems = []
    checked = 0
    for chapter, block in all_blocks(chapters):
        checked += 1
        problems += check_block(chapter, block)
        if block.get("gui") and windows and not block.get("fragment"):
            problems += run_window(chapter, block)
    return checked, problems


def transcript_for(block):
    """The text the book should display for a non-window example."""
    folder = tempfile.mkdtemp(prefix="sai-book-")
    try:
        return run_program(block, folder)
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def main():
    from part1 import CHAPTERS_1_5  # noqa: E402
    from part2 import CHAPTERS_6_10  # noqa: E402
    chapters = CHAPTERS_1_5 + CHAPTERS_6_10
    use_display = bool(os.environ.get("DISPLAY"))
    checked, problems = run_all(chapters, windows=use_display)
    print(f"Checked {checked} code examples.")
    if not use_display:
        print("No display found, so window examples were parsed but not started.")
    if problems:
        print(f"\n{len(problems)} problem(s):")
        for problem in problems:
            print(" -", problem)
        return 1
    print("All examples are correct.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
