wordpy
======

![puzzle](./puzzle.jpg)

Word puzzle solver.


## Use as solver

``` shell
$ git clone https://github.com/macrat/wordpy.git
$ python3.10 -m wordpy
candidates 0:               
cares
cores
bares
carey
bores
canes
carts
ceras
cires
corey

what did you input?
  _____
> cares
what was correct? (input incorrect character as .)
  _____
> ..r..
what characters was yellow?
> a
```

`what did you input?` -> enter what you have input to the game.

`what was correct?` -> enter what letters was correct. please input incorrect letters as `.`.

`what characters was yellow?` -> enter what letters was included in the answer but not correct position.


## Make your own solver

``` python
import wordpy


class MySolver(wordpy.Solver):
    def __init__(self, game: wordpy.Game):
        super().__init__(game)

        # do initialization here

    def guess(self) -> wordpy.WordTable:
        self.state # current game status.
        self.words # current word candidates.

        self.drop_words_by_state() # drop words that can't be the answer, from self.words.

        return self.words[:10] # return some next word candidates.


if __name__ == '__main__':
    words = wordpy.get_words()
    average_attempts, average_wins = wordpy.benchmark(words, MySolver)

    print(f'average {average_attempts} attempts, {average_wins:.0%} wins')
```

There are 3 solvers in this repository.
The solvers are defined in [solver.py](./solver.py).

- __wordpy.solver.RandomSolver__: Just choices random word from possible words.
- __wordpy.solver.MajorLetterSolver__: Tries to use letters that commonly use.
- __wordpy.solver.MinorLetterSolver__: The opposite of MajorLetterSolver. Uses minor letters.
- __wordpy.solver.MarkSolver__: Tries to all letters as many as possible to detect what letters used in the answer. (this is most efficient in this repository)
