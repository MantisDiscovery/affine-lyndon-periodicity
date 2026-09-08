"""rectangle switches on zero-weight multisets."""

import json
from itertools import combinations_with_replacement
from pathlib import Path


def matching(vals):
    pending = {}
    out = [-1] * len(vals)
    for i, x in enumerate(vals):
        if pending.get(-x):
            j = pending[-x].pop()
            out[i], out[j] = j, i
        else:
            pending.setdefault(x, []).append(i)
    if any(pending.values()):
        raise ValueError('coordinate weights do not sum to zero')
    return out


def components(left, right):
    seen = set()
    count = 0
    for i in range(len(left)):
        if i in seen:
            continue
        count += 1
        stack = [i]
        while stack:
            j = stack.pop()
            if j not in seen:
                seen.add(j)
                stack.extend([left[j], right[j]])
    return count


def pair(weights):
    w = list(weights)
    left = matching([a for a, b in w])
    right = matching([b for a, b in w])
    c = components(left, right)
    moves = []
    for i, j in enumerate(left):
        if i > j or right[i] == j:
            continue
        a, b = right[i], right[j]
        w[j], w[a] = (w[j][0], w[a][1]), (w[a][0], w[j][1])
        right[i], right[j] = j, i
        right[a], right[b] = b, a
        moves.append((j, a))
    assert left == right
    assert len(moves) == len(w) // 2 - c
    assert all(w[j] == (-w[i][0], -w[i][1]) for i, j in enumerate(left))
    return w, moves


def check(kind, r, s, k):
    left = [x for a in range(1, r + 1) for x in (a, -a)]
    right = [x for b in range(1, s + 1) for x in (b, -b)]
    if kind == 'B':
        right.append(0)
    weights = [(a, b) for a in left for b in right]
    count = 0
    for w in combinations_with_replacement(weights, 2 * k):
        try:
            matching([a for a, b in w])
            matching([b for a, b in w])
        except ValueError:
            continue
        out, moves = pair(w)
        assert len(moves) <= k - 1
        count += 1
    return dict(type=kind, r=r, s=s, k=k, multisets=count)


if __name__ == '__main__':
    rows = [check(kind, 2, 2, k) for kind in 'BD' for k in (1, 2)]
    rows += [check('B', 2, 0, k) for k in (1, 2, 3)]
    Path('switch_checks.json').write_text(json.dumps(rows, indent=2) + '\n')
    print(sum(row['multisets'] for row in rows), 'passed')
