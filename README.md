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

### A Tool for Detecting Tautologies

Plain and simple, `src/infera/tabulate.py` explores the entire space of
possible truths in order to determine whether a certain logical formula is a
tautology. The algorithm is very naive, but it does work for simple formulas.

## License

The code in this repository is licensed under the GPL 3.0.
