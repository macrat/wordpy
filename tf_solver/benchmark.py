import string
from typing import Callable
from functools import lru_cache

import numpy
import tensorflow as tf

import wordpy
from dataset import encode_x, encode_includes, decode


def edit_distance(x: str) -> Callable[[str], int]:
    return lambda y: sum(a != b for a, b in zip(x, y))


cached_encoder = lru_cache(32)(encode_x)


def WordeepSolverGenerator(path: str):
    model = tf.keras.models.load_model(path)

    class WordeepSolver(wordpy.Solver):
        def guess(self) -> wordpy.WordTable:
            self.drop_words_by_state()

            x = {
                'possibilities_input': cached_encoder((self.words, )),
                'includes_input': encode_includes((self.state.includes, )),
            }
            y = model.predict(x)[0]

            candidate = decode(y)[0]
            print(f'{candidate} ({len(self.words)} candidates)')

            return wordpy.WordTable(sorted(self.words, key=edit_distance(candidate))[:10])

    return WordeepSolver


if __name__ == '__main__':
    words = wordpy.get_words()
    average_attempts, average_wins = wordpy.benchmark(words, WordeepSolverGenerator('output/model'))

    print(f'average {average_attempts} attempts, {average_wins:.0%} wins')
