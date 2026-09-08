"""all six orders in d4 triality through nine null roots."""

import itertools
import json
import time
from twisted_words import Words, bracket
from root_model import fold
from check_twisted import fit


def run():
    g, e, d = fold('D4tw')
    out = []
    for order in itertools.permutations(range(3)):
        start = time.time()
        c = Words(e, d, order, 9, comm=bracket)
        fs = fit(c, 9, 3)
        out.append({'type': 'D4tw', 'n': 2, 'delta': d,
                    'order': order, 'K': 9, 'families': fs,
                    'root_spaces': len(c.spaces)})
        print(order, round(time.time() - start, 2), flush=True)
    return out


if __name__ == '__main__':
    with open('triality_checks.json', 'w') as f:
        json.dump(run(), f, indent=2)
