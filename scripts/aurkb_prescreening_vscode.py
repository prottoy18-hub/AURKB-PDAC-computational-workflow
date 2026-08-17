#!/usr/bin/env python3
"""
Publication-ready prescreening workflow for COCONUT/natural-product libraries
prior to AURKB QSAR/GCN screening.

This script is designed to run in VS Code or any local Python environment.
It performs reproducible structure standardization, descriptor calculation,
kinase-like physicochemical filtering, nucleic-acid intercalation-risk mitigation,
optional PAINS removal, optional chemical-superclass enrichment, and full audit logging.

Recommended usage:
python aurkb_prescreening_vscode.py \
  --input "C:/path/to/coconut_csv-05-2026.csv" \
  --output-root "C:/path/to/AURKB_Project/prescreening_runs" \
  --chunksize 100000

The main output used by Notebook 2 is:
<run_dir>/Data/Prescreening_coconut_AURKB.csv
"""

from __future__ import annotations

import argparse
import csv
import gc
import json
import logging
import math
import os
import platform
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from tqdm.auto import tqdm

# Matplotlib is imported only when plotting, to keep CLI startup light.

from rdkit import Chem, RDLogger, rdBase
from rdkit.Chem import AllChem, Crippen, Descriptors, Lipinski, QED, rdMolDescriptors
from rdkit.Chem.FilterCatalog import FilterCatalog, FilterCatalogParams

try:
    from rdkit.Chem.MolStandardize import rdMolStandardize
except Exception as exc:  # pragma: no cover - import location differs across RDKit builds
    rdMolStandardize = None
    print(f"WARNING: rdMolStandardize could not be imported: {exc}")

RDLogger.DisableLog("rdApp.*")


@dataclass
class PrescreenConfig:
    """User-editable configuration for robust prescreening."""

    input_file: str
    output_root: str = "AURKB_Prescreening_Runs"
    run_name: Optional[str] = None
    chunksize: int = 100_000
    encoding: str = "utf-8"

    # Core kinase-like and oral/lead-like physicochemical window.
    mw_min: float = 250.0
    mw_max: float = 550.0
    logp_min: float = 1.0
    logp_max: float = 5.0
    tpsa_min: float = 70.0
    tpsa_max: float = 140.0
    rotb_max: int = 10
    qed_min: float = 0.50

    # Hinge-binding/kinase-like capacity. This is intentionally permissive:
    # it avoids requiring a donor because many kinase hinge-binding motifs are acceptor-dominant.
    hba_min: int = 1
    hetero_atoms_min: int = 2
    ring_count_min: int = 1

    # Nucleic-acid/RNA intercalation-risk mitigation. These do NOT prove RNA selectivity;
    # they reduce highly planar/aromatic/promiscuous scaffolds before QSAR screening.
    fsp3_min: float = 0.15
    aromatic_rings_max: int = 4

    # Medicinal chemistry alerts.
    remove_pains: bool = True

    # Optional COCONUT class-based enrichment. Keep False for less biased screening;
    # set True only when you explicitly want a smaller natural-product-class enriched set.
    apply_superclass_filter: bool = False
    target_superclasses: List[str] = field(default_factory=lambda: [
        "Alkaloids and derivatives",
        "Phenylpropanoids and polyketides",
        "Organoheterocyclic compounds",
        "Benzenoids",
    ])

    # Optional AURKB reference-ligand similarity annotation/filter.
    # The file should contain a SMILES column. Use only curated active AURKB inhibitors if filtering.
    aurkb_reference_file: Optional[str] = None
    similarity_threshold: Optional[float] = None  # e.g., 0.15 or 0.20; None means annotate only/no filtering.
    max_reference_ligands: int = 500

    # Output controls.
    write_parquet: bool = True
    make_figures: bool = True
    save_all_structural_pass: bool = True

    # Deduplication.
    deduplicate_by_standardized_smiles: bool = True


def setup_run_dirs(config: PrescreenConfig) -> Dict[str, Path]:
    """Create a timestamped run directory with Data/Figures/Logs subfolders."""
    if config.run_name is None:
        config.run_name = f"AURKB_prescreen_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    root = Path(config.output_root).expanduser().resolve()
    run_dir = root / config.run_name
    dirs = {
        "run": run_dir,
        "data": run_dir / "Data",
        "figures": run_dir / "Figures",
        "logs": run_dir / "Logs",
    }
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)
    return dirs


def setup_logging(log_dir: Path) -> None:
    """Configure file and console logging."""
    log_file = log_dir / "prescreening.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(log_file, mode="w", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
        force=True,
    )


def detect_delimiter(path: Path, encoding: str = "utf-8") -> str:
    """Detect delimiter from the first lines of a CSV/TSV file."""
    with path.open("r", encoding=encoding, errors="ignore", newline="") as handle:
        sample = handle.read(8192)
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=[",", "\t", ";", "|"])
        return dialect.delimiter
    except Exception:
        return "\t" if "\t" in sample.splitlines()[0] else ","


def normalize_columns(columns: Iterable[str]) -> List[str]:
    """Normalize dataframe column names for robust detection."""
    return [str(c).replace('"', "").replace("'", "").strip() for c in columns]


def find_column(columns: Sequence[str], candidates: Sequence[str]) -> Optional[str]:
    """Return the first matching column name using case-insensitive exact matching."""
    lower_map = {c.lower(): c for c in columns}
    for cand in candidates:
        if cand.lower() in lower_map:
            return lower_map[cand.lower()]
    return None


def build_pains_catalog() -> Optional[FilterCatalog]:
    """Build RDKit PAINS filter catalog."""
    try:
        params = FilterCatalogParams()
        params.AddCatalog(FilterCatalogParams.FilterCatalogs.PAINS_A)
        params.AddCatalog(FilterCatalogParams.FilterCatalogs.PAINS_B)
        params.AddCatalog(FilterCatalogParams.FilterCatalogs.PAINS_C)
        return FilterCatalog(params)
    except Exception as exc:
        logging.warning("PAINS catalog could not be created and will be skipped: %s", exc)
        return None


class MoleculeProcessor:
    """Standardize molecules and calculate RDKit descriptors."""

    def __init__(self, remove_pains: bool = True):
        self.remove_pains = remove_pains
        self.pains_catalog = build_pains_catalog() if remove_pains else None
        if rdMolStandardize is not None:
            self.largest_fragment_chooser = rdMolStandardize.LargestFragmentChooser()
            self.uncharger = rdMolStandardize.Uncharger()
        else:
            self.largest_fragment_chooser = None
            self.uncharger = None

    def standardize(self, smiles: object) -> Tuple[Optional[Chem.Mol], Optional[str]]:
        """Parse and standardize a SMILES string; return RDKit Mol and canonical SMILES."""
        if pd.isna(smiles):
            return None, None
        smi = str(smiles).strip()
        if not smi or smi.lower() in {"nan", "none", "null"}:
            return None, None

        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            return None, None

        try:
            if rdMolStandardize is not None:
                mol = rdMolStandardize.Cleanup(mol)
                mol = self.largest_fragment_chooser.choose(mol)
                mol = self.uncharger.uncharge(mol)
            Chem.SanitizeMol(mol)
            std_smi = Chem.MolToSmiles(mol, canonical=True, isomericSmiles=True)
            return mol, std_smi
        except Exception:
            return None, None

    def has_pains(self, mol: Chem.Mol) -> bool:
        if self.pains_catalog is None:
            return False
        try:
            return bool(self.pains_catalog.HasMatch(mol))
        except Exception:
            return False

    def descriptors(self, mol: Chem.Mol) -> Dict[str, object]:
        """Calculate reproducible RDKit descriptors used in prescreening."""
        return {
            "rdkit_mw": float(Descriptors.MolWt(mol)),
            "rdkit_logp": float(Crippen.MolLogP(mol)),
            "rdkit_tpsa": float(rdMolDescriptors.CalcTPSA(mol)),
            "rdkit_rotatable_bonds": int(Lipinski.NumRotatableBonds(mol)),
            "rdkit_qed": float(QED.qed(mol)),
            "rdkit_fsp3": float(rdMolDescriptors.CalcFractionCSP3(mol)),
            "rdkit_aromatic_rings": int(rdMolDescriptors.CalcNumAromaticRings(mol)),
            "rdkit_ring_count": int(rdMolDescriptors.CalcNumRings(mol)),
            "rdkit_hbd": int(Lipinski.NumHDonors(mol)),
            "rdkit_hba": int(Lipinski.NumHAcceptors(mol)),
            "rdkit_hetero_atoms": int(rdMolDescriptors.CalcNumHeteroatoms(mol)),
            "rdkit_heavy_atoms": int(rdMolDescriptors.CalcNumHeavyAtoms(mol)),
            "rdkit_aromatic_heterocycles": int(rdMolDescriptors.CalcNumAromaticHeterocycles(mol)),
            "pains_alert": self.has_pains(mol),
        }


def load_reference_fingerprints(reference_file: Optional[str], max_reference_ligands: int = 500) -> List[object]:
    """Load optional AURKB reference ligand Morgan fingerprints for similarity annotation."""
    if reference_file is None:
        return []

    path = Path(reference_file).expanduser().resolve()
    if not path.exists():
        logging.warning("AURKB reference file not found; similarity annotation skipped: %s", path)
        return []

    ref_df = pd.read_csv(path)
    ref_df.columns = normalize_columns(ref_df.columns)
    smi_col = find_column(ref_df.columns, ["smiles", "canonical_smiles", "standardized_smiles", "SMILES"])
    if smi_col is None:
        logging.warning("AURKB reference file lacks a SMILES column; similarity annotation skipped.")
        return []

    fps = []
    for smi in ref_df[smi_col].dropna().astype(str).head(max_reference_ligands):
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            continue
        fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=2048)
        fps.append(fp)

    logging.info("Loaded %d AURKB reference ligand fingerprints for similarity annotation.", len(fps))
    return fps


def max_tanimoto_to_reference(mol: Chem.Mol, reference_fps: Sequence[object]) -> float:
    """Calculate maximum Morgan fingerprint Tanimoto similarity to optional references."""
    if not reference_fps:
        return float("nan")
    from rdkit import DataStructs

    fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=2048)
    sims = DataStructs.BulkTanimotoSimilarity(fp, list(reference_fps))
    return float(max(sims)) if sims else float("nan")


def superclass_allowed(value: object, allowed: Sequence[str]) -> bool:
    """Case-insensitive chemical superclass check."""
    if pd.isna(value):
        return False
    v = str(value).strip().lower()
    allowed_lower = {a.lower() for a in allowed}
    return v in allowed_lower


def evaluate_filters(row: Dict[str, object], config: PrescreenConfig) -> Dict[str, bool]:
    """Evaluate all prescreening criteria for a standardized molecule."""
    flags = {
        "pass_mw": config.mw_min <= row["rdkit_mw"] <= config.mw_max,
        "pass_logp": config.logp_min <= row["rdkit_logp"] <= config.logp_max,
        "pass_tpsa": config.tpsa_min <= row["rdkit_tpsa"] <= config.tpsa_max,
        "pass_rotatable_bonds": row["rdkit_rotatable_bonds"] <= config.rotb_max,
        "pass_qed": row["rdkit_qed"] >= config.qed_min,
        "pass_hba": row["rdkit_hba"] >= config.hba_min,
        "pass_hetero_atoms": row["rdkit_hetero_atoms"] >= config.hetero_atoms_min,
        "pass_ring_count": row["rdkit_ring_count"] >= config.ring_count_min,
        "pass_fsp3": row["rdkit_fsp3"] >= config.fsp3_min,
        "pass_aromatic_rings": row["rdkit_aromatic_rings"] <= config.aromatic_rings_max,
        "pass_pains": (not bool(row["pains_alert"])) if config.remove_pains else True,
    }

    if config.similarity_threshold is not None and not math.isnan(float(row.get("max_tanimoto_aurkb_ref", float("nan")))):
        flags["pass_aurkb_similarity"] = row["max_tanimoto_aurkb_ref"] >= config.similarity_threshold
    else:
        flags["pass_aurkb_similarity"] = True

    return flags


def sequential_filter_counts(df: pd.DataFrame, filter_columns: Sequence[str]) -> List[Dict[str, object]]:
    """Create an audit trail showing remaining compounds after each criterion."""
    remaining = pd.Series(True, index=df.index)
    rows = []
    n_start = len(df)
    rows.append({"step": "standardized_valid", "remaining": int(n_start), "removed_at_step": 0})
    for col in filter_columns:
        before = int(remaining.sum())
        remaining &= df[col].fillna(False).astype(bool)
        after = int(remaining.sum())
        rows.append({"step": col, "remaining": after, "removed_at_step": before - after})
    return rows


def process_chunk(
    chunk: pd.DataFrame,
    config: PrescreenConfig,
    processor: MoleculeProcessor,
    reference_fps: Sequence[object],
    seen_smiles: set,
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, int]]:
    """Process one input chunk and return final-pass and structural-pass dataframes plus counters."""
    chunk.columns = normalize_columns(chunk.columns)
    smi_col = find_column(chunk.columns, ["canonical_smiles", "standardized_smiles", "smiles", "SMILES"])
    id_col = find_column(chunk.columns, ["identifier", "id", "coconut_id", "Coconut ID", "molecule_id"])
    name_col = find_column(chunk.columns, ["name", "molecule_name", "compound_name"])
    class_col = find_column(chunk.columns, ["chemical_super_class", "superclass", "chemical_superclass"])

    counters = {
        "input_rows": int(len(chunk)),
        "missing_smiles_column": 0,
        "invalid_smiles": 0,
        "duplicates_removed": 0,
        "standardized_valid": 0,
        "structural_pass": 0,
        "final_pass": 0,
    }

    if smi_col is None:
        counters["missing_smiles_column"] = int(len(chunk))
        return pd.DataFrame(), pd.DataFrame(), counters

    records: List[Dict[str, object]] = []
    for _, source_row in chunk.iterrows():
        mol, std_smi = processor.standardize(source_row.get(smi_col))
        if mol is None or std_smi is None:
            counters["invalid_smiles"] += 1
            continue

        if config.deduplicate_by_standardized_smiles:
            if std_smi in seen_smiles:
                counters["duplicates_removed"] += 1
                continue
            seen_smiles.add(std_smi)

        desc = processor.descriptors(mol)
        record: Dict[str, object] = {
            "identifier": source_row.get(id_col) if id_col else np.nan,
            "name": source_row.get(name_col) if name_col else np.nan,
            "smiles_original": source_row.get(smi_col),
            "smiles": std_smi,
            "chemical_super_class": source_row.get(class_col) if class_col else np.nan,
        }
        record.update(desc)

        if reference_fps:
            record["max_tanimoto_aurkb_ref"] = max_tanimoto_to_reference(mol, reference_fps)
        else:
            record["max_tanimoto_aurkb_ref"] = np.nan

        flags = evaluate_filters(record, config)
        record.update(flags)
        record["pass_core_structural_filters"] = all(flags.values())
        if config.apply_superclass_filter and class_col is not None:
            record["pass_superclass_filter"] = superclass_allowed(record["chemical_super_class"], config.target_superclasses)
        elif config.apply_superclass_filter and class_col is None:
            record["pass_superclass_filter"] = False
        else:
            record["pass_superclass_filter"] = True

        record["pass_final_prescreen"] = bool(record["pass_core_structural_filters"] and record["pass_superclass_filter"])
        records.append(record)

    if not records:
        return pd.DataFrame(), pd.DataFrame(), counters

    df = pd.DataFrame(records)
    counters["standardized_valid"] = int(len(df))
    structural_df = df[df["pass_core_structural_filters"]].copy()
    final_df = df[df["pass_final_prescreen"]].copy()
    counters["structural_pass"] = int(len(structural_df))
    counters["final_pass"] = int(len(final_df))

    return final_df, structural_df, counters


def save_environment(config: PrescreenConfig, dirs: Dict[str, Path], delimiter: str) -> None:
    """Save run configuration and package versions for reproducibility."""
    config_path = dirs["logs"] / "prescreening_config.json"
    with config_path.open("w", encoding="utf-8") as handle:
        json.dump(asdict(config), handle, indent=2)

    versions = {
        "python": sys.version,
        "platform": platform.platform(),
        "pandas": pd.__version__,
        "numpy": np.__version__,
        "rdkit": rdBase.rdkitVersion,
        "input_file": str(Path(config.input_file).expanduser().resolve()),
        "detected_delimiter": delimiter,
        "run_timestamp": datetime.now().isoformat(),
    }
    with (dirs["logs"] / "software_versions.json").open("w", encoding="utf-8") as handle:
        json.dump(versions, handle, indent=2)


def make_summary_tables_and_figures(final_df: pd.DataFrame, structural_df: pd.DataFrame, dirs: Dict[str, Path], config: PrescreenConfig) -> None:
    """Save chemical-space summary and publication-resolution diagnostic figures."""
    if final_df.empty:
        return

    descriptor_cols = [
        "rdkit_mw", "rdkit_logp", "rdkit_tpsa", "rdkit_rotatable_bonds", "rdkit_qed",
        "rdkit_fsp3", "rdkit_aromatic_rings", "rdkit_hbd", "rdkit_hba", "rdkit_hetero_atoms",
        "max_tanimoto_aurkb_ref",
    ]
    available = [c for c in descriptor_cols if c in final_df.columns]
    summary = final_df[available].describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]).T
    summary.to_csv(dirs["data"] / "Prescreening_chemical_space_summary.csv")

    if not config.make_figures:
        return

    import matplotlib.pyplot as plt

    plot_specs = [
        ("rdkit_mw", "Molecular weight (Da)", "01_molecular_weight_distribution.png"),
        ("rdkit_logp", "RDKit Crippen LogP", "02_logp_distribution.png"),
        ("rdkit_tpsa", "TPSA (Å²)", "03_tpsa_distribution.png"),
        ("rdkit_qed", "QED", "04_qed_distribution.png"),
        ("rdkit_fsp3", "Fraction Csp³", "05_fsp3_distribution.png"),
    ]
    for col, xlabel, filename in plot_specs:
        if col not in final_df.columns:
            continue
        plt.figure(figsize=(7, 5))
        plt.hist(final_df[col].dropna().values, bins=40)
        plt.xlabel(xlabel)
        plt.ylabel("Number of compounds")
        plt.title(f"Prescreened AURKB library: {xlabel}")
        plt.tight_layout()
        plt.savefig(dirs["figures"] / filename, dpi=300)
        plt.close()

    # Chemical superclass bar chart only if informative.
    if "chemical_super_class" in final_df.columns and final_df["chemical_super_class"].notna().any():
        counts = final_df["chemical_super_class"].fillna("Unknown").value_counts().head(20)
        plt.figure(figsize=(8, max(5, 0.3 * len(counts))))
        plt.barh(range(len(counts)), counts.values)
        plt.yticks(range(len(counts)), counts.index)
        plt.xlabel("Number of compounds")
        plt.title("Top chemical superclasses in prescreened set")
        plt.gca().invert_yaxis()
        plt.tight_layout()
        plt.savefig(dirs["figures"] / "06_chemical_superclass_distribution.png", dpi=300)
        plt.close()


def run_prescreening(config: PrescreenConfig) -> Path:
    """Main prescreening runner. Returns the path to Prescreening_coconut_AURKB.csv."""
    input_path = Path(config.input_file).expanduser().resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    dirs = setup_run_dirs(config)
    setup_logging(dirs["logs"])

    logging.info("Starting AURKB publication-ready prescreening.")
    logging.info("Input file: %s", input_path)
    logging.info("Run directory: %s", dirs["run"])

    delimiter = detect_delimiter(input_path, config.encoding)
    save_environment(config, dirs, delimiter)
    logging.info("Detected delimiter: %r", delimiter)

    processor = MoleculeProcessor(remove_pains=config.remove_pains)
    reference_fps = load_reference_fingerprints(config.aurkb_reference_file, config.max_reference_ligands)

    reader = pd.read_csv(
        input_path,
        sep=delimiter,
        chunksize=config.chunksize,
        low_memory=False,
        encoding=config.encoding,
        encoding_errors="ignore",
    )

    final_chunks: List[pd.DataFrame] = []
    structural_chunks: List[pd.DataFrame] = []
    seen_smiles: set = set()
    audit_rows: List[Dict[str, object]] = []
    t0 = time.time()

    for chunk_idx, chunk in enumerate(tqdm(reader, desc="Processing COCONUT chunks", unit="chunk"), start=1):
        final_df, structural_df, counters = process_chunk(chunk, config, processor, reference_fps, seen_smiles)
        counters["chunk"] = chunk_idx
        audit_rows.append(counters)

        if not structural_df.empty and config.save_all_structural_pass:
            structural_chunks.append(structural_df)
        if not final_df.empty:
            final_chunks.append(final_df)

        if chunk_idx % 5 == 0:
            total_input = sum(r["input_rows"] for r in audit_rows)
            total_final = sum(r["final_pass"] for r in audit_rows)
            logging.info("Processed %s rows; cumulative final pass = %s", f"{total_input:,}", f"{total_final:,}")

        del chunk, final_df, structural_df
        gc.collect()

    audit_df = pd.DataFrame(audit_rows)
    audit_df.to_csv(dirs["data"] / "Prescreening_chunk_audit.csv", index=False)

    if final_chunks:
        final_all = pd.concat(final_chunks, ignore_index=True)
    else:
        final_all = pd.DataFrame()

    if structural_chunks:
        structural_all = pd.concat(structural_chunks, ignore_index=True)
    else:
        structural_all = pd.DataFrame()

    # A global final deduplication is retained as an additional safeguard.
    if not final_all.empty and config.deduplicate_by_standardized_smiles:
        final_all = final_all.drop_duplicates(subset=["smiles"]).reset_index(drop=True)
    if not structural_all.empty and config.deduplicate_by_standardized_smiles:
        structural_all = structural_all.drop_duplicates(subset=["smiles"]).reset_index(drop=True)

    # Reorder columns to make downstream QSAR notebooks easier.
    preferred_cols = [
        "identifier", "name", "smiles", "smiles_original", "chemical_super_class",
        "rdkit_mw", "rdkit_logp", "rdkit_tpsa", "rdkit_rotatable_bonds", "rdkit_qed",
        "rdkit_fsp3", "rdkit_aromatic_rings", "rdkit_ring_count", "rdkit_hbd", "rdkit_hba",
        "rdkit_hetero_atoms", "rdkit_heavy_atoms", "rdkit_aromatic_heterocycles", "pains_alert",
        "max_tanimoto_aurkb_ref",
        "pass_core_structural_filters", "pass_superclass_filter", "pass_final_prescreen",
    ]
    other_cols = [c for c in final_all.columns if c not in preferred_cols]
    if not final_all.empty:
        final_all = final_all[[c for c in preferred_cols if c in final_all.columns] + other_cols]
    if not structural_all.empty:
        structural_all = structural_all[[c for c in preferred_cols if c in structural_all.columns] + [c for c in structural_all.columns if c not in preferred_cols]]

    output_csv = dirs["data"] / "Prescreening_coconut_AURKB.csv"
    final_all.to_csv(output_csv, index=False)
    logging.info("Saved final prescreened library: %s (%s compounds)", output_csv, f"{len(final_all):,}")

    if config.write_parquet:
        try:
            final_all.to_parquet(dirs["data"] / "Prescreening_coconut_AURKB.parquet", index=False)
        except Exception as exc:
            logging.warning("Could not write Parquet output: %s", exc)

    if config.save_all_structural_pass and not structural_all.empty:
        structural_csv = dirs["data"] / "Prescreening_coconut_AURKB_structural_all_classes.csv"
        structural_all.to_csv(structural_csv, index=False)
        logging.info("Saved structural-pass library before optional superclass filtering: %s (%s compounds)", structural_csv, f"{len(structural_all):,}")

    # Filter audit across the final standardized/structural dataframe.
    if not structural_all.empty:
        filter_cols = [
            "pass_mw", "pass_logp", "pass_tpsa", "pass_rotatable_bonds", "pass_qed",
            "pass_hba", "pass_hetero_atoms", "pass_ring_count", "pass_fsp3",
            "pass_aromatic_rings", "pass_pains", "pass_aurkb_similarity", "pass_superclass_filter",
        ]
        filter_cols = [c for c in filter_cols if c in structural_all.columns]
        # Structural_all already passed core filters, so sequential counts are most useful on all retained standardized rows,
        # but only structural pass rows were stored to limit disk usage. Chunk audit therefore remains the primary audit.
    
    aggregate = audit_df.drop(columns=["chunk"], errors="ignore").sum(numeric_only=True).to_dict()
    aggregate.update({
        "final_unique_compounds": int(len(final_all)),
        "structural_unique_compounds": int(len(structural_all)),
        "elapsed_seconds": round(time.time() - t0, 2),
    })
    with (dirs["data"] / "Prescreening_aggregate_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(aggregate, handle, indent=2)

    make_summary_tables_and_figures(final_all, structural_all, dirs, config)

    logging.info("Completed prescreening in %.2f seconds.", time.time() - t0)
    logging.info("Main output for Notebook 2: %s", output_csv)
    return output_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publication-ready AURKB COCONUT prescreening workflow.")
    parser.add_argument("--input", required=True, help="Path to COCONUT CSV/TSV file.")
    parser.add_argument("--output-root", default="AURKB_Prescreening_Runs", help="Directory where timestamped output run folder will be created.")
    parser.add_argument("--run-name", default=None, help="Optional run name. Default: timestamped folder.")
    parser.add_argument("--chunksize", type=int, default=100000, help="Rows per chunk. Increase on high-RAM machines.")
    parser.add_argument("--encoding", default="utf-8", help="Input file encoding.")
    parser.add_argument("--apply-superclass-filter", action="store_true", help="Restrict to selected COCONUT chemical superclasses.")
    parser.add_argument("--keep-pains", action="store_true", help="Do not remove PAINS-alert compounds.")
    parser.add_argument("--aurkb-reference-file", default=None, help="Optional CSV of curated AURKB inhibitor SMILES for similarity annotation.")
    parser.add_argument("--similarity-threshold", type=float, default=None, help="Optional minimum Tanimoto similarity to curated AURKB reference ligands.")
    parser.add_argument("--no-figures", action="store_true", help="Skip diagnostic figure generation.")
    parser.add_argument("--no-parquet", action="store_true", help="Skip Parquet output.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = PrescreenConfig(
        input_file=args.input,
        output_root=args.output_root,
        run_name=args.run_name,
        chunksize=args.chunksize,
        encoding=args.encoding,
        apply_superclass_filter=args.apply_superclass_filter,
        remove_pains=not args.keep_pains,
        aurkb_reference_file=args.aurkb_reference_file,
        similarity_threshold=args.similarity_threshold,
        make_figures=not args.no_figures,
        write_parquet=not args.no_parquet,
    )
    output_csv = run_prescreening(config)
    print(f"\n✅ Prescreening complete. Use this file in Notebook 2:\n{output_csv}")


if __name__ == "__main__":
    main()
