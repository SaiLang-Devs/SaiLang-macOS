"""The SaiLang tokenizer. Turns source text into a list of Tokens."""

from .errors import SaiSyntaxError

KEYWORDS = {
    "make", "say", "when", "otherwise", "repeat", "times", "while", "for",
    "each", "in", "stop", "skip", "command", "give", "import", "try", "on",
    "error", "true", "false", "nothing", "and", "or", "not",
}
TWO_CHAR_OPS = {"==", "!=", "<=", ">="}
ONE_CHAR_OPS = set("=<>+-*/%()[]{},")
ESCAPES = {"n": "\n", "t": "\t", '"': '"', "\\": "\\"}


class Token:
    __slots__ = ("kind", "value", "line")

    def __init__(self, kind, value, line):
        self.kind = kind    # NUM, STR, NAME, KW, OP, NL, EOF
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.kind}, {self.value!r}, line {self.line})"


def _read_string(source, start, line, filename):
    i = start + 1
    buf = []
    n = len(source)
    while True:
        if i >= n or source[i] == "\n":
            raise SaiSyntaxError('This text is missing its closing quote (")', filename, line)
        ch = source[i]
        if ch == '"':
            return i + 1, "".join(buf)
        if ch == "\\":
            esc = source[i + 1] if i + 1 < n else ""
            if esc not in ESCAPES:
                raise SaiSyntaxError(f"Unknown escape sequence '\\{esc}' in text", filename, line)
            buf.append(ESCAPES[esc])
            i += 2
        else:
            buf.append(ch)
            i += 1


def tokenize(source, filename="<input>"):
    tokens = []
    i = 0
    line = 1
    n = len(source)
    while i < n:
        c = source[i]
        if c == "\n":
            tokens.append(Token("NL", "\n", line))
            line += 1
            i += 1
        elif c in " \t\r":
            i += 1
        elif c == "#":
            while i < n and source[i] != "\n":
                i += 1
        elif c == '"':
            i, text = _read_string(source, i, line, filename)
            tokens.append(Token("STR", text, line))
        elif c.isdigit():
            j = i
            while j < n and source[j].isdigit():
                j += 1
            if j + 1 < n and source[j] == "." and source[j + 1].isdigit():
                j += 1
                while j < n and source[j].isdigit():
                    j += 1
                tokens.append(Token("NUM", float(source[i:j]), line))
            else:
                tokens.append(Token("NUM", int(source[i:j]), line))
            i = j
        elif c.isalpha() or c == "_":
            j = i
            while j < n and (source[j].isalnum() or source[j] == "_"):
                j += 1
            word = source[i:j]
            tokens.append(Token("KW" if word in KEYWORDS else "NAME", word, line))
            i = j
        elif source[i:i + 2] in TWO_CHAR_OPS:
            tokens.append(Token("OP", source[i:i + 2], line))
            i += 2
        elif c in ONE_CHAR_OPS:
            tokens.append(Token("OP", c, line))
            i += 1
        else:
            raise SaiSyntaxError(f"I don't understand the character {c!r}", filename, line)
    tokens.append(Token("EOF", None, line))
    return tokens
