
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
import re
from typing import Any, NewType

type SExp = Atom | List

@dataclass
class Keyword:
    name: str

@dataclass
class Sym:
    name: str

@dataclass
class Lit:
    value: bool | int | str

type Atom = Sym | Lit | Keyword

@dataclass
class List:
    head: Sequence[SExp]
    tail: SExp | None = None

EOF = '\uFFFF'

TokenType = NewType('TokenType', int)

END_OF_FILE = TokenType(0)
INTEGER = TokenType(1)
STRING = TokenType(2)
LPAREN = TokenType(3)
RPAREN = TokenType(4)
IDENTIFIER = TokenType(5)
DOT = TokenType(6)
TRUE = TokenType(7)
FALSE = TokenType(8)
KEYWORD = TokenType(9)

@dataclass
class Token:
    ty: TokenType
    value: Any = None

class ScanError(RuntimeError):
    pass

def is_operator(ch: str) -> bool:
    return re.match(r"[-+*/%^&|<>=?!$]", ch) is not None

class Scanner:

    def __init__(self, text: str) -> None:
        self.text = text
        self.offset = 0

    def _get(self) -> str:
        if self.offset == len(self.text):
            return EOF
        ch = self.text[self.offset]
        self.offset += 1
        return ch

    def _peek(self) -> str:
        return self.text[self.offset] if self.offset < len(self.text) else EOF

    def _scan_identifier(self) -> str:
        text = ''
        while True:
            c1 = self._peek()
            if not (c1.isalnum() or c1 == '_' or is_operator(c1)):
                break
            text += c1
            self._get()
        return text

    def scan(self) -> Token:
        while True:
            c0 = self._get()
            if re.match("[\n\r\t ]", c0) is not None:
                continue
            if c0 == ';':
                while True:
                    c1 = self._get()
                    if c1 == '\n' or c1 == EOF:
                        break
                continue
            break
        if c0 == EOF:
            return Token(END_OF_FILE)
        if c0 == '(':
            return Token(LPAREN)
        if c0 == ')':
            return Token(RPAREN)
        if c0 == '#':
            if self._peek() == ':':
                self._get()
                return Token(KEYWORD, self._scan_identifier())
            c1 = self._scan_identifier()
            if c1 == 't':
                return Token(TRUE)
            if c1 == 'f':
                return Token(FALSE)
            raise ScanError("unknown special form (expected #t or #f)")
        if c0 == '.':
            # TODO check not followed by alpha | underscore | operator
            return Token(DOT)
        if c0.isdigit():
            value = int(c0)
            while True:
                c1 = self._peek()
                if not c1.isdigit():
                    break
                value = value * 10 + int(c1)
                self._get()
            return Token(INTEGER, value)
        if c0.isalpha() or c0 == '_' or is_operator(c0):
            text = c0 + self._scan_identifier()
            return Token(IDENTIFIER, text)
        raise ScanError(f"unexpected character '{c0}'")

    def scan_all(self) -> Iterable[Token]:
        while True:
            t0 = self.scan()
            if t0.ty == END_OF_FILE:
                break
            yield t0

def tokenize(text: str) -> list[Token]:
    return list(Scanner(text).scan_all())

class ParseError(RuntimeError):
    pass

class Parser:

    def __init__(self, tokens: Sequence[Token]) -> None:
        self.tokens = tokens
        self.offset = 0

    def _get(self) -> Token:
        if self.offset == len(self.tokens):
            return Token(END_OF_FILE)
        token = self.tokens[self.offset]
        self.offset += 1
        return token

    def _peek(self) -> Token:
        return self.tokens[self.offset] if self.offset < len(self.tokens) else Token(END_OF_FILE)

    def _expect_token(self, ty: TokenType) -> None:
        if self._get().ty != ty:
            raise ParseError(f"expected {ty}")

    def parse_expr(self) -> SExp:
        t0 = self._get()
        if t0.ty == IDENTIFIER:
            return Sym(t0.value)
        if t0.ty == TRUE:
            return Lit(True)
        if t0.ty == FALSE:
            return Lit(False)
        if t0.ty == INTEGER:
            return Lit(t0.value)
        if t0.ty == STRING:
            return Lit(t0.value)
        if t0.ty == KEYWORD:
            print(t0.value)
            return Keyword(t0.value)
        if t0.ty == LPAREN:
            head = []
            tail = None
            if self._peek() != RPAREN:
                while True:
                    head.append(self.parse_expr())
                    t2 = self._peek()
                    if t2.ty == RPAREN:
                        self._get()
                        break
                    if t2.ty == DOT:
                        self._get()
                        tail = self.parse_expr()
                        self._expect_token(RPAREN)
                        break
            return List(head, tail)
        raise ParseError(f"unexpected token {t0.ty}")

    def parse_file(self) -> Sequence[SExp]:
        elements = []
        while True:
            t0 = self._peek()
            if t0.ty == END_OF_FILE:
                break
            elements.append(self.parse_expr())
        self._expect_token(END_OF_FILE)
        return elements


def parse_file(text: str, filename: str | None = None) -> Sequence[SExp]:
    return Parser(tokenize(text)).parse_file()
