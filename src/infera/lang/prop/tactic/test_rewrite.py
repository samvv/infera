
from infera.lang.prop.node import Prop, PropTerm, PropVar, TermChildIndex
from infera.lang.prop.tactic.rewrite import enumerate_paths
from infera.util import frozen


def PropAnd(a: Prop, b: Prop) -> Prop:
    return PropTerm('and', frozen([ a, b ]))


def PropNot(a: Prop) -> Prop:
    return PropTerm('not', frozen([ a ]))


def PropOr(a: Prop, b: Prop) -> Prop:
    return PropTerm('or', frozen([ a, b ]))

def PropEquiv(a: Prop, b: Prop) -> Prop:
    return PropTerm('equiv', frozen([ a, b ]))


def test_enumerate_paths():
    x1 = PropVar('x')
    p1 = set(enumerate_paths(x1))
    assert(len(p1) == 1)
    assert(frozen([]) in p1)

    x2 = PropNot(PropVar('x'))
    p2 = set(enumerate_paths(x2))
    assert(len(p2) == 2)
    assert(frozen([]) in p2)
    assert(frozen([ TermChildIndex(0) ]) in p2)


    x3 = PropAnd(PropVar('x'), PropVar('y'))
    p3 = set(enumerate_paths(x3))
    assert(len(p3) == 3)
    assert(frozen([]) in p3)
    assert(frozen([ TermChildIndex(0) ]) in p3)
    assert(frozen([ TermChildIndex(1) ]) in p3)

    x4 = PropOr(PropVar('x'), PropVar('y'))
    p4 = set(enumerate_paths(x4))
    assert(len(p4) == 3)
    assert(frozen([]) in p4)
    assert(frozen([ TermChildIndex(0) ]) in p4)
    assert(frozen([ TermChildIndex(1) ]) in p4)

    x5 = PropOr(PropNot(PropVar('x')), PropNot(PropVar('y')))
    p5 = set(enumerate_paths(x5))
    assert(len(p5) == 5)
    assert(frozen([]) in p5)
    assert(frozen([ TermChildIndex(0) ]) in p5)
    assert(frozen([ TermChildIndex(1) ]) in p5)
    assert(frozen([ TermChildIndex(0), TermChildIndex(0) ]) in p5)
    assert(frozen([ TermChildIndex(1), TermChildIndex(0) ]) in p5)


# def test_expand():
#     kb = PropKB()
#     x0 = PropNot(PropOr(PropVar('x'), PropVar('y')))
#     y0 = PropAnd(PropNot(PropVar('x')), PropNot(PropVar('y')))
#     kb.add(PropEquiv(x0, y0))
#     x = PropVar('k')
#     ys = list(expand(Node(x, None, frozen([]), None), kb))
#     assert(len(ys) == 0)
