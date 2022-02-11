import random
import functools
from typing import Set
from abc import ABC, abstractmethod
from collections import Counter
import itertools

from .wordtable import WordTable
from .game import Game, GameState


def default_logger(state: GameState, submitted: str, correct: bool):
    print(f'{state.num_tried:3d} {state.color_str()}')


class Solver(ABC):
    def __init__(self, game: Game):
        self.words = game.candidates
        self.game = game

    @property
    def state(self) -> GameState:
        return self.game.state

    @abstractmethod
    def guess(self) -> WordTable:
        raise NotImplementedError()

    def solve(self, log=default_logger) -> GameState:
        correct = False
        while not correct:
            word = self.guess()[0]
            correct = self.game.submit(word)
            log(self.state, word, correct)
        return self.state

    def drop_words_by_state(self) -> None:
        self.words = self.words.take_matches(self.state.found, self.state.includes)
        if len(self.state.wrongs) > 0:
            self.words = self.words.drop_wrong(self.state.wrongs[-1]).drop_by_letters(self.state.not_includes)


class RandomSolver(Solver):
    def guess(self) -> WordTable:
        self.drop_words_by_state()

        return WordTable(
            random.choice(self.words)
            for _ in range(10)
        )


class MajorLetterSolver(Solver):
    @functools.lru_cache(maxsize=8)
    @staticmethod
    def __sort_words(words: WordTable, answer_length: int) -> WordTable:
        ranking = [
            [c for (c, _) in Counter(w[i] for w in words).most_common()]
            for i in range(answer_length)
        ]

        def calc_score(word: str):
            return sum(
                26 - idx
                for i, (w, idx) in enumerate((w, ranking[i].index(w)) for i, w in enumerate(word))
                if idx >= 0 and w not in word[:i]
            )

        return WordTable(sorted(words, key=calc_score, reverse=True))

    def __init__(self, game: Game):
        super().__init__(game)

        self.words = MajorLetterSolver.__sort_words(game.candidates, game.answer_length)

    def guess(self) -> WordTable:
        self.drop_words_by_state()

        return self.words[:10]


class MinorLetterSolver(MajorLetterSolver):
    @functools.lru_cache(maxsize=8)
    @staticmethod
    def __reverse_words(words: WordTable) -> WordTable:
        return WordTable(reversed(words))

    def __init__(self, game: Game):
        super().__init__(game)

        self.words = MinorLetterSolver.__reverse_words(self.words)


class MarkSolver(MajorLetterSolver):
    def __init__(self, game: Game):
        super().__init__(game)

        self.markset = WordTable(
            word
            for word in self.words
            if all(w not in word[:i] for i, w in enumerate(word))
        )
        self.tried: Set[str] = set()

    def guess(self) -> WordTable:
        if not all(x == '.' for x in self.state.last_tried):
            self.drop_words_by_state()

            self.tried |= set(self.state.last_tried)

            # letters that can be included in the answer.
            candidates = set(itertools.chain.from_iterable(
                (c for c, f in zip(word, self.state.found) if f == '.')
                for word in self.words
            ))
            positional_candidates = [
                set(
                    c
                    for c in candidates
                    if c not in (w[i] for w in self.state.wrongs)
                )
                for i in range(self.game.answer_length)
            ]

            # letters that included in the answer but position is still undetermined.
            float_chars = self.state.includes - set(self.state.found)

            self.markset = WordTable(sorted(
                (w for w in self.markset if w != self.state.last_tried),
                key=lambda word: (
                    100 * sum(t not in word for t in self.tried) # try to use untried letter first.
                    + 10000 * sum(w in cs or self.state.found[i] != '.' for i, (cs, w) in enumerate(zip(positional_candidates, word))) # prefer to use candidate letters.
                    + sum(i in word for i in float_chars) # prefer to use candidate float letters.
                ),
                reverse=True,
            ))

        if ('.' not in self.state.found
            or len(self.markset) == 0
            or len(self.words) <= 3
            or len(self.state.includes) >= self.game.answer_length):
            return self.words[:10]
        else :
            return self.markset[:10]
