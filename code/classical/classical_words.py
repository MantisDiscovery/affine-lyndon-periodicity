"""imaginary standard lyndon words for a mark-two least letter."""

from dataclasses import dataclass
from typing import Iterable


class Arm:
    def __init__(self, stem: Iterable[int], ends=None):
        self.stem = tuple(stem)
        self.ends = None if ends is None else tuple(ends)
        self.last = len(self.stem) if ends is None else 2 * len(self.stem) + 3

    def edges(self, i: int):
        if self.ends is None:
            return [] if i == self.last else [(self.stem[i], i + 1)]
        m = len(self.stem)
        a, b = self.ends
        if i < m:
            return [(self.stem[i], i + 1)]
        if i == m:
            return [(a, m + 1), (b, m + 2)]
        if i == m + 1:
            return [(b, m + 3)]
        if i == m + 2:
            return [(a, m + 3)]
        if i == self.last:
            return []
        return [(self.stem[2 * m + 2 - i], i + 1)]

    def leq(self, i: int, j: int) -> bool:
        if i > j:
            return False
        m = len(self.stem)
        return not (self.ends is not None and i == m + 1 and j == m + 2)


def arms(kind: str, n: int, r: int):
    if kind == 'C':
        left = Arm([*range(r - 1, 0, -1), 0, *range(1, r)])
        right = Arm([*range(r + 1, n), n, *range(n - 1, r, -1)])
    else:
        left = Arm(range(r - 1, 1, -1), (0, 1))
        if kind == 'D':
            right = Arm(range(r + 1, n - 1), (n - 1, n))
        elif r == n:
            right = Arm([])
        else:
            right = Arm([*range(r + 1, n), n, n, *range(n - 1, r, -1)])
    return left, right


def block(left: Arm, right: Arm, p: int, q: int, r: int, rank: dict):
    i = j = 0
    w = [r]
    while (i, j) != (p, q):
        opts = [(a, b, j) for a, b in left.edges(i) if left.leq(b, p)]
        opts += [(a, i, b) for a, b in right.edges(j) if right.leq(b, q)]
        a, i, j = max(opts, key=lambda v: rank[v[0]])
        w.append(a)
    return tuple(w)


def projection(kind: str, n: int, w: tuple):
    v = [0] * n
    for a in w:
        if a == 0:
            v[0] -= 2 if kind == 'C' else 1
            if kind != 'C':
                v[1] -= 1
        elif a < n:
            v[a - 1] += 1
            v[a] -= 1
        elif kind == 'C':
            v[-1] += 2
        elif kind == 'B':
            v[-1] += 1
        else:
            v[-2] += 1
            v[-1] += 1
    return tuple((i, x) for i, x in enumerate(v) if x)


def independent(v: tuple, cols: list, n: int) -> bool:
    # each component has at most one free kernel coordinate.
    adj = [[] for _ in range(n)]
    pinned = set()
    for col in cols:
        if len(col) == 1:
            pinned.add(col[0][0])
        else:
            (a, x), (b, y) = col
            sign = -x * y
            adj[a].append((b, sign))
            adj[b].append((a, sign))
    comp = [-1] * n
    sign = [0] * n
    free = []
    for a in range(n):
        if comp[a] >= 0:
            continue
        c = len(free)
        comp[a], sign[a] = c, 1
        stack = [a]
        ok = True
        while stack:
            b = stack.pop()
            if b in pinned:
                ok = False
            for d, s in adj[b]:
                t = sign[b] * s
                if comp[d] < 0:
                    comp[d], sign[d] = c, t
                    stack.append(d)
                elif sign[d] != t:
                    ok = False
        free.append(ok)
    vals = {}
    for a, x in v:
        c = comp[a]
        if free[c]:
            vals[c] = vals.get(c, 0) + x * sign[a]
    return any(vals.values())


@dataclass(frozen=True)
class Entry:
    left: tuple
    period: tuple
    right: tuple
    parent: int

    def word(self, k: int = 1) -> tuple:
        if not isinstance(k, int) or k < 1:
            raise ValueError('k must be a positive integer')
        return self.left + self.period * (k - 1) + self.right

    def letter(self, k: int, t: int) -> int:
        if not isinstance(k, int) or k < 1:
            raise ValueError('k must be a positive integer')
        h = len(self.period)
        if not isinstance(t, int) or not 0 <= t < k * h:
            raise IndexError('letter index outside the word')
        if t < len(self.left):
            return self.left[t]
        t -= len(self.left)
        if t < (k - 1) * h:
            return self.period[t % h]
        return self.right[t - (k - 1) * h]


def table(kind: str, n: int, order: Iterable[int]) -> list[Entry]:
    kind = kind.upper()
    if kind not in ('B', 'C', 'D') or not isinstance(n, int):
        raise ValueError('use type B, C, or D and an integer rank')
    if n < (4 if kind == 'D' else 2):
        raise ValueError('rank is too small')
    order = tuple(order)
    if any(not isinstance(a, int) for a in order) or sorted(order) != list(range(n + 1)):
        raise ValueError('order must permute 0 through n')
    r = order[0]
    valid = (1 <= r < n if kind == 'C' else
             2 <= r <= n if kind == 'B' else 2 <= r <= n - 2)
    if not valid:
        raise ValueError('this constructor requires a mark-two least letter')
    rank = {a: i for i, a in enumerate(order)}
    key = lambda w: tuple(rank[a] for a in w)
    left, right = arms(kind, n, r)
    ws = {(p, q): block(left, right, p, q, r, rank)
          for p in range(left.last + 1) for q in range(right.last + 1)}
    where = {w: ij for ij, w in ws.items()}
    pairs = []
    for (p, q), u in ws.items():
        v = ws[left.last - p, right.last - q]
        if key(u) < key(v):
            pairs.append((u, v))
    pairs.sort(key=lambda uv: key(uv[0] + uv[1]), reverse=True)
    cols, chosen = [], []
    for u, v in pairs:
        col = projection(kind, n, u)
        if independent(col, cols, n):
            cols.append(col)
            chosen.append((u, v))
    if len(chosen) != n:
        raise ArithmeticError('unexpected imaginary multiplicity')
    index = {u + v: i for i, (u, v) in enumerate(chosen, 1)}
    out = []
    for i, (u, v) in enumerate(chosen, 1):
        if i == 1:
            out.append(Entry(u, u + v, v, 1))
            continue
        p = v[:-1]
        a, b = where[p]
        q = ws[left.last - a, right.last - b]
        parent = q + p if key(q) < key(p) else p + q
        j = index[parent]
        if j >= i:
            raise ArithmeticError('parent is not earlier')
        out.append(Entry(u + p, q + p, v[-1:], j))
    return out


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('kind', choices=['B', 'C', 'D'])
    p.add_argument('n', type=int)
    p.add_argument('order', help='comma-separated labels, least first')
    p.add_argument('k', type=int, nargs='?', default=1)
    a = p.parse_args()
    rows = table(a.kind, a.n, map(int, a.order.split(',')))
    for i, row in enumerate(rows, 1):
        print(i, ' '.join(map(str, row.word(a.k))))
