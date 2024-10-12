(defthm simple-neg-and-or
    (equiv (not (and (not (not a)) b))
           (or (not a) (not b))))

(defthm simple-taut
    (equiv (not (not (not (not a))))
           a))
