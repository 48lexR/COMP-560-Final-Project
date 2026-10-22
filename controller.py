#!/usr/bin/env python3

from model import Model
from heuristics.heuristic import Heuristic

class Controller:

    model: Model

    def __init__(self):
        model = Model()

    def __call__(self):
        # TODO: Implement
