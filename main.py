#!/usr/bin/env python3

from heuristics.heuristic import Heuristic
from model import Model
from controller import Controller

def main():
    heuristic_a = Heuristic()
    heuristic_b = Heuristic()
    c = Controller(3, 3)
    a_wins = 0
    b_wins = 0
    for i in range(10):
        a = c(heuristic_a, heuristic_b)
        if a == 0:
            a += 1
        elif a == 1:
            b += 1

if __name__ == "__main__":
    main()
