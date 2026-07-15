"""
Step 5 (Exposé Abschnitt 5, RQ4): Whole-map test-retest similarity.

Fuer jeden der 43 Probanden wird die individuelle Test-Map mit der
individuellen Retest-Map korreliert (Pearson, ueber alle 59412
Kortex-Vertices). Das ergibt einen "r_self"-Wert pro Proband.

r_self(sub_001) = corr(map_sub001_test, map_sub001_retest)

Pairwise NaN-Handling pro Proband (Vertices, die bei diesem Probanden
in mind. einer Session NaN sind, werden fuer diesen Probanden
ausgeschlossen).

Output:
  results/tables/whole_map_similarity.csv   (ein r_self Wert pro Proband)
  Konsolen-Summary: mean, sd, min, max, Verteilung
"""

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (RAW_TEST_DIR, RAW_RETEST_DIR,
                    TABLES_DIR, FIGURES_DIR)

import nibabel as nib
import numpy as np
import glob
import os
import csv

TEST_DIR = RAW_TEST_DIR
RETEST_DIR = RAW_RETEST_DIR
OUT_TABLE_DIR = TABLES_DIR
OUT_FIG_DIR = FIGURES_DIR


def subject_id_from_filename(path):
    return os.path.basename(path)[:6]


def load_cortex_matrix(directory):
    files = sorted(glob.glob(os.path.join(directory, "*.dscalar.nii")))
    subj_ids = [subject_id_from_filename(f) for f in files]
    mat = np.full((len(files), 59412), np.nan, dtype=np.float64)
    for i, f in enumerate(files):
        img = nib.load(f)
        mat[i] = img.get_fdata()[0, :59412]
    return subj_ids, mat


if __name__ == "__main__":
    os.makedirs(OUT_TABLE_DIR, exist_ok=True)
    os.makedirs(OUT_FIG_DIR, exist_ok=True)

    print("Lade Test-Daten...")
    subj_test, X_test = load_cortex_matrix(TEST_DIR)
    print("Lade Retest-Daten...")
    subj_retest, X_retest = load_cortex_matrix(RETEST_DIR)

    assert subj_test == subj_retest, "Subject-ID-Reihenfolge stimmt nicht ueberein!"
    n_subj = len(subj_test)
    print(f"\nN = {n_subj} Probanden\n")

    results = []
    for i in range(n_subj):
        a = X_test[i]
        b = X_retest[i]
        valid = ~(np.isnan(a) | np.isnan(b))
        r = np.corrcoef(a[valid], b[valid])[0, 1]
        n_valid_vert = int(valid.sum())
        results.append({
            "subject_id": subj_test[i],
            "r_self": r,
            "n_valid_vertices": n_valid_vert,
        })
        print(f"  {subj_test[i]}: r = {r:.4f}  (n_vertices = {n_valid_vert})")

    r_values = np.array([row["r_self"] for row in results])

    print(f"\n{'=' * 50}")
    print("ZUSAMMENFASSUNG: Whole-map test-retest similarity")
    print(f"{'=' * 50}")
    print(f"  mean:   {np.mean(r_values):.4f}")
    print(f"  sd:     {np.std(r_values, ddof=1):.4f}")
    print(f"  min:    {np.min(r_values):.4f}  ({results[np.argmin(r_values)]['subject_id']})")
    print(f"  max:    {np.max(r_values):.4f}  ({results[np.argmax(r_values)]['subject_id']})")
    print(f"  median: {np.median(r_values):.4f}")

    table_path = os.path.join(OUT_TABLE_DIR, "whole_map_similarity.csv")
    with open(table_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["subject_id", "r_self", "n_valid_vertices"])
        writer.writeheader()
        for row in results:
            writer.writerow(row)
    print(f"\nTabelle gespeichert: {table_path}")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.hist(r_values, bins=15, color="steelblue", edgecolor="white")
        ax.axvline(np.mean(r_values), color="red", linestyle="--",
                   label=f"mean = {np.mean(r_values):.3f}")
        ax.set_xlabel("Whole-map test-retest correlation (r_self)")
        ax.set_ylabel("Anzahl Probanden")
        ax.set_title("Verteilung der Within-Person Map-Similarity (N=43)")
        ax.legend()
        fig.tight_layout()
        fig_path = os.path.join(OUT_FIG_DIR, "whole_map_similarity_distribution.png")
        fig.savefig(fig_path, dpi=150)
        print(f"Histogramm gespeichert: {fig_path}")
    except ImportError:
        print("matplotlib nicht verfuegbar - Plot uebersprungen.")

    print("\nFertig.")
