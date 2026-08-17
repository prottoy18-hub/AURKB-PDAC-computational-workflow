# Reproducibility and lineage

This document records what each stage of the computational workflow consumed and produced, which
values can be recomputed, which values exist only as preserved historical artifacts, and where the
workflow is sensitive to software versions.

The scientific state of the study is frozen. No notebook in this repository was re-executed to
produce this documentation, and no scientific value in this repository was recalculated.

---

## 1. Stage-to-stage lineage

```text
COCONUT natural-product export (coconut_csv-05-2026.csv)
        |  738,827 input records
        |  RDKit standardization; 5 invalid SMILES removed; 3,261 duplicate standardized structures removed
        |  735,561 valid standardized structures
        |  kinase-oriented lead-like window + PAINS removal
        v
Notebook 1  01_AURKB_COCONUT_Prescreening.ipynb
        |
        |  86,056 prescreened compounds  (Prescreening_coconut_AURKB.csv)
        v
Notebook 2  02_AURKB_Classical_QSAR_Reproduction.ipynb
        |    inputs: curated ChEMBL AURKB set (3,248 raw records -> 1,854 curated compounds;
        |            1,429 active / 425 inactive), frozen 217-descriptor matrix (165 selected),
        |            archived model / calibrator / preprocessing checkpoints
        |    screening: 86,056 scored -> 34,721 inside the descriptor applicability domain
        |               -> 31,020 at probability >= 0.50 -> 6,232 at probability >= 0.75 and leverage <= h*
        |
        |  frozen / historical QSAR artifact layer
        |  exact 6,232-row transfer snapshot
        |  SHA-256 8821947e92d8b209d291b627bae3b1d5068c6e2f1c0154f695abf0e73673f4df
        v
Notebook 3  03_AURKB_GCN_Consensus_Screening.ipynb
        |    GCN validation splits: random 1,112 / 371 / 371; scaffold 1,109 / 371 / 374
        |    selected architecture [128, 128], dense 256, dropout 0.30, learning rate 0.0005
        |    calibrated ROC-AUC 0.8881 (random test), 0.9058 (scaffold-disjoint test)
        |    consensus filters: GCN pass 5,293; uncertainty pass 5,296; structural support 1,006;
        |                       alert-free 5,232
        |
        |  Tier 1 = 615, Tier 2 = 3,742, Tier 3 = 936, Tier 4 = 939
        |  Tier 1A = 29
        v
site-specific AutoDock Vina docking of the 29 Tier 1A candidates against AURKB (PDB 4AF3)
        |  17 candidates at or below -9.0 kcal/mol
        v
developability / ADMET / toxicity triage of those 17 candidates
        |  SwissADME, admetSAR 3.0, ProTox 3.0
        v
3 candidates advanced to 100-ns molecular dynamics (YASARA Structure, AMBER14)
        |  CNP0570388.1, CNP0047084.1, CNP0050461.1
        v
MM-PBSA endpoint binding energies, PCA and DCCM analyses (completed)
```

A parallel regulatory arm (miRTarBase, RNAfold, RNAComposer) prioritized AURKB-regulatory miRNAs.
Neither the docking, developability, MD nor miRNA stages are implemented in these notebooks; they
were performed with the external tools named in the manuscript Methods and are already complete.

---

## 2. What each notebook actually does

### Notebook 1 — `01_AURKB_COCONUT_Prescreening.ipynb`

Imports `scripts/aurkb_prescreening_vscode.py` and runs the chunk-wise standardization, descriptor
calculation, physicochemical filtering and PAINS removal pipeline over the COCONUT export. The
notebook itself contains configuration and inspection code; the scientific logic lives in the script.

Recorded outputs retained in the notebook: the run log line
`Saved final prescreened library: ... (86,056 compounds)`, the loaded shape `(86056, 35)`, zero
duplicate standardized SMILES and zero retained PAINS alerts.

Also retained: a `Could not write Parquet output` warning (pyarrow/fastparquet were absent; the CSV
output is unaffected) and, at the end of the notebook, a VS Code
`The Kernel crashed while executing code in the current cell or a previous cell` notice. That notice
appears after the final file-listing cell, after every scientific output had already been produced and
verified, and it is retained rather than removed so the executed record stays complete.

### Notebook 2 — `02_AURKB_Classical_QSAR_Reproduction.ipynb`

A provenance-controlled reproduction notebook with two deliberately isolated branches:

1. the production / random-split QSAR branch, and
2. the corrected scaffold-disjoint validation branch, replayed from its train-only model and external
   sigmoid calibrator with zero scaffold overlap.

The notebook verifies frozen inputs by SHA-256 before use, replays archived checkpoints, and labels
regenerated, checkpoint-replayed, archived-only and irreproducible results separately. The corrected
scaffold model is never substituted for the production screening model.

Its central verification is the QSAR-to-GCN transfer confirmation, which is recorded as `PASS` with
identical expected, archived and transfer-copy SHA-256 values
(`8821947e…3673f4df`), 6,232 rows on both sides, identical ordered identifier, SMILES, probability
and inside-applicability-domain hashes, a maximum probability difference of 0.0 and zero
identifier-level mismatches. The historical run identifier is `run_20260715T124827Z_79cebaa2`.

### Notebook 3 — `03_AURKB_GCN_Consensus_Screening.ipynb`

Featurizes the curated training molecules with the DeepChem `ConvMolFeaturizer`, searches three GCN
architectures, calibrates the selected model, benchmarks it against ECFP logistic-regression and
random-forest baselines, bootstraps confidence intervals, trains a three-seed production ensemble
(seeds 11, 42, 77), screens the 6,232 transferred candidates, and applies the rank-based consensus
score

```text
0.45 * QSAR_rank_pct + 0.45 * calibrated_GCN_rank_pct + 0.10 * low_uncertainty_rank_pct
```

producing the tier assignments and the 29 Tier 1A elite candidates.

---

## 3. Values that can be reproduced exactly

| Value | How it is established |
|---|---|
| The 6,232-row QSAR-to-GCN transfer snapshot | Byte-level SHA-256 verification inside Notebook 2. Recomputing the hash of the archived file reproduces `8821947e…3673f4df` exactly. |
| Ordered identifiers, SMILES, probabilities and applicability-domain labels of the transfer | Column-wise ordered hashes recorded in the Notebook 2 output, all matching. |
| Notebook identity | The SHA-256 of each locked original notebook (see `provenance/notebook_original_hashes.txt`). |
| The 12 archived QSAR input artifacts | `Input_Hashes` of Supplementary Data File S4 records expected and actual SHA-256 for each, all matching. |
| Row counts of the supplementary data workbooks | 86,056 (S1), 3,248 raw and 1,854 curated (S2), 217 and 165 descriptors (S3), 6,232 (S4, S5), 29 (S6, S8). |

## 4. Values preserved as historical artifacts and not regenerated

| Value | Why |
|---|---|
| The 217-descriptor frozen matrix | Regeneration under a current RDKit build changes `BertzCT` and `NumHAcceptors`. The frozen matrix is the authoritative analytical input. |
| Production QSAR model, calibrator, preprocessing and applicability-domain artifacts | Preserved joblib checkpoints; the original training environment is only partially recoverable (scikit-learn 1.6.1 from serialization metadata; xgboost version not recorded). |
| The historical 30-value Y-randomization vector (observed CV ROC-AUC 0.888611; permuted mean 0.504881; SD 0.023899; empirical p approximately 0.032258) | Fresh permutation in the reproduction environment disagrees; the hash-verified archived vector remains authoritative. |
| The upstream screening counts 34,721 and 31,020, and the exact re-selection of 6,232 | The original all-screened CSV and the complete historical QSAR environment are absent. Notebook 2 states this limitation explicitly. |
| The trained GCN ensemble and its calibrated probabilities | Colab-trained; the exact TensorFlow / DeepChem / Keras-compatibility combination is recorded but the trained weights are not redistributed here. |
| All docking, ADMET/toxicity and MD results | Produced by external tools (PyRx/AutoDock Vina, SwissADME, admetSAR 3.0, ProTox 3.0, YASARA Structure). Not re-run. |

## 5. Known software-version sensitivity

- **RDKit descriptor drift.** `BertzCT` and `NumHAcceptors` differ between the historical RDKit build
  and the reproduction build. Supplementary Data File S3 sheet `S3B_Selected_165_Descriptors` carries
  per-descriptor drift columns for this reason.
- **Fresh QSAR fitting differs from the archived values.** Notebook 2 stores explicit `RuntimeWarning`
  records for cross-validation, calibrated held-out fitting and Y-randomization. These are diagnostics
  of environment sensitivity, not corrections.
- **DeepChem / TensorFlow coupling.** Notebook 3 requires `TF_USE_LEGACY_KERAS=1`; internal batch
  normalization was excluded from the selected architecture because of TensorFlow/Keras compatibility
  limits. Several DeepChem descriptors were dropped by the featurizer for lack of normalization
  constants, and several optional DeepChem model families were unavailable in the Colab image.
- **Three different Python environments.** Python 3.13.5 (Notebook 1), 3.12.13 conda (Notebook 2),
  3.12.13 Colab (Notebook 3). See `environment/environment_versions.md`.

## 6. What is missing, and what that prevents

The following are required to re-derive the workflow end to end and are **not** present in this
repository:

- the COCONUT export `coconut_csv-05-2026.csv` (third-party source data);
- the raw ChEMBL AURKB extraction for target CHEMBL2185;
- the frozen 217-descriptor matrix file, the production model, calibrator, preprocessing and
  applicability-domain artifacts, and the split assignments (these live in the archived
  `QSAR_Final_Reproduction/run_20260715T124827Z_79cebaa2` run folder and its input ZIPs);
- the complete historical all-screened QSAR output CSV, which no longer exists;
- the trained GCN ensemble weights;
- the receptor preparation, grid configuration and Vina logs of one of the docking campaigns
  (see `audit_private/DOCKING_SCORE_PROVENANCE_REPORT.md`).

Because of these, this package is **not** a complete end-to-end re-execution of the study. It is a
verifiable record of the executed notebooks, the exact stage-to-stage transfer, the recorded
environments and the hash-based integrity checks. Claims of full reproducibility would not be
supported by the evidence and are not made.

## 7. Integrity of this package

- `provenance/notebook_original_hashes.txt` — SHA-256 of the three locked original notebooks.
- `provenance/notebook_integrity_report.json` — per-notebook PASS/FAIL for code-cell count, ordering,
  cell identifiers, execution counts, output objects and executable Python content, produced by static
  comparison without executing anything.
- `provenance/comment_only_code_diff.tsv` — every changed line of every changed code cell, with the
  proof that each changed line is a comment in both versions and that the executable token streams are
  identical.
- `provenance/artifact_manifest_sha256.csv` and `MANIFEST.sha256` — SHA-256 of every file shipped here.
