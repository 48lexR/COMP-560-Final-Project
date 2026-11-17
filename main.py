#!/usr/bin/env python3

from heuristics.minimax import Heuristic as Minimax
from heuristics.random_player import Heuristic as Random
from heuristics.greedy import Heuristic as Greedy
from heuristics.qes_heuristic import QES_Heuristic
from model import Model
import sys
from controller import Controller

def create_heuristic(name: str, depth=5) -> any:
    code = name[:3].lower().strip()
    match code:
        case "qes":
            return QES_Heuristic(depth=depth)
        case "min":
            return Minimax(depth=depth)
        case "gre":
            return Greedy()
        case "ran":
            return Random()
        case _:
            raise Exception("Heuristic not recognized")

def main():
    num_iters = 50
    if len(sys.argv) < 3:
        print(f"""Usage: python3 -m main <heuristic> <heuristic> [options]
        Options: --debug   print debug info.
                 --depth   manually assign a depth (default: 5)""")
        sys.exit(1)

    depth=5
    if "--depth" in sys.argv:
        try:
            depth=int(sys.argv.index("--depth") + 1)
        except Exception:
            print(f"Failed to read depth!")

    heuristic_a = None
    heuristic_b = None
    try:
        heuristic_a = create_heuristic(sys.argv[1], depth=5)
    except Exception:
        print("Didn't recognize that heuristic: ", sys.argv[1])
        sys.exit(1)

    debug = False
    if "--debug" in sys.argv:
        debug=True

    try:
        heuristic_b = create_heuristic(sys.argv[2])
    except Exception:
        print("Didn't recognize that heuristic: ", sys.arv[2])
        sys.exit(1)

    c = Controller(5, 5, debug=debug)
    a_wins = 0
    b_wins = 0
    ties = 0
    for i in range(num_iters):
        a = c(heuristic_a, heuristic_b)
        if a == 0:
            a_wins += 1
        elif a == 1:
            b_wins += 1
        else:
            ties += 1
    print("=== STATISTICS ===")
    print(f"* {sys.argv[1]} W/L: {a_wins} / {b_wins}: {a_wins*100/(num_iters)}%")
    print(f"* {sys.argv[2]} W/L: {b_wins} / {a_wins}: {b_wins*100/(num_iters)}%")
    print(f"* Ties: {ties}, {ties * 100 / num_iters}%")
    print(f"=== {sys.argv[1]} wins ==="
          if a_wins > b_wins
          else f"=== {sys.argv[2]} wins ===")

if __name__ == "__main__":
    main()
