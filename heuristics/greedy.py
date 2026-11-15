#!/usr/bin/env python3
import random
from collections import deque

UP, RIGHT, DOWN, LEFT = 0, 1, 2, 3
CREATE_OBSTACLE = 4
DELTAS = {UP: (-1, 0), RIGHT: (0, 1), DOWN: (1, 0), LEFT: (0, -1)}


class Heuristic:
    def __init__(self):
        pass

    def evaluate(self, model, player):
        r, c = model.get_player_position(player)
        goal = model.rows - 1 if player == 0 else 0
        legal = [d for d, (dr, dc) in DELTAS.items()
                 if not model.is_obstacle_or_player((r + dr, c + dc))]
        if not legal:
            return (CREATE_OBSTACLE, (0, 0))

        # Shuffle so that equally good steps are chosen at random.
        random.shuffle(legal)
        best = self._best_step(model, player, goal, legal)
        return (best if best is not None else random.choice(legal), None)

    def _best_step(self, model, player, goal, legal):
        r, c = model.get_player_position(player)
        best, best_dist = None, None
        for d in legal:
            dr, dc = DELTAS[d]
            dist = self._dist(model, (r + dr, c + dc), goal)
            if dist is not None and (best_dist is None or dist < best_dist):
                best, best_dist = d, dist
        return best

    def _dist(self, model, start, goal):
        # BFS over non-obstacle cells; pawns are passable here.
        seen = {start}
        q = deque([(start, 0)])
        while q:
            (r, c), d = q.popleft()
            if r == goal:
                return d
            for dr, dc in DELTAS.values():
                n = (r + dr, c + dc)
                if (0 <= n[0] < model.rows and 0 <= n[1] < model.cols
                        and n not in seen and model.at_position(n) != 2):
                    seen.add(n)
                    q.append((n, d + 1))
        return None