"""independent root and multiplicity checks for the exact loop models."""

import argparse
import json
from fractions import Fraction
from twisted_words import Words, model, bracket, scale
from root_model import ADE, fold, untwisted, plus


def affine(a, lengths, marks):
    n = len(a)
    b = [[Fraction(lengths[i]) * a[i][j] for j in range(n)] for i in range(n)]
    z = list(marks[1:])
    g = [[Fraction(0) for j in range(n + 1)] for i in range(n + 1)]
    for i in range(n):
        for j in range(n):
            g[i + 1][j + 1] = b[i][j]
        g[0][i + 1] = g[i + 1][0] = -sum(z[j] * b[j][i] for j in range(n))
    g[0][0] = sum(z[i] * z[j] * b[i][j] for i in range(n) for j in range(n))
    out = [[2 * x / g[i][i] for x in row] for i, row in enumerate(g)]
    assert all(x.denominator == 1 for row in out for x in row)
    return [[int(x) for x in row] for row in out]


def cartan(name, n, marks):
    if name == 'E':
        return affine(ADE('E', n).a, [1] * n, marks)
    if name in ('E6tw', 'F4'):
        return affine([[2, -1, 0, 0], [-1, 2, -2, 0],
                       [0, -1, 2, -1], [0, 0, -1, 2]], [1, 1, 2, 2], marks)
    if name in ('D4tw', 'G2'):
        return affine([[2, -3], [-1, 2]], [1, 3], marks)
    c = [[0] * n for _ in range(n)]
    for i in range(n):
        c[i][i] = 2
        if i:
            c[i][i - 1] = c[i - 1][i] = -1
    lengths = [1] * n
    if name == 'Aodd':
        c[n - 2][n - 1] = -2
        lengths[-1] = 2
    elif n > 1:
        c[n - 1][n - 2] = -2
        lengths = [2] * (n - 1) + [1]
    return affine(c, lengths, marks)


def real_roots(a, cap):
    n = len(a)
    out = {tuple(int(i == j) for j in range(n)) for i in range(n)}
    todo = list(out)
    while todo:
        d = todo.pop()
        for i in range(n):
            z = list(d)
            z[i] -= sum(x * y for x, y in zip(a[i], d))
            t = tuple(z)
            if any(x < 0 or x > y for x, y in zip(t, cap)):
                continue
            if t not in out:
                out.add(t)
                todo.append(t)
    return out


def setup(name, n):
    if name in ('Aeven', 'Aodd'):
        e, d = model(name, n)
        return e, d, bracket
    if name == 'E':
        g, e, d = untwisted(name, n)
    else:
        g, e, d = fold(name, n)
    return e, d, bracket if name == 'D4tw' else g.comm


def multiplicity(name, n, k):
    if name == 'Aeven':
        return n
    if name == 'Aodd':
        return n - 1 + int(k % 2 == 0)
    if name == 'Dtw':
        return 1 + (n - 1) * int(k % 2 == 0)
    if name == 'E6tw':
        return 2 + 2 * int(k % 2 == 0)
    if name == 'D4tw':
        return 1 + int(k % 3 == 0)
    return n


def audit(name, n, K):
    e, d, comm = setup(name, n)
    a = cartan(name, n, d)
    assert all(sum(x * y for x, y in zip(row, d)) == 0 for row in a)
    for i in e:
        for j in e:
            if i == j:
                continue
            v = e[j]
            for k in range(-a[i][j]):
                v = comm(e[i], v)
                assert v, (name, i, j, k)
            assert not comm(e[i], v), (name, i, j, 'serre')
    c = Words(e, d, tuple(range(len(d))), K, comm=comm)
    roots = real_roots(a, scale(d, K))
    expected = {x: 1 for x in roots}
    for k in range(1, K + 1):
        expected[scale(d, k)] = multiplicity(name, n, k)
    actual = {x: len(b) for x, b in c.spaces.items()}
    assert actual == expected, (name, 'root dimensions',
                               set(actual) ^ set(expected),
                               [(x, y, actual.get(x)) for x, y in expected.items()
                                if actual.get(x) != y])
    return {'type': name, 'n': n, 'K': K, 'delta': d, 'cartan': a,
            'positive_real_roots_in_box': len(roots),
            'total_homogeneous_spaces': len(actual),
            'serre_and_root_dimensions': 'passed'}


def jacobi_D4():
    g = ADE('D', 4)
    count = 0
    for i in range(g.dim):
        for j in range(g.dim):
            for k in range(g.dim):
                z = g.comm({i: 1}, g.pair(j, k))
                z = plus(z, g.comm({j: 1}, g.pair(k, i)))
                z = plus(z, g.comm({k: 1}, g.pair(i, j)))
                assert not z, ('jacobi', i, j, k)
                count += 1
    return {'algebra': 'D4', 'basis_triples': count, 'jacobi': 'passed'}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--type')
    p.add_argument('-n', type=int, default=2)
    p.add_argument('-k', type=int, default=6)
    p.add_argument('--out', default='model_audit.json')
    args = p.parse_args()
    if args.type:
        rows = [audit(args.type, args.n, args.k)]
    else:
        cases = [('Aeven', n, 6) for n in (1, 2, 3)]
        cases += [('Aodd', n, 6) for n in (2, 3)]
        cases += [('Dtw', 3, 6), ('E6tw', 4, 6), ('D4tw', 2, 9)]
        cases += [('G2', 2, 3), ('F4', 4, 3), ('E', 6, 3), ('E', 7, 3)]
        rows = []
        for name, n, K in cases:
            row = audit(name, n, K)
            rows.append(row)
            print(name, n, row['total_homogeneous_spaces'], flush=True)
        rows.append(jacobi_D4())
    with open(args.out, 'w') as f:
        json.dump(rows, f, indent=2)
