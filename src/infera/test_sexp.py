
from infera.sexp import END_OF_FILE, IDENTIFIER, INTEGER, List, Lit, Parser, Scanner, Sym, tokenize


def test_scan_ident():
    scanner = Scanner("foo")
    t0 = scanner.scan()
    assert(t0.ty == IDENTIFIER)
    assert(t0.value == "foo")
    t1 = scanner.scan()
    assert(t1.ty == END_OF_FILE)
    assert(t1.value is None)


def test_scan_ident_2():
    scanner = Scanner("foobar")
    t0 = scanner.scan()
    assert(t0.ty == IDENTIFIER)
    assert(t0.value == "foobar")
    t1 = scanner.scan()
    assert(t1.ty == END_OF_FILE)
    assert(t1.value is None)


def test_scan_ident_underscore():
    scanner = Scanner("_foobar")
    t0 = scanner.scan()
    assert(t0.ty == IDENTIFIER)
    assert(t0.value == "_foobar")
    t1 = scanner.scan()
    assert(t1.ty == END_OF_FILE)
    assert(t1.value is None)


def test_scan_ident_underscore_2():
    scanner = Scanner("__foobar")
    t0 = scanner.scan()
    assert(t0.ty == IDENTIFIER)
    assert(t0.value == "__foobar")
    t1 = scanner.scan()
    assert(t1.ty == END_OF_FILE)
    assert(t1.value is None)


def test_scan_ident_underscore_3():
    scanner = Scanner("foo_bar")
    t0 = scanner.scan()
    assert(t0.ty == IDENTIFIER)
    assert(t0.value == "foo_bar")
    t1 = scanner.scan()
    assert(t1.ty == END_OF_FILE)
    assert(t1.value is None)


def test_scan_ident_underscore_4():
    scanner = Scanner("foo__bar")
    t0 = scanner.scan()
    assert(t0.ty == IDENTIFIER)
    assert(t0.value == "foo__bar")
    t1 = scanner.scan()
    assert(t1.ty == END_OF_FILE)
    assert(t1.value is None)


def test_scan_integer():
    scanner = Scanner("1")
    t0 = scanner.scan()
    assert(t0.ty == INTEGER)
    assert(t0.value == 1)
    t1 = scanner.scan()
    assert(t1.ty == END_OF_FILE)
    assert(t1.value is None)


def test_scan_integer_2():
    scanner = Scanner("2")
    t0 = scanner.scan()
    assert(t0.ty == INTEGER)
    assert(t0.value == 2)
    t1 = scanner.scan()
    assert(t1.ty == END_OF_FILE)
    assert(t1.value is None)


def test_scan_integer_3():
    scanner = Scanner("3")
    t0 = scanner.scan()
    assert(t0.ty == INTEGER)
    assert(t0.value == 3)
    t1 = scanner.scan()
    assert(t1.ty == END_OF_FILE)
    assert(t1.value is None)


def test_scan_integer_multiple_digits():
    scanner = Scanner("12345")
    t0 = scanner.scan()
    assert(t0.ty == INTEGER)
    assert(t0.value == 12345)
    t1 = scanner.scan()
    assert(t1.ty == END_OF_FILE)
    assert(t1.value is None)


def test_scan_integer_multiple_zeroes():
    scanner = Scanner("00345")
    t0 = scanner.scan()
    assert(t0.ty == INTEGER)
    assert(t0.value == 345)
    t1 = scanner.scan()
    assert(t1.ty == END_OF_FILE)
    assert(t1.value is None)


def test_parse_file_with_syms():
    tokens = tokenize("""
one
two
three
""")
    parser = Parser(tokens)
    els = parser.parse_file()
    assert(len(els) == 3)
    assert(isinstance(els[0], Sym))
    assert(els[0].name == 'one')
    assert(isinstance(els[1], Sym))
    assert(els[1].name == 'two')
    assert(isinstance(els[2], Sym))
    assert(els[2].name == 'three')


def test_parse_list():
    tokens = tokenize("(one two three)")
    parser = Parser(tokens)
    l = parser.parse_expr()
    assert(isinstance(l, List))
    assert(len(l.head) == 3)
    assert(isinstance(l.head[0], Sym))
    assert(l.head[0].name == 'one')
    assert(isinstance(l.head[1], Sym))
    assert(l.head[1].name == 'two')
    assert(isinstance(l.head[2], Sym))
    assert(l.head[2].name == 'three')
    assert(l.tail is None)


def test_parse_list_with_tail():
    tokens = tokenize("(one two three . four)")
    parser = Parser(tokens)
    l = parser.parse_expr()
    assert(isinstance(l, List))
    assert(len(l.head) == 3)
    assert(isinstance(l.head[0], Sym))
    assert(l.head[0].name == 'one')
    assert(isinstance(l.head[1], Sym))
    assert(l.head[1].name == 'two')
    assert(isinstance(l.head[2], Sym))
    assert(l.head[2].name == 'three')
    assert(isinstance(l.tail, Sym))
    assert(l.tail.name == 'four')


def test_parse_true():
    parser = Parser(tokenize("#t"))
    b = parser.parse_expr()
    assert(isinstance(b, Lit))
    assert(b.value is True)


def test_parse_false():
    parser = Parser(tokenize("#f"))
    b = parser.parse_expr()
    assert(isinstance(b, Lit))
    assert(b.value is False)
