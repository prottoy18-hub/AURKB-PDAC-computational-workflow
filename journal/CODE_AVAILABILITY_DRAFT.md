# Code Availability — draft for author review

The manuscript currently contains a Data Availability Statement but no Code Availability statement.
The text below is a draft. It states only what the repository actually contains. It must be reviewed
by the authors and must not be inserted into the manuscript automatically.

Placeholders in square brackets must be completed before submission.

---

## Draft statement

> **Code availability.** The three computational notebooks implementing the compound-screening arm of
> this study — natural-product prescreening, descriptor-based classical QSAR with scaffold-disjoint
> validation, and graph convolutional network validation with QSAR–GCN consensus prioritization — are
> available at [repository URL], together with the prescreening script imported by the first notebook,
> the recorded software environments of each execution, and integrity documentation. The notebooks are
> provided as executed, with their original outputs retained. An archived release will be deposited at
> [DOI to be assigned on archival].
>
> The notebooks are provided as a record of the executed workflow rather than as a fully re-executable
> pipeline. The COCONUT export, the raw ChEMBL extraction, the frozen 217-descriptor matrix, the
> trained QSAR and GCN artifacts and the trained ensemble weights are not redistributed; their sources
> and access routes are documented in the repository. The complete historical all-screened QSAR output
> no longer exists, so the intermediate counts of 34,721 applicability-domain-included and 31,020
> predicted-active compounds, and the exact re-selection of the 6,232 transferred candidates, cannot be
> regenerated; the exact 6,232-row transfer snapshot is instead preserved and verified by SHA-256
> (`8821947e92d8b209d291b627bae3b1d5068c6e2f1c0154f695abf0e73673f4df`). Descriptor regeneration under
> a current RDKit build alters the BertzCT and NumHAcceptors descriptors, so the frozen descriptor
> matrix was retained as the authoritative analytical input. The molecular docking, ADMET/toxicity
> triage, molecular-dynamics and miRNA analyses were performed with the external software described in
> the Methods and are not implemented in these notebooks.

## Shorter variant, if the journal limits statement length

> **Code availability.** The three computational screening notebooks, the prescreening script they
> depend on, the recorded execution environments and the integrity documentation are available at
> [repository URL]; an archived release will be deposited at [DOI to be assigned on archival]. The
> notebooks are provided as executed. Third-party source data (COCONUT, ChEMBL, PDB 4AF3, miRTarBase)
> and the trained model artifacts are not redistributed; their sources and the limits on re-execution
> are documented in the repository.

## Suggested addition on AI assistance, for the authors to consider

The journal may require disclosure of AI use. The following is factual for this repository:

> Preparation of the code repository (notebook Markdown and comment cleanup, integrity checking and
> documentation) was assisted by a large language model (Claude, Anthropic). No scientific result,
> model, prediction, descriptor, structure, docking score or reported value was generated or altered by
> that assistance.

Whether and where to place this disclosure is the authors' decision, and it should be reconciled with
any AI-use statement already present elsewhere in the manuscript.

## Facts this draft relies on

| Statement | Evidence |
|---|---|
| three notebooks, provided as executed | `provenance/notebook_integrity_report.json` (all PASS) |
| prescreening script included unchanged | SHA-256 `27f4979142422cb657278508bac89a91e6b63d42d209ca2ffec58ee8075b101e` |
| transfer snapshot hash | Notebook 2 transfer-confirmation output; Supplementary Data File S4 `README` and `Input_Hashes` |
| 34,721 / 31,020 not regenerable | Notebook 2 markdown "Authoritative interpretation"; Supplementary Table S6 |
| BertzCT / NumHAcceptors drift | manuscript Methods; Supplementary Data File S3 sheet `S3B_Selected_165_Descriptors` |
| docking, ADMET, MD, miRNA outside the notebooks | manuscript Methods; the notebooks contain no such code |

## Before this statement can be used

- The repository must be public, or the statement must describe the access route that will apply.
- The DOI placeholder must be replaced by a real archived DOI.
- The docking-score discrepancy recorded in `audit_private/DOCKING_SCORE_PROVENANCE_REPORT.md` must be
  resolved, because a public repository would expose docking evidence that is currently inconsistent
  with the manuscript.
