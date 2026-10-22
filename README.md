# COMP-560-Final-Project

An A* heuristic search implementation for the game Quoridors.

## Implementation

Model.py keeps track of the state of the board. It is agnostic to the state of the game (i.e. who is winning or losing) and it basically just tracks game metadata (like player and obstacle positions).

Controller.py keeps track of the game state and implements the heuristic algorithm. I.e. it will use your heuristic algorithm to simulate the players playing.

All heuristics should go in the heuristics subfolder. I.e. your implementation of your heuristic should just be another file in the heuristics folder. Feel free to copy `heuristics/heuristic.py`. All you need to implement is `evaluate(self, model, player)` which will return a move (UP/DOWN/LEFT/RIGHT/CREATE_OBSTACLE) and a position (i.e. (0, 0)) as a list.

## Game Rules

When the game begins, both players begin in the center of the board. The goal is acheived when the maximizer (A) reaches the top row or the minimizer (B) reaches the bottom row, whichever happens first. 
