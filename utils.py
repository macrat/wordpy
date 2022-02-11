from typing import Type
import random
import readline

from .game import Game, FixedGame, TerminalGame
from .solver import Solver
from .wordtable import WordTable


def new_game(words: WordTable) -> Game:
    return FixedGame(words, random.choice(words))


def benchmark(words: WordTable, cls: Type[Solver], num_tries=100) -> tuple[float, float]:
    total = 0
    win = 0
    for i in range(num_tries):
        print(f'{cls.__name__} game {i}')
        solver = cls(new_game(words))
        result = solver.solve()
        total += result.num_tried
        if result.num_tried <= len(words[0]) + 1:
            win += 1
        print()
    return total / num_tries, win / num_tries


def solve(words: WordTable, cls: Type[Solver]):
    game = TerminalGame(words)
    solver = cls(game)

    history: list[GameState] = []

    for i in range(6):
        print(f'candidates {i}:')
        print(solver.guess())
        print()
        word = input('what did you input?\n  _____\n> ')

        ok = game.submit(word)

        history.append(game.state)

        for s in history:
            print(s.color_str())
        print()

        if ok:
            break
