(equiv (not (not a)) a)
(equiv (and (not a) (not b)) (not (or a b)))
(equiv (or (not a) (not b)) (not (and a b)))
(equiv (=> a b) (or (not a) b))
