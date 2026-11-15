#!/usr/bin/env python3
"""Minimax with alpha-beta pruning, a transposition table, and move ordering for the Quorodor model."""

from collections import deque

EMPTY = 0
PLAYER = 1
OBSTACLE = 2

UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3
PLACE_OBSTACLE = 4   # matches controller.py; defined here to avoid a circular import

DELTAS = {UP: (-1, 0), RIGHT: (0, 1), DOWN: (1, 0), LEFT: (0, -1)}

WIN = 100_000
INF = float("inf")
EXACT, LOWER, UPPER = 0, 1, 2


class Heuristic:
    """
    Minimax with alpha-beta pruning. The controller calls evaluate(model, player)
    and expects back (move, pos), where move is UP/DOWN/LEFT/RIGHT or PLACE_OBSTACLE
    and pos is the target cell for PLACE_OBSTACLE (None for steps).
    Scores are always from the perspective of the player passed to evaluate().
    """
    def __init__(self, depth=5, max_placements=8):
        self.depth = depth                      # plies, including our own move
        self.max_placements = max_placements    # cap on obstacle candidates per node
        self.tt = {}

    # ---------- entry point used by the controller ----------

    def evaluate(self, model, player):
        self.root = player                      # the player we are maximizing for
        self.rows, self.cols = model.rows, model.cols
        self.no_path = 4 * self.rows * self.cols
        self.tt = {}
        board = [row[:] for row in model.board]
        pos = [tuple(p) for p in model.player_positions]

        best_move, best_score, alpha = None, -INF, -INF
        for mv in self._ordered(board, pos, player):
            old = pos[player]
            self._apply(board, pos, player, mv)
            # Our move is ply 1. The opponent moves next and is the minimizer.
            score = self._minimax(board, pos, 1 - player, self.depth - 1, alpha, INF, 1)
            self._undo(board, pos, player, mv, old)
            if score > best_score:
                best_score, best_move = score, mv
            alpha = max(alpha, best_score)

        if best_move is None:
            raise RuntimeError("Heuristic: player has no legal moves")
        kind, cell = best_move
        return (PLACE_OBSTACLE, cell) if kind == PLACE_OBSTACLE else (kind, None)

    # ---------- search ----------

    def _minimax(self, board, pos, turn, depth, alpha, beta, ply):
        """Value is always from self.root's perspective. turn == self.root maximizes."""
        prev = 1 - turn
        if self._reached(pos, prev):            # the previous mover has already won
            return WIN - ply if prev == self.root else -(WIN - ply)
        if depth == 0:
            return self._eval(board, pos)

        key = (tuple(map(tuple, board)), tuple(pos), turn, depth)
        if key in self.tt:
            val, flag = self.tt[key]
            if flag == EXACT:
                return val
            if flag == LOWER:
                alpha = max(alpha, val)
            else:
                beta = min(beta, val)
            if alpha >= beta:
                return val

        moves = self._ordered(board, pos, turn)
        if not moves:                           # the player to move is trapped and loses
            return -(WIN - ply) if turn == self.root else WIN - ply

        orig_alpha, orig_beta = alpha, beta

        if turn == self.root:
            best = -INF
            for mv in moves:
                old = pos[turn]
                self._apply(board, pos, turn, mv)
                val = self._minimax(board, pos, 1 - turn, depth - 1, alpha, beta, ply + 1)
                self._undo(board, pos, turn, mv, old)
                best = max(best, val)
                alpha = max(alpha, best)
                if alpha >= beta:
                    break
        else:
            best = INF
            for mv in moves:
                old = pos[turn]
                self._apply(board, pos, turn, mv)
                val = self._minimax(board, pos, 1 - turn, depth - 1, alpha, beta, ply + 1)
                self._undo(board, pos, turn, mv, old)
                best = min(best, val)
                beta = min(beta, best)
                if alpha >= beta:
                    break

        # Store the bound type relative to the window this node was searched with.
        if best <= orig_alpha:
            flag = UPPER
        elif best >= orig_beta:
            flag = LOWER
        else:
            flag = EXACT
        self.tt[key] = (best, flag)
        return best

    # ---------- move generation and ordering ----------

    def _ordered(self, board, pos, turn):
        """All legal moves, best-for-the-mover first. Obstacle placements are capped."""
        sign = 1 if turn == self.root else -1   # the mover wants the highest/lowest root score
        scored = []
        for mv in self._steps(board, pos, turn) + self._placements(board, pos, turn):
            old = pos[turn]
            self._apply(board, pos, turn, mv)
            if self._reached(pos, turn):
                s = sign * WIN                  # immediate win for the mover
            else:
                s = self._eval(board, pos)
            self._undo(board, pos, turn, mv, old)
            scored.append((s, mv))
        # Maximizer tries high scores first; minimizer tries low scores first.
        scored.sort(key=lambda x: x[0], reverse=(turn == self.root))

        result, kept_placements = [], 0
        for _, mv in scored:
            if mv[0] == PLACE_OBSTACLE:
                if kept_placements >= self.max_placements:
                    continue
                kept_placements += 1
            result.append(mv)
        return result

    def _steps(self, board, pos, turn):
        r, c = pos[turn]
        out = []
        for kind, (dr, dc) in DELTAS.items():
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols and board[nr][nc] == EMPTY:
                out.append((kind, (nr, nc)))
        return out

    def _placements(self, board, pos, turn):
        """Obstacles on the opponent's shortest path that leave both players a route."""
        opp = 1 - turn
        path = self._path(board, pos[opp], self._goal_row(opp)) or []
        out = []
        for r, c in path:
            if board[r][c] != EMPTY:
                continue
            board[r][c] = OBSTACLE
            legal = all(self._path(board, pos[p], self._goal_row(p)) for p in (0, 1))
            board[r][c] = EMPTY
            if legal:
                out.append((PLACE_OBSTACLE, (r, c)))
        return out

    # ---------- apply / undo (in place, so no copies per node) ----------

    def _apply(self, board, pos, turn, mv):
        kind, (r, c) = mv
        if kind == PLACE_OBSTACLE:
            board[r][c] = OBSTACLE
        else:
            pr, pc = pos[turn]
            board[pr][pc] = EMPTY
            board[r][c] = PLAYER
            pos[turn] = (r, c)

    def _undo(self, board, pos, turn, mv, old):
        kind, (r, c) = mv
        board[r][c] = EMPTY
        if kind != PLACE_OBSTACLE:
            board[old[0]][old[1]] = PLAYER
            pos[turn] = old

    # ---------- evaluation (always from self.root's perspective) ----------

    def _eval(self, board, pos):
        me, opp = self.root, 1 - self.root
        d_me = self._dist(board, pos, me)
        d_opp = self._dist(board, pos, opp)
        mobility = len(self._steps(board, pos, me)) - len(self._steps(board, pos, opp))
        return 10 * (d_opp - d_me) + mobility

    def _dist(self, board, pos, p):
        path = self._path(board, pos[p], self._goal_row(p))
        return len(path) - 1 if path else self.no_path

    def _path(self, board, start, goal_row):
        """BFS through non-obstacle cells (pawns are treated as passable)."""
        prev = {start: None}
        queue = deque([start])
        while queue:
            cell = queue.popleft()
            if cell[0] == goal_row:
                path = []
                while cell is not None:
                    path.append(cell)
                    cell = prev[cell]
                return path[::-1]
            r, c = cell
            for dr, dc in DELTAS.values():
                n = (r + dr, c + dc)
                if (0 <= n[0] < self.rows and 0 <= n[1] < self.cols
                        and n not in prev and board[n[0]][n[1]] != OBSTACLE):
                    prev[n] = cell
                    queue.append(n)
        return None

    def _goal_row(self, p):
        return self.rows - 1 if p == 0 else 0

    def _reached(self, pos, p):
        return pos[p][0] == self._goal_row(p)