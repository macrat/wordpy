from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Set
import itertools

from .wordtable import WordTable


@dataclass(frozen=True)
class GameState:
    # letters that determined.
    # e.g. "w..ld"
    found: str

    # letters that includes in the answer but position is not determined yet.
    # e.g. set(["o", "r"])
    includes: Set[str]

    # words that tried and wrong.
    # e.g. wordpy.WordTable(["hel.o", ".ie.."])
    wrongs: WordTable

    # number of attempts.
    num_tried: int

    # the word that latest tried.
    last_tried: str

    @property
    def not_includes(self) -> str:
        """ letters that not includes in the answer """

        return ''.join(
            w
            for w in itertools.chain.from_iterable(self.wrongs)
            if w not in self.includes and w != '.'
        )

    def __str__(self) -> str:
        includes = self.includes - set(self.found)
        if len(includes) > 0:
            return f'{self.found} + {"".join(sorted(includes))}'
        else:
            return f'{self.found}'

    def color_str(self) -> str:
        """ pretty string with ASCII color sequence. """

        result = ''
        for f, t in zip(self.found, self.last_tried):
            esc = '\033[30;47m'
            if f == t:
                esc = '\033[42;30m'
            elif t in self.includes:
                esc = '\033[43;30m'
            result += esc + ' ' + t + ' '
        return result + '\033[0m'


class Game(ABC):
    """ A game session of wordpy.
    """

    state: GameState
    candidates: WordTable
    answer_length: int

    @abstractmethod
    def submit(self, word: str) -> bool:
        ...

    def __str__(self) -> str:
        return str(self.state)


class FixedGame(Game):
    """ A normal game session of wordpy.

    >>> words = WordTable(["hello", "world", "heart"])
    >>> game = FixedGame(words, "hello")

    >>> game.submit("world")
    False
    >>> game.state.found
    '...l.'
    >>> sorted(game.state.includes)
    ['l', 'o']
    >>> game.state.wrongs
    WordTable(['wor.d'])
    >>> game.state.num_tried
    1

    >>> game.submit("heart")
    False
    >>> game.state.found
    'he.l.'
    >>> sorted(game.state.includes)
    ['e', 'h', 'l', 'o']
    >>> game.state.wrongs
    WordTable(['wor.d', '..art'])
    >>> game.state.num_tried
    2

    >>> game.submit("hello")
    True
    >>> game.state.found
    'hello'
    >>> sorted(game.state.includes)
    ['e', 'h', 'l', 'o']
    >>> game.state.wrongs
    WordTable(['wor.d', '..art'])
    >>> game.state.num_tried
    3
    """

    def __init__(self, words: WordTable, answer: str):
        if '.' in answer:
            raise ValueError('answer can not include dot in answer')
        if answer not in words:
            raise ValueError('answer is not in the candidate words')

        self.__answer = answer
        self.candidates = words

        self.state = GameState(
            found='.' * len(answer),
            includes=set(),
            wrongs=WordTable([]),
            num_tried=0,
            last_tried='.' * len(answer),
        )

    @property
    def answer_length(self) -> int:
        return len(self.__answer)

    def submit(self, word: str) -> bool:
        if len(word) != len(self.__answer):
            raise ValueError(f'invalid length {repr(word)} (expected {len(self.__answer)} characters)')
        if word not in self.candidates:
            raise ValueError(f'{repr(word)} is not in the candidates')

        wrongs = self.state.wrongs
        if self.__answer != word:
            w = ''.join(w if w != a else '.' for a, w in zip(self.__answer, word))
            if w not in wrongs:
                wrongs |= [w]

        self.state = GameState(
            found=''.join(
                a if a == w or a == f else '.'
                for a, w, f in zip(self.__answer, word, self.state.found)
            ),
            includes=self.state.includes | set(w for w in word if w in self.__answer),
            wrongs=wrongs,
            num_tried=self.state.num_tried + 1,
            last_tried=word,
        )

        return self.__answer == word


class TerminalGame(Game):
    """ A game session of wordpy, for making a solver tool.
    """

    def __init__(self, candidates: WordTable):
        self.candidates = candidates
        self.answer_length = len(candidates[0])
        self.state = GameState(
            found='.' * self.answer_length,
            includes=set(),
            wrongs=WordTable([]),
            num_tried=0,
            last_tried='.' * self.answer_length,
        )

    def ask_result(self) -> tuple[str, str]:
        return input('what was correct? (input incorrect character as .)\n  _____\n> '), input('what characters was yellow?\n> ')

    def submit(self, word: str) -> bool:
        result = self.ask_result()
        correct = result[0]
        includes = set(result[1])

        wrongs = self.state.wrongs
        if correct != word:
            w = ''.join(w if w != c else '.' for c, w in zip(correct, word))
            if w not in wrongs:
                wrongs |= [w]

        self.state = GameState(
            found=''.join(
                c if c == w else f
                for c, w, f in zip(correct, word, self.state.found)
            ),
            includes=self.state.includes | set(w for w in word if w in set(correct) | includes),
            wrongs=wrongs,
            num_tried=self.state.num_tried + 1,
            last_tried=word,
        )

        return correct == word
