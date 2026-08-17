# AURKB–PDAC computational workflow

This repository contains the computational notebooks and supporting files associated with the study:

> **Chemotype-aware QSAR–GCN consensus screening and molecular modeling prioritize natural-product-derived AURKB-targeting candidates for pancreatic ductal adenocarcinoma**

The repository documents the natural-product prescreening, classical QSAR modeling, graph convolutional network (GCN) analysis, and QSAR–GCN consensus prioritization stages of the study.

## 1. Workflow overview

The computational screening workflow consisted of three consecutive stages:

```text
COCONUT natural-product library
        |
        v
[1] Prescreening
    738,827 records
        |
        v
    86,056 retained compounds
        |
        v
[2] Classical QSAR
    34,721 within applicability domain
    31,020 with P(active) >= 0.50
        |
        v
    6,232 compounds transferred to GCN analysis
        |
        v
[3] GCN + QSAR–GCN consensus
    615 Tier 1 candidates
    29 Tier 1A candidates
        |
        v
    Molecular docking and downstream analysis
```

The 29 Tier 1A candidates were subsequently evaluated by molecular docking. Seventeen met the predefined docking-score threshold, followed by developability/toxicity assessment and molecular-dynamics analysis of three prioritized compounds. These downstream analyses were performed outside the notebooks included in this repository and are described in the manuscript and supplementary information.

## 2. Notebooks

The notebooks should be considered in the following order.

| Stage | Notebook                                               | Main input                                                                                            | Main output                                                                   |
| ----- | ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| 1     | `notebooks/01_AURKB_COCONUT_Prescreening.ipynb`        | COCONUT natural-product export                                                                        | 86,056-compound prescreened library                                           |
| 2     | `notebooks/02_AURKB_Classical_QSAR_Reproduction.ipynb` | Curated AURKB bioactivity data, frozen descriptor matrix, model artifacts, and the Notebook 1 library | Classical QSAR validation and the 6,232-compound QSAR→GCN transfer            |
| 3     | `notebooks/03_AURKB_GCN_Consensus_Screening.ipynb`     | 6,232-compound transfer set                                                                           | GCN evaluation, consensus scores, tier assignments, and 29 Tier 1A candidates |

Each notebook contains an introductory documentation cell describing its role in the workflow, principal inputs and outputs, and relationship to the adjacent stages.

## 3. Key workflow checkpoints

| Item                                             |       Value |
| ------------------------------------------------ | ----------: |
| COCONUT records screened                         |     738,827 |
| Valid standardized structures                    |     735,561 |
| Prescreened compounds                            |      86,056 |
| Raw ChEMBL AURKB records                         |       3,248 |
| Curated AURKB compounds                          |       1,854 |
| Active / inactive compounds                      | 1,429 / 425 |
| Initial / selected descriptors                   |   217 / 165 |
| Compounds within descriptor applicability domain |      34,721 |
| Compounds with P(active) ≥ 0.50                  |      31,020 |
| QSAR→GCN transfer set                            |       6,232 |
| Tier 1 candidates                                |         615 |
| Tier 1A candidates                               |          29 |
| Docking candidates meeting ≤ −9.0 kcal/mol       |          17 |
| Compounds advanced to 100-ns MD                  |           3 |

The manuscript-linked 6,232-row QSAR→GCN transfer was verified against the following SHA-256 checksum:

```text
8821947e92d8b209d291b627bae3b1d5068c6e2f1c0154f695abf0e73673f4df
```

Detailed model-performance values, validation results, split definitions, and provenance information are provided in `REPRODUCIBILITY.md` and in the notebooks themselves.

## 4. Supporting code

Notebook 1 depends on:

```text
scripts/aurkb_prescreening_vscode.py
```

The file included here is the preserved script used with the prescreening notebook.

SHA-256:

```text
27f4979142422cb657278508bac89a91e6b63d42d209ca2ffec58ee8075b101e
```

When reproducing the prescreening workflow, the script should be available on the notebook's Python import path.

## 5. Reproducibility and provenance

The notebooks in this repository retain the computational state used for the study.

* Executable notebook code, cell order, cell identifiers, execution counts, and stored scientific outputs were preserved during preparation of the repository.
* The notebooks were not re-executed solely for repository preparation.
* Historical results and provenance records are preserved where software-version sensitivity affects exact reproduction. Where required computational artifacts are not distributed with this repository, this is stated explicitly in `REPRODUCIBILITY.md`.
* Checksums, notebook-comparison records, and other provenance information are available in `provenance/`.
* Detailed information on the relationship between the three computational stages is provided in `REPRODUCIBILITY.md`.

## 6. Computational environments

The three notebooks were executed in different software environments.

| Stage      | Python                      | Selected recorded packages                                                                             |
| ---------- | --------------------------- | ------------------------------------------------------------------------------------------------------ |
| Notebook 1 | 3.13.5, Windows/VS Code     | pandas 2.2.3, NumPy 2.2.5, RDKit 2026.03.2                                                             |
| Notebook 2 | 3.12.13, Windows/conda      | NumPy 2.3.5, pandas 2.2.3, scikit-learn 1.8.0, XGBoost 3.1.3, RDKit 2025.9.4                           |
| Notebook 3 | 3.12.13, Google Colab/Linux | NumPy 1.26.4, pandas 2.2.2, scikit-learn 1.6.1, TensorFlow 2.20.0, DeepChem 2.8.1.dev, RDKit 2026.03.2 |

Additional environment information and the evidence supporting recorded package versions are available in:

```text
environment/environment_versions.md
environment/requirements-recorded.txt
```

The historical QSAR training environment could only be partially reconstructed from preserved artifacts. Where an exact historical version was not recorded, the repository documentation identifies it as unavailable rather than inferring a version.

## 7. Data sources

The study used publicly available or externally maintained scientific resources together with derived study data.

| Source                           | Role in the study                    | Included here                         |
| -------------------------------- | ------------------------------------ | ------------------------------------- |
| COCONUT natural-product database | Natural-product prescreening         | No                                    |
| ChEMBL, target CHEMBL2185        | AURKB bioactivity curation           | No                                    |
| RCSB PDB 4AF3                    | Structural modeling/docking receptor | No                                    |
| miRTarBase 2025                  | AURKB-related miRNA evidence         | No                                    |
| Study supplementary data         | Derived computational results        | See manuscript supplementary material |

Third-party data sources and redistribution considerations are summarized in `THIRD_PARTY_DATA_AND_LICENSE_NOTES.md`.

## 8. Repository structure

```text
AURKB-PDAC-computational-workflow/
│
├── README.md
├── REPRODUCIBILITY.md
├── CITATION.cff
├── LICENSE
├── MANIFEST.sha256
├── THIRD_PARTY_DATA_AND_LICENSE_NOTES.md
│
├── notebooks/
│   ├── 01_AURKB_COCONUT_Prescreening.ipynb
│   ├── 02_AURKB_Classical_QSAR_Reproduction.ipynb
│   └── 03_AURKB_GCN_Consensus_Screening.ipynb
│
├── scripts/
│   └── aurkb_prescreening_vscode.py
│
├── environment/
│   ├── environment_versions.md
│   ├── requirements-recorded.txt
│   └── requirements_aurkb_prescreening.txt
│
├── provenance/
│   ├── artifact_manifest_sha256.csv
│   ├── comment_only_code_diff.tsv
│   ├── notebook_integrity_report.json
│   └── notebook_original_hashes.txt
│
├── data/
│   └── supplementary/
│
└── journal/
```

## 9. Reproducibility notes

This repository is intended to support verification of the three-stage screening workflow rather than serve as a complete end-to-end rerun package for every analysis reported in the study.

Several large or externally sourced inputs are not distributed here, including the original COCONUT export, raw ChEMBL extraction, frozen descriptor matrix, trained model artifacts, split assignments, and GCN ensemble weights.

The historical complete QSAR screening output is also not available as a standalone artifact. Consequently, the intermediate totals of 34,721 compounds within the descriptor applicability domain and 31,020 compounds above the probability threshold cannot be regenerated independently from the repository alone. The downstream 6,232-compound transfer set is retained as a hash-verified workflow checkpoint.

Descriptor calculations were also found to be sensitive to RDKit version, particularly for `BertzCT` and `NumHAcceptors`. The historical descriptor matrix used in the study therefore represents the computational input underlying the reported QSAR workflow rather than a matrix regenerated with a newer RDKit release.

Molecular docking, developability/toxicity assessment, molecular dynamics, and miRNA analyses were performed using separate software workflows and are documented in the manuscript and supplementary information.

Further details on reproducible and preserved components of the analysis are provided in `REPRODUCIBILITY.md`.

## 10. Citation

Citation information for this repository is provided in `CITATION.cff`.

Please cite the associated article when using this workflow or its derived results. Final bibliographic information and DOI should be added after publication.

## 11. License

Original source code and notebook code in this repository are released under the BSD 3-Clause License. See [`LICENSE`](LICENSE).

Third-party databases, source data, software packages, molecular structures, and other externally sourced materials are not relicensed by this repository and remain subject to their respective terms of use and licences.
