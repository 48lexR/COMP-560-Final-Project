#!/usr/bin/env python3

UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3
CREATE_OBSTACLE = 4

class Heuristic:
    """
    The base heuristic class. Does nothing.
    PLEASE MAKE SURE YOUR HEURISTIC ALGORITHM
    IMPLEMENTS THIS API. THE MODEL WILL TAKE IN
    YOUR HEURISTIC AND USE IT TO CARRY OUT ITS MEANS.
    IF YOU DO NOT IMPLEMENT THE API CORRECTLY,
    YOU WILL BREAK THE PROGRAM.
    """
    def __init__(self):
        return

    def evaluate(self, model, player):
        """
        This is where the magic happens. The controller will call this function.
        The model contains the board metadata and the board itself.
        The player tells you whether you are the maximizer (0) or minimizer (1)
        You should return BOTH the move you want (UP/DOWN/LEFT/RIGHT/CREATE_OBSTACLE)
        AND you should return a position (tuple)
        This could be anything for UP/DOWN/LEFT/RIGHT, but is needed for CREATE_OBSTACLE
        """
        # Greedy approach: just go as quickly as possible without placing any obstacles
        deltas = {
            UP: (-1, 0),
            RIGHT: (0, 1),
            DOWN: (1, 0),
            LEFT: (0, -1)
        }

        r, c = model.get_player_position(player)
        for key in deltas:
            dr, dc = deltas[key]
            if not model.is_obstacle_or_player((dr + r, dc + c)):
                return (key, (0, 0))
        return (CREATE_OBSTACLE, (0, 0))
