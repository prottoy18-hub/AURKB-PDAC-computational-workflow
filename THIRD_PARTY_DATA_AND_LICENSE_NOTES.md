# Third-party data and licensing notes

This file records the third-party sources the study drew on and states plainly what could and could
not be established about redistribution. No licence has been invented, and no licence has been chosen
for the authors' own code.

**Nothing in this repository redistributes third-party source data.** Every third-party dataset below
is referenced by its origin and access route only.

---

## 1. Third-party sources used by the study

### COCONUT (COlleCtion of Open NatUral producTs)

- **Used for:** the natural-product library that was standardized and prescreened in Notebook 1. The
  study's input file is named `coconut_csv-05-2026.csv` (738,827 records).
- **Identifiers:** all compound identifiers of the form `CNP…` in this study are COCONUT identifiers.
- **Redistribution status:** *not established from project files.* No licence text, download receipt or
  terms-of-use record for the specific COCONUT export was found in the project.
- **How to obtain:** from the COCONUT project's own distribution channels. The exact export used here
  is a dated snapshot (`05-2026`); a later snapshot will not necessarily reproduce the same 86,056
  compounds.
- **Action required:** the authors must confirm the licence attached to the COCONUT release they
  downloaded before any COCONUT-derived structure file is published from this repository.

### ChEMBL

- **Used for:** AURKB bioactivity curation. Records were retrieved for target `CHEMBL2185`
  (3,248 raw records, curated to 1,854 unique compounds).
- **Redistribution status:** *not established from project files.* ChEMBL releases carry their own
  licence terms and an attribution requirement; the specific release version used was not recorded in
  the project, so the applicable terms cannot be stated here with confidence.
- **How to obtain:** query ChEMBL for target `CHEMBL2185` with the curation filters described in the
  manuscript Methods and in Supplementary Table S2 (exact `standard_relation` `=`, `standard_units`
  `nM`, `assay_type` `B`, RDKit standardization, deduplication by standardized InChIKey using the
  median activity).
- **Action required:** the authors must record the ChEMBL release version and confirm its licence and
  attribution requirements before publishing any ChEMBL-derived table.

### RCSB Protein Data Bank — entry 4AF3

- **Used for:** the AURKB receptor structure (AURKB in complex with the INCENP activation-domain
  peptide and VX-680; 2.75 Å) used for site-specific docking and as the basis of the MD systems.
- **Redistribution status:** PDB coordinate entries are distributed by the RCSB PDB under its own
  public terms. The specific terms applicable to redistribution of a *prepared and modified* receptor
  (`4AF3_A_clean_EM.pdbqt`) were not established from project files.
- **How to obtain:** download entry 4AF3 from the RCSB PDB, then follow the receptor-preparation steps
  in the manuscript Methods (Discovery Studio Visualizer 2021: remove VX-680, waters, the INCENP
  peptide and other non-essential heteroatoms; retain both chains; add polar hydrogens; assign Kollman
  charges; convert to PDBQT).
- **Note:** no PDB-derived structure is included in this repository.

### miRTarBase 2025

- **Used for:** experimentally supported human miRNAs targeting AURKB, in the parallel regulatory arm.
- **Redistribution status:** *not established from project files.*
- **How to obtain:** query miRTarBase for target gene AURKB, organism *Homo sapiens*.

### Prediction web services

SwissADME (`http://www.swissadme.ch`), admetSAR 3.0
(`http://lmmd.ecust.edu.cn/admetsar3/`) and ProTox 3.0 (`https://tox.charite.de`) were used as
external prediction services. Their outputs are reported in the supplementary tables. Terms of use for
redistributing their outputs were not established from project files.

### Software

RDKit, scikit-learn, XGBoost, DeepChem, TensorFlow, pandas, NumPy, matplotlib, Open Babel, PyRx,
AutoDock Vina, YASARA Structure, RNAfold (ViennaRNA), RNAComposer and BIOVIA Discovery Studio
Visualizer were used as tools. They are not redistributed here. Recorded versions are in
`environment/environment_versions.md`. Several of these are commercial or academically licensed
products; users must obtain their own licences.

---

## 2. Derived data produced by this study

Supplementary Data Files S1–S8 are derived results tables authored by the study team. They contain
compound identifiers and structures that originate from COCONUT (S1, S5, S6, S8) and from ChEMBL
(S2, S3, S4).

Because the redistribution terms of the underlying COCONUT and ChEMBL releases could not be
established from project files, **no supplementary data workbook has been copied into this
repository**. See `data/supplementary/README.md`.

The derived tables are in any case supplied to the journal as Supplementary Data Files and will be
distributed through the article.

---

## 3. Licence for the authors' own code

No licence has been chosen for the notebooks and the prescreening script in this repository. That
decision belongs to the authors and, where relevant, to their institution.

Before public release the authors must:

1. choose a licence for their own code and add it as a `LICENSE` file;
2. confirm the COCONUT and ChEMBL licence terms for the specific releases used, and record the release
   versions;
3. decide, in the light of (2), which derived data files may be published from this repository and
   which must be obtained through the journal's supplementary material instead;
4. add the attribution statements that the confirmed licences require.

Until step (1) is done, this repository has no licence and the default position — all rights reserved
— applies.
