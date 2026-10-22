"""The SaiLang parser.

Produces a tree of tuples. Every node is (tag, line, ...). The grammar is
documented in docs/LANGUAGE_SPEC.md.
"""

from .lexer import tokenize
from .errors import SaiSyntaxError

COMPARISON_OPS = {"==", "!=", "<", "<=", ">", ">="}


def parse(source, filename="<input>"):
    return Parser(tokenize(source, filename), filename).parse_program()


class Parser:
    def __init__(self, tokens, filename):
        self.toks = tokens
        self.pos = 0
        self.file = filename

    # ----- token helpers -------------------------------------------------
    def peek(self, offset=0):
        return self.toks[min(self.pos + offset, len(self.toks) - 1)]

    def advance(self):
        tok = self.toks[self.pos]
        self.pos = min(self.pos + 1, len(self.toks) - 1)
        return tok

    def describe(self, tok):
        if tok.kind == "EOF":
            return "the end of the file"
        if tok.kind == "NL":
            return "the end of the line"
        if tok.kind == "STR":
            return f'"{tok.value}"'
        return f"'{tok.value}'"

    def error(self, message, tok=None):
        tok = tok or self.peek()
        raise SaiSyntaxError(message, self.file, tok.line)

    def is_op(self, value, offset=0):
        tok = self.peek(offset)
        return tok.kind == "OP" and tok.value == value

    def is_kw(self, value):
        tok = self.peek()
        return tok.kind == "KW" and tok.value == value

    def expect_op(self, value):
        if not self.is_op(value):
            self.error(f"Expected '{value}' but found {self.describe(self.peek())}")
        return self.advance()

    def expect_kw(self, word):
        if not self.is_kw(word):
            self.error(f"Expected '{word}' but found {self.describe(self.peek())}")
        return self.advance()

    def name(self):
        tok = self.peek()
        if tok.kind != "NAME":
            self.error(f"Expected a name but found {self.describe(tok)}")
        return self.advance().value

    def skip_newlines(self):
        while self.peek().kind == "NL":
            self.advance()

    def end_statement(self):
        tok = self.peek()
        if tok.kind in ("NL", "EOF") or self.is_op("}"):
            return
        self.error(
            f"Unexpected {self.describe(tok)} after a statement. "
            "Put each statement on its own line."
        )

    # ----- statements ----------------------------------------------------
    def parse_program(self):
        statements = []
        while True:
            self.skip_newlines()
            if self.peek().kind == "EOF":
                return statements
            statements.append(self.statement())
            self.end_statement()

    def block(self):
        self.expect_op("{")
        statements = []
        while True:
            self.skip_newlines()
            if self.is_op("}"):
                self.advance()
                return statements
            if self.peek().kind == "EOF":
                self.error("This block is missing its closing '}'")
            statements.append(self.statement())
            self.end_statement()

    def statement(self):
        tok = self.peek()
        line = tok.line
        if tok.kind == "KW":
            handler = getattr(self, "_kw_" + tok.value, None)
            if handler is not None:
                return handler(line)
        if tok.kind == "NAME" and self.is_op("=", 1):
            self.advance()
            self.advance()
            return ("assign", line, tok.value, self.expression())

        expr = self.expression()
        if self.is_op("="):
            if expr[0] != "index":
                self.error("Only variables and list items can be given a new value")
            self.advance()
            return ("setindex", line, expr, self.expression())
        if expr[0] != "call":
            self.error(
                "This line does nothing. Use 'say', 'make', or call a command such as greet(name)."
            )
        return ("expr", line, expr)

    def _kw_make(self, line):
        self.advance()
        name = self.name()
        self.expect_op("=")
        return ("make", line, name, self.expression())

    def _kw_say(self, line):
        self.advance()
        args = []
        if self.peek().kind not in ("NL", "EOF") and not self.is_op("}"):
            args.append(self.expression())
            while self.is_op(","):
                self.advance()
                args.append(self.expression())
        return ("say", line, args)

    def _kw_when(self, line):
        self.advance()
        first_cond = self.expression()
        branches = [(first_cond, self.block())]
        else_body = None
        while self.is_kw("otherwise"):
            self.advance()
            if self.is_kw("when"):
                self.advance()
                cond = self.expression()
                branches.append((cond, self.block()))
            else:
                else_body = self.block()
                break
        return ("when", line, branches, else_body)

    def _kw_repeat(self, line):
        self.advance()
        count = self.expression()
        self.expect_kw("times")
        return ("repeat", line, count, self.block())

    def _kw_while(self, line):
        self.advance()
        cond = self.expression()
        return ("while", line, cond, self.block())

    def _kw_for(self, line):
        self.advance()
        self.expect_kw("each")
        name = self.name()
        self.expect_kw("in")
        iterable = self.expression()
        return ("foreach", line, name, iterable, self.block())

    def _kw_stop(self, line):
        self.advance()
        return ("stop", line)

    def _kw_skip(self, line):
        self.advance()
        return ("skip", line)

    def _kw_command(self, line):
        self.advance()
        name = self.name()
        self.expect_op("(")
        params = []
        if not self.is_op(")"):
            params.append(self.name())
            while self.is_op(","):
                self.advance()
                params.append(self.name())
        self.expect_op(")")
        return ("command", line, name, params, self.block())

    def _kw_give(self, line):
        self.advance()
        if self.peek().kind in ("NL", "EOF") or self.is_op("}"):
            return ("give", line, None)
        return ("give", line, self.expression())

    def _kw_import(self, line):
        self.advance()
        tok = self.peek()
        if tok.kind != "STR":
            self.error("'import' must be followed by a file name in quotes, e.g. import \"lib/tools.sai\"")
        self.advance()
        return ("import", line, tok.value)

    def _kw_try(self, line):
        self.advance()
        body = self.block()
        self.expect_kw("on")
        self.expect_kw("error")
        handler = self.block()
        return ("try", line, body, handler)

    # ----- expressions (lowest to highest precedence) ----------------------
    def expression(self):
        return self.or_expr()

    def or_expr(self):
        left = self.and_expr()
        while self.is_kw("or"):
            line = self.advance().line
            left = ("logic", line, "or", left, self.and_expr())
        return left

    def and_expr(self):
        left = self.not_expr()
        while self.is_kw("and"):
            line = self.advance().line
            left = ("logic", line, "and", left, self.not_expr())
        return left

    def not_expr(self):
        if self.is_kw("not"):
            line = self.advance().line
            return ("not", line, self.not_expr())
        return self.comparison()

    def comparison(self):
        left = self.additive()
        tok = self.peek()
        if tok.kind == "OP" and tok.value in COMPARISON_OPS:
            self.advance()
            return ("bin", tok.line, tok.value, left, self.additive())
        return left

    def additive(self):
        left = self.term()
        while self.peek().kind == "OP" and self.peek().value in ("+", "-"):
            tok = self.advance()
            left = ("bin", tok.line, tok.value, left, self.term())
        return left

    def term(self):
        left = self.unary()
        while self.peek().kind == "OP" and self.peek().value in ("*", "/", "%"):
            tok = self.advance()
            left = ("bin", tok.line, tok.value, left, self.unary())
        return left

    def unary(self):
        if self.is_op("-"):
            line = self.advance().line
            return ("neg", line, self.unary())
        return self.postfix()

    def postfix(self):
        node = self.primary()
        while self.is_op("["):
            line = self.advance().line
            index = self.expression()
            self.expect_op("]")
            node = ("index", line, node, index)
        return node

    def comma_list(self, closer):
        items = []
        self.skip_newlines()
        while not self.is_op(closer):
            items.append(self.expression())
            self.skip_newlines()
            if self.is_op(","):
                self.advance()
                self.skip_newlines()
            elif not self.is_op(closer):
                self.error(f"Expected ',' or '{closer}' but found {self.describe(self.peek())}")
        self.advance()
        return items

    def primary(self):
        tok = self.peek()
        if tok.kind in ("NUM", "STR"):
            self.advance()
            return ("lit", tok.line, tok.value)
        if tok.kind == "KW" and tok.value in ("true", "false", "nothing"):
            self.advance()
            return ("lit", tok.line, {"true": True, "false": False, "nothing": None}[tok.value])
        if tok.kind == "NAME":
            self.advance()
            if self.is_op("("):
                self.advance()
                return ("call", tok.line, tok.value, self.comma_list(")"))
            return ("var", tok.line, tok.value)
        if self.is_op("("):
            self.advance()
            inner = self.expression()
            self.skip_newlines()
            self.expect_op(")")
            return inner
        if self.is_op("["):
            self.advance()
            return ("list", tok.line, self.comma_list("]"))
        self.error(f"Expected a value but found {self.describe(tok)}")
