# Online Resource caption — draft for author review

For the computational Online Resource (Electronic Supplementary Material) accompanying the
*Molecular Diversity* submission. Draft text; to be reviewed by the authors.

---

## Caption

> **Online Resource — Computational notebooks and reproducibility documentation.**
> Executed Jupyter notebooks implementing the compound-screening arm of the study, with the supporting
> script, the recorded software environments and the integrity documentation.
> **Notebook 1 (AURKB-focused COCONUT prescreening)** standardizes the COCONUT natural-product library
> with RDKit and applies the kinase-oriented lead-like, PAINS-free prescreening window, reducing
> 738,827 records to 86,056 compounds.
> **Notebook 2 (AURKB classical QSAR and reproducibility workflow)** reproduces the descriptor-based
> QSAR workflow under provenance control: curation audit, SHA-256 verification of the frozen
> 217-descriptor matrix, leakage-controlled model comparison, sigmoid-calibrated random held-out
> validation, 30-permutation Y-randomization, applicability-domain reconstruction, the corrected
> scaffold-disjoint validation branch, and verification of the exact 6,232-row QSAR–GCN transfer
> snapshot.
> **Notebook 3 (AURKB DeepChem GCN and QSAR–GCN consensus screening)** trains and calibrates the graph
> convolutional network, benchmarks it against ECFP baselines, quantifies seed-ensemble uncertainty and
> performs the rank-based consensus prioritization that yields 615 Tier 1 and 29 Tier 1A candidates.
> The notebooks are supplied as executed, with their original outputs, execution counts, environment
> records and warnings retained. Accompanying files document the lineage between stages, the values
> that can be verified exactly, the values preserved as historical artifacts, and the known
> software-version sensitivities. The docking, ADMET/toxicity, molecular-dynamics and miRNA analyses
> were performed with the external software described in the Methods and are not implemented in these
> notebooks.

## Compact variant

> **Online Resource — Computational notebooks and reproducibility documentation.** Three executed
> Jupyter notebooks covering COCONUT prescreening (738,827 → 86,056 compounds), provenance-controlled
> descriptor-based QSAR with scaffold-disjoint validation and hash-verified transfer of 6,232
> candidates, and DeepChem GCN validation with QSAR–GCN consensus prioritization (615 Tier 1; 29
> Tier 1A), together with the prescreening script, the recorded execution environments and integrity
> documentation. Notebooks are supplied as executed, with original outputs retained.

## Contents of the Online Resource

```text
README.md                                  scope, workflow, execution order, expected counts, limitations
REPRODUCIBILITY.md                         stage lineage; reproducible vs preserved values; drift
THIRD_PARTY_DATA_AND_LICENSE_NOTES.md      third-party sources and access routes
CITATION.cff                               citation metadata
MANIFEST.sha256                            SHA-256 of every included file

notebooks/01_AURKB_COCONUT_Prescreening.ipynb
notebooks/02_AURKB_Classical_QSAR_Reproduction.ipynb
notebooks/03_AURKB_GCN_Consensus_Screening.ipynb

scripts/aurkb_prescreening_vscode.py       imported by Notebook 1

environment/environment_versions.md        recorded versions with the evidence for each
environment/requirements-recorded.txt      machine-readable version record
environment/requirements_aurkb_prescreening.txt   the authors' declared dependency floor for stage 1

provenance/notebook_original_hashes.txt    SHA-256 of the three locked originals
provenance/notebook_integrity_report.json  per-notebook PASS/FAIL integrity comparison
provenance/comment_only_code_diff.tsv      every changed code-cell line, with comment-only proof
provenance/artifact_manifest_sha256.csv    SHA-256 of every included file, with roles
```

## Notes for the submission system

- The Online Resource contains no confidential manuscript or supplementary-manuscript document.
- It redistributes no third-party source data.
- File sizes are dominated by the two large executed notebooks (approximately 1.2 MB and 1.1 MB), which
  retain their stored outputs.
