"""exact lyndon words from homogeneous matrix generators."""

from functools import lru_cache
from itertools import combinations
from math import gcd
from functools import reduce


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def scale(a, k):
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


def primitive(a):
    a = {p: x for p, x in a.items() if x}
    if not a:
        return a
    g = reduce(gcd, map(abs, a.values()))
    if a[min(a)] < 0:
        g = -g
    return {p: x // g for p, x in a.items()}


def insert(a, basis):
    a = primitive(a)
    for p in sorted(basis):
        if p not in a:
            continue
        b, x = basis[p], a[p]
        y = b[p]
        a = primitive({q: y * a.get(q, 0) - x * b.get(q, 0)
                       for q in a.keys() | b.keys()})
        if not a:
            return False
    if not a:
        return False
    basis[min(a)] = a
    return True


def model(name, n):
    if name == 'Aeven':
        if n < 1:
            raise ValueError('require n >= 1')
        z = 2 * n
        gens = {0: {(n, 0): 1},
                n: {(n - 1, z): 1, (z, 2 * n - 1): -1}}
        for i in range(1, n):
            gens[i] = {(i - 1, i): 1, (n + i, n + i - 1): -1}
        delta = (1,) + (2,) * n
        return gens, delta
    if name == 'Aodd':
        if n < 2:
            raise ValueError('require n >= 2')
        gens = {0: {(n + 1, 0): 1, (n, 1): -1},
                n: {(n - 1, 2 * n - 1): 1}}
        for i in range(1, n):
            gens[i] = {(i - 1, i): 1, (n + i, n + i - 1): -1}
        delta = (1, 1) + (2,) * (n - 2) + (1,)
        return gens, delta
    raise ValueError('unknown model')


class Words:
    def __init__(self, gens, delta, order, K=2, comm=bracket):
        self.gens = gens
        self.comm = comm
        self.delta = tuple(delta)
        self.order = tuple(order)
        self.rank = {a: i for i, a in enumerate(order)}
        self.n = len(delta)
        if sorted(order) != list(range(self.n)) or K < 1:
            raise ValueError('invalid order or height')
        self.cap = scale(delta, K)
        self.units = [tuple(int(j == i) for j in range(self.n))
                      for i in range(self.n)]
        self.spaces = {}
        self.layers = {}
        self.words = {}
        self.lyndon = lru_cache(None)(self._lyndon)
        self.b = lru_cache(None)(self._b)
        self.closure()
        self.degs = sorted(self.spaces, key=lambda d: (sum(d), d))
        for d in self.degs:
            self.compute(d)

    def closure(self):
        for i, d in enumerate(self.units):
            self.spaces[d] = {min(self.gens[i]): primitive(self.gens[i])}
            self.layers.setdefault(1, set()).add(d)
        for h in range(1, sum(self.cap)):
            for d in sorted(self.layers.get(h, ())):
                for j, e in enumerate(self.units):
                    if d[j] >= self.cap[j]:
                        continue
                    t = add(d, e)
                    for b in self.spaces[d].values():
                        a = self.comm(self.gens[j], b)
                        if not a:
                            continue
                        basis = self.spaces.setdefault(t, {})
                        if insert(a, basis):
                            self.layers.setdefault(h + 1, set()).add(t)

    def key(self, w):
        return tuple(self.rank[i] for i in w)

    def _lyndon(self, w):
        return bool(w) and all(self.key(w) < self.key(w[i:])
                               for i in range(1, len(w)))

    def _b(self, w):
        if len(w) == 1:
            return self.gens[w[0]]
        i = next(i for i in range(1, len(w)) if self.lyndon(w[i:]))
        return self.comm(self.b(w[:i]), self.b(w[i:]))

    def lcp(self, w):
        return next(w[:i] for i in range(len(w) - 1, 0, -1)
                    if self.lyndon(w[:i]))

    def deg(self, w):
        return tuple(w.count(i) for i in range(self.n))

    def compute(self, d):
        if sum(d) == 1:
            self.words[d] = [(d.index(1),)]
            return
        cs = set()
        for h in range(1, sum(d) // 2 + 1):
            for a in self.layers.get(h, ()):
                z = sub(d, a)
                if z not in self.words:
                    continue
                for u in self.words[a]:
                    for v in self.words[z]:
                        x, y = sorted((u, v), key=self.key)
                        if x != y and self.comm(self.b(x), self.b(y)):
                            cs.add(x + y)
        basis, chosen = {}, []
        for w in sorted(cs, key=self.key, reverse=True):
            if not self.lyndon(w):
                raise AssertionError(('non-lyndon', w))
            if insert(self.b(w), basis):
                chosen.append(w)
        if len(chosen) != len(self.spaces[d]):
            raise AssertionError(('dimension', d, len(chosen), len(self.spaces[d])))
        self.words[d] = chosen

    def exhaustive_binary(self, d):
        if self.n != 2:
            raise ValueError('binary words only')
        cs = []
        for zeroes in combinations(range(sum(d)), d[0]):
            w = [1] * sum(d)
            for j in zeroes:
                w[j] = 0
            w = tuple(w)
            if self.lyndon(w):
                cs.append(w)
        basis, out = {}, []
        for w in sorted(cs, key=self.key, reverse=True):
            if insert(self.b(w), basis):
                out.append(w)
        return out


if __name__ == '__main__':
    import argparse
    import json
    p = argparse.ArgumentParser()
    p.add_argument('--type', default='Aeven', choices=['Aeven', 'Aodd'])
    p.add_argument('-n', type=int, default=1)
    p.add_argument('-k', type=int, default=6)
    p.add_argument('--order', default=None)
    p.add_argument('--exhaustive', action='store_true')
    a = p.parse_args()
    gens, delta = model(a.type, a.n)
    order = tuple(map(int, a.order.split(','))) if a.order else tuple(range(a.n + 1))
    c = Words(gens, delta, order, a.k)
    rows = []
    for k in range(1, a.k + 1):
        d = scale(delta, k)
        ws = c.words[d]
        if a.exhaustive:
            assert c.exhaustive_binary(d) == ws
        rows.append({'k': k, 'words': ws,
                     'prefixes': [c.lcp(w) for w in ws],
                     'brackets': [sorted((str(p), x) for p, x in c.b(w).items())
                                  for w in ws]})
    print(json.dumps({'type': a.type, 'n': a.n, 'order': order, 'delta': delta,
                      'root_spaces': len(c.spaces), 'rows': rows}, indent=2))
