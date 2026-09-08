"""the two-arm grid."""


def grid(n: int, r: int, order):
    if n < 2 or not 1 <= r < n:
        raise ValueError('require n >= 2 and an internal r')
    order = tuple(order)
    if sorted(order) != list(range(n + 1)) or order[0] != r:
        raise ValueError('order must permute 0 through n with r first')
    rank = {x: i for i, x in enumerate(order)}
    a = tuple(range(r - 1, -1, -1)) + tuple(range(1, r))
    b = tuple(range(r + 1, n + 1)) + tuple(range(n - 1, r, -1))

    def key(w):
        return tuple(rank[x] for x in w)

    d = {}
    for p in range(len(a) + 1):
        for q in range(len(b) + 1):
            cs = []
            if p:
                cs.append(d[p - 1, q] + (a[p - 1],))
            if q:
                cs.append(d[p, q - 1] + (b[q - 1],))
            d[p, q] = max(cs, key=key) if cs else (r,)
    cs = []
    for (p, q), u in d.items():
        z = (len(a) - p, len(b) - q)
        v = d[z]
        if key(u) < key(v):
            cs.append((u + v, u, v, (p, q), z))
    cs.sort(key=lambda x: key(x[0]), reverse=True)
    return d, cs, key
