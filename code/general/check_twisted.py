"""finite checks of divisibility-stratified insertion formulas."""

import argparse
import itertools
import json
import time
from twisted_words import Words, model, scale


def rotation(a, b):
    return len(a) == len(b) and any(a == b[j:] + b[:j] for j in range(len(b)))


def fit(c, K, stride):
    if stride < 1 or K < 2 * stride:
        raise ValueError('require at least two degrees for each stride')
    rows = {k: c.words[scale(c.delta, k)] for k in range(1, K + 1)}
    families = []
    for q in sorted(set((1, stride))):
        old = {f['l'] + f['w'] * (q // f['q'] - 1) + f['r']
               for f in families if q % f['q'] == 0}
        for base in rows[q]:
            if base in old:
                continue
            l = c.lcp(base)
            r = base[len(l):]
            found = []
            for nxt in rows[2 * q]:
                if not nxt[:len(l)] == l or not nxt[-len(r):] == r:
                    continue
                w = nxt[len(l):-len(r)]
                if len(w) != q * sum(c.delta):
                    continue
                if all(l + w * (k // q - 1) + r in rows[k]
                       and c.lcp(l + w * (k // q - 1) + r) == l + w * (k // q - 1)
                       for k in range(q, K + 1, q)):
                    found.append(w)
            if len(found) != 1:
                raise AssertionError(('fit', c.order, q, base, found))
            parents = [j + 1 for j, w in enumerate(rows[q]) if rotation(found[0], w)]
            if len(parents) != 1 or parents[0] > rows[q].index(base) + 1:
                raise AssertionError(('parent', c.order, q, base, parents))
            families.append({'q': q, 'l': l, 'w': found[0], 'r': r,
                             'parents': parents})
    for k in rows:
        got = [f['l'] + f['w'] * (k // f['q'] - 1) + f['r']
               for f in families if k % f['q'] == 0]
        if sorted(got, key=c.key, reverse=True) != rows[k]:
            raise AssertionError(('coverage', c.order, k))
    return families


def run(nmax, K):
    out = []
    for name in ('Aeven', 'Aodd'):
        for n in range(1 if name == 'Aeven' else 2, nmax + 1):
            g, d = model(name, n)
            start = time.time()
            count = 0
            for order in itertools.permutations(range(n + 1)):
                c = Words(g, d, order, K)
                fs = fit(c, K, 1 if name == 'Aeven' else 2)
                out.append({'type': name, 'n': n, 'order': order, 'K': K,
                            'families': fs, 'root_spaces': len(c.spaces)})
                count += 1
            print(name, n, count, round(time.time() - start, 2), flush=True)
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('-n', type=int, default=3)
    p.add_argument('-k', type=int, default=6)
    p.add_argument('--out', default='twisted_checks.json')
    a = p.parse_args()
    out = run(a.n, a.k)
    with open(a.out, 'w') as f:
        json.dump(out, f, indent=2)
