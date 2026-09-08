"""selected orthogonal and exceptional twists through six null roots."""

import json
from pathlib import Path
from root_model import fold
from twisted_words import Words
from check_twisted import fit


def run():
    cases = [('Dtw', 3, [(0, 1, 2, 3), (0, 1, 3, 2),
                        (0, 2, 1, 3), (3, 2, 1, 0)]),
             ('E6tw', 0, [(0, 1, 2, 3, 4), (0, 1, 2, 4, 3),
                          (0, 1, 3, 2, 4), (3, 4, 2, 1, 0),
                          (4, 3, 2, 1, 0)])]
    out = []
    for name, n, orders in cases:
        g, e, d = fold(name, n)
        for order in orders:
            c = Words(e, d, order, 6, comm=g.comm)
            out.append({'type': name, 'n': n, 'delta': d, 'order': order,
                        'K': 6, 'families': fit(c, 6, 2),
                        'root_spaces': len(c.spaces)})
            print(name, order, flush=True)
    return out


if __name__ == '__main__':
    Path('folded_checks.json').write_text(json.dumps(run(), indent=2))
