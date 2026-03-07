

def implies(precedent: bool, consequent: bool) -> bool:
    """
    Python has no built-in operator for calculating the logical implication.
    """
    return not precedent or consequent


