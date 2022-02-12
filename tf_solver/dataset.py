from typing import Iterable
import string
import random

import numpy

import wordpy


class StateCollectSolver(wordpy.Solver):
    def __init__(self, game: wordpy.Game):
        super().__init__(game)
        self.possibilities = []
        self.includes = []

    def guess(self) -> wordpy.WordTable:
        self.drop_words_by_state()

        self.possibilities.append(self.words)
        self.includes.append(self.state.includes)

        return wordpy.WordTable([
            random.choice(self.words)
        ])


def encode_x(words: Iterable[wordpy.WordTable]) -> numpy.ndarray:
    return numpy.array([
        numpy.sum([
            [
                [1 if w == a else 0 for a in string.ascii_lowercase]
                for w in word
            ]
            for word in ws
        ], axis=0) / len(ws)
        for ws in words
    ])


def encode_includes(possibilities: Iterable[Iterable[str]]) -> numpy.ndarray:
    return numpy.array([
        numpy.sum([
            [0] * len(string.ascii_lowercase)
        ] + [
            [1 if c == a else 0 for a in string.ascii_lowercase]
            for c in charset
        ], axis=0)
        for charset in possibilities
    ])


def encode_y(words: Iterable[str]) -> numpy.ndarray:
    return numpy.array([
        [string.ascii_lowercase.index(w) for w in word]
        for word in words
    ])


def decode(data: numpy.ndarray) -> wordpy.WordTable:
    return [
        ''.join(string.ascii_lowercase[i] for i in xs)
        for xs in numpy.argmax(data, axis=-1)
    ]


def generate_dataset(n=100):
    words = wordpy.get_words()
    possibilities = []
    includes = []
    ys = []
    for i in range(n):
        if i%10 == 0:
            print(f'\r{i/n:6.1%}', end='')
        answer = random.choice(words)
        game = wordpy.FixedGame(words, answer)
        solver = StateCollectSolver(game)
        solver.solve(lambda x, y, z: None)
        possibilities.extend(encode_x(solver.possibilities))
        includes.extend(encode_includes(solver.includes))
        ys.extend(encode_y([answer] * len(solver.possibilities)))
    print('\r100.0%')

    return {
        'possibilities': numpy.array(possibilities),
        'includes': numpy.array(includes),
        'answers': numpy.array(ys),
    }


if __name__ == '__main__':
    data = generate_dataset(10000)
    numpy.savez_compressed('output/dataset.npz', **data)
