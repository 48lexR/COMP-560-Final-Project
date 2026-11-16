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
    Controller calls evaluate() to get the best move for the given model and player. The returned move is a tuple (kind, cell) where kind is one of UP, RIGHT, DOWN, LEFT, PLACE_OBSTACLE and cell is a (row, col) tuple for obstacle placements or None for pawn moves.
    The method returns: (move, pos)

    Move = UP, DOWN, LEFT, RIGHT, PLACE_OBSTACLE
    Pos = (row, col) for obstacle placements or None for pawn moves

    Allscores are calculated from the perspective of the AI player (self.root). The opponent is the minimizer. The evaluation function is a linear combination of the difference in shortest path lengths to the goal and the difference in mobility (number of legal moves).
    """
    def __init__(self, depth=5, max_placements=8):
        self.depth = depth                      # plies, including our own move
        self.max_placements = max_placements    # cap on obstacle candidates per node
        self.tt = {}
        # of moves that the AI searches ahead
        # Each move by either player is a ply. The depth is the number of plies to search, including the AI's move. For example, depth=5 means the AI looks 2 moves ahead (AI move, opponent move, AI move, opponent move, AI move). 


    def evaluate(self, model, player):
        self.root = player                      # the player we are maximizing for
        self.rows, self.cols = model.rows, model.cols # Get the board dimensions from the game model.
        self.no_path = 4 * self.rows * self.cols # Penalty distance for a player with no path to the goal. This is set to a value larger than any possible path length on the board.
        self.tt = {} # Fresh transposition table for each evaluation to avoid stale entries from previous evaluations.
        board = [row[:] for row in model.board]
        pos = [tuple(p) for p in model.player_positions]
        # Makes copies of the board and player positions to avoid modifying the original game state during the evaluation.

        best_move, best_score, alpha = None, -INF, -INF
        for mv in self._ordered(board, pos, player):
            # Examine the possible moves, consider promising moves first.
            old = pos[player]
            self._apply(board, pos, player, mv)
            # Our move is ply 1. The opponent moves next and is the minimizer.
            score = self._minimax(board, pos, 1 - player, self.depth - 1, alpha, INF, 1)
            self._undo(board, pos, player, mv, old)
            # Evaluate the move by applying it, running minimax to see the outcome, and then undoing it to restore the board state.
            if score > best_score:
                best_score, best_move = score, mv
            alpha = max(alpha, best_score)

        if best_move is None:
            raise RuntimeError("Heuristic: player has no legal moves")
        kind, cell = best_move
        return (PLACE_OBSTACLE, cell) if kind == PLACE_OBSTACLE else (kind, None)


    def _minimax(self, board, pos, turn, depth, alpha, beta, ply):
        """
        Score is always from the original AI player's perspective (self.root). The minimax function recursively evaluates the game tree, applying alpha-beta pruning to eliminate branches that won't affect the final decision. It uses a transposition table to cache previously computed states for efficiency.
        The player whose turn it is determines whether we maximize or minimize the score.
        """
        prev = 1 - turn
        if self._reached(pos, prev):            # the previous mover has already won
            return WIN - ply if prev == self.root else -(WIN - ply)
        # If we reach depth search limit, evaluate the board state using the heuristic evaluation function.
        if depth == 0:
            return self._eval(board, pos)

        key = (tuple(map(tuple, board)), tuple(pos), turn, depth) # Create a unique key for the current board state. This allows us to recognize positions we have already searched.
        if key in self.tt:
            val, flag = self.tt[key] 
            if flag == EXACT:
                return val
            if flag == LOWER:
                alpha = max(alpha, val) # Alpha-Beta pruning implementation.
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


    def _ordered(self, board, pos, turn):
        """All legal moves, best-for-the-mover first. Obstacle placements are capped.
        Generate all possible movement and obstacle placement moves.
        Moves are ranked based on how useful they are to the player.

        AI wants high scores, while opponent wants low scores.
        """
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
        # Sort moves so the best options are examined first.
        # The maximizing player wants high scores.
        # The minimizing player wants low scores.

        result, kept_placements = [], 0
        for _, mv in scored:
            if mv[0] == PLACE_OBSTACLE:
                if kept_placements >= self.max_placements:
                    continue
                kept_placements += 1
            result.append(mv)
        return result

    def _steps(self, board, pos, turn):
        # Get the current player's row and column.
        r, c = pos[turn]
        out = []
        for kind, (dr, dc) in DELTAS.items():
            # Calculate the destination cell, and check:
            # A move being legal is if:
            # 1. inside the board
            # 2. the destination cell is empty
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols and board[nr][nc] == EMPTY:
                out.append((kind, (nr, nc)))
        return out

    def _placements(self, board, pos, turn):
        """Obstacles on the opponent's shortest path that leave both players a route."""
        opp = 1 - turn # Find the opponent
        path = self._path(board, pos[opp], self._goal_row(opp)) or []
        # Find the opponent's shortest path to their goal. If there is no path, return an empty list.
        out = []
        for r, c in path:
            if board[r][c] != EMPTY:
                continue
            board[r][c] = OBSTACLE
            # Check that both players still have a route to their goals.
            # An obstacle placement is illegal if it completely blocks either player.
            legal = all(self._path(board, pos[p], self._goal_row(p)) for p in (0, 1))
            board[r][c] = EMPTY # Remove the temp obstacle, then only keep placements that preserves both routes/paths.
            if legal:
                out.append((PLACE_OBSTACLE, (r, c)))
        return out


    def _apply(self, board, pos, turn, mv):
        # Separate the move type and destination.
        kind, (r, c) = mv
        if kind == PLACE_OBSTACLE:
            # If a move is an obstacle placement, mark the cell.
            board[r][c] = OBSTACLE
        else:
            # Save player's prev location, clear the old cell, place player in the destination cell, and update their position.
            pr, pc = pos[turn]
            board[pr][pc] = EMPTY
            board[r][c] = PLAYER
            pos[turn] = (r, c)

    def _undo(self, board, pos, turn, mv, old):
            # If it was a normal movement move, restore the player's
        # original position.
        kind, (r, c) = mv
        board[r][c] = EMPTY
        if kind != PLACE_OBSTACLE:
            board[old[0]][old[1]] = PLAYER
            pos[turn] = old

    def _eval(self, board, pos):
        # Identify the current player and the opponent, calculate their distances to their respective routes/goals.
        me, opp = self.root, 1 - self.root
        d_me = self._dist(board, pos, me)
        d_opp = self._dist(board, pos, opp)

        # Calculate mobility, more avaiable moves for AI player is good, while more available moves for the opponent is bad.
        mobility = len(self._steps(board, pos, me)) - len(self._steps(board, pos, opp))
        return 10 * (d_opp - d_me) + mobility # Return an overall heuristic score. A larger opponent distance and smaller AI distance.

    def _dist(self, board, pos, p):
        # Find shortest path from player's current position to the goal row.
        path = self._path(board, pos[p], self._goal_row(p))
        # Return the # of moves required, if no route exists return a large penalty distance.
        return len(path) - 1 if path else self.no_path

    def _path(self, board, start, goal_row):
        """
        Uses Breadth-First Search to find the shortest path
        from a starting cell to any cell in the goal row.
        
        BFS will explore the neighboring cells in all directions, and guarantees the shortest path on an unweighted gird.
        """
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