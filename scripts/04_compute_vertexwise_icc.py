"""
Step 4 (Exposé Abschnitt 5, RQ3): Vertex-wise ICC.

Fuer jeden Kortex-Vertex wird die Test-Retest-Reliabilitaet ueber alle
Probanden berechnet (participant x session Design, k=2 Sessions).

Hauptmass (laut Exposé): ICC(2,1), absolute agreement, two-way random
  -> beantwortet: bekommt derselbe Proband am selben Vertex einen
     aehnlichen Wert in beiden Sessions?

Ergaenzend: ICC(3,1), consistency, two-way mixed
  -> ignoriert systematische Mittelwertsunterschiede zwischen den
     Sessions und fragt nur nach der Rangordnung.

Formeln nach Shrout & Fleiss (1979), vektorisiert ueber alle Vertices
gleichzeitig (kein Python-Loop pro Vertex -> schnell).

Pairwise NaN-Handling: pro Vertex werden nur die Probanden verwendet,
die in BEIDEN Sessions einen validen (nicht-NaN) Wert haben. Die
Stichprobengroesse n_valid wird pro Vertex separat getrackt und fliesst
korrekt in die Freiheitsgrade ein.

Output (exakt nach Exposé-Namensschema):
  group_maps/icc/vertexwise_icc_left.func.gii
  group_maps/icc/vertexwise_icc_right.func.gii
  group_maps/icc/vertexwise_icc.func.gii        (L+R konkateniert,
                                                   praktisch fuer
                                                   schnelle Auswertung;
                                                   fuer wb_view bitte
                                                   die L/R Dateien nutzen)
  results/tables/icc_summary_table.csv
"""

import nibabel as nib
import numpy as np
import glob
import os
import csv

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (RAW_TEST_DIR as TEST_DIR, RAW_RETEST_DIR as RETEST_DIR,
                    TABLES_DIR as OUT_TABLE_DIR)
import os
OUT_ICC_DIR = os.path.join(__import__('config').GROUP_MAPS_DIR, "icc")

L_START, L_END = 0, 29696
R_START, R_END = 29696, 59412

ICC_THRESHOLDS = [0.40, 0.60, 0.75]


def subject_id_from_filename(path):
    return os.path.basename(path)[:6]


def load_cortex_matrix(directory):
    """Laedt alle CIFTI-Dateien eines Ordners, sortiert nach Subject-ID.
    Gibt (subject_ids, matrix[n_subj, 59412]) zurueck."""
    files = sorted(glob.glob(os.path.join(directory, "*.dscalar.nii")))
    subj_ids = [subject_id_from_filename(f) for f in files]
    mat = np.full((len(files), 59412), np.nan, dtype=np.float64)
    for i, f in enumerate(files):
        img = nib.load(f)
        mat[i] = img.get_fdata()[0, :59412]
    return subj_ids, mat


def compute_icc_vertexwise(X1, X2):
    """X1, X2: (n_subj, n_vert) Arrays fuer Session 1 (test) und 2 (retest).
    Gibt ICC21 (absolute agreement), ICC31 (consistency) und n_valid
    pro Vertex zurueck, alle Shape (n_vert,)."""

    valid = ~(np.isnan(X1) | np.isnan(X2))          # (n_subj, n_vert)
    n_valid = valid.sum(axis=0).astype(np.float64)  # (n_vert,)

    X1z = np.where(valid, X1, 0.0)
    X2z = np.where(valid, X2, 0.0)

    sum1 = X1z.sum(axis=0)
    sum2 = X2z.sum(axis=0)
    grand_sum = sum1 + sum2
    n_total = 2.0 * n_valid

    with np.errstate(invalid="ignore", divide="ignore"):
        GM = grand_sum / n_total

        Si = np.where(valid, (X1z + X2z) / 2.0, 0.0)
        SS_subjects = 2.0 * np.sum(valid * (Si - GM[None, :]) ** 2, axis=0)

        M1 = sum1 / n_valid
        M2 = sum2 / n_valid
        SS_sessions = n_valid * ((M1 - GM) ** 2 + (M2 - GM) ** 2)

        SS_total = (
            np.sum(valid * (X1z - GM[None, :]) ** 2, axis=0)
            + np.sum(valid * (X2z - GM[None, :]) ** 2, axis=0)
        )
        SS_error = SS_total - SS_subjects - SS_sessions

        df_subjects = n_valid - 1.0
        df_sessions = 1.0
        df_error = (n_valid - 1.0) * 1.0  # (n-1)(k-1), k=2

        MSR = SS_subjects / df_subjects
        MSC = SS_sessions / df_sessions
        MSE = SS_error / df_error

        k = 2.0
        icc21 = (MSR - MSE) / (MSR + (k - 1.0) * MSE + k * (MSC - MSE) / n_valid)
        icc31 = (MSR - MSE) / (MSR + (k - 1.0) * MSE)

    # Vertices mit zu wenig validen Probanden (n_valid < 3) als NaN markieren
    too_few = n_valid < 3
    icc21 = np.where(too_few, np.nan, icc21)
    icc31 = np.where(too_few, np.nan, icc31)

    return icc21, icc31, n_valid


def save_gifti(data, path):
    da = nib.gifti.GiftiDataArray(
        data=data.astype(np.float32),
        intent=nib.nifti1.intent_codes["NIFTI_INTENT_NONE"],
        datatype="NIFTI_TYPE_FLOAT32",
    )
    nib.save(nib.gifti.GiftiImage(darrays=[da]), path)


def summarize(icc_values, label):
    valid = icc_values[~np.isnan(icc_values)]
    print(f"\n{label}:")
    print(f"  n valide Vertices: {len(valid)} / {len(icc_values)}")
    print(f"  mean:   {np.mean(valid):.4f}")
    print(f"  median: {np.median(valid):.4f}")
    print(f"  range:  {np.min(valid):.4f} bis {np.max(valid):.4f}")
    pct_above = {}
    for thr in ICC_THRESHOLDS:
        pct = 100.0 * np.sum(valid >= thr) / len(valid)
        pct_above[thr] = pct
        print(f"  % Vertices >= {thr}: {pct:.1f}%")
    return {
        "n_valid_vertices": len(valid),
        "mean": float(np.mean(valid)),
        "median": float(np.median(valid)),
        "min": float(np.min(valid)),
        "max": float(np.max(valid)),
        **{f"pct_above_{thr}": pct_above[thr] for thr in ICC_THRESHOLDS},
    }


if __name__ == "__main__":
    os.makedirs(OUT_ICC_DIR, exist_ok=True)
    os.makedirs(OUT_TABLE_DIR, exist_ok=True)

    print("Lade Test-Daten...")
    subj_test, X_test = load_cortex_matrix(TEST_DIR)
    print(f"  {len(subj_test)} Probanden geladen.")

    print("Lade Retest-Daten...")
    subj_retest, X_retest = load_cortex_matrix(RETEST_DIR)
    print(f"  {len(subj_retest)} Probanden geladen.")

    # Sicherheitscheck: Probanden-Reihenfolge muss identisch sein
    assert subj_test == subj_retest, (
        "Subject-ID-Reihenfolge stimmt zwischen Test und Retest nicht ueberein!\n"
        f"Test:   {subj_test}\nRetest: {subj_retest}"
    )
    print(f"\nSubject-IDs stimmen ueberein: N = {len(subj_test)}")

    print("\nBerechne vertex-wise ICC (vektorisiert ueber alle 59412 Vertices)...")
    icc21, icc31, n_valid = compute_icc_vertexwise(X_test, X_retest)

    summary_abs = summarize(icc21, "ICC(2,1) absolute agreement (Hauptmass)")
    summary_cons = summarize(icc31, "ICC(3,1) consistency (ergaenzend)")

    print(f"\nProbanden pro Vertex (median): {np.median(n_valid):.0f} von {len(subj_test)}")

    # -----------------------------------------------------------------
    # Speichern: L/R getrennt (anatomisch korrekt fuer wb_view)
    # -----------------------------------------------------------------
    save_gifti(icc21[L_START:L_END], os.path.join(OUT_ICC_DIR, "vertexwise_icc_left.func.gii"))
    save_gifti(icc21[R_START:R_END], os.path.join(OUT_ICC_DIR, "vertexwise_icc_right.func.gii"))
    # Kombinierte Datei (L+R konkateniert) fuer schnelle Weiterverarbeitung
    save_gifti(icc21, os.path.join(OUT_ICC_DIR, "vertexwise_icc.func.gii"))

    # Consistency-ICC zusaetzlich speichern (nicht im Exposé-Namensschema
    # explizit gefordert, aber fuer die Ergebnisdarstellung nuetzlich)
    save_gifti(icc31[L_START:L_END], os.path.join(OUT_ICC_DIR, "vertexwise_icc_consistency_left.func.gii"))
    save_gifti(icc31[R_START:R_END], os.path.join(OUT_ICC_DIR, "vertexwise_icc_consistency_right.func.gii"))

    print(f"\nGIFTI-Dateien gespeichert in: {OUT_ICC_DIR}")

    # -----------------------------------------------------------------
    # Summary-Tabelle
    # -----------------------------------------------------------------
    table_path = os.path.join(OUT_TABLE_DIR, "icc_summary_table.csv")
    with open(table_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["icc_type", "measure", "value"])
        for k, v in summary_abs.items():
            writer.writerow(["ICC(2,1)_absolute_agreement", k, v])
        for k, v in summary_cons.items():
            writer.writerow(["ICC(3,1)_consistency", k, v])
    print(f"Summary-Tabelle gespeichert: {table_path}")

    print("\nFertig.")
