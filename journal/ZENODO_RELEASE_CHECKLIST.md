# Archival release checklist

The intended end state is a frozen GitHub release deposited in a DOI-issuing repository (for example
Zenodo), cited from the manuscript's Code Availability statement.

**No DOI has been minted and none may be minted automatically.** The repository is private and must
stay private until a human has completed the checks below. Archival is the last step, not the first.

---

## Blocking items — archival cannot proceed while any of these is open

- [ ] **Docking-score discrepancy resolved.** The manuscript and Supplementary Table S12 report −11.8,
      −10.0 and −9.9 kcal/mol for CNP0570388.1, CNP0047084.1 and CNP0050461.1; Supplementary Data File
      S8 reports −11.4, −9.8 and −9.5. Each value has been traced to a real file, but they come from
      different docking campaigns and no single campaign reproduces the manuscript triple. See
      `../audit_private/DOCKING_SCORE_PROVENANCE_REPORT.md`,
      `../audit_private/DOCKING_CAMPAIGN_COMPARISON.tsv` and
      `../audit_private/DOCKING_AUTHOR_DECISION_BRIEF.md`. The authors must decide which campaign is of
      record and make the manuscript, S12 and S8 consistent. The correction options in the brief are
      documentation-only; none requires redocking, rescoring or rerunning any simulation.
- [ ] **Docking Methods description corrected.** Settle these together with the item above, since they
      arise from the same campaign heterogeneity:
      the reported grid dimensions come from one campaign and the reported exhaustiveness of 32 from
      another, and no preserved configuration combines them;
      the Methods state that both protein chains were retained, but the preserved receptor used for the
      29-compound campaign contains chain A only;
      the three 100-ns MD systems were not built on the same receptor (two include the INCENP peptide,
      one does not, as is also true of the VX-680 control);
      the VX-680 redocking control used a differently minimised receptor from the ligand campaigns.
- [ ] **Author metadata supplied.** The manuscript file contains no author block. `CITATION.cff` and
      `README.md` carry placeholders that must be replaced with the real author list, affiliations,
      ORCIDs and corresponding author. Do not archive with placeholders.
- [ ] **Licence chosen.** No licence has been selected for the authors' own code. Add a `LICENSE` file.
- [ ] **Third-party licence terms confirmed.** COCONUT and ChEMBL release versions must be recorded and
      their redistribution terms confirmed before any derived data file is added. See
      `../THIRD_PARTY_DATA_AND_LICENSE_NOTES.md`.

## Content checks

- [ ] `provenance/notebook_integrity_report.json` reports `overall_result: PASS`.
- [ ] The SHA-256 of each locked original notebook still matches
      `provenance/notebook_original_hashes.txt`.
- [ ] `MANIFEST.sha256` verifies against the working tree.
- [ ] No confidential manuscript or supplementary-manuscript DOCX is present anywhere in the tree.
- [ ] The excluded development notebook
      `02_AURKB_Classical_QSAR_ML_Modeling_PublicationReady_FINAL_MANUSCRIPT_REPRODUCIBLE.ipynb`
      (SHA-256 `06085c6669b4020dd9187c0b1986e7b023669160d5aa012d4d0919fa29bff7ab`) is not present.
- [ ] `audit_private/` is excluded by `.gitignore` and is absent from the release archive.
- [ ] No credential, token, `.env`, private key, session log, `.ipynb_checkpoints` directory or
      editor-history file is present.
- [ ] The three notebooks still open and render, and their stored outputs are intact.

## Release sequence, once the blocking items are closed

1. Complete the author metadata in `CITATION.cff` and `README.md`.
2. Add the chosen `LICENSE` file and any attribution statements the confirmed third-party licences
   require.
3. Update `MANIFEST.sha256` and `provenance/artifact_manifest_sha256.csv` for any file added or changed.
4. Commit on `main`. Do not rewrite history and do not force-push.
5. Have a named human reviewer confirm the checklist above. Record who signed off and when.
6. Change the repository visibility from private to public. This is a manual, human decision.
7. Create an annotated, immutable release tag (for example `v1.0.0`) from the reviewed commit.
8. Connect the DOI-issuing repository to the GitHub repository and let it archive that release.
9. Record the DOI and replace the `[DOI to be assigned]` placeholders in
   `journal/CODE_AVAILABILITY_DRAFT.md`, `README.md` and `CITATION.cff`.
10. Add the DOI to the manuscript's Code Availability statement before final submission or at proof
    stage.

## Notes on the deposit record

- Title: use the article title, or the repository title with the article title in the description.
- Authors: identical to the manuscript author list, in the same order, with ORCIDs.
- Version: match the GitHub release tag.
- Related identifier: link the deposit to the article DOI once it is known (`isSupplementTo`).
- Description: reuse `journal/ONLINE_RESOURCE_CAPTION.md`, and keep its statements about what is and is
  not reproducible.
- Licence in the deposit metadata must match the `LICENSE` file.

## What must not happen

- Do not mint a DOI before a human has signed off the blocking items.
- Do not make the repository public to make archival convenient.
- Do not delete or rewrite an earlier release, and do not force-push over one.
- Do not upload the confidential manuscript or supplementary-manuscript documents.
- Do not describe the deposit as fully reproducible. Several required scientific artifacts are absent
  and the historical all-screened QSAR output no longer exists; `REPRODUCIBILITY.md` section 6 states
  the limits.
