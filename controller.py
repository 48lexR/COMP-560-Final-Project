#!/usr/bin/env python3

from model import Model
from heuristics.heuristic import Heuristic

UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3
PLACE_OBSTACLE = 4

class Controller:

    model: Model
    state: int
    rows: int
    cols: int

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        model = Model(self.rows, self.cols)

    def __call__(self, heuristic_a, heuristic_b):
        """Simulates a single game between two adversaries, A and B"""
        # TODO: Implement
        self.state = 0 # initial state
        Model() # Model state
        while self.state == 0:
            # Main gameplay loop
            is_valid = False
            while not is_valid:
                a = heuristic_a.evaluate(model, 0)
                is_valid = self.move_helper(1, a)

            if self.player_has_reached_goal(0):
                self.state = 1
                print(f"Player 0 has won the game!")
                return

            is_valid = False
            while not is_valid:
                b = heuristic_b.evaluate(model, 1)
                is_valid = self.move_helper(1, b)

            if self.player.has_reached_goal(1):
                self.state = 1
                print(f"Player 1 has won the game!")
                return

    def move_helper(self, heuristic, player, direction):
        """Helper function to do the switch-cases"""
        a, pos = heuristic_a.evaluate(model, 0)
        match a:
            case 0:
                self.model.move(0, 0)
                return True
            case 1:
                self.model.move(0, 1)
                return True
            case 2:
                self.model.move(0, 2)
                return True
            case 3:
                self.model.move(0, 3)
                return True
            case 4:
                self.model.place_obstacle(pos)
                return True
            case _:
                return False

    def player_has_reached_goal(self, player) -> bool:
        if self.model.player_position(0)[0] == self.rows - 1:
            return True
        return False
