from .dictionary import get_words
from .solver import MarkSolver
from .utils import solve


solve(get_words(), MarkSolver)
