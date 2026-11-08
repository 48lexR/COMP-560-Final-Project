#!/usr/bin/env python3

from heuristics.heuristic import Heuristic
from model import Model
from controller import Controller

def main():
    num_iters = 10
    heuristic_a = Heuristic()
    heuristic_b = Heuristic()
    c = Controller(3, 3)
    a_wins = 0
    b_wins = 0
    for i in range(num_iters):
        a = c(heuristic_a, heuristic_b)
        if a == 0:
            a_wins += 1
        elif a == 1:
            b_wins += 1
    print("=== STATISTICS ===")
    print(f"* A W/L: {a_wins} / {b_wins}: {a_wins*100/(num_iters)}%")
    print(f"* B W/L: {b_wins} / {a_wins}: {b_wins*100/(num_iters)}%")
    print("=== A wins ==="
          if a_wins > b_wins
          else "=== B wins ===")

if __name__ == "__main__":
    main()
