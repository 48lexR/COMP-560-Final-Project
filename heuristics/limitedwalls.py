#!/usr/bin/env python3


from heuristics.minimax import Heuristic as MinimaxSearch

UP, RIGHT, DOWN, LEFT, CREATE_OBSTACLE = 0, 1, 2, 3, 4
EMPTY, PLAYER, OBSTACLE = 0, 1, 2


class _TileTracker:
    """Tracks obstacles left"""

    def __init__(self, tile_limit=None):
        self.tile_limit = tile_limit
        self.placed = 0

    def new_game_check(self, model):
        if not any(OBSTACLE in row for row in model.board):
            self.placed = 0  # fresh board -> new game

    def tiles(self, model, player):
        """[tiles for player 0, tiles for player 1], from `player`'s point of view."""
        if hasattr(model, "tiles_remaining"):
            return list(model.tiles_remaining)
        limit = self.tile_limit if self.tile_limit is not None else (3 * model.cols) // 4
        walls = sum(row.count(OBSTACLE) for row in model.board)
        mine = max(0, limit - self.placed)
        theirs = max(0, limit - max(0, walls - self.placed))
        return [mine, theirs] if player == 0 else [theirs, mine]


class _TileKeyedTT(dict):
    """
    A transposition table stores previously searched game positions.
    It includes both players' remaining tiles in every key.
    """

    def __init__(self, owner):
        super().__init__()
        self.owner = owner

    def _k(self, key):
        return (key, tuple(self.owner._tiles))

    def __contains__(self, key):
        return super().__contains__(self._k(key))

    def __getitem__(self, key):
        return super().__getitem__(self._k(key))

    def __setitem__(self, key, val):
        super().__setitem__(self._k(key), val)


class Computer(MinimaxSearch):
    """A heuristic that inherits MinimaxSearch but places limit on number of tiles placed.
    """

    def __init__(self, depth=5, max_placements=8, tile_limit=None):
        self.tracker = _TileTracker(tile_limit)
        self._tiles = [0, 0]  # [player 0, player 1] tiles left, updated during search
        super().__init__(depth=depth, max_placements=max_placements)

    # The base class resets self.tt = {} on every search to keep track of tiles
    # @property turns tt from plain variable into method
    @property
    def tt(self):
        return self._tt

    # sets tt to _TileKeyedTT instead of received input
    @tt.setter
    def tt(self, _value):
        self._tt = _TileKeyedTT(self)


    def tiles_left(self, model, player):
        return self.tracker.tiles(model, player)[player]

    def evaluate(self, model, player):
        self.tracker.new_game_check(model)
        self._tiles = self.tracker.tiles(model, player)
        action, cell = super().evaluate(model, player)
        if action == CREATE_OBSTACLE:
            self.tracker.placed += 1
        return action, cell

    def _placements(self, board, pos, turn):
        if self._tiles[turn] <= 0:
            return []
        return super()._placements(board, pos, turn)


    def _apply(self, board, pos, turn, mv):
        super()._apply(board, pos, turn, mv)
        if mv[0] == CREATE_OBSTACLE:
            self._tiles[turn] -= 1


    def _undo(self, board, pos, turn, mv, old):
        super()._undo(board, pos, turn, mv, old)
        if mv[0] == CREATE_OBSTACLE:
            self._tiles[turn] += 1
