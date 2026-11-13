#!/usr/bin/env python3
import random

UP, RIGHT, DOWN, LEFT = 0, 1, 2, 3
CREATE_OBSTACLE = 4
DELTAS = {UP: (-1, 0), RIGHT: (0, 1), DOWN: (1, 0), LEFT: (0, -1)}


class Heuristic:
    def __init__(self):
        pass

    def evaluate(self, model, player):
        r, c = model.get_player_position(player)
        legal = [d for d, (dr, dc) in DELTAS.items()
                 if not model.is_obstacle_or_player((r + dr, c + dc))]
        if legal:
            return (random.choice(legal), None)
        return (CREATE_OBSTACLE, (0, 0))