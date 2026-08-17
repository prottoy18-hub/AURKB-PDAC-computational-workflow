# Recorded software environments

Every version below was read from evidence preserved at the time of execution: notebook output cells,
the provenance JSON files written by the Notebook 2 run, and the joblib serialization metadata of the
archived model artifacts. Nothing was re-executed, no package was upgraded, and no version was
inferred. Where a version was not recorded, this file says `not directly recorded`.

The three notebooks were executed in three different environments. That is a property of the study as
it was performed, not an error.

---

## Notebook 1 — COCONUT prescreening (local Windows, VS Code)

Source of evidence: stdout of the first code cell of the executed notebook.

| Component | Recorded version |
|---|---|
| Python | 3.13.5 (tags/v3.13.5:6cb20a2, Jun 11 2025) [MSC v.1943 64 bit (AMD64)] |
| pandas | 2.2.3 |
| numpy | 2.2.5 |
| RDKit | 2026.03.2 |
| tqdm | not directly recorded (required by `scripts/aurkb_prescreening_vscode.py`) |
| matplotlib | not directly recorded (required for the chemical-space figures) |
| pyarrow / fastparquet | not installed at run time; the notebook log records `Could not write Parquet output: Unable to find a usable engine`. The CSV output is unaffected. |
| Notebook kernel metadata | `kernelspec` name `python3`, `language_info.version` 3.12.13 |

Declared dependency floor for this stage, as preserved next to the script
(`environment/requirements_aurkb_prescreening.txt`): `pandas>=2.0`, `numpy>=1.24`, `rdkit>=2023.9`,
`tqdm>=4.65`, `matplotlib>=3.7`, `pyarrow>=12.0`. These are floors declared by the authors, not the
versions actually used; the actual versions are the table above.

**Note.** The notebook's `language_info.version` metadata (3.12.13) disagrees with the Python version
printed by the notebook itself (3.13.5). The printed value is the run-time evidence and is treated as
authoritative for this stage.

---

## Notebook 2 — classical QSAR reproduction (local Windows, conda)

Source of evidence: `Provenance/package_versions.json` and `Provenance/environment_information.json`
of the authoritative run `run_20260715T124827Z_79cebaa2`.

| Component | Recorded version |
|---|---|
| Python | 3.12.13, packaged by conda-forge (main, Mar 5 2026, 16:36:12) [MSC v.1944 64 bit (AMD64)] |
| Interpreter | `C:\Users\Prottoy\miniconda3\envs\research-py312\python.exe` |
| Platform | Windows-11-10.0.26200-SP0, AMD64 |
| numpy | 2.3.5 |
| pandas | 2.2.3 |
| scikit-learn | 1.8.0 |
| xgboost | 3.1.3 |
| rdkit | 2025.9.4 (runtime string `2025.09.4`) |
| joblib | 1.5.3 |
| matplotlib | 3.10.8 |
| nbformat | 5.10.4 |
| jupyter | not installed / metadata unavailable |
| Notebook kernel metadata | `kernelspec` display name `research-py312`, `language_info.version` 3.12.13 |

Execution settings recorded for that run: `QSAR_EXECUTION_PROFILE=full`, `QSAR_N_JOBS=1`,
`PYTHONHASHSEED` not set before interpreter start.

### The original historical QSAR training environment

This is a different environment from the reproduction environment above, and it is only partially
recoverable:

| Component | Recorded value | Source of evidence |
|---|---|---|
| scikit-learn | 1.6.1 | serialization metadata of the archived joblib model artifacts |
| xgboost | not directly recorded | recorded as "not directly recoverable" in the run provenance |
| Python | not directly recorded | — |
| RDKit | not directly recorded for the QSAR stage | — |
| Same-day prescreening environment (supporting evidence only) | Python 3.13.5, numpy 2.2.5, pandas 2.2.3, RDKit 2026.03.2 | the Notebook 1 run of the same day |

The run provenance explicitly labels the same-day prescreening versions as supporting evidence and
not as a direct record of the QSAR environment. They are reproduced here with that qualification.

### Recorded software-drift evidence

- Regenerating the RDKit descriptor matrix under the reproduction environment produced version-sensitive
  differences in the `BertzCT` and `NumHAcceptors` descriptors. The frozen 217-descriptor matrix is
  therefore the authoritative analytical input and was not replaced.
- The notebook stores a `RuntimeWarning` recording that fresh five-fold cross-validation differs from
  the archived historical metrics in the reproduction environment.
- The notebook stores a `RuntimeWarning` recording that fresh calibrated random held-out fitting
  differs from the historical target in the reproduction environment.
- The notebook stores a `RuntimeWarning` recording that fresh Y-randomization differs from the
  preserved historical 30-score vector, which remains authoritative.

These warnings are scientific evidence of environment sensitivity and are deliberately retained in
the submission copy.

---

## Notebook 3 — DeepChem GCN and consensus screening (Google Colab, Linux)

Source of evidence: stdout of the environment cells of the executed notebook.

| Component | Recorded version |
|---|---|
| Python | 3.12.13 (main, Mar 4 2026, 09:23:07) [GCC 11.4.0] |
| Platform | Linux-6.6.122+-x86_64-with-glibc2.35 (Google Colab) |
| numpy | 1.26.4 |
| pandas | 2.2.2 |
| scikit-learn | 1.6.1 |
| TensorFlow | 2.20.0 |
| DeepChem | 2.8.1.dev |
| RDKit | 2026.03.2 |
| Keras compatibility | `TF_USE_LEGACY_KERAS = 1` |
| Notebook kernel metadata | `kernelspec` name `python3`, `language_info.version` 3.10 |

Recorded environment notes preserved in the notebook output:

- DeepChem emitted `No normalization for ...` warnings for the SPS, AvgIpc, NumAmideBonds,
  NumAtomStereoCenters, NumBridgeheadAtoms, NumHeterocycles, NumSpiroAtoms,
  NumUnspecifiedAtomStereoCenters and Phi descriptors, which were dropped by the featurizer.
- DeepChem skipped optional model families whose dependencies were absent in Colab
  (`torch_geometric`, `transformers`, `lightning`, `haiku`).
- Weights & Biases was installed but not logged in; no run was logged.
- Internal batch normalization was excluded from the selected GCN because of TensorFlow/Keras
  compatibility limits, as stated in the manuscript Methods.
- The notebook's `language_info.version` metadata (3.10) disagrees with the Python version printed by
  the notebook itself (3.12.13). The printed value is the run-time evidence and is authoritative.

---

## What this means for reproduction

- Notebook 1 can be re-executed if the COCONUT export named in the notebook is available; RDKit
  version differences may change descriptor values and therefore the retained set.
- Notebook 2 does not re-derive the manuscript production values. It verifies frozen artifacts by
  hash and replays archived checkpoints. Fresh fitting in a modern environment is documented to
  disagree with the historical values.
- Notebook 3 requires DeepChem with the legacy-Keras TensorFlow path. The version combination above
  is the one that produced the stored results.
