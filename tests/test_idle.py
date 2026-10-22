"""Tests for SaiLang IDLE. Run with:  python -m unittest discover -s tests -v"""

import os
import sys
import tempfile
import time
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from sailang import idle  # noqa: E402
from sailang.idle import child_command, highlight_ranges  # noqa: E402


def display_available():
    try:
        import tkinter
        root = tkinter.Tk()
        root.destroy()
        return True
    except Exception:
        return False


class HighlightTests(unittest.TestCase):
    def test_keywords_strings_numbers_comments(self):
        ranges = highlight_ranges('make x = "hi" # note\nsay x1 + 3.5\n')
        self.assertIn(("keyword", "1.0", "1.4"), ranges)
        self.assertIn(("string", "1.9", "1.13"), ranges)
        self.assertIn(("comment", "1.14", "1.20"), ranges)
        self.assertIn(("keyword", "2.0", "2.3"), ranges)
        self.assertIn(("number", "2.9", "2.12"), ranges)

    def test_variable_names_are_not_coloured(self):
        tags = [r[0] for r in highlight_ranges("make score = 5")]
        self.assertEqual(tags, ["keyword", "number"])  # 'score' is not coloured

    def test_builtins_are_coloured_differently(self):
        self.assertIn(("builtin", "1.0", "1.6"), highlight_ranges("length(x)"))

    def test_hash_inside_text_is_not_a_comment(self):
        tags = [r[0] for r in highlight_ranges('say "# not a comment"')]
        self.assertEqual(tags, ["keyword", "string"])

    def test_unfinished_text_while_typing_is_still_highlighted(self):
        self.assertIn("string", [r[0] for r in highlight_ranges('say "hello')])


class ChildProcessTests(unittest.TestCase):
    def test_command_uses_python_not_a_bat_file(self):
        cmd = child_command("C:\\x\\hello.sai")
        self.assertEqual(cmd[1:], ["-m", "sailang", "C:\\x\\hello.sai"])
        self.assertFalse(cmd[0].lower().endswith(".bat"))

    def test_check_mode_command(self):
        self.assertEqual(child_command("a.sai", mode="check")[-2:], ["check", "a.sai"])

    def test_pythonw_is_swapped_for_python(self):
        with tempfile.TemporaryDirectory() as tmp:
            pythonw = os.path.join(tmp, "pythonw.exe")
            python = os.path.join(tmp, "python.exe")
            open(python, "w").close()
            with mock.patch.object(sys, "executable", pythonw):
                self.assertEqual(idle.child_python(), python)

    def test_child_runs_a_program_end_to_end(self):
        import subprocess
        result = subprocess.run(child_command(os.path.join(ROOT, "examples", "hello.sai")),
                                cwd=ROOT, env=idle.child_env(), capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Level complete!", result.stdout)


@unittest.skipUnless(display_available(), "Needs a display (run under xvfb-run on Linux)")
class IdleWindowTests(unittest.TestCase):
    def setUp(self):
        import tkinter
        self.root = tkinter.Tk()
        self.app = idle.SaiIDLE(self.root)
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        self.app.stop_program(silent=True)
        self.root.destroy()

    def wait_until_finished(self, seconds=30):
        deadline = time.time() + seconds
        while self.app.running and time.time() < deadline:
            self.root.update()
            time.sleep(0.01)
        self.assertFalse(self.app.running, "program did not finish in time")

    def output_text(self):
        return self.app.output.get("1.0", "end-1c")

    def write_program(self, name, source):
        path = os.path.join(self.tmp, name)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(source)
        return path

    def test_open_file_shows_text_and_colours(self):
        path = self.write_program("p.sai", 'make x = 1\nsay "hi"\n')
        self.app.open_path(path)
        self.assertEqual(self.app.text.get("1.0", "end-1c"), 'make x = 1\nsay "hi"\n')
        self.assertIn("keyword", self.app.text.tag_names("1.0"))
        self.assertIn("SaiLang IDLE", self.app.root.title())
        self.assertIn("p.sai", self.app.root.title())

    def test_editing_marks_document_unsaved(self):
        self.app.open_path(self.write_program("q.sai", "say 1\n"))
        self.app.text.insert("end", "say 2\n")
        self.root.update()
        self.assertTrue(self.app.dirty)
        self.assertIn("*", self.root.title())

    def test_save_writes_file(self):
        path = self.write_program("s.sai", "say 1\n")
        self.app.open_path(path)
        self.app.text.insert("end", "say 2\n")
        self.root.update()
        self.assertTrue(self.app.save())
        with open(path, encoding="utf-8") as handle:
            self.assertEqual(handle.read(), "say 1\nsay 2\n")
        self.assertFalse(self.app.dirty)

    def test_run_shows_program_output(self):
        self.app.open_path(os.path.join(ROOT, "examples", "hello.sai"))
        self.app.run_program()
        self.wait_until_finished()
        self.assertIn("Level complete!", self.output_text())
        self.assertIn("exit code 0", self.output_text())

    def test_run_error_highlights_the_line(self):
        self.app.open_path(self.write_program("bad.sai", "say 1\nsay missing\n"))
        self.app.run_program()
        self.wait_until_finished()
        self.assertIn("bad.sai:2:", self.output_text())
        ranges = self.app.text.tag_ranges("errline")
        self.assertTrue(ranges, "error line was not highlighted")
        self.assertEqual(str(ranges[0]), "2.0")

    def test_input_is_sent_to_program(self):
        self.app.open_path(self.write_program("in.sai", 'make name = ask("Name? ")\nsay "Hi", name\n'))
        self.app.run_program()
        deadline = time.time() + 30
        while "Name?" not in self.output_text() and time.time() < deadline:
            self.root.update()
            time.sleep(0.01)
        self.app.input_entry.insert(0, "Sai")
        self.app.send_input()
        self.wait_until_finished()
        self.assertIn("Hi Sai", self.output_text())

    def test_check_reports_syntax_error(self):
        self.app.open_path(self.write_program("syn.sai", "say 1\nmake = 2\n"))
        self.app.check_program()
        self.assertIn("syn.sai:2:", self.output_text())

    def test_check_passes_clean_file(self):
        self.app.open_path(os.path.join(ROOT, "examples", "hello.sai"))
        self.app.check_program()
        self.assertIn("no problems found", self.output_text())

    def test_stop_ends_a_running_program(self):
        self.app.open_path(self.write_program("loop.sai", "while true {\nsay 1\n}\n"))
        self.app.run_program()
        self.root.update()
        self.app.stop_program()
        self.wait_until_finished()
        self.assertIn("Stopped by user", self.output_text())


if __name__ == "__main__":
    unittest.main()
