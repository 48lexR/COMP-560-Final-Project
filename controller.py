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
        self.model = Model(self.rows, self.cols)

    def __call__(self, heuristic_a, heuristic_b):
        """Simulates a single game between two adversaries, A and B"""
        self.state = 0 # initial state
        self.model() # Model state
        while self.state == 0:
            # Main gameplay loop
            if self.move_helper(heuristic_a, 0) == False:
                raise Exception("Invalid move")

            if self.player_has_reached_goal(0):
                self.state = 1
                print(f"Player 0 has won the game!")
                return 0

            if self.move_helper(heuristic_b, 1) == False:
                raise Exception("Invalid move")

            if self.player_has_reached_goal(1):
                self.state = 1
                print(f"Player 1 has won the game!")
                return 1

    def move_helper(self, heuristic, player):
        """Helper function to do the switch-cases"""
        a, pos = heuristic.evaluate(self.model, player)
        if a == PLACE_OBSTACLE:
            return self.model.place_obstacle(pos) == 0
        return self.model.move(a, player) == 0

    def player_has_reached_goal(self, player) -> bool:
        goal_row = self.rows - 1 if player == 0 else 0
        return self.model.get_player_position(player)[0] == goal_row
