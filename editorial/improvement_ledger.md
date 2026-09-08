# Untwisted completion and the general-affine extension

Revision: September 7, 2026.

## Scope of the delivered results

The main manuscript is **Imaginary standard Lyndon periodicity in untwisted affine types**. It states the insertion theorem for every untwisted affine type and every alphabet order. The remaining classical cases are supplied by the preceding manuscript's all-rank proofs. The exceptional cases are prior computer-assisted results of Elkins and Tsymbaliuk, not new exceptional-type proofs in this revision.

The companion, **Finite affine block alphabets and twisted imaginary Lyndon words**, proves structural results for every indecomposable symmetrizable affine root system and an all-degree formula for A2^(2). It does **not** prove the proposed insertion formula in the other twisted families. The two documents have deliberately different theorem scopes.

No quantum/shuffle-algebra analogue or full Gröbner–Shirshov presentation is claimed.

## Source audit that changes the main theorem's framing

In the June 19, 2025 author-hosted revision of *Affine standard Lyndon words*, Remark 6.29 verifies the two degree-2-delta identities for every exceptional type and every alphabet order. Proposition 6.32 propagates them to all positive imaginary degrees, and Remark 6.28 supplies the parent condition. These statements already establish the exceptional cases of the original, **untwisted** conjecture. Combining them with the classical manuscript proves the original conjecture in all untwisted types, including every Kac mark occurring there.

In the August 15, 2026 author-hosted revision of *Chains of affine standard Lyndon words*, Remark 4.30 verifies the standard/costandard prefix discrepancy in every exceptional type and order. Proposition 4.28 implies flag connectivity from that discrepancy; Lemma 4.31 handles coefficient-one minima. The new all-rank classical arguments therefore complete that untwisted conjecture as well.

This is an explicit use of published preprint computations. The new supplementary computations do not replace those all-order exceptional verifications. A type-independent analytic proof of the exceptional periodicity and connectivity assertions has **not** been produced here.

## Added mathematical statements

| Result | Location | Scope and proof status |
|---|---|---|
| Imaginary insertion in every untwisted type | Main Theorem 1.1 and Section 13.1 | Complete argument by the new all-rank classical proofs plus the precisely cited prior exceptional verification and propagation theorem. |
| Imaginary-flag connectivity in every untwisted type | Main Proposition 13.1 | Classical proof plus the prior exceptional discrepancy verification and its connectivity implication. |
| Exact phase and preperiod | Main Theorem 13.3 | Type-independent derivation. If the Lyndon parent is B=AC and the insertion period is W=CA, with C shorter than a full period, then y=LC. The real appends are exactly the canonical nonincreasing Lyndon factors of C. |
| Uniform preperiod bound and exact onset | Main Theorem 13.3 | The bound is |y| <= 2h-2. The eventual-prefix onset is degree delta exactly when C is empty, and degree 2 delta otherwise. This uses the full insertion theorem and the existing increasing-chain construction, not the converse. |
| Complete Dynkin parent tree | Main Corollary 13.4 | All untwisted types. Period parents are identified with the chain parents, after which ETC Lemma 4.32 supplies the Dynkin edges. That conditional lemma is prior work. |
| Reconstruction of every real-chain orientation | Main Corollary 13.5 | For a given root datum, the imaginary words at delta and 2 delta recover the increasing simple roots beta_i=Pr(deg(L_i C_i)), and hence the increasing/decreasing orientation of every real-root chain and all Cartan bond data. This does not claim to reconstruct every real standard word directly. |
| Uniform finite preprocessing | Main Theorem 13.6 | O(n^7) rational arithmetic operations and alphabet comparisons, O(n^5) storage; output-linear word generation after retaining O(n^2) factors. This is an arithmetic model, not a constant-bit-cost bound. The sharper classical O(n^3 log n) construction remains. |
| Rational imaginary-word language | Main Corollary 13.7 | The disjoint language union L_i W_i^* R_i has an unambiguous finite automaton with O(nh) states. The statement concerns imaginary words only, and does not claim this bound after determinization. |
| Finite block alphabet in every affine type | Companion Theorem 2.1 | All twisted and untwisted types, every mark. Cutting at a least letter of mark m gives km standard blocks. For m>=2 they are real; for m=1 the possible imaginary degree-delta blocks are retained separately. The proof uses the positive-definite quotient by the primitive null root. |
| Finite root-path block construction | Companion Proposition 2.3 | All affine types for m>=2. The greatest word at a block root is obtained from its coefficient-one simple-root predecessors. No chain, fork, or rectangular model is assumed. |
| Nonzero bracketing of primitive configurations | Companion Theorem 3.2 and Corollary 3.3 | All affine types. A negative-inner-product merger gives a nonzero bracket; primitivity keeps every proper internal degree real. Every m-block configuration of degree delta is primitive. |
| A nonzero Lyndon ordering | Companion Corollary 3.4 | Free-Lie expansion converts the preceding bracketing into at least one nonzero Lyndon ordering with the same block multiplicities. This does not say that every ordering works or that the surviving word is the first flag selection. |
| Cyclic grading for arbitrary untwisted marks | Companion Proposition 4.1 | The block weights form the degree-one eigenspace of the simple-coefficient cyclic grading. Complementation returns to that space only at mark two. This is a weight-space description, not a Lie-subalgebra identification. |
| Twisted multiplicities and indexing obstruction | Companion Theorem 5.1 and Corollary 5.2 | Derived directly from the diagram automorphism's simple-coroot orbits. This is standard twisted-loop structure applied to the proposed indexing, not a claim of a new multiplicity formula. A3^(2) is exhibited by a complete 14-word degree-two bracket calculation. |
| Full A2^(2) insertion theorem | Companion Theorem 6.2 | Both alphabet orders and every k>=1. The proof uses the Cartan sandwich lemma and explicit nonzero bracket coefficients; it is not inferred from finite tests or from untwisted propagation. |
| Divisibility-stratified twisted insertion | Companion Conjecture 7.1 | A precise conjecture, not an established theorem outside A2^(2). Families have strides d/|O| and first appear at that multiple of delta. |

## The complete rank-one twisted formula

With delta=alpha_0+2 alpha_1:

- For 0<1: SL(k delta)=01(011)^(k-1)1, with longest proper Lyndon prefix 01(011)^(k-1).
- For 1<0: SL(k delta)=1(110)^(k-1)10, with longest proper Lyndon prefix 1(110)^(k-1).

For k>=2, the two displayed candidate brackets have nonzero E11 coefficients 3(-3)^(k-2) and -3^(k-1), respectively, after suppressing loop powers. The upper bound is a word comparison using the abelian zero-weight subalgebra. The k=1 cases are checked separately.

## Completed computations in this revision

Every insertion fit below is performed **after** constructing homogeneous Lie spaces by simple-generator brackets and selecting actual costandard brackets. The fitting procedure is not the source of the benchmark words. The proposed longest prefixes, coverage of each imaginary degree, and earlier-parent condition are all checked.

| Scope | Orders | Maximum degree | Recorded output |
|---|---:|---:|---|
| A2^(2), A4^(2), A6^(2), A3^(2), A5^(2), all orders | 62 | 6 delta | twisted_checks.json |
| D4^(2), four specified orders | 4 | 6 delta | folded_checks.json |
| E6^(2), five specified orders | 5 | 6 delta | folded_checks.json |
| D4^(3), all six orders | 6 | 9 delta | triality_checks.json |
| A2^(2), both orders, direct enumeration of every binary Lyndon word in the specified imaginary degrees | 2 | 6 delta | A2_twisted_01.json, A2_twisted_10.json |
| G2^(1), every order; insertion and independently replayed greedy preperiod | 6 | 3 delta | phase_G2.json |
| F4^(1), every order; insertion and independently replayed greedy preperiod | 120 | 3 delta | phase_F4.json |
| E6^(1), E7^(1), E8^(1), one specified order each; insertion and independently replayed greedy preperiod | 3 | 3 delta | phase_E6.json, phase_E7.json, phase_E8.json |

The twisted rows comprise **77 distinct type/order cases and 214 fitted families**. The binary enumeration is an additional method for two cases already counted, not two extra type/order cases. Triality is checked at 3 delta, 6 delta, and 9 delta for its stride-three family, rather than fitted only from two points.

The untwisted phase rows comprise **129 type/order cases and 513 imaginary-index comparisons**. The chosen E8 order has a least letter of mark six. These selected E-type checks are not all-order E-type enumerations.

An independent audit derives positive real roots from the specified affine Cartan matrices by Weyl reflections, then adds the known imaginary multiplicities. Its root-space dimensions agree with the Lie closure in 13 model/cutoff configurations. The simple generators satisfy the corresponding positive Serre relations with the expected nonzero preceding powers. The D4 root-table implementation also passes all **21,952 ordered basis-triple Jacobi identities**. Diagram folds are checked on every finite basis structure constant when constructed. These audits are implemented in check_models.py, with model_audit.json and model_audit_E8.json recording the completed runs.

The preceding classical programs and their recorded results are preserved byte-for-byte in code/classical. Their much larger previously reported test counts are inherited; those entire campaigns were not rerun in this revision.

Additional rank-four twisted family-wide runs and an extra E8 mark-five phase run were started but did not finish. They are excluded from every completed count above.

## Remaining proof obligations

The full twisted insertion assertion remains open **within this work**. In four twisted families the number of imaginary words changes with k, so simply repeating the untwisted theorem is not even a complete formulation. The companion supplies the correct dimension-compatible stride multiset and a tested word conjecture, but two further arguments are required:

1. Relate the ordered imaginary flag quotients in the different diagram eigenspaces, including families absent in some degrees.
2. Prove propagation of the proposed seed and standard-prefix identities at the appropriate strides.

The finite-block and primitive-bracketing theorems do not supply those steps: they establish finiteness and some nonvanishing, not lexicographic maximality in all subsequent flag layers. The untwisted degree-two propagation theorem is not applied to twisted data.

A type-independent analytic replacement for the prior exceptional computations would be a separate strengthening of the all-untwisted theorem. It has not been claimed here. Quantum deformation, canonical-basis statements, categorification, and a full Gröbner–Shirshov presentation remain outside the delivered theorem scope.

## Editorial and submission status

The author order, MIT affiliations, correspondence address, exact contribution paragraph, and declarations are unchanged. The new files replace neither provenance nor prior citations with claims of sole authorship of the exceptional results.

The new uniform phase proof, the general-affine root-string merger, and the rank-one Cartan sandwich argument require coauthor review before submission. The earlier classical fork comparison and short-column ordering remain appropriate review targets as well. No external referee approval or proof-assistant verification is claimed.

The main manuscript and companion are separate files so that unproved twisted propagation is not inadvertently included in the main theorem. The cover letter concerns the main manuscript. The earlier provisional venue is not re-evaluated in this revision, and no acceptance probability or December 31 guarantee is inferred from the enlarged scope. Nothing has been submitted, emailed, or uploaded to a journal.
