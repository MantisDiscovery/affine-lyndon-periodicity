"""finite checks of the exchange inequality and the proposed bracket."""

from functools import lru_cache
from itertools import permutations
from pathlib import Path
import argparse
import json

from exact_lyndon import bracket, insert_basis
from grid_probe import grid
from parent_probe import projection, deg

if not __debug__:
    raise RuntimeError('run without -O')


def run(limit: int = 6) -> dict:
    if limit < 2:
        raise ValueError('max-rank must be at least 2')
    rows = []
    for n in range(2, limit + 1):
        row = dict(n=n, orders=0, exchange_implications=0,
                   target_brackets=0, bracket_cases={})
        for order in permutations(range(n + 1)):
            r = order[0]
            if r in (0, n):
                continue
            d, cs, key = grid(n, r, order)
            for w, U, V, (u, v), (p, q) in cs[1:]:
                assert key(U) < key(V[:-1])
                a = V[-1]
                if a < r:
                    assert d[p - 1, q] == V[:-1]
                    Q = d[u + 1, v]
                    pairs = ((d[p - 1, t], d[p, t])
                             for t in range(2 * (n - r)))
                else:
                    assert d[p, q - 1] == V[:-1]
                    Q = d[u, v + 1]
                    pairs = ((d[t, q - 1], d[t, q]) for t in range(2 * r))
                for first, last in pairs:
                    if key(first) <= key(U):
                        assert key(last) <= key(Q), (n, order, w, first, last)
                        row['exchange_implications'] += 1
            gens = {0: {(n, 0): 1}, n: {(n - 1, 2 * n - 1): 1}}
            for a in range(1, n):
                gens[a] = {(a - 1, a): 1, (n + a, n + a - 1): -1}

            @lru_cache(None)
            def lyndon(w):
                return bool(w) and all(key(w) < key(w[j:])
                                       for j in range(1, len(w)))

            @lru_cache(None)
            def b(w):
                if len(w) == 1:
                    return gens[w[0]]
                j = next(j for j in range(1, len(w)) if lyndon(w[j:]))
                return bracket(b(w[:j]), b(w[j:]))

            chosen = []
            basis = []
            for item in cs:
                if insert_basis(projection(deg(item[1], n)), basis):
                    chosen.append(item)
            assert len(chosen) == n
            index = {item[0]: i for i, item in enumerate(chosen)}
            prior = []
            for i, (w, U, V, (u, v), (p, q)) in enumerate(chosen):
                base = tuple(b(w).get((j, j), 0) for j in range(n))
                assert any(base)
                if i:
                    P, a = V[:-1], V[-1]
                    Q = d[u + 1, v] if a < r else d[u, v + 1]
                    Z = U + P + Q + V
                    assert lyndon(Z) and lyndon(Z[:-1])
                    value = b(Z)
                    assert value and all(j == k for j, k in value)
                    vec = tuple(value.get((j, j), 0) for j in range(n))
                    assert insert_basis(vec, list(prior))
                    basis = list(prior)
                    assert insert_basis(base, basis)
                    assert not insert_basis(vec, basis)
                    parent = Q + P if key(Q) < key(P) else P + Q
                    assert index[parent] < i
                    if key(Q) < key(P):
                        case = 'Q<P'
                    elif key(Q) < key(V):
                        case = 'P<Q<V'
                    else:
                        case = 'P<V<Q'
                    row['bracket_cases'][case] = row['bracket_cases'].get(case, 0) + 1
                    row['target_brackets'] += 1
                assert insert_basis(base, prior)
            b.cache_clear()
            lyndon.cache_clear()
            row['orders'] += 1
        rows.append(row)
    result = dict(scope='Finite exact checks; not the all-rank proof', ranks=rows)
    out = Path('outputs')
    out.mkdir(exist_ok=True)
    (out / 'periodicity_proof_checks.json').write_text(
        json.dumps(result, indent=2), encoding='utf-8')
    print('ok')
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--max-rank', type=int, default=6)
    run(p.parse_args().max_rank)
