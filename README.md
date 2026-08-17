# AURKB–PDAC computational workflow

Computational notebooks and reproducibility documentation for the study:

> **Chemotype-aware QSAR–GCN consensus screening and molecular modeling prioritize
> natural-product-derived AURKB-targeting candidates for pancreatic ductal adenocarcinoma**

Target journal: *Molecular Diversity*.

> **Author information.** The author list, affiliations and corresponding-author details are not
> recorded in the manuscript file supplied with this repository and have deliberately not been
> reconstructed. They must be filled in by the authors here and in `CITATION.cff` before release.

---

## 1. Purpose

This repository contains the three executed notebooks that implement the compound-screening arm of
the study, together with the exact supporting script, the recorded software environments and the
integrity evidence needed to audit them.

The notebooks cover natural-product prescreening, descriptor-based classical QSAR with
scaffold-disjoint validation, and graph convolutional network (GCN) validation with QSAR–GCN
consensus prioritization. The downstream molecular docking, developability/ADMET/toxicity triage,
molecular-dynamics and miRNA analyses were performed with external tools described in the manuscript
Methods and are **not** part of these notebooks.

## 2. Workflow

```text
COCONUT export
   738,827 records
       |
       v
[1] Prescreening ................ 86,056 standardized, lead-like, PAINS-free compounds
       |
       v
[2] Classical QSAR ............. 86,056 screened -> 34,721 inside applicability domain
       |                          -> 31,020 at p >= 0.50 -> 6,232 transferred
       |                          (exact snapshot, SHA-256 8821947e...3673f4df)
       v
[3] GCN + consensus ............ 6,232 scored -> Tier 1 615 / Tier 2 3,742 /
                                  Tier 3 936 / Tier 4 939 -> Tier 1A 29
       |
       v
   docking (29) -> 17 at <= -9.0 kcal/mol -> ADMET/toxicity triage -> 3 x 100-ns MD
   (performed outside this repository)
```

## 3. Notebooks, in execution order

| Order | File | Input | Output |
|---|---|---|---|
| 1 | `notebooks/01_AURKB_COCONUT_Prescreening.ipynb` | COCONUT natural-product export | 86,056-compound prescreened library, filter audits, configuration and version logs, chemical-space figures |
| 2 | `notebooks/02_AURKB_Classical_QSAR_Reproduction.ipynb` | curated ChEMBL AURKB set, frozen 217-descriptor matrix, archived model artifacts, the Notebook 1 library | hash-verified reproduction status and the exact 6,232-row QSAR→GCN transfer |
| 3 | `notebooks/03_AURKB_GCN_Consensus_Screening.ipynb` | the 6,232-row transfer snapshot | calibrated GCN metrics, consensus scores, tier assignments, 29 Tier 1A candidates |

Each notebook opens with a documentation cell stating its purpose, workflow stage, inputs, outputs
and relationship to the adjacent stages.

## 4. Expected major counts

| Stage | Value |
|---|---|
| COCONUT records screened | 738,827 |
| Valid standardized structures | 735,561 |
| Prescreened compounds | 86,056 |
| Raw ChEMBL AURKB records | 3,248 |
| Curated compounds (active / inactive) | 1,854 (1,429 / 425) |
| Descriptors (raw / selected) | 217 / 165 |
| Random held-out ROC-AUC / PR-AUC / BA / MCC / Brier | 0.9063 / 0.9665 / 0.7903 / 0.6107 / 0.0915 |
| Scaffold-disjoint train / calibration / test | 1,062 / 348 / 444 |
| Scaffold-disjoint ROC-AUC / PR-AUC / BA / MCC / Brier | 0.8531 / 0.9542 / 0.6798 / 0.4279 / 0.1160 |
| Y-randomization | 30 permutations; observed CV ROC-AUC 0.888611; permuted mean 0.504881 ± 0.023899; empirical p ≈ 0.032258 |
| Inside descriptor applicability domain | 34,721 |
| Probability ≥ 0.50 | 31,020 |
| QSAR→GCN transfer | 6,232 rows, SHA-256 `8821947e92d8b209d291b627bae3b1d5068c6e2f1c0154f695abf0e73673f4df` |
| GCN random split (train / validation / test) | 1,112 / 371 / 371 |
| GCN scaffold split (train / validation / test) | 1,109 / 371 / 374 |
| Selected GCN architecture | graph layers [128, 128], dense 256, dropout 0.30, learning rate 0.0005 |
| Selected validation ROC-AUC | 0.8670 |
| Calibrated random-test / scaffold-test ROC-AUC | 0.8881 / 0.9058 |
| Consensus filters (GCN / uncertainty / structural support / alert-free) | 5,293 / 5,296 / 1,006 / 5,232 |
| Tiers 1 / 2 / 3 / 4 | 615 / 3,742 / 936 / 939 |
| Tier 1A | 29 |
| Docked candidates meeting ≤ −9.0 kcal/mol | 17 |
| Candidates advanced to 100-ns MD | 3 |

## 5. Required supporting script

`scripts/aurkb_prescreening_vscode.py` — the prescreening implementation imported by Notebook 1 as
`from aurkb_prescreening_vscode import PrescreenConfig, run_prescreening`. It is the original file,
copied unchanged.

SHA-256: `27f4979142422cb657278508bac89a91e6b63d42d209ca2ffec58ee8075b101e`

To re-run Notebook 1, place this script in the same directory as the notebook.

No other local script is imported by any of the three notebooks; every other import is a published
third-party package.

## 6. Frozen-artifact policy

The scientific state of this study is frozen.

- The notebooks here are presentation-only copies of the executed originals. Only Markdown text and
  Python comments were edited. Executable code, cell order, cell identifiers, execution counts and all
  stored outputs are unchanged.
- No notebook was re-executed to build this repository.
- Historical, manuscript-authoritative artifacts are never replaced by values recalculated in a current
  software environment. Where the two disagree, the historical value stands and the disagreement is
  recorded as software-drift evidence.
- Scientific warnings, environment records and run identifiers are retained deliberately.

Evidence for these statements is in `provenance/`.

## 7. Environment

The three notebooks ran in three different environments, and their pinned versions are mutually
incompatible in a single environment. Full detail, with the source of evidence for each version, is in
`environment/environment_versions.md`; the machine-readable record is
`environment/requirements-recorded.txt`.

Summary:

| Stage | Python | Key packages |
|---|---|---|
| Notebook 1 | 3.13.5 (Windows, VS Code) | pandas 2.2.3, numpy 2.2.5, RDKit 2026.03.2 |
| Notebook 2 | 3.12.13 (Windows, conda `research-py312`) | numpy 2.3.5, pandas 2.2.3, scikit-learn 1.8.0, xgboost 3.1.3, RDKit 2025.9.4 |
| Notebook 3 | 3.12.13 (Google Colab, Linux) | numpy 1.26.4, pandas 2.2.2, scikit-learn 1.6.1, TensorFlow 2.20.0, DeepChem 2.8.1.dev, RDKit 2026.03.2, `TF_USE_LEGACY_KERAS=1` |

The original historical QSAR training environment is only partially recoverable: scikit-learn 1.6.1
from joblib serialization metadata; the xgboost version was not recorded.

## 8. Data provenance

| Source | Used for | Shipped here |
|---|---|---|
| COCONUT natural-product database (`coconut_csv-05-2026.csv`) | prescreening input | no |
| ChEMBL, target CHEMBL2185 | AURKB IC50 bioactivity curation | no |
| RCSB PDB entry 4AF3 (AURKB–INCENP–VX-680, 2.75 Å) | docking receptor | no |
| miRTarBase 2025 | AURKB-regulatory miRNA evidence | no |
| Supplementary Data Files S1–S8 | derived results tables | not yet; see `data/supplementary/README.md` |

Redistribution terms for each third-party source are discussed in
`THIRD_PARTY_DATA_AND_LICENSE_NOTES.md`. No data file is redistributed here until its redistribution
status has been confirmed by the authors.

## 9. Repository structure

```text
AURKB-PDAC-computational-workflow/
    README.md                                  this file
    REPRODUCIBILITY.md                         lineage, reproducible vs preserved values, limitations
    THIRD_PARTY_DATA_AND_LICENSE_NOTES.md      third-party data sources and licence questions
    CITATION.cff                               citation metadata (author fields to be completed)
    MANIFEST.sha256                            SHA-256 of every shipped file
    .gitignore

    notebooks/                                 the three submission notebooks
    scripts/                                   the exact prescreening script imported by Notebook 1
    data/supplementary/                        placeholder; see its README
    environment/                               recorded environments and dependency records
    provenance/                                hashes, integrity report, comment-only diff, manifest
    journal/                                   Code Availability draft, Online Resource caption,
                                               archival checklist
    audit_private/                             internal audit output; excluded from Git by .gitignore
```

## 10. Reproduction limitations

This package is not a complete end-to-end re-execution of the study, and it does not claim to be.

- The COCONUT export, the raw ChEMBL extraction, the frozen descriptor matrix, the trained QSAR and
  GCN artifacts, the split assignments and the trained GCN ensemble weights are not included.
- The complete historical all-screened QSAR output no longer exists, so the upstream counts 34,721 and
  31,020 and the exact re-selection of the 6,232 candidates cannot be regenerated.
- Descriptor regeneration under a current RDKit build changes `BertzCT` and `NumHAcceptors`, so the
  frozen descriptor matrix is the authoritative input rather than a recomputable one.
- Fresh model fitting in a modern environment is recorded to disagree with the archived historical
  metrics; those disagreements are retained as evidence, not corrected.
- Docking, ADMET/toxicity, molecular dynamics and miRNA analyses were performed with external tools
  and are outside these notebooks.

What can be verified independently, and how, is listed in `REPRODUCIBILITY.md` sections 3 and 7.

## 11. Citation

Citation metadata is in `CITATION.cff`. The author fields and the DOI are placeholders until the
authors complete them.

```text
[Authors]. Chemotype-aware QSAR-GCN consensus screening and molecular modeling prioritize
natural-product-derived AURKB-targeting candidates for pancreatic ductal adenocarcinoma.
Molecular Diversity, [year]. DOI: [to be assigned]
```

## 12. Use of AI assistance

The submission-preparation work in this repository — notebook Markdown cleanup, comment cleanup,
integrity checking and documentation — was carried out with AI assistance (Claude, Anthropic). No
scientific result, model, prediction, descriptor, structure, score or reported value was generated,
altered or recalculated by that assistance. The AI assistance is not an author of the study.
