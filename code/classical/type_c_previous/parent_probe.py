"""cartan selection from the grid."""

from exact_lyndon import insert_basis
from grid_probe import grid


def projection(d):
    n = len(d) - 1
    v = [0] * n
    v[0] = -2 * d[0]
    for i in range(1, n):
        v[i - 1] += d[i]
        v[i] -= d[i]
    v[-1] += 2 * d[-1]
    return tuple(v)


def deg(w, n):
    return tuple(w.count(i) for i in range(n + 1))


def lyndon(w, key):
    return bool(w) and all(key(w) < key(w[i:]) for i in range(1, len(w)))


def selected(n: int, order):
    d, cs, key = grid(n, order[0], order)
    basis, out = [], []
    for item in cs:
        if insert_basis(projection(deg(item[1], n)), basis):
            out.append(item)
    return d, out, key
