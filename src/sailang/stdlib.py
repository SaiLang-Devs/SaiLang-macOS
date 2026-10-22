"""SaiLang's standard library.

Every builtin is a function (interp, args, line) -> value, registered with
the @builtin decorator. Tkinter is imported only when a window or game is
used, so the language itself works even where Tk is missing.
"""

import base64
import math
import os
import random
import time
import urllib.request

from .errors import SaiError
from .values import Handle, is_num, to_text, type_name, values_equal

BUILTINS = {}          # name -> (function, min_args, max_args or -1)
MAX_IMAGE_BYTES = 5 * 1024 * 1024
DOWNLOAD_TIMEOUT_SECONDS = 10


def builtin(name, low, high=None):
    def register(fn):
        BUILTINS[name] = (fn, low, low if high is None else high)
        return fn
    return register


# ----- argument helpers ----------------------------------------------------
def _text(it, value, line, what="text"):
    if not isinstance(value, str):
        raise it.fail(f"{what} needs text, but got {type_name(value)}", line)
    return value


def _num(it, value, line, what="number"):
    if not is_num(value):
        raise it.fail(f"{what} needs a number, but got {type_name(value)}", line)
    return value


def _list(it, value, line, what="list"):
    if not isinstance(value, list):
        raise it.fail(f"{what} needs a list, but got {type_name(value)}", line)
    return value


# ----- text and lists -------------------------------------------------------
@builtin("length", 1)
def _length(it, a, line):
    if isinstance(a[0], (str, list)):
        return len(a[0])
    raise it.fail(f"length needs text or a list, but got {type_name(a[0])}", line)


@builtin("upper", 1)
def _upper(it, a, line):
    return _text(it, a[0], line, "upper").upper()


@builtin("lower", 1)
def _lower(it, a, line):
    return _text(it, a[0], line, "lower").lower()


@builtin("trim", 1)
def _trim(it, a, line):
    return _text(it, a[0], line, "trim").strip()


@builtin("split", 1, 2)
def _split(it, a, line):
    s = _text(it, a[0], line, "split")
    if len(a) == 1:
        return s.split()
    return s.split(_text(it, a[1], line, "split"))


@builtin("join", 2)
def _join(it, a, line):
    items = _list(it, a[0], line, "join")
    sep = _text(it, a[1], line, "join")
    return sep.join(to_text(x) for x in items)


@builtin("replace", 3)
def _replace(it, a, line):
    s = _text(it, a[0], line, "replace")
    return s.replace(_text(it, a[1], line, "replace"), _text(it, a[2], line, "replace"))


@builtin("contains", 2)
def _contains(it, a, line):
    container, item = a
    if isinstance(container, str):
        return _text(it, item, line, "contains") in container
    if isinstance(container, list):
        return any(values_equal(x, item) for x in container)
    raise it.fail(f"contains needs text or a list, but got {type_name(container)}", line)


@builtin("append", 2)
def _append(it, a, line):
    _list(it, a[0], line, "append").append(a[1])


@builtin("remove_at", 2)
def _remove_at(it, a, line):
    items = _list(it, a[0], line, "remove_at")
    items.pop(it.check_index(a[1], items, line))


@builtin("range", 1, 2)
def _range(it, a, line):
    if len(a) == 1:
        return list(range(int(_num(it, a[0], line, "range"))))
    return list(range(int(_num(it, a[0], line, "range")), int(_num(it, a[1], line, "range"))))


# ----- conversion and type -----------------------------------------------
@builtin("text", 1)
def _to_text(it, a, line):
    return to_text(a[0])


@builtin("number", 1)
def _to_number(it, a, line):
    value = a[0]
    if is_num(value):
        return value
    if isinstance(value, str):
        cleaned = value.strip()
        try:
            return int(cleaned)
        except ValueError:
            try:
                return float(cleaned)
            except ValueError:
                pass
    raise it.fail(f"'{to_text(value, True)}' is not a number", line)


@builtin("type_of", 1)
def _type_of(it, a, line):
    return type_name(a[0])


# ----- maths -----------------------------------------------------------------
@builtin("abs", 1)
def _abs(it, a, line):
    return abs(_num(it, a[0], line, "abs"))


@builtin("round", 1, 2)
def _round(it, a, line):
    if len(a) == 1:
        return round(_num(it, a[0], line, "round"))
    return round(_num(it, a[0], line, "round"), int(_num(it, a[1], line, "round")))


@builtin("floor", 1)
def _floor(it, a, line):
    return math.floor(_num(it, a[0], line, "floor"))


@builtin("ceil", 1)
def _ceil(it, a, line):
    return math.ceil(_num(it, a[0], line, "ceil"))


@builtin("sqrt", 1)
def _sqrt(it, a, line):
    value = _num(it, a[0], line, "sqrt")
    if value < 0:
        raise it.fail("sqrt needs a number that is zero or more", line)
    return math.sqrt(value)


@builtin("min", 1, -1)
def _min(it, a, line):
    values = a[0] if len(a) == 1 and isinstance(a[0], list) else a
    if not values:
        raise it.fail("min needs at least one number", line)
    return min(_num(it, v, line, "min") for v in values)


@builtin("max", 1, -1)
def _max(it, a, line):
    values = a[0] if len(a) == 1 and isinstance(a[0], list) else a
    if not values:
        raise it.fail("max needs at least one number", line)
    return max(_num(it, v, line, "max") for v in values)


@builtin("random", 2)
def _random(it, a, line):
    low = _num(it, a[0], line, "random")
    high = _num(it, a[1], line, "random")
    if low > high:
        raise it.fail(f"random needs the smaller number first ({low} is bigger than {high})", line)
    if isinstance(low, int) and isinstance(high, int):
        return random.randint(low, high)
    return random.uniform(low, high)


@builtin("now", 0)
def _now(it, a, line):
    return time.time()


# ----- input and files -------------------------------------------------------
@builtin("ask", 0, 1)
def _ask(it, a, line):
    prompt = to_text(a[0]) if a else ""
    return it.input_fn(prompt)


def _read_text(it, path, line):
    path = _text(it, path, line, "read_file")
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read()
    except OSError as ex:
        raise it.fail(f"I could not read '{path}': {ex.strerror or ex}", line)


@builtin("read_file", 1)
def _read_file(it, a, line):
    return _read_text(it, a[0], line)


def _write(it, path, text, line, mode):
    path = _text(it, path, line, "write_file")
    try:
        with open(path, mode, encoding="utf-8") as handle:
            handle.write(to_text(text))
    except OSError as ex:
        raise it.fail(f"I could not write '{path}': {ex.strerror or ex}", line)


@builtin("write_file", 2)
def _write_file(it, a, line):
    _write(it, a[0], a[1], line, "w")


@builtin("append_file", 2)
def _append_file(it, a, line):
    _write(it, a[0], a[1], line, "a")


@builtin("file_exists", 1)
def _file_exists(it, a, line):
    return os.path.exists(_text(it, a[0], line, "file_exists"))


# ----- desktop windows -------------------------------------------------------
def _tk(it, line):
    try:
        import tkinter
    except ImportError:
        raise it.fail(
            "Desktop windows need Tkinter. Install Python from python.org and keep the "
            "'tcl/tk and IDLE' option ticked.", line)
    return tkinter


def _gui(it):
    if it.gui is None:
        it.gui = {"root": None, "canvas": None, "keys": set(), "timers": []}
    return it.gui


def _parent(it, handle, line):
    if not isinstance(handle, Handle) or handle.kind != "window":
        raise it.fail(f"Expected a window from open_window(...), but got {type_name(handle)}", line)
    return handle.obj


def _make_window(it, title, width, height, line):
    tk = _tk(it, line)
    g = _gui(it)
    width = int(_num(it, width, line, "open_window"))
    height = int(_num(it, height, line, "open_window"))
    try:
        if g["root"] is None:
            top = tk.Tk()
            g["root"] = top
            top.report_callback_exception = lambda exc, val, tb: it.report_error(str(val))
        else:
            top = tk.Toplevel(g["root"])
        top.title(to_text(title))
        top.geometry(f"{width}x{height}")
        frame = tk.Frame(top)
        frame.pack(fill="both", expand=True, padx=8, pady=8)
    except tk.TclError as ex:
        raise it.fail(f"I could not open a window on this computer ({ex})", line)
    return Handle("window", frame, {"top": top, "tk": tk})


@builtin("open_window", 3)
def _open_window(it, a, line):
    return _make_window(it, a[0], a[1], a[2], line)


@builtin("label", 2)
def _label(it, a, line):
    tk = _tk(it, line)
    widget = tk.Label(_parent(it, a[0], line), text=to_text(a[1]))
    widget.pack(pady=4)
    return Handle("label", widget)


@builtin("button", 3)
def _button(it, a, line):
    tk = _tk(it, line)
    parent = _parent(it, a[0], line)
    command_name = _text(it, a[2], line, "button (third input: the command name in quotes)")

    def clicked():
        it.call(command_name, [], it.globals, line)

    widget = tk.Button(parent, text=to_text(a[1]), command=clicked)
    widget.pack(pady=4)
    return Handle("button", widget)


@builtin("entry", 1)
def _entry(it, a, line):
    tk = _tk(it, line)
    widget = tk.Entry(_parent(it, a[0], line), width=30)
    widget.pack(pady=4)
    return Handle("entry", widget)


@builtin("entry_text", 1)
def _entry_text(it, a, line):
    if not isinstance(a[0], Handle) or a[0].kind != "entry":
        raise it.fail("entry_text needs an entry from entry(window)", line)
    return a[0].obj.get()


@builtin("set_text", 2)
def _set_text(it, a, line):
    handle = a[0]
    if not isinstance(handle, Handle) or handle.kind not in ("label", "button", "entry"):
        raise it.fail("set_text needs a label, button, or entry", line)
    text = to_text(a[1])
    if handle.kind == "entry":
        handle.obj.delete(0, "end")
        handle.obj.insert(0, text)
    else:
        handle.obj.config(text=text)


def _load_image_bytes(it, source, line):
    """Read image bytes from a local path or an http(s) URL, with size and time limits."""
    if source.startswith(("http://", "https://")):
        request = urllib.request.Request(source, headers={"User-Agent": "SaiLang/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=DOWNLOAD_TIMEOUT_SECONDS) as response:
                data = response.read(MAX_IMAGE_BYTES + 1)
        except Exception as ex:
            reason = getattr(ex, "reason", None) or ex
            raise it.fail(f"I could not download the image from '{source}': {reason}", line)
        if len(data) > MAX_IMAGE_BYTES:
            raise it.fail("That image is larger than 5 MB. Please choose a smaller image.", line)
        return data
    if "://" in source:
        raise it.fail(f"'{source}' is not a supported address. Use a local file or an http:// or https:// URL.", line)
    try:
        with open(source, "rb") as handle:
            return handle.read()
    except OSError as ex:
        raise it.fail(f"I could not open the image '{source}': {ex.strerror or ex}", line)


@builtin("show_image", 2)
def _show_image(it, a, line):
    tk = _tk(it, line)
    parent = _parent(it, a[0], line)
    source = _text(it, a[1], line, "show_image")
    data = _load_image_bytes(it, source, line)
    try:
        photo = tk.PhotoImage(data=base64.b64encode(data).decode("ascii"))
    except tk.TclError:
        raise it.fail(f"'{source}' is not a supported image. This version shows PNG and GIF images.", line)
    widget = tk.Label(parent, image=photo)
    widget.image = photo  # keep a reference so Tk does not discard the picture
    widget.pack(pady=4)
    return Handle("image", widget)


@builtin("run_app", 0)
def _run_app(it, a, line):
    g = _gui(it)
    if g["root"] is None:
        raise it.fail("There is no window to run yet. Create one with open_window(...) first.", line)
    g["root"].mainloop()
    g["root"] = None
    g["canvas"] = None


# ----- games -----------------------------------------------------------------
@builtin("open_game", 3)
def _open_game(it, a, line):
    window = _make_window(it, a[0], a[1], a[2], line)
    tk = window.extra["tk"]
    top = window.extra["top"]
    g = _gui(it)
    canvas = tk.Canvas(window.obj, width=int(a[1]), height=int(a[2]), bg="white", highlightthickness=0)
    canvas.pack()
    top.bind_all("<KeyPress>", lambda e: g["keys"].add(e.keysym.lower()))
    top.bind_all("<KeyRelease>", lambda e: g["keys"].discard(e.keysym.lower()))
    g["canvas"] = canvas
    return window


def _canvas(it, line):
    g = _gui(it)
    if g["canvas"] is None:
        raise it.fail("Start a game first with open_game(title, width, height).", line)
    return g["canvas"]


@builtin("clear_screen", 0)
def _clear_screen(it, a, line):
    _canvas(it, line).delete("all")


@builtin("draw_rect", 5)
def _draw_rect(it, a, line):
    x, y, w, h = (_num(it, v, line, "draw_rect") for v in a[:4])
    _canvas(it, line).create_rectangle(x, y, x + w, y + h, fill=to_text(a[4]), outline="")


@builtin("draw_circle", 4)
def _draw_circle(it, a, line):
    x, y, r = (_num(it, v, line, "draw_circle") for v in a[:3])
    _canvas(it, line).create_oval(x - r, y - r, x + r, y + r, fill=to_text(a[3]), outline="")


@builtin("draw_text", 4)
def _draw_text(it, a, line):
    x, y = (_num(it, v, line, "draw_text") for v in a[:2])
    _canvas(it, line).create_text(
        x, y, text=to_text(a[2]), fill=to_text(a[3]), anchor="nw", font=("Arial", 14, "bold"))


@builtin("key_down", 1)
def _key_down(it, a, line):
    return _text(it, a[0], line, "key_down").lower() in _gui(it)["keys"]


@builtin("overlaps", 8)
def _overlaps(it, a, line):
    x1, y1, w1, h1, x2, y2, w2, h2 = (_num(it, v, line, "overlaps") for v in a)
    return not (x1 + w1 <= x2 or x2 + w2 <= x1 or y1 + h1 <= y2 or y2 + h2 <= y1)


@builtin("every", 2)
def _every(it, a, line):
    g = _gui(it)
    if g["root"] is None:
        raise it.fail("Open a window or game before using every(...).", line)
    interval = int(_num(it, a[0], line, "every"))
    command_name = _text(it, a[1], line, "every (second input: the command name in quotes)")
    state = {"active": True, "id": None}
    g["timers"].append(state)

    def tick():
        if not state["active"]:
            return
        state["id"] = g["root"].after(interval, tick)   # schedule first so errors cannot stop the loop
        it.call(command_name, [], it.globals, line)

    state["id"] = g["root"].after(interval, tick)


@builtin("stop_timer", 0)
def _stop_timer(it, a, line):
    g = _gui(it)
    for state in g["timers"]:
        state["active"] = False
        if state["id"] is not None and g["root"] is not None:
            try:
                g["root"].after_cancel(state["id"])
            except Exception:
                pass
    g["timers"].clear()
