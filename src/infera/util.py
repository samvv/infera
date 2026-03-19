

import sys
from typing import Any, BinaryIO, TextIO, override


def implies(precedent: bool, consequent: bool) -> bool:
    """
    Python has no built-in operator for calculating the logical implication.
    """
    return not precedent or consequent


ANSI_CLEAR_LINE = '\33[2K\r'

def splitlast(text: str, seek: str) -> tuple[str, str | None]:
    for i, ch in enumerate(reversed(text)):
        if ch == seek:
            k = len(text)-i
            return text[:k-1], text[k:]
    return text, None

class Progress(TextIO):

    def __init__(self, out: TextIO = sys.stderr) -> None:
        self.enabled = True
        self._line_buffer = ''
        self.out = out
        self._progress_text = ''

    @property
    @override
    def buffer(self) -> BinaryIO:
        return self.out.buffer

    @property
    @override
    def encoding(self) -> str:
        return self.out.encoding

    @property
    @override
    def errors(self) -> str | None:
        return self.out.errors

    @property
    @override
    def line_buffering(self) -> int:
        return self.out.line_buffering

    @property
    @override
    def newlines(self) -> Any:
        return self.out.newlines

#     @override
#     def __enter__(self) -> 'Progress':
#         return self

#     def __exit__(self, type: type[BaseException] | None, value: BaseException | None, traceback: TracebackType | None, /) -> None:
#         self.out.__exit__(type, value, traceback)

    @override
    def write(self, data: str) -> int:
        if not self._progress_text:
            return self.out.write(data)
        chunk, last = splitlast(data, '\n')
        if last is None: # no newline in data
            self._line_buffer += chunk
            return len(data)
        self.out.write(ANSI_CLEAR_LINE + '\r' + self._line_buffer + chunk + '\n')
        self._write_progress()
        self._line_buffer = last
        return len(data)

    def _replace_last_line(self, text: str) -> None:
        self.out.write(ANSI_CLEAR_LINE + '\r' + text)

    def _write_progress(self) -> None:
        self._replace_last_line(self._progress_text)

    def status(self, text: str) -> None:
        self.enabled = True
        self._progress_text = text
        self._write_progress()

    def finish(self, message: str) -> None:
        if not self._progress_text:
            self.out.write(message + '\n')
            return
        self._replace_last_line(self._line_buffer + message)
        self.out.write('\n')
        self.enabled = False
