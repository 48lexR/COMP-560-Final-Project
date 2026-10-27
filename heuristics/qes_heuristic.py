#!/usr/bin/env python3

from model import UP, DOWN, LEFT, RIGHT, CREATE_OBSTACLE

class QES:
    """Quick, Easy Search for quorodors"""

    depth: int
    weights: dict

    def __init__(self, depth: int):
        self.depth = depth

    def evalute(self, model, player):
        move: tuple = ()
        match player:
            case 0:
                move = self.maximizer_evaluate_helper(model, player, self.depth)
            case 1:
                move = self.minimizer_evalute_helper(model, player, self.depth)
            case _:
                raise Exception("invalid player!")
        dir, pos, _ = move
        return (dir, pos)

    def maximizer_evaluate_helper(model, player, d):
        evalutation = self.evalute_position(model, player)
        if dir == 0:
            pass
        return minimizer_evaluate_helper(model, (player + 1) % 2, d - 1)

    def minimizer_evaluate_helper(model, player, d):
        evaluation = self.evalute_position(model, player)
        if dir == 0:
            raise Exception("Unimplemented")
        return maximizer_evaluate_helper(model, (player + 1) % 2, d - 1)

    def evaluate_position(self, model, player):
        # TODO: Implement
        raise Exception("Unimplemented")

    def find_shortest_path(self, model, player, row):
        raise Exception("Unimplemented")
        position = model.get_player_position(player)
        goals = set((model.rows if player == 1 else 0, x) for x in model.cols)
        seen = []
        frontier = []
        dirs = []
        deltas = {
            UP: (-1, 0),
            DOWN: (1, 0),
            LEFT: (0, -1),
            RIGHT: (0, 1)
        }
        # BFS is fine for short searches.
        # May need to switch to DFS if we ever up the ante
        return # TODO: Implement BFS
