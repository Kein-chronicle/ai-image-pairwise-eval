#!/usr/bin/env python3
"""Resolve an order-swapped pairwise judgement. Position bias => tie.
usage: pairwise.py <answer_when_shown_A_B> <answer_when_shown_B_A>   each answer is the *position* picked: first|second
Interpretation: in run 1 the order was (A,B); in run 2 the order was (B,A)."""
import sys
if len(sys.argv) != 3 or any(a not in ("first", "second") for a in sys.argv[1:]):
    print(__doc__); sys.exit(2)
r1, r2 = sys.argv[1:]
w1 = "A" if r1 == "first" else "B"          # run 1: first = A
w2 = "B" if r2 == "first" else "A"          # run 2: first = B
print(w1 if w1 == w2 else "TIE (answer flipped with order: position bias)")
sys.exit(0 if w1 == w2 else 1)
