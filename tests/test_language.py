"""SaiLang test suite. Run with:  python -m unittest discover -s tests -v   (from the project folder)

GUI tests are skipped automatically when Tkinter or a display is unavailable.
"""

import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from sailang.errors import SaiRuntimeError, SaiSyntaxError  # noqa: E402
from sailang.interpreter import Interpreter  # noqa: E402
from sailang.lexer import tokenize  # noqa: E402
from sailang.parser import parse  # noqa: E402
from sailang.values import Handle  # noqa: E402


def run(source, filename="test.sai"):
    lines = []
    interp = Interpreter(out=lines.append)
    interp.execute(source, filename)
    return lines


def gui_available():
    try:
        import tkinter
        root = tkinter.Tk()
        root.destroy()
        return True
    except Exception:
        return False


class LexerTests(unittest.TestCase):
    def test_numbers_and_strings(self):
        kinds = [t.kind for t in tokenize('make x = 3.5 + "hi"')]
        self.assertEqual(kinds, ["KW", "NAME", "OP", "NUM", "OP", "STR", "EOF"])

    def test_escapes_in_text(self):
        tok = tokenize('say "a\\nb\\"c"')[1]
        self.assertEqual(tok.value, 'a\nb"c')

    def test_comments_are_ignored(self):
        self.assertEqual(run("say 1 # this is ignored\n"), ["1"])

    def test_unterminated_string_reports_line(self):
        with self.assertRaises(SaiSyntaxError) as ctx:
            tokenize('say 1\nsay "oops\n', "bad.sai")
        self.assertEqual(ctx.exception.line, 2)

    def test_unknown_character(self):
        with self.assertRaises(SaiSyntaxError):
            tokenize("make x = 5 @ 2")


class ParserTests(unittest.TestCase):
    def test_missing_closing_brace(self):
        with self.assertRaises(SaiSyntaxError) as ctx:
            parse("when true {\nsay 1\n", "f.sai")
        self.assertIn("closing '}'", ctx.exception.message)

    def test_statement_must_do_something(self):
        with self.assertRaises(SaiSyntaxError):
            parse("5 + 5", "f.sai")

    def test_make_requires_equals(self):
        with self.assertRaises(SaiSyntaxError) as ctx:
            parse("make x 5", "f.sai")
        self.assertEqual(ctx.exception.line, 1)


class ArithmeticAndValueTests(unittest.TestCase):
    def test_precedence(self):
        self.assertEqual(run("say 2 + 3 * 4"), ["14"])

    def test_parentheses_and_negatives(self):
        self.assertEqual(run("say (2 + 3) * -2"), ["-10"])

    def test_integer_division_stays_integer_when_exact(self):
        self.assertEqual(run("say 8 / 2"), ["4"])

    def test_division_gives_decimal(self):
        self.assertEqual(run("say 7 / 2"), ["3.5"])

    def test_modulo(self):
        self.assertEqual(run("say 17 % 5"), ["2"])

    def test_text_joins_with_plus_and_numbers(self):
        self.assertEqual(run('say "Score: " + 5'), ["Score: 5"])

    def test_booleans_and_nothing_display(self):
        self.assertEqual(run("say true, false, nothing"), ["true false nothing"])

    def test_true_is_not_equal_to_one(self):
        self.assertEqual(run("say true == 1"), ["false"])

    def test_comparison_of_text(self):
        self.assertEqual(run('say "apple" < "banana"'), ["true"])

    def test_divide_by_zero_is_an_error(self):
        with self.assertRaises(SaiRuntimeError) as ctx:
            run("say 1 / 0", "d.sai")
        self.assertIn("divide by zero", ctx.exception.message)
        self.assertEqual(ctx.exception.line, 1)

    def test_adding_number_and_list_is_an_error(self):
        with self.assertRaises(SaiRuntimeError):
            run("say 1 + [2]")


class VariableTests(unittest.TestCase):
    def test_make_and_reassign(self):
        self.assertEqual(run("make x = 1\nx = x + 4\nsay x"), ["5"])

    def test_make_inside_loop_updates_outer_variable(self):
        lines = run("make score = 0\nrepeat 3 times {\n make score = score + 10\n}\nsay score")
        self.assertEqual(lines, ["30"])

    def test_assign_to_missing_variable_is_an_error(self):
        with self.assertRaises(SaiRuntimeError) as ctx:
            run("ghost = 3")
        self.assertIn("does not exist yet", ctx.exception.message)

    def test_unknown_variable_is_an_error_with_line(self):
        with self.assertRaises(SaiRuntimeError) as ctx:
            run("say 1\nsay missing", "vars.sai")
        self.assertEqual(ctx.exception.line, 2)
        self.assertTrue(ctx.exception.format().startswith("vars.sai:2:"))

    def test_error_names_the_file(self):
        with self.assertRaises(SaiRuntimeError) as ctx:
            run("say missing", "myprogram.sai")
        self.assertIn("myprogram.sai:1", ctx.exception.format())


class ConditionTests(unittest.TestCase):
    def test_when_otherwise(self):
        self.assertEqual(run('when 1 > 2 {\nsay "a"\n} otherwise {\nsay "b"\n}'), ["b"])

    def test_otherwise_when_chain(self):
        src = 'make n = 5\nwhen n > 10 {\nsay "big"\n} otherwise when n > 3 {\nsay "mid"\n} otherwise {\nsay "small"\n}'
        self.assertEqual(run(src), ["mid"])

    def test_condition_must_be_boolean(self):
        with self.assertRaises(SaiRuntimeError) as ctx:
            run('when "yes" {\nsay 1\n}')
        self.assertIn("true or false", ctx.exception.message)

    def test_and_or_not(self):
        self.assertEqual(run("say true and not false, false or false"), ["true false"])

    def test_and_short_circuits(self):
        # The right side would fail (index out of range) if it were evaluated.
        self.assertEqual(run("say false and [1][5] == 1"), ["false"])


class LoopTests(unittest.TestCase):
    def test_repeat(self):
        self.assertEqual(run("repeat 3 times {\nsay \"x\"\n}"), ["x", "x", "x"])

    def test_while_with_stop(self):
        src = "make i = 0\nwhile true {\ni = i + 1\nwhen i == 4 {\nstop\n}\n}\nsay i"
        self.assertEqual(run(src), ["4"])

    def test_skip(self):
        src = "make total = 0\nmake i = 0\nwhile i < 5 {\ni = i + 1\nwhen i == 3 {\nskip\n}\ntotal = total + i\n}\nsay total"
        self.assertEqual(run(src), ["12"])

    def test_for_each_over_list(self):
        self.assertEqual(run('for each c in ["a", "b"] {\nsay c\n}'), ["a", "b"])

    def test_for_each_over_text(self):
        self.assertEqual(run('for each c in "hi" {\nsay c\n}'), ["h", "i"])

    def test_stop_outside_loop_is_an_error(self):
        with self.assertRaises(SaiRuntimeError) as ctx:
            run("stop", "s.sai")
        self.assertIn("inside a loop", ctx.exception.message)

    def test_repeat_needs_whole_number(self):
        with self.assertRaises(SaiRuntimeError):
            run('repeat "many" times {\nsay 1\n}')


class CommandTests(unittest.TestCase):
    def test_command_with_return(self):
        self.assertEqual(run("command add(a, b) {\ngive a + b\n}\nsay add(2, 3)"), ["5"])

    def test_recursion(self):
        src = ("command fib(n) {\nwhen n < 2 {\ngive n\n}\ngive fib(n - 1) + fib(n - 2)\n}\n"
               "say fib(12)")
        self.assertEqual(run(src), ["144"])

    def test_wrong_argument_count(self):
        with self.assertRaises(SaiRuntimeError) as ctx:
            run("command f(a) {\nsay a\n}\nf(1, 2)")
        self.assertIn("needs 1 input(s) but got 2", ctx.exception.message)

    def test_command_without_give_returns_nothing(self):
        self.assertEqual(run("command f() {\nsay 1\n}\nsay f()"), ["1", "nothing"])

    def test_local_variables_do_not_leak(self):
        src = "command f() {\nmake secret = 42\n}\nf()\nsay secret"
        with self.assertRaises(SaiRuntimeError):
            run(src)

    def test_make_inside_command_creates_local_not_global(self):
        src = "make x = 1\ncommand f() {\nmake x = 99\n}\nf()\nsay x"
        self.assertEqual(run(src), ["1"])

    def test_command_can_read_and_update_globals(self):
        src = "make total = 0\ncommand add_one() {\ntotal = total + 1\n}\nadd_one()\nadd_one()\nsay total"
        self.assertEqual(run(src), ["2"])

    def test_give_outside_command_is_an_error(self):
        with self.assertRaises(SaiRuntimeError):
            run("give 5")

    def test_infinite_recursion_is_reported(self):
        with self.assertRaises(SaiRuntimeError) as ctx:
            run("command loop_forever() {\nloop_forever()\n}\nloop_forever()")
        self.assertIn("too many times", ctx.exception.message)

    def test_unknown_command(self):
        with self.assertRaises(SaiRuntimeError) as ctx:
            run("nope()")
        self.assertIn("don't know a command called 'nope'", ctx.exception.message)


class ListTests(unittest.TestCase):
    def test_index_and_length(self):
        self.assertEqual(run('make l = ["a", "b"]\nsay l[1], length(l)'), ["b 2"])

    def test_list_out_of_range(self):
        with self.assertRaises(SaiRuntimeError) as ctx:
            run("make l = [1]\nsay l[3]")
        self.assertIn("out of range", ctx.exception.message)

    def test_set_item_and_append(self):
        self.assertEqual(run("make l = [1, 2]\nl[0] = 9\nappend(l, 3)\nsay l"), ["[9, 2, 3]"])

    def test_remove_at(self):
        self.assertEqual(run("make l = [1, 2, 3]\nremove_at(l, 0)\nsay l"), ["[2, 3]"])

    def test_contains_and_range(self):
        self.assertEqual(run("say contains(range(3), 2), range(2, 4)"), ["true [2, 3]"])

    def test_text_helpers(self):
        self.assertEqual(run('say upper("abc"), join(split("a b c", " "), "-")'), ["ABC a-b-c"])

    def test_number_conversion_error(self):
        with self.assertRaises(SaiRuntimeError) as ctx:
            run('say number("abc")')
        self.assertIn("is not a number", ctx.exception.message)

    def test_wrong_argument_count_for_builtin(self):
        with self.assertRaises(SaiRuntimeError) as ctx:
            run("say length()")
        self.assertIn("'length' needs 1 input(s)", ctx.exception.message)


class ErrorHandlingTests(unittest.TestCase):
    def test_try_catches_error_and_sets_message(self):
        src = 'try {\nsay 1 / 0\n} on error {\nsay "caught:", error_message\n}'
        self.assertEqual(run(src), ["caught: I can't divide by zero"])

    def test_try_without_error_skips_handler(self):
        src = 'try {\nsay "fine"\n} on error {\nsay "never"\n}'
        self.assertEqual(run(src), ["fine"])

    def test_syntax_error_has_file_and_line(self):
        with self.assertRaises(SaiSyntaxError) as ctx:
            run("say 1\nmake = 2", "syntax.sai")
        self.assertEqual(ctx.exception.format().split(":")[0], "syntax.sai")
        self.assertEqual(ctx.exception.line, 2)


class FileTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.path = os.path.join(self.tmp, "notes.txt").replace("\\", "/")

    def test_write_append_read(self):
        src = (f'write_file("{self.path}", "one\\n")\n'
               f'append_file("{self.path}", "two")\n'
               f'say read_file("{self.path}")\n'
               f'say file_exists("{self.path}")')
        self.assertEqual(run(src), ["one\ntwo", "true"])

    def test_missing_file_error_is_friendly(self):
        with self.assertRaises(SaiRuntimeError) as ctx:
            run(f'say read_file("{self.tmp}/missing.txt")')
        self.assertIn("I could not read", ctx.exception.message)


class ModuleTests(unittest.TestCase):
    def test_import_relative_to_importing_file(self):
        tmp = tempfile.mkdtemp()
        os.makedirs(os.path.join(tmp, "lib"))
        with open(os.path.join(tmp, "lib", "helpers.sai"), "w", encoding="utf-8") as h:
            h.write('command double(n) {\n give n * 2\n}\nmake label = "helper"\n')
        main_path = os.path.join(tmp, "main.sai")
        with open(main_path, "w", encoding="utf-8") as m:
            m.write('import "lib/helpers.sai"\nsay label, double(21)\n')
        lines = []
        with open(main_path, encoding="utf-8") as handle:
            Interpreter(out=lines.append).execute(handle.read(), main_path)
        self.assertEqual(lines, ["helper 42"])

    def test_missing_import_is_reported(self):
        with self.assertRaises(SaiRuntimeError) as ctx:
            run('import "nope.sai"')
        self.assertIn("could not import", ctx.exception.message)


class ImageInputTests(unittest.TestCase):
    """These check URL and file validation, which does not need a display."""

    def test_loader_rejects_unsupported_scheme(self):
        from sailang.stdlib import _load_image_bytes
        interp = Interpreter()
        with self.assertRaises(SaiRuntimeError) as ctx:
            _load_image_bytes(interp, "ftp://example.com/a.png", 1)
        self.assertIn("not a supported address", ctx.exception.message)

    def test_loader_reports_missing_local_file(self):
        from sailang.stdlib import _load_image_bytes
        with self.assertRaises(SaiRuntimeError) as ctx:
            _load_image_bytes(Interpreter(), "no/such/picture.png", 1)
        self.assertIn("could not open the image", ctx.exception.message)


class GameLogicTests(unittest.TestCase):
    def test_overlaps(self):
        self.assertEqual(run("say overlaps(0, 0, 10, 10, 5, 5, 10, 10)"), ["true"])
        self.assertEqual(run("say overlaps(0, 0, 10, 10, 20, 20, 5, 5)"), ["false"])

    def test_key_down_is_false_before_any_key_press(self):
        self.assertEqual(run('say key_down("left")'), ["false"])


@unittest.skipUnless(gui_available(), "Tkinter with a display is required for these tests")
class DesktopTests(unittest.TestCase):
    def test_window_button_and_label_update(self):
        interp = Interpreter(out=lambda s: None)
        interp.execute(
            'make clicks = 0\n'
            'make win = open_window("Test", 300, 200)\n'
            'make status = label(win, "start")\n'
            'button(win, "Go", "press")\n'
            'command press() {\nclicks = clicks + 1\nset_text(status, "clicked " + clicks)\n}\n',
            "gui.sai")
        button = [w for w in interp.gui["root"].winfo_children()[0].winfo_children()
                  if w.winfo_class() == "Button"][0]
        button.invoke()
        button.invoke()
        status = interp.globals.vars["status"]
        self.assertEqual(status.obj.cget("text"), "clicked 2")
        interp.execute("stop_timer()", "gui.sai")
        interp.gui["root"].destroy()
        interp.gui = None

    def test_entry_text_is_read(self):
        interp = Interpreter(out=lambda s: None)
        interp.execute('make win = open_window("T", 200, 100)\nmake box = entry(win)\n', "e.sai")
        box = interp.globals.vars["box"]
        box.obj.insert(0, "Sai")
        interp.execute('say entry_text(box)', "e.sai")
        interp.gui["root"].destroy()
        interp.gui = None

    def test_show_local_png(self):
        png = os.path.join(ROOT, "examples", "assets", "sample.png")
        interp = Interpreter(out=lambda s: None)
        interp.execute(f'make win = open_window("Img", 200, 150)\nshow_image(win, "{png}")\n', "img.sai")
        self.assertIsInstance(interp.globals.vars["win"], Handle)
        interp.gui["root"].destroy()
        interp.gui = None

    def test_game_tick_collects_coin(self):
        interp = Interpreter(out=lambda s: None)
        interp.execute(
            'make player_x = 10\nmake player_y = 10\nmake coin_x = 12\nmake coin_y = 12\nmake score = 0\n'
            'open_game("G", 200, 200)\n'
            'command tick() {\nwhen overlaps(player_x, player_y, 30, 30, coin_x, coin_y, 16, 16) {\nscore = score + 1\n}\n}\n'
            'tick()\n', "game.sai")
        self.assertEqual(interp.globals.vars["score"], 1)
        interp.execute("stop_timer()", "game.sai")
        interp.gui["root"].destroy()
        interp.gui = None


class ExampleProgramTests(unittest.TestCase):
    """Runs the shipped example programs through the command line."""

    def run_example(self, name):
        return subprocess.run(
            [sys.executable, "-m", "sailang", os.path.join("examples", name)],
            cwd=ROOT, env=dict(os.environ, PYTHONPATH=os.path.join(ROOT, "src")),
            capture_output=True, text=True, timeout=60,
        )

    def test_hello(self):
        result = self.run_example("hello.sai")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Level complete!", result.stdout)

    def test_all_core_examples_run(self):
        for name in ["variables.sai", "conditions.sai", "loops.sai", "functions.sai",
                     "lists.sai", "errors.sai", "modules.sai"]:
            with self.subTest(example=name):
                result = self.run_example(name)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(result.stdout.strip())

    def test_files_example_runs_in_temp_folder(self):
        tmp = tempfile.mkdtemp()
        result = subprocess.run(
            [sys.executable, "-m", "sailang", os.path.join(ROOT, "examples", "files.sai")],
            cwd=tmp, env=dict(os.environ, PYTHONPATH=os.path.join(ROOT, "src")),
            capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Remember to feed the cat.", result.stdout)

    def test_check_command_reports_syntax_error(self):
        with tempfile.NamedTemporaryFile("w", suffix=".sai", delete=False, encoding="utf-8") as f:
            f.write("say 1\nmake = 2\n")
        result = subprocess.run(
            [sys.executable, "-m", "sailang", "check", f.name],
            cwd=ROOT, env=dict(os.environ, PYTHONPATH=os.path.join(ROOT, "src")),
            capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 1)
        self.assertIn(":2:", result.stderr)

    def test_repl_keeps_state_between_lines(self):
        result = subprocess.run(
            [sys.executable, "-m", "sailang", "repl"],
            cwd=ROOT, env=dict(os.environ, PYTHONPATH=os.path.join(ROOT, "src")),
            input="make x = 20\nsay x + 1\nexit\n", capture_output=True, text=True, timeout=60)
        self.assertIn("21", result.stdout)


if __name__ == "__main__":
    unittest.main()
