# Supplementary finite checks

Python 3.10 or later is sufficient. There are no third-party dependencies.
Run from this directory without `-O`:

```sh
./run_checks.sh
```

On Windows, run the three commands separately:

```text
python verify_periodicity_proof.py --max-rank 6
python check_endpoint_rule.py
python verify_research.py --max-rank 5
```

Each command prints `ok` on success. The two main verifiers write JSON summaries
under `outputs/`; an assertion failure stops the run. Runtime grows rapidly with
rank because all internal-minimum alphabet orders are enumerated.

`exact_lyndon.py` implements sparse integer matrix brackets and exact rational
row reduction. `CWords(n, order, K)` constructs the generalized Leclerc recursion
through height `2*n*K`. It supports arbitrary alphabet orders. The grid and chain
comparison programs use an internal least letter. `grid_probe.py` computes the
same block candidates from the two arms; `parent_probe.py` and `chain_probe.py`
record the selected words, parents, and preperiods.

The full runs were repeated after refactoring with Python 3.13.5. Both output
JSON objects agree with the corresponding original certificates. The proof-specific
run covers all 4,166 internal-minimum orders in ranks two through six, 49,700
reflected-extension implications, and 20,162 target brackets. The structural run
covers all 566 internal-minimum orders in ranks two through five, 10,664 real grid
words, 5,332 complementary candidates, and 468 direct small-rank Lyndon evaluations.
The rectangle test covers 396 zero-weight multisets for `r=s=2`, `1 <= k <= 3`.

These are corroborative finite checks. They are not certificates of the universal
all-rank theorem. The proof treats all three possible bracket-order cases, although
only `Q<P` and `P<V<Q` occur in the finite runs. The endpoint-minimum cases imported
from the literature are not part of this exhaustive internal-minimum enumeration.

The refactor retains the mathematical checks and JSON fields, reduces exploratory
printing, adds input validation, and makes the endpoint checker importable without
running its search. Historical exploratory probes remain unchanged in the original
archive supplied with the complete working package. No claim about human-only code
authorship or a new license is made.
