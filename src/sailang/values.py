"""Runtime values: scopes, commands, GUI handles, and conversion helpers.

SaiLang values map onto Python values as follows:
    number   -> int or float        text    -> str
    truth    -> bool                nothing -> None
    list     -> list                command -> Command
    window / label / ... -> Handle
"""


class Scope:
    """A set of variables. Only command calls and the top level create scopes."""

    __slots__ = ("vars", "parent", "is_function")

    def __init__(self, parent=None, is_function=False):
        self.vars = {}
        self.parent = parent
        self.is_function = is_function


class Command:
    """A command defined with the 'command' keyword."""

    def __init__(self, name, params, body, file, line):
        self.name = name
        self.params = params
        self.body = body
        self.file = file
        self.line = line


class Handle:
    """A reference to a desktop or game widget (window, label, button, ...)."""

    def __init__(self, kind, obj, extra=None):
        self.kind = kind
        self.obj = obj
        self.extra = extra or {}


MISSING = object()


def is_num(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def type_name(value):
    if value is None:
        return "nothing"
    if isinstance(value, bool):
        return "truth value"
    if isinstance(value, str):
        return "text"
    if is_num(value):
        return "number"
    if isinstance(value, list):
        return "list"
    if isinstance(value, Command):
        return "command"
    if isinstance(value, Handle):
        return value.kind
    return type(value).__name__


def to_text(value, quote=False):
    """Convert a value to the text that 'say' shows."""
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "nothing"
    if isinstance(value, str):
        return f'"{value}"' if quote else value
    if isinstance(value, list):
        return "[" + ", ".join(to_text(v, True) for v in value) + "]"
    if isinstance(value, Command):
        return f"<command {value.name}>"
    if isinstance(value, Handle):
        return f"<{value.kind}>"
    return str(value)


def values_equal(a, b):
    """Equality that never treats truth values as numbers (true != 1)."""
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a == b
    if is_num(a) and is_num(b):
        return a == b
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(values_equal(x, y) for x, y in zip(a, b))
    return type(a) is type(b) and a == b
