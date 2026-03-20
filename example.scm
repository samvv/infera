;; These are some tests
;; All of these formulas should be reported as being a tautology

; Double negation
(defthm neg-neg
  (equiv
    a
    (not (not a)))
  #:tactic tabulate)

; De Morgan's law for OR
(defthm de-morgan-or
  (equiv
    (not (and a b))
    (or (not a) (not b)))
  #:tactic tabulate)

; De Morgan's law for AND
(defthm de-morgan-and
  (equiv
    (not (or a b))
    (and (not a) (not b)))
  #:tactic tabulate)

; Commutativity of AND
(defthm comm-and
  (equiv
    (and a b)
    (and b a))
  #:tactic tabulate)

; Commutativity of OR
(defthm comm-or
  (equiv
    (or a b)
    (or b a))
  #:tactic tabulate)

; Contraposition
(defthm contraposition
  (equiv
    (implies p q)
    (implies (not q) (not p)))
  #:tactic tabulate)

; If either a implies c or b implies c (or both), then a and b, taken together, surely must imply c.
; If we can infer both a and b from c, we can either imply c from a or c from b (or both).
(defthm disj-implies-conj
  (equiv
    (or
      (implies a c)
      (implies b c))
    (implies
      (and a b)
      c))
  #:tactic tabulate)

; If from c we can imply a, and from c we can imply b, we can imply both a and b from c alone.
; If we can infer a as well as b from c, we can separately imply a from c and b from c.
(defthm conj-implies-conj
  (equiv
    (and
      (implies c a)
      (implies c b))
    (implies
      c
      (and a b)))
  #:tactic tabulate)

(defthm test-0
  (equiv
    (and (not (or d c)) k)
    (and (not (or d c)) k)))

(defthm test-1
  (equiv
    (and (not (or d c)) k)
    (and (and (not (not (not d))) (not c)) k)))

(defthm test-2
  (equiv
    (or a b)
    (not (not (or a b)))))
