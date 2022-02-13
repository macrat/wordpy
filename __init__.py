""" Word guess game.

>>> class MySolver(wordpy.Solver):
...     def __init__(self, game: wordpy.Game):
...         super().__init__(game)
...
...         # do initialization here
...
...     def guess(self) -> wordpy.WordTable:
...         self.state # current game status.
...         self.words # current word candidates.
...
...         self.drop_words_by_state() # drop words that can't be the answer, from self.words.
...
...         return self.words[:10] # return some next word candidates.
...


>>> words = wordpy.get_words()
>>> wordpy.benchmark(words, MySolver)
"""

from .game import Game, FixedGame, TerminalGame
from .solver import Solver
from .utils import benchmark, solve
from .wordtable import WordTable
from .dictionary import get_words
