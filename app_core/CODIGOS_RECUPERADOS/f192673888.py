#   Copyright 2000-2010 Michael Hudson-Doyle <micahel@gmail.com>
#                       Alex Gaynor
#                       Antonio Cuni
#                       Armin Rigo
#                       Holger Krekel
#
#                        All Rights Reserved
#
#
# Permission to use, copy, modify, and distribute this software and
# its documentation for any purpose is hereby granted without fee,
# provided that the above copyright notice appear in all copies and
# that both that copyright notice and this permission notice appear in
# supporting documentation.
#
# THE AUTHOR MICHAEL HUDSON DISCLAIMS ALL WARRANTIES WITH REGARD TO
# THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS, IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL,
# INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER
# RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF
# CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""A compatibility wrapper reimplementing the 'readline' standard module
on top of pyrepl.  Not all functionalities are supported.  Contains
extensions for multiline input.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field

import os
from site import gethistoryfile
import sys
from rlcompleter import Completer as RLCompleter

from . import commands, historical_reader
from .completing_reader import CompletingReader
from .console import Console as ConsoleType

Console: type[ConsoleType]
_error: tuple[type[Exception], ...] | type[Exception]

if os.name == "nt":
    from .windows_console import WindowsConsole as Console, _error
else:
    from .unix_console import UnixConsole as Console, _error

ENCODING = sys.getdefaultencoding() or "latin1"


# types
Command = commands.Command
from collections.abc import Callable, Collection
from .types import Callback, Completer, KeySpec, CommandName

TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import Any, Mapping


MoreLinesCallable = Callable[[str], bool]


__all__ = [
    "add_history",
    "clear_history",
    "get_begidx",
    "get_completer",
    "get_completer_delims",
    "get_current_history_length",
    "get_endidx",
    "get_history_item",
    "get_history_length",
    "get_line_buffer",
    "insert_text",
    "parse_and_bind",
    "read_history_file",
    # "read_init_file",
    # "redisplay",
    "remove_history_item",
    "replace_history_item",
    "set_auto_history",
    "set_completer",
    "set_completer_delims",
    "set_history_length",
    # "set_pre_input_hook",
    "set_startup_hook",
    "write_history_file",
    # ---- multiline extensions ----
    "multiline_input",
]

# ____________________________________________________________

@dataclass
class ReadlineConfig:
    readline_completer: Completer | None = None
    completer_delims: frozenset[str] = frozenset(" \t\n`~!@#$%^&*()-=+[{]}\\|;:'\",<>/?")


@dataclass(kw_only=True)
class ReadlineAlikeReader(historical_reader.HistoricalReader, CompletingReader):
    # Class fields
    assume_immutable_completions = False
    use_brackets = False
    sort_in_column = True

    # Instance fields
    config: ReadlineConfig
    more_lines: MoreLinesCallable | None = None
    last_used_indentation: str | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        self.commands["maybe_accept"] = maybe_accept
        self.commands["maybe-accept"] = maybe_accept
        self.commands["backspace_dedent"] = backspace_dedent
        self.commands["backspace-dedent"] = backspace_dedent

    def error(self, msg: str = "none") -> None:
        pass  # don't show error messages by default

    def get_stem(self) -> str:
        b = self.buffer
        p = self.pos - 1
        completer_delims = self.config.completer_delims
        while p >= 0 and b[p] not in completer_delims:
            p -= 1
        return "".join(b[p + 1 : self.pos])

    def get_completions(self, stem: str) -> list[str]:
        if len(stem) == 0 and self.more_lines is not None:
            b = self.buffer
            p = self.pos
            while p > 0 and b[p - 1] != "\n":
                p -= 1
            num_spaces = 4 - ((self.pos - p) % 4)
            return [" " * num_spaces]
        result = []
        function = self.config.readline_completer
        if function is not None:
            try:
                stem = str(stem)  # rlcompleter.py seems to not like unicode
            except UnicodeEncodeError:
                pass  # but feed unicode anyway if we have no choice
            state = 0
            while True:
                try:
                    next = function(stem, state)
                except Exception:
                    break
                if not isinstance(next, str):
                    break
                result.append(next)
                state += 1
            # emulate the behavior of the standard readline that sorts
            # the completions before displaying them.
            result.sort()
        return result

    def get_trimmed_history(self, maxlength: int) -> list[str]:
        if maxlength >= 0:
            cut = len(self.history) - maxlength
            if cut < 0:
                cut = 0
        else:
            cut = 0
        return self.history[cut:]

    def update_last_used_indentation(self) -> None:
        indentation = _get_first_indentation(self.buffer)
        if indentation is not None:
            self.last_used_indentation = indentation

    # --- simplified support for reading multiline Python statements ---

    def collect_keymap(self) -> tuple[tuple[KeySpec, CommandName], ...]:
        return super().collect_keymap() + (
            (r"\n", "maybe-accept"),
            (r"\<backspace>", "backspace-dedent"),
        )

    def after_command(self, cmd: Command) -> None:
        super().after_command(cmd)
        if self.more_lines is None:
            # Force single-line input if we are in raw_input() mode.
            # Although there is no direct way to add a \n in this mode,
            # multiline buffers can still show up using various
            # commands, e.g. navigating the history.
            try:
                index = self.buffer.index("\n")
            except ValueError:
                pass
            else:
                self.buffer = self.buffer[:index]
                if self.pos > len(self.buffer):
                    self.pos = len(self.buffer)


def set_auto_history(_should_auto_add_history: bool) -> None:
    """Enable or disable automatic history"""
    historical_reader.should_auto_add_history = bool(_should_auto_add_history)


def _get_this_line_indent(buffer: list[str], pos: int) -> int:
    indent = 0
    while pos > 0 and buffer[pos - 1] in " \t":
        indent += 1
        pos -= 1
    if pos > 0 and buffer[pos - 1] == "\n":
        return indent
    return 0


def _get_previous_line_indent(buffer: list[str], pos: int) -> tuple[int, int | None]:
    prevlinestart = pos
    while prevlinestart > 0 and buffer[prevlinestart - 1] != "\n":
        prevlinestart -= 1
    prevlinetext = prevlinestart
    while prevlinetext < pos and buffer[prevlinetext] in " \t":
        prevlinetext += 1
    if prevlinetext == pos:
        indent = None
    else:
        indent = prevlinetext - prevlinestart
    return prevlinestart, indent


def _get_first_indentation(buffer: list[str]) -> str | None:
    indented_line_start = None
    for i in range(len(buffer)):
        if (i < len(buffer) - 1
            and buffer[i] == "\n"
            and buffer[i + 1] in " \t"
        ):
            indented_line_start = i + 1
        elif indented_line_start is not None and buffer[i] not in " \t\n":
            return ''.join(buffer[indented_line_start : i])
    return None


def _should_auto_indent(buffer: list[str], pos: int) -> bool:
    # check if last character before "pos" is a colon, ignoring
    # whitespaces and comments.
    last_char = None
    while pos > 0:
        pos -= 1
        if last_char is None:
            if buffer[pos] not in " \t\n#":  # ignore whitespaces and comments
      