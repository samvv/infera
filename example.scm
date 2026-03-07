;; These are some tests for the tabulator
;; All of these formulas should be reported as being a tautology

; If either a implies c or b implies c (or both), then a and b, taken together, surely must imply c.
; If we can infer both a and b from c, we can either imply c from a or c from b (or both).
(equiv
  (or
    (implies a c)
    (implies b c))
  (implies
    (and a b)
    c))

; If from c we can imply a, and from c we can imply b, we can imply both a and b from c alone.
; If we can infer a as well as b from c, we can separately imply a from c and b from c.
(equiv
  (and
    (implies c a)
    (implies c b))
  (implies
    c
    (and a b)))
