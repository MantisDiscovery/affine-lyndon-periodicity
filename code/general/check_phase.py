"""compare insertion phases with the independent greedy preperiod."""

import argparse
import itertools
import json
from pathlib import Path
from twisted_words import Words, add, sub, scale, insert
from root_model import fold, untwisted


def canonical(c, w):
    if not w:
        return []
    j = min(range(len(w)), key=lambda j: c.key(w[j:]))
    return canonical(c, w[:j]) + [w[j:]]


def projection(c, d):
    return tuple(x - d[0] * y for x, y in zip(d[1:], c.delta[1:]))


def chain_data(c):
    basis, flags = {}, []
    for w in c.words[c.delta]:
        assert insert(c.b(w), basis)
        flags.append(dict(basis))
    info = {}
    for d in c.degs:
        if sum(d) >= sum(c.delta):
            continue
        opp = sub(c.delta, d)
        if opp not in c.words or add(d, c.delta) not in c.words:
            continue
        w, v = c.words[d][0], c.words[opp][0]
        h = c.comm(c.b(w), c.b(v))
        assert h
        i = next(i + 1 for i, f in enumerate(flags) if not insert(h, dict(f)))
        inc = c.key(w) < c.key(c.words[add(d, c.delta)][0])
        g = projection(c, d)
        assert g not in info
        info[g] = {'degree': d, 'word': w, 'i': i, 'inc': inc}
    return info


def greedy(c, l, i, info):
    dec = [v['word'] for v in info.values() if not v['inc']]
    seeds = c.words[c.delta]
    u, parts = l, []
    for _ in range(sum(c.delta)):
        opts = []
        for v in dec + seeds:
            d = add(c.deg(u), c.deg(v))
            s = info.get(projection(c, d))
            if s and s['inc'] and s['i'] == i and c.comm(c.b(u), c.b(v)):
                opts.append(v)
        v = max(opts, key=c.key)
        if c.deg(v) == c.delta:
            return u, parts, v
        u += v
        assert c.words[c.deg(u)] == [u]
        parts.append(v)
    raise AssertionError('preperiod did not terminate')


def audit(c):
    rows = []
    info = chain_data(c)
    bases = c.words[c.delta]
    for i, base in enumerate(bases, 1):
        l = c.lcp(base)
        r = base[len(l):]
        w2 = c.words[scale(c.delta, 2)][i - 1]
        assert w2[:len(l)] == l and w2[-len(r):] == r
        w = w2[len(l):-len(r)]
        assert c.words[scale(c.delta, 3)][i - 1] == l + w * 2 + r
        parents = [(j + 1, b, cut) for j, b in enumerate(bases)
                   for cut in range(len(b))
                   if b[cut:] + b[:cut] == w]
        assert len(parents) == 1
        j, b, cut = parents[0]
        tail = b[cut:] if cut else ()
        y = l + tail
        vs = canonical(c, tail)
        yy, vv, bb = greedy(c, l, i, info)
        assert (yy, vv, bb) == (y, vs, b), (i, yy, y, vv, vs)
        assert len(y) <= 2 * sum(c.delta) - 2
        for v in vs:
            assert c.words[c.deg(v)] == [v]
        assert (i == 1 and j == 1) or j < i
        rows.append({'i': i, 'parent': j, 'L': l, 'R': r, 'W': w,
                     'C': tail, 'Y': y, 'appends': vs,
                     'independent_greedy_match': True})
    return rows


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--type', default='F4', choices=['G2', 'F4', 'E'])
    p.add_argument('-n', type=int, default=4)
    p.add_argument('--order')
    p.add_argument('--limit', type=int, default=0)
    p.add_argument('--out', default='phase_checks.json')
    a = p.parse_args()
    g, e, d = untwisted('E', a.n) if a.type == 'E' else fold(a.type)
    orders = [tuple(map(int, a.order.split(',')))] if a.order else itertools.permutations(range(len(d)))
    path = Path(a.out)
    out = json.loads(path.read_text()) if path.exists() else []
    if any(x['type'] != a.type or tuple(x['delta']) != tuple(d) for x in out):
        raise ValueError('existing output belongs to another root datum')
    seen = {tuple(x['order']) for x in out}
    for z, order in enumerate(orders):
        if a.limit and z >= a.limit:
            break
        if order in seen:
            continue
        c = Words(e, d, order, 3, comm=g.comm)
        rows = audit(c)
        out.append({'type': a.type, 'n': len(d) - 1, 'delta': d,
                    'order': order, 'K': 3, 'rows': rows})
        path.write_text(json.dumps(out, indent=2))
        if z % 10 == 0:
            print(z, order, max(len(x['appends']) for x in rows), flush=True)
    with open(a.out, 'w') as f:
        json.dump(out, f, indent=2)
