"""reproducible checks at larger ranks and degrees."""

import json
from pathlib import Path
from random import Random
from check_classical import check


def run(seed=731):
    rng = Random(seed)
    out = []
    for kind in 'BCD':
        for n, count, depth in [(6, 3, 2), (7, 3, 2),
                                (7, 8, 0), (8, 8, 0), (10, 8, 0), (12, 8, 0)]:
            lo, hi = ((1, n - 1) if kind == 'C' else
                      (2, n) if kind == 'B' else (2, n - 2))
            for t in range(count):
                r = lo if t == 0 else hi if t == 1 else rng.randint(lo, hi)
                tail = [a for a in range(n + 1) if a != r]
                rng.shuffle(tail)
                order = (r, *tail)
                tests = check(kind, n, order, depth)
                out.append(dict(type=kind, rank=n, order=order,
                                depth=depth, raising=tests))
            print(kind, n, depth, count, 'passed', flush=True)
    return dict(seed=seed, cases=out)


if __name__ == '__main__':
    Path('extra_checks.json').write_text(json.dumps(run(), indent=2) + '\n')
