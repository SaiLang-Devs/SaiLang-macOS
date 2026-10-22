"""SaiLang IDLE 1.0.0: an editor and runner for .sai programs.

Programs run in a separate Python process, the same way 'python -m sailang'
runs them. This keeps a program's own windows (run_app) separate from the
editor and lets the Stop button work.
"""

import bisect
import codecs
import os
import queue
import re
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import font as tkfont

from . import __version__
from .lexer import KEYWORDS
from .stdlib import BUILTINS

APP_NAME = f"SaiLang IDLE {__version__}"
SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_RE = re.compile(
    r'#[^\n]*'                              # comment
    r'|"(?:\\.|[^"\\\n])*"?'                # text (closing quote optional while typing)
    r'|\b\d+(?:\.\d+)?\b'                   # number
    r'|[A-Za-z_][A-Za-z_0-9]*'              # word
)
ERROR_RE = re.compile(r"^(.+):(\d+): ", re.MULTILINE)
TAG_STYLES = {
    "keyword": {"foreground": "#0000cc"},
    "builtin": {"foreground": "#007a7a"},
    "string": {"foreground": "#008000"},
    "number": {"foreground": "#b35900"},
    "comment": {"foreground": "#808080"},
    "errline": {"background": "#ffd6d6"},
}


def highlight_ranges(text):
    """Return (tag, start, end) for each coloured piece of text.

    start and end are Tk index strings such as '3.4'.
    """
    starts = [0] + [m.end() for m in re.finditer("\n", text)]

    def index(offset):
        line = bisect.bisect_right(starts, offset)
        return f"{line}.{offset - starts[line - 1]}"

    ranges = []
    for match in TOKEN_RE.finditer(text):
        word = match.group(0)
        if word[0] == "#":
            tag = "comment"
        elif word[0] == '"':
            tag = "string"
        elif word[0].isdigit():
            tag = "number"
        elif word in KEYWORDS:
            tag = "keyword"
        elif word in BUILTINS:
            tag = "builtin"
        else:
            continue
        ranges.append((tag, index(match.start()), index(match.end())))
    return ranges


def child_python():
    """The python.exe that runs programs. pythonw.exe would hide the output."""
    exe = sys.executable
    if os.path.basename(exe).lower() == "pythonw.exe":
        candidate = os.path.join(os.path.dirname(exe), "python.exe")
        if os.path.exists(candidate):
            return candidate
    return exe


def child_command(path, mode=None):
    if mode == "check":
        return [child_python(), "-m", "sailang", "check", path]
    return [child_python(), "-m", "sailang", path]


def child_env():
    env = dict(os.environ)
    env["PYTHONPATH"] = SRC_DIR + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUNBUFFERED"] = "1"
    return env


def _no_window_flags():
    return getattr(subprocess, "CREATE_NO_WINDOW", 0)


class SaiIDLE:
    def __init__(self, root):
        self.root = root
        self.path = None
        self.dirty = False
        self.child = None
        self.running = False
        self.events = queue.Queue()

        root.title(APP_NAME)
        root.geometry("920x660")
        self._set_window_icon()
        root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.font = tkfont.Font(family="Consolas", size=12)
        self.bold_font = tkfont.Font(font=self.font)
        self.bold_font.configure(weight="bold")
        self.italic_font = tkfont.Font(font=self.font)
        self.italic_font.configure(slant="italic")

        self._build_menus()
        self._build_layout()
        self._new_document_state()
        self.update_status()

    def _set_window_icon(self):
        """Use the SaiLang logo as the window icon. If it cannot be loaded, keep the default icon."""
        logo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "sailang-logo.png")
        try:
            self.icon_image = tk.PhotoImage(file=logo)
            self.root.iconphoto(True, self.icon_image)
        except tk.TclError:
            pass

    # ----- layout ----------------------------------------------------------
    def _build_menus(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", accelerator="Ctrl+N", command=self.new_file)
        file_menu.add_command(label="Open...", accelerator="Ctrl+O", command=self.open_file)
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.save)
        file_menu.add_command(label="Save As...", accelerator="Ctrl+Shift+S", command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", accelerator="Ctrl+Q", command=self.on_close)
        menubar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo", accelerator="Ctrl+Z", command=lambda: self.text.edit_undo())
        edit_menu.add_command(label="Redo", accelerator="Ctrl+Y", command=lambda: self.text.edit_redo())
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", accelerator="Ctrl+X", command=lambda: self.text.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copy", accelerator="Ctrl+C", command=lambda: self.text.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Paste", accelerator="Ctrl+V", command=lambda: self.text.event_generate("<<Paste>>"))
        edit_menu.add_command(label="Select All", accelerator="Ctrl+A", command=self.select_all)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        run_menu = tk.Menu(menubar, tearoff=0)
        run_menu.add_command(label="Run Program", accelerator="F5", command=self.run_program)
        run_menu.add_command(label="Stop Program", accelerator="Esc", command=self.stop_program)
        run_menu.add_separator()
        run_menu.add_command(label="Check Syntax", accelerator="F6", command=self.check_program)
        menubar.add_cascade(label="Run", menu=run_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About SaiLang IDLE", command=self.about)
        menubar.add_cascade(label="Help", menu=help_menu)
        self.root.config(menu=menubar)

    def _build_layout(self):
        self.status = tk.Label(self.root, anchor="w", relief="sunken", padx=6)
        self.status.pack(side="bottom", fill="x")
        panes = tk.PanedWindow(self.root, orient="vertical", sashwidth=6)
        panes.pack(fill="both", expand=True)

        editor_frame = tk.Frame(panes)
        self.text = tk.Text(editor_frame, undo=True, wrap="none", font=self.font,
                            tabs=("1c",), padx=6, pady=4, insertwidth=2)
        y_scroll = tk.Scrollbar(editor_frame, command=self.text.yview)
        x_scroll = tk.Scrollbar(editor_frame, orient="horizontal", command=self.text.xview)
        self.text.config(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        x_scroll.pack(side="bottom", fill="x")
        y_scroll.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)
        panes.add(editor_frame, minsize=160)

        output_frame = tk.Frame(panes)
        self.output = tk.Text(output_frame, height=10, state="disabled", font=self.font, wrap="word",
                              padx=6, pady=4)
        out_scroll = tk.Scrollbar(output_frame, command=self.output.yview)
        self.output.config(yscrollcommand=out_scroll.set)
        out_scroll.pack(side="right", fill="y")
        self.output.tag_config("info", foreground="#555555")
        self.output.tag_config("input", foreground="#0000cc")
        self.output.tag_config("error", foreground="#b00000")

        input_row = tk.Frame(output_frame)
        input_row.pack(side="bottom", fill="x")
        tk.Label(input_row, text="Program input (press Enter to send):").pack(side="left", padx=4)
        self.input_entry = tk.Entry(input_row, font=self.font, state="disabled")
        self.input_entry.pack(side="left", fill="x", expand=True, padx=4, pady=2)
        self.input_entry.bind("<Return>", self.send_input)
        self.output.pack(side="top", fill="both", expand=True)
        panes.add(output_frame, minsize=80)


        for name, style in TAG_STYLES.items():
            if name == "keyword":
                self.text.tag_config(name, font=self.bold_font, **style)
            elif name == "comment":
                self.text.tag_config(name, font=self.italic_font, **style)
            else:
                self.text.tag_config(name, **style)
        self.text.tag_raise("errline")

        self.text.bind("<<Modified>>", self._on_modified)
        self.text.bind("<Return>", self.on_return)
        self.text.bind("<Tab>", self.on_tab)
        self.text.bind("<KeyRelease>", self.update_status)
        self.text.bind("<ButtonRelease>", self.update_status)

        self.bind_shortcut("<Control-n>", self.new_file)
        self.bind_shortcut("<Control-o>", self.open_file)
        self.bind_shortcut("<Control-s>", self.save)
        self.bind_shortcut("<Control-S>", self.save_as)
        self.bind_shortcut("<Control-q>", self.on_close)
        self.bind_shortcut("<Control-a>", self.select_all)
        self.bind_shortcut("<Control-y>", lambda: self.text.edit_redo())
        self.bind_shortcut("<F5>", self.run_program)
        self.bind_shortcut("<F6>", self.check_program)
        self.bind_shortcut("<Escape>", self.stop_program)

    def bind_shortcut(self, sequence, func):
        def handler(_event):
            func()
            return "break"
        self.root.bind(sequence, handler)
        self.text.bind(sequence, handler)
        self.output.bind(sequence, handler)

    # ----- document state --------------------------------------------------
    def _new_document_state(self):
        self.path = None
        self.dirty = False
        self.text.delete("1.0", "end")
        self.text.edit_reset()
        self.text.edit_modified(False)
        self.dirty = False
        self._update_title()

    def _update_title(self):
        name = os.path.basename(self.path) if self.path else "Untitled"
        marker = " *" if self.dirty else ""
        self.root.title(f"{name}{marker} - {APP_NAME}")

    def _on_modified(self, _event=None):
        if self.text.edit_modified():
            self.dirty = True
            self._update_title()
            self.text.edit_modified(False)
            self.highlight()

    def highlight(self):
        content = self.text.get("1.0", "end-1c")
        for tag in TAG_STYLES:
            self.text.tag_remove(tag, "1.0", "end")
        for tag, start, end in highlight_ranges(content):
            self.text.tag_add(tag, start, end)

    def update_status(self, _event=None):
        line, column = self.text.index("insert").split(".")
        state = "running" if self.running else "ready"
        location = self.path or "untitled"
        self.status.config(text=f"  {location}    Line {line}, Column {int(column) + 1}    {state}")

    def confirm_discard(self):
        """Ask before throwing away unsaved changes. Returns True to carry on."""
        if not self.dirty:
            return True
        name = os.path.basename(self.path) if self.path else "Untitled"
        answer = messagebox.askyesnocancel(APP_NAME, f"Save changes to {name}?")
        if answer is None:
            return False
        if answer:
            return self.save()
        return True

    # ----- file commands ---------------------------------------------------
    def new_file(self):
        if self.confirm_discard():
            self._new_document_state()
            self.update_status()

    def open_file(self):
        if not self.confirm_discard():
            return
        path = filedialog.askopenfilename(
            title="Open SaiLang program",
            filetypes=[("SaiLang programs", "*.sai"), ("All files", "*.*")])
        if path:
            self.open_path(path)

    def open_path(self, path):
        try:
            with open(path, encoding="utf-8-sig") as handle:
                content = handle.read()
        except OSError as ex:
            messagebox.showerror(APP_NAME, f"Could not open the file:\n{ex.strerror or ex}")
            return
        self._new_document_state()
        self.path = os.path.abspath(path)
        self.text.insert("1.0", content)
        self.text.edit_reset()
        self.text.edit_modified(False)
        self.dirty = False
        self._update_title()
        self.highlight()
        self.update_status()

    def save(self):
        if self.path is None:
            return self.save_as()
        try:
            with open(self.path, "w", encoding="utf-8") as handle:
                handle.write(self.text.get("1.0", "end-1c"))
        except OSError as ex:
            messagebox.showerror(APP_NAME, f"Could not save the file:\n{ex.strerror or ex}")
            return False
        self.dirty = False
        self._update_title()
        self.update_status()
        return True

    def save_as(self):
        path = filedialog.asksaveasfilename(
            title="Save SaiLang program", defaultextension=".sai",
            filetypes=[("SaiLang programs", "*.sai"), ("All files", "*.*")])
        if not path:
            return False
        self.path = os.path.abspath(path)
        return self.save()

    def on_close(self):
        if not self.confirm_discard():
            return
        self.stop_program(silent=True)
        self.root.destroy()

    # ----- editing helpers --------------------------------------------------
    def select_all(self):
        self.text.tag_add("sel", "1.0", "end-1c")
        self.text.mark_set("insert", "1.0")

    def on_return(self, _event):
        current = self.text.get("insert linestart", "insert")
        indent = re.match(r"[ \t]*", current).group(0)
        extra = "    " if current.rstrip().endswith("{") else ""
        self.text.insert("insert", "\n" + indent + extra)
        return "break"

    def on_tab(self, _event):
        self.text.insert("insert", "    ")
        return "break"

    def clear_output(self):
        self.output.config(state="normal")
        self.output.delete("1.0", "end")
        self.output.config(state="disabled")

    def append_output(self, text, tag=None):
        self.output.config(state="normal")
        if tag:
            self.output.insert("end", text, tag)
        else:
            self.output.insert("end", text)
        self.output.see("end")
        self.output.config(state="disabled")

    def clear_error_highlight(self):
        self.text.tag_remove("errline", "1.0", "end")

    def highlight_error(self, text):
        """Find the first 'file.sai:LINE:' in the text and highlight that line if it is this file."""
        if not self.path:
            return
        base = os.path.basename(self.path)
        for match in ERROR_RE.finditer(text):
            if os.path.basename(match.group(1)) != base:
                continue
            line = match.group(2)
            self.clear_error_highlight()
            self.text.tag_add("errline", f"{line}.0", f"{line}.end")
            self.text.see(f"{line}.0")
            self.text.mark_set("insert", f"{line}.0")
            self.update_status()
            return

    # ----- running programs -------------------------------------------------
    def ensure_saved(self):
        if self.path is None or self.dirty:
            return self.save()
        return True

    def run_program(self):
        if self.running:
            messagebox.showinfo(APP_NAME, "A program is already running. Stop it first (Esc).")
            return
        if not self.ensure_saved():
            return
        self.clear_output()
        self.clear_error_highlight()
        try:
            self.child = subprocess.Popen(
                child_command(self.path), cwd=os.path.dirname(self.path), env=child_env(),
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                creationflags=_no_window_flags())
        except OSError as ex:
            messagebox.showerror(APP_NAME, f"Could not start SaiLang:\n{ex}")
            self.child = None
            return
        self.running = True
        self.input_entry.config(state="normal")
        self.input_entry.focus_set()
        self.append_output(f"Running {os.path.basename(self.path)}...\n", "info")
        self.update_status()
        threading.Thread(target=self._reader, args=(self.child,), daemon=True).start()
        self.root.after(30, self._poll)

    def _reader(self, child):
        decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")
        while True:
            chunk = child.stdout.read1(1024)
            if not chunk:
                break
            self.events.put(("text", decoder.decode(chunk)))
        child.wait()
        self.events.put(("done", child.returncode))

    def _poll(self):
        finished = False
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == "text":
                    self.append_output(value)
                else:
                    self._finished(value)
                    finished = True
        except queue.Empty:
            pass
        if not finished and self.running:
            self.root.after(30, self._poll)

    def _finished(self, code):
        self.running = False
        self.child = None
        self.input_entry.config(state="disabled")
        self.append_output(f"\n[Program finished with exit code {code}]\n", "info")
        self.highlight_error(self.output.get("1.0", "end-1c"))
        self.update_status()

    def send_input(self, _event=None):
        if not self.running or self.child is None:
            return "break"
        line = self.input_entry.get()
        self.input_entry.delete(0, "end")
        self.append_output(line + "\n", "input")
        try:
            self.child.stdin.write((line + "\n").encode("utf-8"))
            self.child.stdin.flush()
        except (OSError, ValueError):
            pass
        return "break"

    def stop_program(self, silent=False):
        if not self.running or self.child is None:
            return
        self.child.kill()
        if not silent:
            self.append_output("[Stopped by user]\n", "info")

    def check_program(self):
        if self.running:
            messagebox.showinfo(APP_NAME, "Stop the running program before checking syntax.")
            return
        if not self.ensure_saved():
            return
        self.clear_output()
        self.clear_error_highlight()
        try:
            result = subprocess.run(
                child_command(self.path, mode="check"), cwd=os.path.dirname(self.path),
                env=child_env(), capture_output=True, text=True, encoding="utf-8",
                errors="replace", timeout=20, creationflags=_no_window_flags())
        except (OSError, subprocess.TimeoutExpired) as ex:
            messagebox.showerror(APP_NAME, f"Could not check the program:\n{ex}")
            return
        combined = (result.stdout or "") + (result.stderr or "")
        self.append_output(combined if combined.strip() else "No problems found.\n",
                           None if result.returncode == 0 else "error")
        if result.returncode != 0:
            self.highlight_error(combined)

    def about(self):
        messagebox.showinfo(
            APP_NAME,
            f"{APP_NAME}\n\nAn editor and runner for SaiLang programs (.sai).\n"
            "Language version 1.0. Built with Python and Tkinter.")


def main(argv=None):
    args = sys.argv[1:] if argv is None else list(argv)
    root = tk.Tk()
    app = SaiIDLE(root)
    if args and os.path.isfile(args[0]):
        app.open_path(args[0])
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
