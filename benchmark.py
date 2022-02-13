""" Benchmark embedded solvers

Run this benchmark using below command.

$ python3.10 -m wordpy.benchmark
"""

from .dictionary import get_words
from .solver import RandomSolver, MajorLetterSolver, MinorLetterSolver, MarkSolver
from .utils import benchmark


if __name__ == '__main__':
    benchmark(get_words(), RandomSolver, MajorLetterSolver, MinorLetterSolver, MarkSolver)
