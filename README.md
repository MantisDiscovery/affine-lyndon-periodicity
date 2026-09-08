# Affine Lyndon manuscript and extension

Editorial revision: the main paper (33 pages) and companion (8 pages) have been revised at sentence and paragraph level. The mathematical scopes and supplementary code are unchanged. `editorial/prose_revision_audit.json` records the preservation checks. Old mathematical audits and computation logs remain historical records, not new runs.

`manuscript/` contains the revised paper and its LaTeX source. Its insertion and connectivity theorems cover **all untwisted affine types**. The exceptional cases are explicitly credited to the prior computer-assisted verifications of Elkins and Tsymbaliuk.

`extensions/` contains a separate note with finite-block and primitive-bracketing results in all affine types, the twisted multiplicity obstruction, and a complete A2^(2) theorem. The proposed insertion formula in the other twisted families is a **conjecture**. This note should not be described as a proof of all twisted cases.

`code/classical/` is the preceding supplementary code and recorded outputs, unchanged. `code/general/` contains the new exact constructions and checks. Only Python's standard library is needed. See its README for commands and labels.

`editorial/improvement_ledger.md` records theorem scopes, dependencies, completed computations, and remaining proof obligations. The cover letter concerns the main paper. Editorial files are for the authors, not part of the manuscript or a journal supplement.

The mathematical proofs require coauthor review before submission. No external submission has been made. Compile either source with `pdflatex` twice; the bibliographies are included in the sources.
