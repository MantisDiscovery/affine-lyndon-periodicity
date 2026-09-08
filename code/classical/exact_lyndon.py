"""exact standard lyndon words in affine type c."""

from fractions import Fraction
from functools import lru_cache


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def mul(a, k):
    return tuple(k * x for x in a)


def mm(a, b):
    c = {}
    for (i, j), x in a.items():
        for (k, l), y in b.items():
            if j == k:
                c[i, l] = c.get((i, l), 0) + x * y
    return {p: x for p, x in c.items() if x}


def bracket(a, b):
    c = mm(a, b)
    for p, x in mm(b, a).items():
        c[p] = c.get(p, 0) - x
    return {p: x for p, x in c.items() if x}


def insert_basis(v, basis):
    v = list(map(Fraction, v))
    for p, b in basis:
        c = v[p]
        if c:
            v = [x - c * y for x, y in zip(v, b)]
    p = next((i for i, x in enumerate(v) if x), None)
    if p is None:
        return False
    c = v[p]
    basis.append((p, [x / c for x in v]))
    return True


class CWords:
    def __init__(self, n: int, order, K: int = 2):
        order = tuple(order)
        if n < 2 or K < 1:
            raise ValueError('require n >= 2 and K >= 1')
        if sorted(order) != list(range(n + 1)):
            raise ValueError('order must permute 0 through n')
        self.n = n
        self.order = order
        self.rank = {x: i for i, x in enumerate(order)}
        self.delta = (1,) + (2,) * (n - 1) + (1,)
        roots = []
        for a in range(1, n + 1):
            roots.append((0,) + (0,) * (a - 1) + (2,) * (n - a) + (1,))
            for b in range(a + 1, n + 1):
                roots.append(tuple(int(a <= i < b) for i in range(n + 1)))
                roots.append(tuple(0 if i < a else 1 if i < b or i == n else 2
                                   for i in range(n + 1)))
        self.finite = roots
        degs = set()
        for root in roots:
            for t in range(K + 1):
                for d in (add(root, mul(self.delta, t)),
                          sub(mul(self.delta, t), root)):
                    if min(d) >= 0 and any(d) and sum(d) <= 2 * n * K:
                        degs.add(d)
        for k in range(1, K + 1):
            degs.add(mul(self.delta, k))
        self.degs = sorted(degs, key=lambda d: (sum(d), d))
        self.degset = degs
        self.simple = {i: tuple(int(i == j) for j in range(n + 1))
                       for i in range(n + 1)}
        # the degree records the loop power.
        self.gens = {0: {(n, 0): 1}, n: {(n - 1, 2 * n - 1): 1}}
        for i in range(1, n):
            self.gens[i] = {(i - 1, i): 1, (n + i, n + i - 1): -1}
        self.words = {}
        self.byheight = {}
        self.lyndon = lru_cache(None)(self._lyndon)
        self.b = lru_cache(None)(self._b)
        for d in self.degs:
            self.compute(d)

    def key(self, w):
        return tuple(self.rank[x] for x in w)

    def _lyndon(self, w):
        return bool(w) and all(self.key(w) < self.key(w[i:])
                               for i in range(1, len(w)))

    def _b(self, w):
        if len(w) == 1:
            return self.gens[w[0]]
        i = next(i for i in range(1, len(w)) if self.lyndon(w[i:]))
        return bracket(self.b(w[:i]), self.b(w[i:]))

    def lcp(self, w):
        if len(w) < 2:
            raise ValueError('a proper prefix requires at least two letters')
        return next(w[:i] for i in range(len(w) - 1, 0, -1)
                    if self.lyndon(w[:i]))

    def deg(self, w):
        return tuple(w.count(i) for i in range(self.n + 1))

    def projection(self, d):
        v = [0] * self.n
        v[0] = -2 * d[0]
        for i in range(1, self.n):
            v[i - 1] += d[i]
            v[i] -= d[i]
        v[-1] += 2 * d[-1]
        return tuple(v)

    def compute(self, d):
        if sum(d) == 1:
            self.words[d] = [(d.index(1),)]
            self.byheight.setdefault(1, []).append(d)
            return
        cs = set()
        for h in range(1, sum(d) // 2 + 1):
            for a in self.byheight.get(h, []):
                z = sub(d, a)
                if z not in self.words:
                    continue
                for u in self.words[a]:
                    for v in self.words[z]:
                        x, y = sorted((u, v), key=self.key)
                        if x != y and bracket(self.b(x), self.b(y)):
                            cs.add(x + y)
        chosen = []
        basis = []
        real = any(self.projection(d))
        for w in sorted(cs, key=self.key, reverse=True):
            b = self.b(w)
            if not b:
                continue
            if real:
                chosen = [w]
                break
            v = tuple(b.get((i, i), 0) for i in range(self.n))
            if insert_basis(v, basis):
                chosen.append(w)
        want = 1 if real else self.n
        if len(chosen) != want:
            raise AssertionError(('multiplicity', self.n, self.order, d))
        self.words[d] = chosen
        self.byheight.setdefault(sum(d), []).append(d)


def inspect(n: int, order, K: int = 2):
    c = CWords(n, order, K)
    r = c.order[0]
    if r in (0, n):
        raise ValueError('the block display requires an internal least letter')
    out = []
    for i, w in enumerate(c.words[c.delta], 1):
        k = w.index(r, 1)
        u, v = w[:k], w[k:]
        l = c.lcp(w)
        p, z = l[len(u):], w[len(l):]
        parents = []
        if p:
            q = c.words[sub(c.delta, c.deg(p))][0]
            for j, b in enumerate(c.words[c.delta], 1):
                if b in (p + q, q + p):
                    parents.append((j, b, q))
        out.append(dict(i=i, word=w, U=u, P=p, R=z, parents=parents))
    return c, out


if __name__ == '__main__':
    import argparse
    import json

    p = argparse.ArgumentParser()
    p.add_argument('n', type=int, nargs='?', default=3)
    p.add_argument('order', nargs='?', default=None)
    a = p.parse_args()
    order = tuple(map(int, a.order.split(','))) if a.order else (1, 0, *range(2, a.n + 1))
    c, rows = inspect(a.n, order)
    print(json.dumps(dict(delta=rows, twice=c.words[mul(c.delta, 2)])))
