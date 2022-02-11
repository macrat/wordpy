from typing import Iterable
import tempfile
import urllib.request

from .wordtable import WordTable


DICTIONARY_URL = 'https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt'


def fetch() -> Iterable[str]:
    fname = tempfile.gettempdir() + '/wordpy-dictionary.txt'
    try:
        with open(fname, 'r') as f:
            return [l.strip('\n') for l in f]
    except:
        pass

    with urllib.request.urlopen(DICTIONARY_URL) as f:
        result = [l.strip('\n') for l in f.read().decode('utf-8').splitlines()]

    with open(fname, 'w') as f:
        f.write('\n'.join(result) + '\n')

    return result


def get_words(length: int = 5) -> WordTable:
    """ Get words dictionary from https://github.com/dwyl/english-words
    """
    return WordTable(word for word in fetch() if len(word) == length)
