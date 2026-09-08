"""exact checks separate from the all-rank proofs."""

import argparse
import json
from fractions import Fraction
from itertools import permutations
from pathlib import Path

from classical_words import arms, block, independent, projection, table
from exact_classical import Words, add, sub, mul, insert_basis


def det(rows):
    a = [list(map(Fraction, row)) for row in rows]
    out = Fraction(1)
    for i in range(len(a)):
        j = next(j for j in range(i, len(a)) if a[j][i])
        if i != j:
            a[i], a[j] = a[j], a[i]
            out = -out
        v = a[i][i]
        out *= v
        for j in range(i + 1, len(a)):
            q = a[j][i] / v
            a[j] = [x - q * y for x, y in zip(a[j], a[i])]
    return out


def check(kind, n, order, depth=0):
    c = Words(kind, n, order, max(1, depth), bool(depth))
    bs, pairs, chosen = c.pairs()
    rows = table(kind, n, order)
    assert [row.word() for row in rows] == [x[0] for x in chosen]
    left, right = arms(kind, n, order[0])
    words = {block(left, right, p, q, order[0], c.rank)
             for p in range(left.last + 1) for q in range(right.last + 1)}
    assert words == set(bs.values())
    r = order[0]
    ends = {0, n} if kind == 'C' else {0, 1} if kind == 'B' else {0, 1, n - 1, n}
    a = b = 0
    while True:
        opts = [(x, y, b) for x, y in left.edges(a)]
        if kind != 'B' or b < n - r:
            opts += [(x, a, y) for x, y in right.edges(b)]
        x, a, b = max(opts, key=lambda v: c.rank[v[0]])
        if x in ends:
            break
    v = block(left, right, a, b, r, c.rank)
    u = block(left, right, left.last - a, right.last - b, r, c.rank)
    assert (u, v) == chosen[0][1:3]
    exc = [z for z in pairs if c.key(z[2][:-1]) <= c.key(z[1])]
    assert exc == pairs[:1]
    tests = 0
    for w, u, v, d in pairs[1:]:
        p, a = v[:-1], v[-1]
        q = bs[sub(c.delta, c.deg(p))]
        for dr, wr in bs.items():
            ds = add(dr, c.simple[a])
            if ds in bs and c.key(wr) <= c.key(u):
                assert c.key(bs[ds]) <= c.key(q)
                tests += 1
    basis, cols, sparse, betas = [], [], [], []
    for i, ((w, u, v, d), row) in enumerate(zip(chosen, rows)):
        b = c.b(w)
        vec = tuple(b.get((j, j), 0) for j in range(n))
        col = projection(kind, n, u)
        cv = tuple(dict(col).get(j, 0) for j in range(n))
        assert independent(col, sparse, n)
        assert insert_basis(cv, list(basis))
        cols.append(cv)
        sparse.append(col)
        if i:
            assert c.lcp(w) == row.left
            z = row.word(2)
            assert c.lyndon(z) and c.lyndon(z[:-1])
            val = c.b(z)
            assert all(a == b for a, b in val)
            vv = tuple(val.get((j, j), 0) for j in range(n))
            assert insert_basis(vv, list(basis))
            span = list(basis)
            assert insert_basis(vec, span)
            assert not insert_basis(vv, span)
            p = v[:-1]
            q = bs[sub(c.delta, c.deg(p))]
            par = min((p + q, q + p), key=c.key)
            assert rows[row.parent - 1].word() == par and row.parent <= i
        beta_word = u
        if i and c.key(q) < c.key(p):
            beta_word = row.left
        betas.append(c.projection(c.deg(beta_word)))
        assert insert_basis(vec, basis)
        for k in range(1, max(3, depth) + 1):
            out = row.word(k)
            assert c.deg(out) == mul(c.delta, k)
            assert tuple(row.letter(k, j) for j in range(len(out))) == out
            if depth and k <= depth:
                assert c.words[mul(c.delta, k)][i] == out
                assert c.lcp(out) == row.left + row.period * (k - 1)
    edges = set()
    for i in range(n):
        for j in range(i):
            dot = sum(x * y for x, y in zip(betas[i], betas[j]))
            assert dot <= 0
            if dot:
                edges.add((i + 1, j + 1))
    assert edges == {(i, row.parent) for i, row in enumerate(rows, 1) if i > 1}
    val = [sum(i in edge for edge in edges) for i in range(1, n + 1)]
    assert sorted(val) == ([1, 1] + [2] * (n - 2) if kind != 'D' else
                           [1, 1, 1] + [2] * (n - 4) + [3])
    assert abs(det(cols)) == (1 if kind == 'B' else 2)
    if depth:
        assert c.words[c.delta] == [x[0] for x in chosen]
    c.b.cache_clear()
    c.lyndon.cache_clear()
    return tests


def orders(kind, n):
    first = range(1, n) if kind == 'C' else range(2, n + 1) if kind == 'B' else range(2, n - 1)
    for r in first:
        for tail in permutations(a for a in range(n + 1) if a != r):
            yield (r,) + tail


def run(kinds, limit, depth):
    out = []
    for kind in kinds:
        for n in range(4 if kind == 'D' else 2, limit + 1):
            count = tests = 0
            for order in orders(kind, n):
                tests += check(kind, n, order, depth)
                count += 1
            row = dict(type=kind, rank=n, orders=count, raising=tests, depth=depth)
            out.append(row)
            print(kind, n, count, 'passed', flush=True)
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--types', default='BCD')
    p.add_argument('--rank', type=int, default=4)
    p.add_argument('--depth', type=int, default=2)
    p.add_argument('--output', default='checks.json')
    a = p.parse_args()
    if any(t not in 'BCD' for t in a.types) or a.rank < 2 or a.depth < 0:
        p.error('use types BCD, rank at least two, and nonnegative depth')
    Path(a.output).write_text(json.dumps(run(a.types, a.rank, a.depth), indent=2) + '\n')
