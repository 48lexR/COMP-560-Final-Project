#!/usr/bin/env python3


from heuristics.minimax import Heuristic as MinimaxSearch

UP, RIGHT, DOWN, LEFT, CREATE_OBSTACLE = 0, 1, 2, 3, 4
EMPTY, PLAYER, OBSTACLE = 0, 1, 2

KEYS = {"w": UP, "d": RIGHT, "s": DOWN, "a": LEFT}
DELTAS = {UP: (-1, 0), RIGHT: (0, 1), DOWN: (1, 0), LEFT: (0, -1)}
NAMES = {UP: "up", RIGHT: "right", DOWN: "down", LEFT: "left"}
KEY_OF = {d: k for k, d in KEYS.items()}


#for human player accessiblity
def render(model) -> str:
    """Board with coordinates; A = player 0, B = player 1, @ = obstacle."""
    a, b = model.player_positions
    lines = ["    " + " ".join(f"{c:>2}" for c in range(model.cols))]
    for r in range(model.rows):
        cells = []
        for c in range(model.cols):
            if (r, c) == a:
                cells.append(" A")
            elif (r, c) == b:
                cells.append(" B")
            elif model.board[r][c] == OBSTACLE:
                cells.append(" @")
            else:
                cells.append(" .")
        lines.append(f"{r:>3} " + " ".join(cells))
    return "\n".join(lines)

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



class Human:
    def __init__(self, tile_limit=None, hint_depth=5):
        self.tracker = _TileTracker(tile_limit)
        self.hint_depth = hint_depth

    def hint(self, model, player):
        search = MinimaxSearch(depth=self.hint_depth)
        try:
            action, cell = search.evaluate(model, player)
            # minimax.py has no obstacle limit: if it suggests an obstacle you can't
            # place, ask again for the best move without obstacle placements.
            if action == CREATE_OBSTACLE and self.tracker.tiles(model, player)[player] <= 0:
                search = MinimaxSearch(depth=self.hint_depth, max_placements=0)
                action, cell = search.evaluate(model, player)
        except RuntimeError:
            print("Hint: no legal move found.")
            return

        # Path lengths, using minimax.py's own shortest-path search.
        board = [row[:] for row in model.board]
        pos = [tuple(p) for p in model.player_positions]
        mine, theirs = search._dist(board, pos, player), search._dist(board, pos, 1 - player)
        mine_s = "blocked" if mine >= search.no_path else mine
        theirs_s = "blocked" if theirs >= search.no_path else theirs
        print(f"Paths: you {mine_s}, opponent {theirs_s}")

        if action == CREATE_OBSTACLE:
            print(f"Hint: place an obstacle at {cell}  (type: o {cell[0]} {cell[1]})")
        else:
            print(f"Hint: move {NAMES[action]}  (type: {KEY_OF[action]})")

    def evaluate(self, model, player):
        self.tracker.new_game_check(model)

        me = "A" if player == 0 else "B"
        goal = "bottom" if player == 0 else "top"
        while True:
            print()
            print(render(model))
            tiles = self.tracker.tiles(model, player)[player]
            print(f"\nYou are {me} - reach the {goal} row. Obstacles left: {tiles}")
            try:
                raw = input("Move (w/a/s/d, 'o row col', h = hint, q): ").strip().lower()
            except EOFError:
                raise SystemExit("\nProgram interrupted.")
            if not raw:
                continue
            if raw == "q":
                raise SystemExit("Quit.")
            if raw == "h":
                self.hint(model, player)
                input("(press Enter to continue)")
                continue

            if raw in KEYS:
                d = KEYS[raw]
                r, c = model.player_positions[player]
                dr, dc = DELTAS[d]
                nr, nc = r + dr, c + dc
                if not (0 <= nr < model.rows and 0 <= nc < model.cols):
                    print("! That's off the board.")
                elif model.board[nr][nc] != EMPTY:
                    print("! That square is blocked.")
                else:
                    return (d, (0, 0))
                continue

            parts = raw.split()
            if parts[0] == "o":
                if len(parts) != 3 or not all(p.lstrip("-").isdigit() for p in parts[1:]):
                    print("! Use: o <row> <col>   e.g. o 3 2")
                    continue
                pos = (int(parts[1]), int(parts[2]))
                if tiles <= 0:
                    print("! You have no obstacles left.")
                elif not (0 <= pos[0] < model.rows and 0 <= pos[1] < model.cols):
                    print("! That's off the board.")
                elif model.board[pos[0]][pos[1]] != EMPTY:
                    print("! That square isn't empty.")
                else:
                    self.tracker.placed += 1
                    return (CREATE_OBSTACLE, pos)
                continue

            print("! Unknown command.")

