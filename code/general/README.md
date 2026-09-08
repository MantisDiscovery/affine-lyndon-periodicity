# Exact affine checks

Use Python 3.10 or later. No packages are required. Run from this directory; recorded outputs are in `results/`.

```sh
python twisted_words.py --type Aeven -n 1 -k 6 --order 0,1 --exhaustive
python twisted_words.py --type Aeven -n 1 -k 6 --order 1,0 --exhaustive
python check_twisted.py -n 3 -k 6 --out replay_twisted.json
python check_folds.py
python check_triality.py
python check_models.py
python check_models.py --type E -n 8 -k 3 --out replay_E8_model.json
python check_phase.py --type G2 -n 2 --out replay_G2_phase.json
python check_phase.py --type F4 --out replay_F4_phase.json
python check_phase.py --type E -n 6 --order 4,0,1,2,3,5,6 --out replay_E6_phase.json
python check_phase.py --type E -n 7 --order 4,0,1,2,3,5,6,7 --out replay_E7_phase.json
python check_phase.py --type E -n 8 --order 4,0,1,2,3,5,6,7,8 --out replay_E8_phase.json
```

The F4 all-order run and the E8 phase check are substantially heavier than the rank-one checks. The phase script writes each completed order and resumes from its output file.

## Labels

`Aeven(n)` is A_(2n)^(2), with delta=(1,2,...,2). `Aodd(n)` is A_(2n-1)^(2), with delta=(1,1,2,...,2,1). `Dtw(n)` is D_(n+1)^(2), with all marks one. `E6tw` has delta=(1,2,3,2,1), and `D4tw` has delta=(1,2,1). The affine letter is 0. Orders are lists from least to greatest.

For F4, the finite simple-root order is short, short, long, long, with Cartan matrix

```text
 2 -1  0  0
-1  2 -2  0
 0 -1  2 -1
 0  0 -1  2
```

Its untwisted marks are (1,2,4,3,2). G2 uses a short root first and a long root second, with finite Cartan matrix [[2,-3],[-1,2]] and untwisted marks (1,3,2). E6, E7, and E8 have a finite chain 1-3-4-5-...-n and the additional edge 2-4. These conventions are also checked by `check_models.py`.

## Methods and limits

`twisted_words.py` first constructs every homogeneous Lie space inside the coefficient box bounded by K delta, using simple-generator brackets and exact integer elimination. It then selects actual costandard brackets by the generalized Leclerc recursion. Insertion patterns are fitted only afterward by `check_twisted.py`; this checks complete degreewise coverage, longest prefixes, and the parent condition.

`root_model.py` implements an ADE lattice-cocycle root table and exact diagram folds. The order-three fold is represented over Q(zeta), zeta^2+zeta+1=0, by rational 2-by-2 blocks. Every diagram automorphism is checked on the full finite bracket table.

`check_models.py` independently generates real roots by Weyl reflections in the specified Cartan matrix, adds the known imaginary multiplicities, and compares every homogeneous dimension with the Lie closure. It also checks the positive Serre relations and all ordered basis-triple Jacobi identities for the D4 root table.

`check_phase.py` extracts the period from the first two imaginary degrees, checks the third, and compares the predicted preperiod with a separate greedy construction using real-chain directions and Cartan-flag independence. It does not use the phase formula to define that greedy construction.

The recorded twisted scopes are 62 A-family orders through 6 delta, nine selected D/E twists through 6 delta, and all six triality orders through 9 delta. These are finite checks, not an all-rank twisted propagation proof. The A2^(2) theorem instead has an all-degree argument in the companion note and an additional raw binary-word enumeration.
