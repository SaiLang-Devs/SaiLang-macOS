"""SaiLang: a beginner-friendly general-purpose programming language."""

__version__ = "1.0.0"
LANGUAGE_VERSION = "1.0"

from .interpreter import Interpreter  # noqa: E402
from .errors import SaiError  # noqa: E402

__all__ = ["Interpreter", "SaiError", "__version__", "LANGUAGE_VERSION"]
