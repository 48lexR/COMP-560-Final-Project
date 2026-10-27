#!/usr/bin/env python3

EMPTY = 0
PLAYER = 1
OBSTACLE = 2

UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3
CREATE_OBSTACLE = 4

class Model:
    """
    The model class for the Quorodor implementation
    It basically just stores metadata
    about the current game. It is agnostic to the
    state of the game. (That's the controller's job)
    """
    rows: int
    cols: int
    player_positions: list(tuple)
    board: list

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols

    def __call__(self) -> None:
        """Creates the board and initializes the player positions"""
        self.board = [[EMPTY] * self.cols for _ in range(self.rows)] # Initialize the board
        self.player_positions = [
            (0, self.cols // 2),
            (self.rows - 1, self.cols // 2)
        ] # Initialize player positions
        self.set_position(
            self.player_positions[0],
            PLAYER) # Initialize player 1 on the board
        self.set_position(
            self.player_positions[1],
            PLAYER) # Initialize player 2 on the board

    def __str__(self) -> str:
        """Returns a string summarizing the state of the board"""
        str_buf = ""
        for r in self.board:
            row_buf = ""
            for c in r:
                if c == PLAYER:
                    row_buf += "|"
                elif c == OBSTACLE:
                    row_buf += "@"
                else:
                    row_buf += "."
            row_buf += '\n'
            str_buf += row_buf
        return str_buf

    def set_position(self, position: tuple, value) -> None:
        """Set a board position to a value"""
        if value not in [EMPTY, PLAYER, OBSTACLE]:
            raise Exception("set_position: cannot set value to non-type")
        self.board[position[0]][position[1]] = value

    def move(self, direction, player, **kwargs) -> int:
        """Move a player. Returns 0 on success, -1 on invalid move, -2 on invalid player"""
        if(player < 0 or player >= len(self.player_positions)):
            return -2 # No such player

        r,c = self.player_positions[player]
        deltas = {
            UP: (-1, 0),
            RIGHT: (0, 1),
            DOWN: (1, 0),
            LEFT: (0, -1)
        }
        if direction not in deltas:
            return -1
        dr, dc = deltas[direction]
        nr, nc = r + dr, c + dc

        if kwargs['debug']:
            print(f"Move player {player} {direction} from {(r, c)} to {(nr, nc)}")


        if not (0 <= nr < self.rows and 0 <= nc < self.cols):
            return -1
        if self.is_obstacle_or_player((nr, nc)):
            return -1

        self.set_position((r, c), EMPTY)
        self.set_position((nr, nc), PLAYER)
        self.player_positions[player] = (nr, nc)
        return 0

    def at_position(self, position: tuple) -> int:
        """Get the value at a position"""
        if position[0] < 0 or position[0] > self.rows - 1 or position[1] < 0 or position[1] > self.cols - 1:
            return -1 # Invalid position
        return self.board[position[0]][position[1]]

    def is_obstacle_or_player(self, position: tuple) -> bool:
        """Returns true if a given position is not available to be moved to"""
        if position[0] < 0 or position[0] > self.rows - 1 or position[1] < 0 or position[1] > self.cols - 1:
            return True # The border is basically an obstacle anyways
        return self.at_position(position) == OBSTACLE or self.at_position(position) == PLAYER

    def place_obstacle(self, position: tuple) -> int:
        """Place an obstacle on the board. Returns 0 for success, -1 for invalid placement"""
        if position[0] < 0 or position[0] > self.rows - 1 or position[1] < 0 or position[1] > self.cols - 1:
            return -1
        self.board[position[0]][position[1]] = OBSTACLE
        return 0

    def get_board(self):
        """Return the entire board buffer"""
        return self.board

    def get_player_position(self, player):
        """Get an invidual player's position"""
        if player > len(self.player_positions):
            raise Error(f"Player {player} not valid in list of {len(self.player_positions)} players")
        return self.player_positions[player]
