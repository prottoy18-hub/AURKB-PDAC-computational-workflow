# Supplementary data — not included

This directory is intentionally empty of data files.

Supplementary Data Files S1–S8 exist and were audited for this repository, but none of them has been
copied here. Two conditions had to be met before a file could be shipped, and neither is met yet:

1. **Redistribution status.** S1, S5, S6 and S8 carry COCONUT-derived structures; S2, S3 and S4 carry
   ChEMBL-derived records. The licence terms of the specific COCONUT and ChEMBL releases used by the
   study could not be established from project files. See `../../THIRD_PARTY_DATA_AND_LICENSE_NOTES.md`.
2. **Confidentiality.** The supplementary data workbooks are held in a directory marked confidential
   and are supplied to the journal through the article's supplementary material.

## What was audited, and where the audit lives

The files below were inspected read-only. Row counts and identifiers were verified; no value was
changed and no prediction was recalculated. Results are in
`../../audit_private/MANUSCRIPT_NOTEBOOK_DATA_CONSISTENCY_MATRIX.tsv`.

| File | Sheet(s) | Verified content |
|---|---|---|
| S1 Full prescreened AURKB natural-product library | `S1_Prescreening_coconut_AURKB_s` | 86,056 data rows, 35 columns |
| S2 curated AURKB ChEMBL training set and curation log | `Raw_ChEMBL_records`, `curated_AURKB_training_data`, `curation log` | 3,248 raw records; 1,854 curated compounds; 8-step curation log |
| S3 Authoritative descriptor package | `S3A_Frozen_217_Descriptors`, `S3B_Selected_165_Descriptors`, `S3C_Preprocessing_and_Provenanc` | 1,854 rows × 217 descriptors; 165 selected descriptors with per-descriptor RDKit drift columns |
| S4 QSAR provenance and exact transfer | `README`, `Exact_6232_Transfer`, `Y_Randomization`, `Reproduction_Status`, `Input_Hashes` | 6,232 transfer rows; snapshot SHA-256 `8821947e…3673f4df`; 30 Y-randomization permutations; 12 input artifacts with matching expected/actual hashes |
| S5 GCN–QSAR consensus, all candidates | `AURKB_GCN_QSAR_consensus_all_ca` | 6,232 candidate rows |
| S6 Novelty and duplicate-risk audit | `Tier1A_29_Audit`, `Prioritized_Top100_Audit` | 29 Tier 1A rows; 100 prioritized rows |
| S7 AURKB mature miRNA | `Sheet1` | 44 mature-miRNA rows |
| S8 Tier 1A molecular docking results | `Docking_29_Tier1A` | 29 docked Tier 1A rows; 17 flagged as meeting ≤ −9.0 kcal/mol |

A docking-score discrepancy between the manuscript / Supplementary Table S12 and S8 was investigated
separately; see `../../audit_private/DOCKING_SCORE_PROVENANCE_REPORT.md`. It must be resolved by the
authors before any docking data are published from this repository.

## Before adding files here

1. Confirm the COCONUT and ChEMBL licence terms for the releases used and record the release versions.
2. Confirm with the journal which files are distributed as supplementary material and which may also
   be mirrored in a code repository.
3. Resolve the docking-score discrepancy so that any published S8 is consistent with the manuscript.
4. Add each file's SHA-256 to `../../MANIFEST.sha256` and
   `../../provenance/artifact_manifest_sha256.csv`.
