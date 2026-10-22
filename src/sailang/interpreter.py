"""The SaiLang interpreter.

Scope rules (see docs/LANGUAGE_SPEC.md):
  * 'when', 'repeat', 'while', and 'for each' blocks do NOT create a new scope.
  * Each command call gets its own scope. It can read top-level variables.
  * 'make x = ...' creates or updates x in the current scope.
  * 'x = ...' updates the nearest existing x, including top-level variables.
"""

import os
import sys

from .errors import SaiError, SaiRuntimeError
from .parser import parse
from .stdlib import BUILTINS
from .values import (
    MISSING, Command, Scope, is_num, to_text, type_name, values_equal,
)


class _Signal(BaseException):
    """Control-flow signals. Derived from BaseException so 'except Exception' never catches them."""

    def __init__(self, line=None, value=None):
        super().__init__()
        self.line = line
        self.value = value


class _Break(_Signal):
    pass


class _Continue(_Signal):
    pass


class _Return(_Signal):
    pass


class Interpreter:
    def __init__(self, out=None, input_fn=None):
        self.globals = Scope()
        self.out = out if out is not None else print
        self.input_fn = input_fn if input_fn is not None else input
        self.current_file = "<input>"
        self.loaded_files = set()
        self.gui = None  # created on first use by the desktop and game builtins

    # ----- public API ------------------------------------------------------
    def execute(self, source, filename="<input>"):
        """Parse and run a block of SaiLang source in the top-level scope."""
        program = parse(source, filename)
        previous = self.current_file
        self.current_file = filename
        try:
            self.exec_block(program, self.globals)
        except _Break as sig:
            raise self.fail("'stop' can only be used inside a loop", sig.line)
        except _Continue as sig:
            raise self.fail("'skip' can only be used inside a loop", sig.line)
        except _Return as sig:
            raise self.fail("'give' can only be used inside a command", sig.line)
        finally:
            self.current_file = previous

    def fail(self, message, line=None):
        return SaiRuntimeError(message, self.current_file, line)

    def report_error(self, message):
        """Used for errors raised inside GUI callbacks, which Tk would otherwise hide."""
        print(message, file=sys.stderr)

    # ----- statements ------------------------------------------------------
    def exec_block(self, statements, scope):
        for stmt in statements:
            getattr(self, "_s_" + stmt[0])(stmt, scope)

    def run_body(self, body, scope):
        """Run one pass of a loop body. Returns False when the loop should stop."""
        try:
            self.exec_block(body, scope)
        except _Break:
            return False
        except _Continue:
            pass
        return True

    def _s_make(self, s, scope):
        scope.vars[s[2]] = self.eval(s[3], scope)

    def _s_assign(self, s, scope):
        _, line, name, expr = s
        value = self.eval(expr, scope)
        frame = scope
        while frame is not None:
            if name in frame.vars:
                frame.vars[name] = value
                return
            frame = frame.parent
        raise self.fail(f"'{name}' does not exist yet. Create it first with: make {name} = ...", line)

    def _s_setindex(self, s, scope):
        _, line, target_node, expr = s
        target = self.eval(target_node[2], scope)
        index = self.eval(target_node[3], scope)
        value = self.eval(expr, scope)
        if not isinstance(target, list):
            raise self.fail(f"Only lists can have items changed, but this is {type_name(target)}", line)
        target[self.check_index(index, target, line)] = value

    def _s_say(self, s, scope):
        self.out(" ".join(to_text(self.eval(arg, scope)) for arg in s[2]))

    def _s_when(self, s, scope):
        _, line, branches, else_body = s
        for cond, body in branches:
            if self.truth(self.eval(cond, scope), line):
                self.exec_block(body, scope)
                return
        if else_body is not None:
            self.exec_block(else_body, scope)

    def _s_repeat(self, s, scope):
        _, line, count_node, body = s
        count = self.eval(count_node, scope)
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise self.fail(f"'repeat' needs a whole number of times, but got {to_text(count, True)}", line)
        for _ in range(count):
            if not self.run_body(body, scope):
                break

    def _s_while(self, s, scope):
        _, line, cond, body = s
        while self.truth(self.eval(cond, scope), line):
            if not self.run_body(body, scope):
                break

    def _s_foreach(self, s, scope):
        _, line, name, iterable_node, body = s
        items = self.eval(iterable_node, scope)
        if not isinstance(items, (list, str)):
            raise self.fail(f"'for each' needs a list or text, but got {type_name(items)}", line)
        for item in list(items):
            scope.vars[name] = item
            if not self.run_body(body, scope):
                break

    def _s_stop(self, s, scope):
        raise _Break(s[1])

    def _s_skip(self, s, scope):
        raise _Continue(s[1])

    def _s_command(self, s, scope):
        _, line, name, params, body = s
        scope.vars[name] = Command(name, params, body, self.current_file, line)

    def _s_give(self, s, scope):
        _, line, expr = s
        value = None if expr is None else self.eval(expr, scope)
        raise _Return(line, value)

    def _s_import(self, s, scope):
        self.import_file(s[2], s[1])

    def _s_try(self, s, scope):
        _, line, body, handler = s
        try:
            self.exec_block(body, scope)
        except SaiError as err:
            scope.vars["error_message"] = err.message
            self.exec_block(handler, scope)

    def _s_expr(self, s, scope):
        self.eval(s[2], scope)

    # ----- expressions -----------------------------------------------------
    def eval(self, node, scope):
        tag = node[0]
        line = node[1]
        if tag == "lit":
            return node[2]
        if tag == "var":
            return self.lookup(node[2], scope, line)
        if tag == "bin":
            return self.binary(node[2], self.eval(node[3], scope), self.eval(node[4], scope), line)
        if tag == "logic":
            left = self.truth(self.eval(node[3], scope), line)
            if node[2] == "and" and not left:
                return False
            if node[2] == "or" and left:
                return True
            return self.truth(self.eval(node[4], scope), line)
        if tag == "not":
            return not self.truth(self.eval(node[2], scope), line)
        if tag == "neg":
            value = self.eval(node[2], scope)
            if not is_num(value):
                raise self.fail(f"'-' needs a number, but got {type_name(value)}", line)
            return -value
        if tag == "list":
            return [self.eval(item, scope) for item in node[2]]
        if tag == "index":
            target = self.eval(node[2], scope)
            index = self.eval(node[3], scope)
            if not isinstance(target, (list, str)):
                raise self.fail(f"Only lists and text can use [ ], but this is {type_name(target)}", line)
            return target[self.check_index(index, target, line)]
        if tag == "call":
            args = [self.eval(arg, scope) for arg in node[3]]
            return self.call(node[2], args, scope, line)
        raise self.fail(f"Internal error: unknown expression '{tag}'", line)

    def lookup(self, name, scope, line):
        frame = scope
        while frame is not None:
            if name in frame.vars:
                return frame.vars[name]
            frame = frame.parent
        raise self.fail(f"I don't know a variable called '{name}'", line)

    def find(self, name, scope):
        frame = scope
        while frame is not None:
            if name in frame.vars:
                return frame.vars[name]
            frame = frame.parent
        return MISSING

    def truth(self, value, line):
        if not isinstance(value, bool):
            raise self.fail(f"A condition must be true or false, but this is {type_name(value)}", line)
        return value

    def check_index(self, index, seq, line):
        if isinstance(index, bool) or not isinstance(index, int):
            raise self.fail(f"A list position must be a whole number, but got {to_text(index, True)}", line)
        if index < 0 or index >= len(seq):
            raise self.fail(f"Position {index} is out of range. The list has {len(seq)} item(s).", line)
        return index

    def binary(self, op, a, b, line):
        if op == "+":
            if is_num(a) and is_num(b):
                return a + b
            if isinstance(a, str) or isinstance(b, str):
                return to_text(a) + to_text(b)
            if isinstance(a, list) and isinstance(b, list):
                return a + b
            raise self.fail(f"I can't add {type_name(a)} and {type_name(b)}", line)
        if op in ("-", "*", "/", "%"):
            if not (is_num(a) and is_num(b)):
                raise self.fail(f"'{op}' needs two numbers, but got {type_name(a)} and {type_name(b)}", line)
            if op == "-":
                return a - b
            if op == "*":
                return a * b
            if b == 0:
                raise self.fail("I can't divide by zero", line)
            if op == "%":
                return a % b
            if isinstance(a, int) and isinstance(b, int) and a % b == 0:
                return a // b
            return a / b
        if op == "==":
            return values_equal(a, b)
        if op == "!=":
            return not values_equal(a, b)
        if (is_num(a) and is_num(b)) or (isinstance(a, str) and isinstance(b, str)):
            if op == "<":
                return a < b
            if op == "<=":
                return a <= b
            if op == ">":
                return a > b
            return a >= b
        raise self.fail(f"'{op}' can only compare two numbers or two texts, but got {type_name(a)} and {type_name(b)}", line)

    # ----- commands --------------------------------------------------------
    def call(self, name, args, scope, line):
        target = self.find(name, scope)
        if isinstance(target, Command):
            return self.invoke(target, args, line)
        if name in BUILTINS:
            return self.call_builtin(name, args, line)
        if target is not MISSING:
            raise self.fail(f"'{name}' is a variable, not a command", line)
        raise self.fail(f"I don't know a command called '{name}'. Define it with: command {name}(...) {{ }}", line)

    def invoke(self, cmd, args, line):
        if len(args) != len(cmd.params):
            raise self.fail(
                f"'{cmd.name}' needs {len(cmd.params)} input(s) but got {len(args)}", line
            )
        frame = Scope(self.globals, is_function=True)
        frame.vars.update(zip(cmd.params, args))
        previous = self.current_file
        self.current_file = cmd.file
        try:
            self.exec_block(cmd.body, frame)
        except _Return as ret:
            return ret.value
        except _Break as sig:
            raise self.fail("'stop' can only be used inside a loop", sig.line)
        except _Continue as sig:
            raise self.fail("'skip' can only be used inside a loop", sig.line)
        except RecursionError:
            raise self.fail(f"'{cmd.name}' calls itself too many times (infinite recursion?)", line)
        finally:
            self.current_file = previous
        return None

    def call_builtin(self, name, args, line):
        fn, low, high = BUILTINS[name]
        if len(args) < low or (high >= 0 and len(args) > high):
            if high < 0:
                expected = f"at least {low}"
            elif low == high:
                expected = str(low)
            else:
                expected = f"{low} to {high}"
            raise self.fail(f"'{name}' needs {expected} input(s) but got {len(args)}", line)
        try:
            return fn(self, args, line)
        except SaiError:
            raise
        except Exception as ex:  # any unexpected Python error becomes a SaiLang error
            raise self.fail(f"'{name}' failed: {ex}", line)

    # ----- modules ---------------------------------------------------------
    def import_file(self, name, line):
        if os.path.isfile(self.current_file):
            base = os.path.dirname(os.path.abspath(self.current_file))
        else:
            base = os.getcwd()
        path = os.path.normpath(os.path.join(base, name))
        if path in self.loaded_files:
            return
        self.loaded_files.add(path)
        try:
            with open(path, encoding="utf-8-sig") as handle:
                source = handle.read()
        except OSError as ex:
            raise self.fail(f"I could not import '{name}': {ex.strerror or ex}", line)
        self.execute(source, path)
