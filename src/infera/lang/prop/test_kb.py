
from infera.lang.prop.node import Prop, PropTerm, PropVar
from infera.util import frozen
from .kb import DTree


def PropAnd(a: Prop, b: Prop) -> Prop:
    return PropTerm('and', frozen([ a, b ]))


def PropNot(a: Prop) -> Prop:
    return PropTerm('not', frozen([ a ]))


def PropOr(a: Prop, b: Prop) -> Prop:
    return PropTerm('or', frozen([ a, b ]))


def test_empty_dtree():
    t = DTree()

    x1 = set(t.lookup(PropVar('a')))
    assert(len(x1) == 0)

    x2 = set(t.lookup(PropVar('b')))
    assert(len(x2) == 0)

    x3 = set(t.lookup(PropAnd(PropVar('a'), PropVar('b'))))
    assert(len(x3) == 0)


def test_dtree_diff_var_same_value():

    t1 = DTree()
    t1.add(PropVar('a'), 42)
    x1 = set(t1.lookup(PropVar('a')))
    assert(len(x1) == 1)
    assert(42 in x1)
    x2 = set(t1.lookup(PropVar('b')))
    assert(len(x2) == 1)
    assert(42 in x2)

    t2 = DTree()
    t2.add(PropAnd(PropVar('a'), PropVar('b')), 42)
    x3 = set(t2.lookup(PropAnd(PropVar('c'), PropVar('d'))))
    assert(len(x3) == 1)
    assert(42 in x3)

    t3 = DTree()
    t3.add(PropNot(PropVar('x')), 42)
    x4 = set(t3.lookup(PropNot(PropVar('y'))))
    assert(len(x4) == 1)
    assert(42 in x4)


def test_dtree_lookup_multiple():
    t1 = DTree()
    t1.add(PropNot(PropVar('x')), 42)
    t1.add(PropNot(PropVar('y')), 43)
    t1.add(PropNot(PropVar('z')), 44)
    x1 = set(t1.lookup(PropNot(PropVar('y'))))
    assert(len(x1) == 3)
    assert(42 in x1)
    assert(43 in x1)
    assert(44 in x1)


def test_dtree_mixed():
    t1 = DTree()
    t1.add(PropNot(PropVar('x')), 42)
    t1.add(PropAnd(PropVar('a'), PropVar('b')), 43)
    t1.add(PropAnd(PropVar('a'), PropNot(PropVar('b'))), 43)
    t1.add(PropNot(PropAnd(PropVar('a'), PropNot(PropVar('b')))), 42)

    x1 = set(t1.lookup(PropNot(PropVar('x'))))
    assert(len(x1) == 1)
    assert(42 in x1)

    x2 = set(t1.lookup(PropAnd(PropVar('a'), PropVar('b'))))
    assert(len(x2) == 1)
    assert(43 in x2)

def test_dtree_long():
    t1 = DTree()
    t1.add(PropVar('k'), 11)
    t1.add(PropVar('k'), 12)
    t1.add(PropNot(PropNot(PropVar('x'))), 42)
    t1.add(PropAnd(PropNot(PropVar('x')), PropNot(PropVar('y'))), 43)
    t1.add(PropAnd(PropVar('x'), PropVar('y')), 43)
    x1 = set(t1.lookup(PropNot(PropNot(PropNot(PropVar('y'))))))
    assert(len(x1) == 3)
    assert(11 in x1)
    assert(12 in x1)
    assert(42 in x1)

    # (and (not (not (not d))) (not c))
    x2 = set(t1.lookup(PropAnd(PropNot(PropNot(PropNot(PropVar('d')))), PropNot(PropVar('c')))))
    assert(len(x2) == 3)
    assert(11 in x2)
    assert(12 in x2)
    assert(43 in x2)

    x3 = set(t1.lookup(PropNot(PropVar('x'))))
    assert(len(x3) == 2)
    assert(11 in x3)
    assert(12 in x3)

    x4 = set(t1.lookup(PropOr(PropVar('x'), PropVar('y'))))
    assert(len(x4) == 2)
    assert(11 in x4)
    assert(12 in x4)

    x5 = set(t1.lookup(PropVar('x')))
    assert(len(x5) == 2)
    assert(11 in x5)
    assert(12 in x5)
