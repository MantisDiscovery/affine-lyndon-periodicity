"""check the first-endpoint rule against every complementary candidate."""

from itertools import permutations
from grid_probe import grid

if not __debug__:
    raise RuntimeError('run without -O')


def run(limit: int = 6) -> int:
    if limit < 2:
        raise ValueError('max-rank must be at least 2')
    count = 0
    for n in range(2, limit + 1):
        for order in permutations(range(n + 1)):
            r = order[0]
            if r in (0, n):
                continue
            s = n - r
            a = tuple(range(r - 1, -1, -1))
            b = tuple(range(r + 1, n + 1))
            rank = {x: i for i, x in enumerate(order)}
            p = q = 0
            h = []
            while True:
                if rank[a[p]] > rank[b[q]]:
                    x = a[p]
                    p += 1
                else:
                    x = b[q]
                    q += 1
                if x in (0, n):
                    break
                h.append(x)
            if x == 0:
                vp = r, q
                up = r - 1, 2 * s - 1 - q
            else:
                vp = p, s
                up = 2 * r - 1 - p, s - 1
            d, cs, key = grid(n, r, order)
            assert cs[0][1:3] == (d[up], d[vp])
            assert d[vp][:-1] == (r,) + tuple(h)
            count += 1
    print('ok')
    return count


if __name__ == '__main__':
    run()
