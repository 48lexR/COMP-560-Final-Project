# COMP-560-Final-Project

An A* heuristic search implementation for the game Quoridors.

## Implementation

Model.py keeps track of the state of the board. It is agnostic to the state of the game (i.e. who is winning or losing) and it basically just tracks game metadata (like player and obstacle positions).

Controller.py keeps track of the game state and implements the heuristic algorithm. I.e. it will use your heuristic algorithm to simulate the players playing.

All heuristics should go in the heuristics subfolder. I.e. your implementation of your heuristic should just be another file in the heuristics folder.
