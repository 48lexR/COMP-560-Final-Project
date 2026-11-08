#!/usr/bin/env python3

from model import UP, DOWN, LEFT, RIGHT, CREATE_OBSTACLE
from utils import minimax_tree_search, a_star_shortest_path

class QES:
    """Quick, Easy Search for quorodors"""

    depth: int

    def __init__(self, depth: int):
        self.depth = depth

    def evalute(self, model, player):
        return minimax_tree_search(model, player, position_estimator, depth=self.depth)

    def position_estimator(self, model):
        return a_star_shortest_path(model, 1) - a_star_shortest_path(model, 0)
