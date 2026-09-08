"""generalized leclerc recursion with exact classical matrix brackets."""

from functools import lru_cache
from exact_lyndon import CWords, add, sub, mul, bracket, insert_basis


def roots(kind, n):
    out = []
    for a in range(1, n + 1):
        if kind in ('B', 'C'):
            d = [0] * (n + 1)
            for j in range(a, n + 1):
                d[j] = 1 if kind == 'B' or j == n else 2
            out.append(tuple(d))
        for b in range(a + 1, n + 1):
            out.append(tuple(int(a <= j < b) for j in range(n + 1)))
            d = [0] * (n + 1)
            if kind == 'D' and b == n:
                for j in range(a, n - 1):
                    d[j] = 1
                d[n] = 1
            else:
                for j in range(a, n + 1):
                    d[j] = 1 if j < b else 2
                if kind == 'C':
                    d[n] = 1
                elif kind == 'D':
                    d[n - 1] = d[n] = 1
            out.append(tuple(d))
    return out


class Words(CWords):
    def __init__(self, kind, n, order, K=2, build=True):
        kind = kind.upper()
        if kind not in ('B', 'C', 'D') or n < (4 if kind == 'D' else 2) or K < 1:
            raise ValueError('invalid root system or cutoff')
        order = tuple(order)
        if sorted(order) != list(range(n + 1)):
            raise ValueError('order must permute 0 through n')
        self.kind, self.n, self.order = kind, n, order
        self.rank = {a: j for j, a in enumerate(order)}
        if kind == 'C':
            self.delta = (1,) + (2,) * (n - 1) + (1,)
        elif kind == 'B':
            self.delta = (1, 1) + (2,) * (n - 1)
        else:
            self.delta = (1, 1) + (2,) * (n - 3) + (1, 1)
        e = [tuple(int(i == j) for j in range(n)) for i in range(n)]
        if kind == 'C':
            first, last = mul(e[0], -2), mul(e[-1], 2)
        else:
            first = mul(add(e[0], e[1]), -1)
            last = e[-1] if kind == 'B' else add(e[-2], e[-1])
        self.simple_proj = [first] + [sub(e[j], e[j + 1]) for j in range(n - 1)] + [last]
        self.finite = roots(kind, n)
        self.simple = {i: tuple(int(i == j) for j in range(n + 1))
                       for i in range(n + 1)}
        self.gens = {i: {(i - 1, i): 1, (n + i, n + i - 1): -1}
                     for i in range(1, n)}
        if kind == 'C':
            self.gens[0] = {(n, 0): 1}
            self.gens[n] = {(n - 1, 2 * n - 1): 1}
        else:
            self.gens[0] = {(n + 1, 0): 1, (n, 1): -1}
            if kind == 'B':
                self.gens[n] = {(n - 1, 2 * n): 1, (2 * n, 2 * n - 1): -1}
            else:
                self.gens[n] = {(n - 2, 2 * n - 1): 1, (n - 1, 2 * n - 2): -1}
        h = sum(self.delta)
        ds = set()
        for d in self.finite:
            for k in range(K + 1):
                for a in (add(d, mul(self.delta, k)), sub(mul(self.delta, k), d)):
                    if min(a) >= 0 and 0 < sum(a) <= K * h:
                        ds.add(a)
        ds.update(mul(self.delta, k) for k in range(1, K + 1))
        self.degs = sorted(ds, key=lambda a: (sum(a), a))
        self.degset = ds
        self.words, self.byheight = {}, {}
        self.lyndon = lru_cache(None)(self._lyndon)
        self.b = lru_cache(None)(self._b)
        if build:
            for d in self.degs:
                self.compute(d)

    def projection(self, d):
        return tuple(sum(d[j] * self.simple_proj[j][i] for j in range(self.n + 1))
                     for i in range(self.n))

    def blocks(self):
        r = self.order[0]
        if self.delta[r] != 2:
            raise ValueError('the least letter must have mark two')
        out = {}
        for d in self.degs:
            if d[r] != 1:
                continue
            if sum(d) == 1:
                out[d] = (r,)
                continue
            opts = []
            for a in range(self.n + 1):
                p = sub(d, self.simple[a])
                if p in out:
                    opts.append(out[p] + (a,))
            if not opts:
                raise ArithmeticError('block has no root predecessor')
            out[d] = max(opts, key=self.key)
        return out

    def pairs(self):
        bs = self.blocks()
        pairs = []
        for d, u in bs.items():
            v = bs[sub(self.delta, d)]
            if self.key(u) < self.key(v):
                pairs.append((u + v, u, v, d))
        pairs.sort(key=lambda row: self.key(row[0]), reverse=True)
        chosen, basis = [], []
        for row in pairs:
            if insert_basis(self.projection(row[-1]), basis):
                chosen.append(row)
        return bs, pairs, chosen


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('kind', choices=['B', 'C', 'D'])
    p.add_argument('n', type=int)
    p.add_argument('order', help='comma-separated labels, least first')
    p.add_argument('k', type=int, nargs='?', default=2)
    a = p.parse_args()
    c = Words(a.kind, a.n, map(int, a.order.split(',')), a.k)
    for i, w in enumerate(c.words[mul(c.delta, a.k)], 1):
        print(i, ' '.join(map(str, w)))
