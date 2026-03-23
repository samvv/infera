
from infera.lang.prop.node import Prop, PropTerm, PropVar
from infera.util import frozen
from .kb import DTree


def PropAnd(a: Prop, b: Prop) -> Prop:
    return PropTerm('and', frozen([ a, b ]))


def PropNot(a: Prop) -> Prop:
    return PropTerm('not', frozen([ a ]))


def test_empty_dtree():
    t = DTree()

    x1 = t.lookup(PropVar('a'))
    assert(len(x1) == 0)

    x2 = t.lookup(PropVar('b'))
    assert(len(x2) == 0)

    x3 = t.lookup(PropAnd(PropVar('a'), PropVar('b')))
    assert(len(x3) == 0)


def test_dtree_diff_var_same_value():

    t1 = DTree()
    t1.add(PropVar('a'), 42)
    x1 = t1.lookup(PropVar('a'))
    assert(len(x1) == 1)
    assert(x1[0] == 42)
    x2 = t1.lookup(PropVar('b'))
    assert(len(x2) == 1)
    assert(x2[0] == 42)

    t2 = DTree()
    t2.add(PropAnd(PropVar('a'), PropVar('b')), 42)
    x3 = t2.lookup(PropAnd(PropVar('c'), PropVar('d')))
    assert(len(x3) == 1)
    assert(x3[0] == 42)

    t3 = DTree()
    t3.add(PropNot(PropVar('x')), 42)
    x4 = t3.lookup(PropNot(PropVar('y')))
    assert(len(x4) == 1)
    assert(x4[0] == 42)


def test_dtree_lookup_multiple():
    t1 = DTree()
    t1.add(PropNot(PropVar('x')), 42)
    t1.add(PropNot(PropVar('y')), 43)
    t1.add(PropNot(PropVar('z')), 44)
    x1 = t1.lookup(PropNot(PropVar('y')))
    assert(len(x1) == 3)
    assert(x1[0] == 42)
    assert(x1[1] == 43)
    assert(x1[2] == 44)


def test_dtree_mixed():
    t1 = DTree()
    t1.add(PropNot(PropVar('x')), 42)
    t1.add(PropAnd(PropVar('a'), PropVar('b')), 43)
    t1.add(PropAnd(PropVar('a'), PropNot(PropVar('b'))), 43)
    t1.add(PropNot(PropAnd(PropVar('a'), PropNot(PropVar('b')))
    ), 42)
    x1 = t1.lookup(PropNot(PropVar('x')))
    assert(len(x1) == 1)
    assert(x1[0] == 42)
    x2 = t1.lookup(PropAnd(PropVar('a'), PropVar('b')))
    assert(len(x2) == 1)
    assert(x2[0] == 43)
