# Infera

Infera is a (for now) random set of tools and libraries for working with formal systems.

## Motivation

I've always been interested in formal systems, but never found the time/energy
to seriously take a deep dive into the literature. I did make some programs
along the way, which are archived here. I learn best by building, so why not
continue building these tools?

## What You'll Find

### A Tiny Theorem Prover

Probably the most interesting program in this repository is
`src/infera/main.py`, a small term rewriter that attempt to prove a certain
formula according to a fixed knowledge base.

**Example:**
```
Premise: ¬(d ∨ c) ∧ k
Goal: (¬¬¬c ∧ ¬d) ∧ k
Searched 342 states
Steps:
1. ¬(d ∨ c) ∧ k ⇒ (¬d ∧ ¬c) ∧ k by rule ¬(a ∨ b) ⊢ ¬a ∧ ¬b
2. (¬d ∧ ¬c) ∧ k ⇒ (¬c ∧ ¬d) ∧ k by rule a ∧ b ⊢ b ∧ a
3. (¬c ∧ ¬d) ∧ k ⇒ (¬¬¬c ∧ ¬d) ∧ k by rule a ⊢ ¬¬a
```

### A Tool for Detecting Tautologies

Plain and simple, `src/infera/tabulate.py` explores the entire space of
possible truths in order to determine whether a certain logical formula is a
tautology. The algorithm is very naive, but it does work for simple formulas.

```
A B C | (equiv (and (implies C A) (implies C B)) (implies C (and A B)))
0 0 0 | 1
0 0 1 | 1
0 1 0 | 1
0 1 1 | 1
1 0 0 | 1
1 0 1 | 1
1 1 0 | 1
1 1 1 | 1
Statement is a tautology!
```

## License

The code in this repository is licensed under the GPL 3.0.
