#!/usr/bin/env python3

EMPTY = 0
PLAYER = 1
OBSTACLE = 2

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
        self.board = [[EMPTY] * self.rows] * self.cols # Initialize the board
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

    def set_position(self, position: tuple, value) -> None:
        self.board[position[0]][position[1]] = value

    def move(self, direction, player) -> int:
        """Move a player. Returns 0 on success, -1 on invalid move, -2 on invalid player"""
        if(player > len(self.player_positions)):
            return -2 # No such player

        pos = self.player_positions[player]
        match direction:
            case 0: # up
                if pos[0] == 0 or self.is_obstacle_or_player(pos[0] - 1, pos[1]):
                    return -1
                pos -= 1
                return 0
            case 1: # right
                if pos[1] == len(cols) - 1 or self.is_obstacle_or_player(pos[0], pos[1] + 1):
                    return -1
                pos[1] += 1
                return 0
            case 2: # down
                if pos[0] == len(rows) - 1 or self.is_obstacle_or_player(pos[0] + 1, pos[1]):
                    return -1
                pos += 1
                return 0
            case 3: # left
                if pos[1] == 0 or self.is_obstacle_or_player(pos[0], pos[1] - 1):
                    return -1
                pos -= 1
                return 0
            case _:
                return -1 # Invalid move

    def at_position(self, position: tuple) -> int:
        if position[0] < 0 or position[0] > self.rows - 1 or position[1] < 0 or position[1] > self.cols - 1:
            raise Error(f"Invalid position")
        return self.board[position[0]][position[1]]

    def is_obstacle_or_player(self, position: tuple) -> bool:
        if position[0] < 0 or position[0] > self.rows - 1 or position[1] < 0 or position[1] > self.cols - 1:
            raise Error(f"Invalid position")
        return self.at_position(position) == OBSTACLE or self.at_position(position) == PLAYER

    def place_obstacle(self, position: tuple) -> int:
        """Place an obstacle on the board. Returns 0 for success, -1 for invalid placement"""
        if position[0] < 0 or position[0] > self.rows - 1 or position[1] < 0 or position[1] > self.cols - 1:
            return -1
        self.board[position[0]][position[1]] = OBSTACLE
        return 0

    def get_board(self):
        return self.board

    def get_player_position(self, player):
        if player > len(player_positions):
            raise Error(f"Player {player} not valid in list of {len(player_positions)} players")
        return player_positions[player]
