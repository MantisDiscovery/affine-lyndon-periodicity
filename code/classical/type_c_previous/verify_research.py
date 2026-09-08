"""exact finite checks of the grid, chains, and rectangle switches."""

if not __debug__:
    raise RuntimeError('run without -O')

from exact_lyndon import CWords, add, sub, mul, insert_basis
from grid_probe import grid
from parent_probe import selected
from chain_probe import chain_data
from itertools import permutations, combinations_with_replacement, product
from collections import Counter
from pathlib import Path
import json
import argparse


def multiwords(counts):
    if not any(counts):
        yield ()
        return
    for i, c in enumerate(counts):
        if c:
            z = list(counts)
            z[i] -= 1
            for tail in multiwords(tuple(z)):
                yield (i,) + tail


def greedy_all(c, d):
    ws = [w for w in multiwords(d) if c.lyndon(w)]
    basis = []
    out = []
    for w in sorted(ws, key=c.key, reverse=True):
        b = c.b(w)
        if insert_basis(tuple(b.get((i, i), 0) for i in range(c.n)), basis):
            out.append(w)
    return out, len(ws)


def matching(values):
    pos = {}
    neg = {}
    for i, x in enumerate(values):
        (pos if x > 0 else neg).setdefault(abs(x), []).append(i)
    out = {}
    for a, ps in pos.items():
        ns = neg[a]
        assert len(ps) == len(ns)
        for i, j in zip(ps, ns):
            out[i] = j
            out[j] = i
    assert len(out) == len(values)
    return out


def collapse(config):
    xy = list(config)
    L = matching([x for x, y in xy])
    R = matching([y for x, y in xy])
    moves = []

    def parts():
        seen = set()
        count = 0
        for i in L:
            if i in seen:
                continue
            count += 1
            stack = [i]
            while stack:
                z = stack.pop()
                if z in seen:
                    continue
                seen.add(z)
                stack.extend([L[z], R[z]])
        return count
    initial = parts()
    while L != R:
        i = next((i for i in L if L[i] != R[i]))
        j = L[i]
        k = R[i]
        l = R[j]
        xj, yj = xy[j]
        xk, yk = xy[k]
        xy[j] = (xj, yk)
        xy[k] = (xk, yj)
        R[i] = j
        R[j] = i
        R[k] = l
        R[l] = k
        moves.append((j, k))
    assert len(moves) == len(config) // 2 - initial
    assert all((xy[L[i]] == (-xy[i][0], -xy[i][1]) for i in L))
    return xy, moves, initial


def run(limit: int = 5) -> dict:
    if limit < 2:
        raise ValueError('max-rank must be at least 2')
    result = {'scope': 'Exact finite checks, separate from proofs', 'ranks': [], 'counterexample': None}
    for n in range(2, limit + 1):
        count = blocks = ncs = total = 0
        branches = Counter()
        for order in permutations(range(n + 1)):
            r = order[0]
            if r in (0, n):
                continue
            c = CWords(n, order, 2)
            d, cs, key = grid(n, r, order)
            for pq, w in d.items():
                assert c.words[c.deg(w)] == [w]
            assert [i for i, x in enumerate(cs) if key(x[2][:-1]) <= key(x[1])] == [0]
            gd, gs, gkey = selected(n, order)
            assert [x[0] for x in gs] == c.words[c.delta]
            cd = chain_data(c)
            for item in cd:
                i = item['i']
                w = item['word']
                L = item['L']
                if i == 1:
                    continue
                U = w[:w.index(r, 1)]
                P = L[len(U):]
                assert w[:-1] == L
                Q = c.words[sub(c.delta, c.deg(P))][0]
                par = P + Q if key(P) < key(Q) else Q + P
                j = c.words[c.delta].index(par) + 1
                assert j < i and item['j'] == j
                want = L + Q if key(P) < key(Q) else L
                assert item['y'] == want
                branches['P<Q' if key(P) < key(Q) else 'Q<P'] += 1
                w2 = c.words[mul(c.delta, 2)][i - 1]
                assert w2 == L + Q + P + w[-1:] and c.lcp(w2) == L + Q + P
            if n <= 3:
                got, num = greedy_all(c, c.delta)
                assert got == c.words[c.delta]
                total += num
            if n == 2:
                got, num = greedy_all(c, mul(c.delta, 2))
                assert got == c.words[mul(c.delta, 2)]
                total += num
            if n == 2 and order == (1, 0, 2):
                result['counterexample'] = cd[1]
            count += 1
            blocks += len(d)
            ncs += len(cs)
        row = dict(n=n, internal_orders=count, real_grid_words=blocks,
                   delta_candidates=ncs, direct_lyndon_evaluations=total,
                   corrected_parent_cases=dict(branches))
        result['ranks'].append(row)
    count_conf = 0
    omega = list(product((1, -1, 2, -2), repeat=2))
    for k in range(1, 4):
        for conf in combinations_with_replacement(omega, 2 * k):
            cx = Counter((x for x, y in conf))
            cy = Counter((y for x, y in conf))
            if any((cx[i] != cx[-i] or cy[i] != cy[-i] for i in (1, 2))):
                continue
            end, moves, cycles = collapse(conf)
            assert len(moves) <= k - 1
            count_conf += 1
    result['quadratic_zero_configurations_r2_s2_k1to3'] = count_conf
    Path('outputs').mkdir(exist_ok=True)
    Path('outputs/certificates.json').write_text(
        json.dumps(result, indent=2), encoding='utf-8')
    print('ok')
    return result

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--max-rank', type=int, default=5)
    a = p.parse_args()
    run(a.max_rank)
