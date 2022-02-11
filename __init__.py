""" wordpy -- word guess game.
"""

from .game import Game, FixedGame, TerminalGame
from .solver import Solver
from .utils import benchmark, solve
from .wordtable import WordTable
from .dictionary import get_words
