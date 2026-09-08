"""greedy real appends before the imaginary period."""

from exact_lyndon import CWords, add, sub, insert_basis


def chain_data(c):
    n = c.n
    iw = c.words[c.delta]
    iv = [tuple(c.b(w).get((i, i), 0) for i in range(n)) for w in iw]

    def dot(x, y):
        return sum(a * b for a, b in zip(x, y))

    def m(p):
        basis = []
        for i, v in enumerate(iv, 1):
            insert_basis(v, basis)
            if not insert_basis(p, list(basis)):
                return i
        raise AssertionError('missing flag layer')

    def M(p):
        return next(i for i, v in enumerate(iv, 1) if dot(p, v))

    short = [d for d in c.degs if sum(d) < sum(c.delta)]
    lifts = {c.projection(d): d for d in short}
    inc = {p for p, d in lifts.items()
           if c.key(c.words[d][0]) < c.key(iw[M(p) - 1])}
    simple = {p for p in inc if not any(sub(p, q) in inc for q in inc)}
    beta = {m(p): p for p in simple}
    out = []
    for i, w in enumerate(iw, 1):
        l = c.lcp(w)
        u = l
        app = []
        for _ in range(2 * n + 1):
            p = c.projection(c.deg(u))
            cs = []
            for q, d in lifts.items():
                z = add(p, q)
                if q not in inc and z in inc and m(z) == i:
                    cs.append((c.words[d][0], True))
            cs.extend((z, False) for z, v in zip(iw, iv) if dot(p, v))
            v, real = max(cs, key=lambda x: c.key(x[0]))
            if not real:
                break
            u += v
            app.append(v)
            d = c.deg(u)
            if d in c.words:
                assert c.words[d] == [u]
        else:
            raise AssertionError('termination')
        out.append(dict(i=i, word=w, L=l, beta=beta[i], j=M(beta[i]),
                        y=u, appends=app))
    return out


if __name__ == '__main__':
    import argparse
    import json

    p = argparse.ArgumentParser()
    p.add_argument('n', type=int)
    p.add_argument('order')
    a = p.parse_args()
    c = CWords(a.n, tuple(map(int, a.order.split(','))))
    print(json.dumps(chain_data(c)))
