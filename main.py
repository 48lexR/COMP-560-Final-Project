#!/usr/bin/env python3

from heuristics.minimax import Heuristic as Minimax
from heuristics.random_player import Heuristic as Random
from heuristics.greedy import Heuristic as Greedy
from model import Model
from controller import Controller

def main():
    num_iters = 50
    heuristic_a = Minimax(depth=5)
    heuristic_b = Greedy()
    c = Controller(5, 5)
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
