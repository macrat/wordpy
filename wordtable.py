from typing import overload, Iterable, Iterator, Callable, Set
import itertools


class WordTable:
    """ A table of words.
    WordTable always drop duplicates.

    >>> table = WordTable([
    ...     "hello",
    ...     "word-",
    ...     "table",
    ...     "world",
    ...     "hello",
    ... ])

    >>> table
    WordTable(['hello', 'word-', 'table', 'world'])

    >>> table[0]
    'hello'

    >>> table[1:3]
    WordTable(['word-', 'table'])

    >>> "hello" in table
    True
    >>> "power" in table
    False
    """

    def __init__(self, words: Iterable[str]):
        self.__words = dict.fromkeys(words)

    def take_matches(self, pattern: str, includes: Set[str] | str = None) -> 'WordTable':
        """ Take words that matches as the pattern.
        "." in the pattern can be any chatacter.

        >>> table = WordTable([
        ...     "hello",
        ...     "world",
        ... ])
        >>> print(table.take_matches('...l.'))
        hello
        world
        >>> print(table.take_matches('h..l.'))
        hello
        >>> print(table.take_matches('.....', includes='r'))
        world
        """

        def isMatch(word: str) -> bool:
            return (
                all(p == '.' or w == p for p, w in zip(pattern, word))
                and (includes is None or all(i in word for i in includes))
            )

        return WordTable(w for w in self if isMatch(w))

    def drop_by_letters(self, letters: Iterable[str]) -> 'WordTable':
        """ Drop words that includes specified letters.

        >>> table = WordTable([
        ...     "hello",
        ...     "world",
        ...     "hotel",
        ... ])
        >>> table.drop_by_letters("e")
        WordTable(['world']) 
        """

        return WordTable(
            word
            for word in self
            if all(l not in word for l in letters)
        )

    def drop_wrong(self, pattern: str) -> 'WordTable':
        """ Drop wrong words using pattern.

        >>> table = WordTable([
        ...     "hello",
        ...     "world",
        ...     "hotel",
        ... ])
        >>> table.drop_wrong("h...l")
        WordTable(['world'])
        >>> table.drop_wrong("wor.d")
        WordTable(['hello'])
        """

        return WordTable(
            word
            for word in self
            if all(p == '.' or w != p for w, p in zip(word, pattern))
        )

    def __eq__(self, other: 'WordTable') -> bool:
        return hash(self) == hash(other)

    def __hash__(self) -> int:
        return hash(tuple(self.__words))

    def __iter__(self) -> Iterator[str]:
        return iter(self.__words)

    def __len__(self) -> int:
        return len(self.__words)

    def __eq__(self, other: 'WordTable') -> bool:
        return len(self) == len(other) and all(x == y for x, y in zip(self, other))

    def __repr__(self) -> str:
        return 'WordTable(' + str(list(self.__words.keys())) + ')'

    def __str__(self) -> str:
        return '\n'.join(self.__words)

    @overload
    def __getitem__(self, idx: int) -> str:
        ...

    @overload
    def __getitem__(self, idx: slice) -> 'WordTable':
        ...

    def __getitem__(self, idx: int | slice) -> 'str | WordTable':
        if isinstance(idx, int):
            try:
                idx = slice(idx, None).indices(len(self))[0]
                return next(itertools.islice(self.__words.keys(), idx, None))
            except StopIteration:
                raise IndexError(f'out of index: {idx} of {len(self)}')
        elif isinstance(idx, slice):
            return WordTable(itertools.islice(self, *idx.indices(len(self))))
        else:
            raise ValueError(f'invalid index: {idx}')

    def __or__(self, other: 'WordTable | Iterable[str]') -> 'WordTable':
        """ Merge 2 word lists.

        >>> a = WordTable(["hello", "tasty", "world"])
        >>> b = WordTable(["tasty", "juice"])

        >>> a | b
        WordTable(['hello', 'tasty', 'world', 'juice'])

        >>> a | ["lemon"]
        WordTable(['hello', 'tasty', 'world', 'lemon'])
        >>> ["lemon"] | a
        WordTable(['hello', 'tasty', 'world', 'lemon'])
        """

        return WordTable((*self, *other))

    def __ror__(self, other: Iterable[str]) -> 'WordTable':
        return self | other

    def __and__(self, other: 'WordTable | Iterable[str]') -> 'WordTable':
        """ Extract words that in both of word lists.

        >>> a = WordTable(["hello", "tasty", "world"])
        >>> b = WordTable(["tasty", "juice"])

        >>> a & b
        WordTable(['tasty'])

        >>> a & ["hello", "world"]
        WordTable(['hello', 'world'])
        >>> ["hello", "world"] & a
        WordTable(['hello', 'world'])
        """

        return WordTable(w for w in self.__words if w in other)

    def __rand__(self, other: Iterable[str]) -> 'WordTable':
        return self & other

    def __sub__(self, other: 'WordTable | Iterable[str]') -> 'WordTable':
        """ Filter words that in another word list.

        >>> a = WordTable(["hello", "tasty", "world"])
        >>> b = WordTable(["tasty", "juice"])

        >>> a - b
        WordTable(['hello', 'world'])

        >>> a - ['hello']
        WordTable(['tasty', 'world'])
        """

        return WordTable(w for w in self.__words if w not in other)

    def __rsub__(self, other: Iterable[str]) -> 'WordTable':
        return WordTable(other) - self

    def __xor__(self, other: 'WordTable | Iterable[str]') -> 'WordTable':
        """ Get words that only included in one of word lists.

        >>> a = WordTable(["hello", "tasty", "world"])
        >>> b = WordTable(["tasty", "juice"])

        >>> a ^ b
        WordTable(['hello', 'world', 'juice'])

        >>> a ^ ['hello', 'world', 'boxes']
        WordTable(['tasty', 'boxes'])
        >>> ['hello', 'world', 'boxes'] ^ a
        WordTable(['tasty', 'boxes'])
        """

        return WordTable((self - other) | (other - self))

    def __rxor__(self, other: Iterable[str]) -> 'WordTable':
        return self ^ other
