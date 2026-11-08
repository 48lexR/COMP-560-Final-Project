#!/usr/bin/env python3

from model import UP, DOWN, LEFT, RIGHT, CREATE_OBSTACLE
import heapq

def min_tree_search(model, eval_func, depth):
    """Returns the move with the minimum evaluation overall"""
    # TODO: Missing game winning logic
    min_pos_val = 1_000_000
    moves = []
    if depth == 0:
        return (None, None, eval_func(model))

    for move in [UP, DOWN, LEFT, RIGHT, CREATE_OBSTACLE]:
        c = model.create_copy()
        m = -1
        pos = ()
        e = 0
        if move != CREATE_OBSTACLE and c.move(move, 1) == 0:
            _, _, e = max_tree_search(c, eval_func, depth-1)
            m = move
        elif move == CREATE_OBSTACLE:
            positions = [(r, c) for r in range(model.rows) for c in range(model.cols)]
            for p in positions:
                if c.place_obsatcle(p) == 0:
                    _, _, e = max_tree_search(c, eval_func, depth-1)
                    m = move
                    pos = p
        if m != -1:
            moves += (m, pos, e)

    candidate = ()
    for m, p, e in moves:
        if e < max_pos_val:
            candidate = (m, p, e)
            max_pos_val = e
    return candidate


def max_tree_search(model, eval_func, depth):
    """Returns the maximum position eval"""
    max_pos_val = -1_000_000
    moves = []
    # TODO: Missing game winning logic
    if depth == 0:
        return (None, None, eval_func(model))

    for move in [UP, DOWN, LEFT, RIGHT, CREATE_OBSTACLE]:
        c = model.create_copy()
        m = -1
        pos = ()
        e = 0
        if move != CREATE_OBSTACLE and c.move(move, 0) == 0:
            _, _, e = min_tree_search(c, eval_func, depth-1)
            m = move
        elif move == CREATE_OBSTACLE:
            positions = [(r, c) for r in range(model.rows) for c in range(model.cols)]
            for p in positions:
                if c.place_obsatcle(p) == 0:
                    _, _, e = min_tree_search(c, eval_func, depth-1)
                    m = move
                    pos = p
        if m != -1:
            moves += (m, pos, e)

    candidate = ()
    for m, p, e in moves:
        if e > max_pos_val:
            candidate = (m, p, e)
            max_pos_val = e
    return candidate


def minimax_tree_search(model: any, eval_func: any, player: int, depth=1):
    """Returns the best move given the position evaluation function."""
    c = model.create_copy()
    move, pos, e = max_tree_search(c, eval_func, depth) if player == 0 else min_tree_search(c, eval_func, depth)
    return (move, pos)


def tmp(model, player):
    x, _ = model.get_player_position(player)
    if player == 0:
        return model.cols - x
    else:
        return x

def a_star_shortest_path(model: any, player: int, h=tmp):
    # TODO: Implement
    c = model.create_copy()
    frontier = heapq()
    seen = []
    frontier.heappush(model.get_player_position(player))
