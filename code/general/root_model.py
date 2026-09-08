"""simply laced root brackets and diagram folds over the rationals."""

from functools import lru_cache
from itertools import product


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def neg(a):
    return tuple(-x for x in a)


def plus(a, b, k=1):
    c = dict(a)
    for p, x in b.items():
        c[p] = c.get(p, 0) + k * x
    return {p: x for p, x in c.items() if x}


class ADE:
    def __init__(self, kind, n):
        self.n = n
        if kind == 'A':
            edges = [(i, i + 1) for i in range(n - 1)]
        elif kind == 'D' and n >= 4:
            edges = [(i, i + 1) for i in range(n - 3)]
            edges += [(n - 3, n - 2), (n - 3, n - 1)]
        elif kind == 'E' and n in (6, 7, 8):
            chain = [0] + list(range(2, n))
            edges = list(zip(chain, chain[1:])) + [(1, 3)]
        else:
            raise ValueError('unsupported diagram')
        self.a = [[2 * int(i == j) for j in range(n)] for i in range(n)]
        for i, j in edges:
            self.a[i][j] = self.a[j][i] = -1
        self.simple = [tuple(int(i == j) for j in range(n)) for i in range(n)]
        roots = set(self.simple)
        todo = list(roots)
        while todo:
            x = todo.pop()
            for i in range(n):
                y = list(x)
                y[i] -= sum(t * z for t, z in zip(self.a[i], x))
                y = tuple(y)
                if y not in roots:
                    roots.add(y)
                    todo.append(y)
        self.roots = sorted(roots)
        self.ids = {a: i for i, a in enumerate(self.roots)}
        self.nr = len(self.roots)
        self.dim = self.nr + n
        self.top = max(self.roots, key=sum)
        self.pair = lru_cache(None)(self._pair)

    def eps(self, x, y):
        z = sum(a * b for a, b in zip(x, y))
        z += sum(self.a[i][j] * x[i] * y[j]
                 for i in range(self.n) for j in range(i))
        return -1 if z % 2 else 1

    def _pair(self, i, j):
        nr = self.nr
        if i >= nr and j >= nr:
            return {}
        if i >= nr:
            c = sum(x * y for x, y in zip(self.a[i - nr], self.roots[j]))
            return {j: c} if c else {}
        if j >= nr:
            return {p: -x for p, x in self.pair(j, i).items()}
        a, b = self.roots[i], self.roots[j]
        t = add(a, b)
        e = self.eps(a, b)
        if t in self.ids:
            return {self.ids[t]: e}
        if not any(t):
            return {nr + k: e * x for k, x in enumerate(a) if x}
        return {}

    def comm(self, a, b):
        c = {}
        for i, x in a.items():
            for j, y in b.items():
                for p, z in self.pair(i, j).items():
                    c[p] = c.get(p, 0) + x * y * z
        return {p: x for p, x in c.items() if x}

    def unit(self, root):
        return {self.ids[root]: 1}

    def automorphism(self, perm):
        if sorted(perm) != list(range(self.n)):
            raise ValueError('not a permutation')
        if any(self.a[perm[i]][perm[j]] != self.a[i][j]
               for i in range(self.n) for j in range(self.n)):
            raise ValueError('not a diagram automorphism')
        def act(a):
            b = [0] * self.n
            for i, x in enumerate(a):
                b[perm[i]] = x
            return tuple(b)
        signs = {a: 1 for a in self.simple}
        for a in sorted((x for x in self.roots if min(x) >= 0), key=sum):
            if sum(a) == 1:
                continue
            for b in self.simple:
                c = add(a, neg(b))
                if c in signs:
                    signs[a] = signs[c] * self.eps(act(c), act(b)) * self.eps(c, b)
                    break
            else:
                raise AssertionError('no positive root predecessor')
        signs.update({neg(a): x for a, x in list(signs.items())})
        image = {i: (self.ids[act(a)], signs[a]) for i, a in enumerate(self.roots)}
        image.update({self.nr + i: (self.nr + perm[i], 1) for i in range(self.n)})
        def sigma(a):
            c = {}
            for i, x in a.items():
                j, s = image[i]
                c[j] = c.get(j, 0) + s * x
            return {p: x for p, x in c.items() if x}
        # check every structure constant, not only generators.
        for i in range(self.dim):
            for j in range(self.dim):
                x, y = image[i], image[j]
                lhs = sigma(self.pair(i, j))
                rhs = {p: x[1] * y[1] * t for p, t in self.pair(x[0], y[0]).items()}
                if lhs != rhs:
                    raise AssertionError(('automorphism', i, j))
        return sigma

    def adjoint(self, v):
        out = {}
        for j in range(self.dim):
            for i, x in self.comm(v, {j: 1}).items():
                out[i, j] = x
        return out


def untwisted(kind, n):
    g = ADE(kind, n)
    gens = {i + 1: g.unit(a) for i, a in enumerate(g.simple)}
    gens[0] = g.unit(neg(g.top))
    return g, gens, (1,) + g.top


def fold(name, n=0):
    if name in ('G2', 'D4tw'):
        g = ADE('D', 4)
        perm = (2, 1, 3, 0)
        orbits = [(0, 2, 3), (1,)]
        order = 3
    elif name in ('F4', 'E6tw'):
        g = ADE('E', 6)
        perm = (5, 1, 4, 3, 2, 0)
        orbits = [(0, 5), (2, 4), (3,), (1,)]
        order = 2
    elif name == 'Dtw':
        if n < 3:
            raise ValueError('use n >= 3')
        g = ADE('D', n + 1)
        perm = tuple(range(n - 1)) + (n, n - 1)
        orbits = [(i,) for i in range(n - 1)] + [(n - 1, n)]
        order = 2
    else:
        raise ValueError('unknown fold')
    sigma = g.automorphism(perm)
    gens = {i + 1: {g.ids[g.simple[j]]: 1 for j in orbit}
            for i, orbit in enumerate(orbits)}
    if name in ('G2', 'F4'):
        root = g.top
        zero = g.unit(neg(root))
        assert sigma(zero) == zero
        gens[0] = zero
    elif order == 2:
        for root in sorted((a for a in g.roots if min(a) >= 0), key=sum, reverse=True):
            v = g.unit(neg(root))
            zero = plus(v, sigma(v), -1)
            if zero:
                break
        assert sigma(zero) == {p: -x for p, x in zero.items()}
        gens[0] = zero
    else:
        # multiplication by zeta on q[zeta], where zeta^2 + zeta + 1 = 0.
        mats = ({(0, 0): 1, (1, 1): 1},
                {(0, 1): -1, (1, 0): 1, (1, 1): -1},
                {(0, 0): -1, (0, 1): 1, (1, 0): -1})
        for root in sorted((a for a in g.roots if min(a) >= 0), key=sum, reverse=True):
            v = g.unit(neg(root))
            parts = [v, sigma(v), sigma(sigma(v))]
            # coefficients are 1, zeta^2, zeta.
            coeffs = [(1, 0), (-1, -1), (0, 1)]
            aa, bb = {}, {}
            for part, (x, y) in zip(parts, coeffs):
                aa = plus(aa, part, x)
                bb = plus(bb, part, y)
            if aa or bb:
                break
        def lift(v, power):
            out = {}
            for (i, j), x in g.adjoint(v).items():
                for (a, b), y in mats[power].items():
                    out[2 * i + a, 2 * j + b] = x * y
            return out
        gens = {i: lift(v, 0) for i, v in gens.items()}
        gens[0] = plus(lift(aa, 0), lift(bb, 1))
        delta = (1,) + tuple(sum(root[j] for j in orbit) for orbit in orbits)
        return g, gens, delta
    delta = (1,) + tuple(sum(root[j] for j in orbit) for orbit in orbits)
    return g, gens, delta
