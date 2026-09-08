# Supplementary calculations

Use Python 3.10 or later. No additional packages are needed. Run from this directory without `-O`.

To print the four D4 words of degree 2 delta:

```sh
python classical_words.py D 4 2,0,1,3,4 2
```

`table(kind, n, order)` returns the factors and parent index for each imaginary word. An entry supplies `word(k)` and `letter(k, t)`, with a zero-based letter position `t`. The constructor accepts coefficient-two least letters. The theorem also covers coefficient-one minima, but this particular constructor does not implement their separate literature formula.

```python
from classical_words import table

rows = table('B', 3, (2, 0, 1, 3))
w = rows[1].word(4)
a = rows[1].letter(10**12, 10**6)
```

The exact recursive checker can also be run directly:

```sh
python exact_classical.py D 4 2,0,1,3,4 2
python check_classical.py --rank 5 --depth 2 --output full_checks.json
python check_classical.py --rank 4 --depth 3 --output depth3_checks.json
python check_classical.py --rank 6 --depth 0 --output local_checks.json
python check_extra.py
python switches.py
```

A positive `--depth` constructs every positive root space through that multiple of the height of delta, independently of the periodic formula. Depth zero checks the finite block construction, the actual predicted degree-two bracket, and the local inequalities; it does not construct the full degree-two standard basis. Exhaustive runs grow rapidly with rank. The default check stops at rank four.

`full_checks.json` and `rank6_checks.json` together record the exhaustive local checks through rank six. `endpoint_checks.json` records the first-endpoint comparisons over the same orders. `depth3_checks.json`, `extra_checks.json`, and `switch_checks.json` record the other runs. These files report finite tests, not certificates for arbitrary rank.

`type_c_previous/` retains the previous type-C programs and recorded outputs without modification. The proof of the expanded theorem is in the manuscript.
