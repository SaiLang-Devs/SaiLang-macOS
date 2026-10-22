"""Error types for SaiLang. Every error knows the file and line it came from."""


class SaiError(Exception):
    """Base class for all errors reported to the SaiLang user."""

    def __init__(self, message, file=None, line=None):
        self.message = message
        self.file = file
        self.line = line
        super().__init__(self.format())

    def format(self):
        where = self.file or "<input>"
        if self.line is not None:
            where += f":{self.line}"
        return f"{where}: {self.message}"


class SaiSyntaxError(SaiError):
    """The program text could not be understood."""


class SaiRuntimeError(SaiError):
    """The program understood, but could not run an instruction."""
