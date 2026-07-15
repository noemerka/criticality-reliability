"""
Step 3 (Exposé Abschnitt 5, RQ2): Group-map replication.

Primaeranalyse:
  - Spatial correlation (Pearson) zwischen unthresholded group t-maps
    (test vs. retest)
  - Spatial correlation (Pearson) zwischen group mean maps (test vs. retest)

Deskriptive Ergaenzung:
  - Dice-Koeffizient der thresholded maps (FDR-WB p < .05)
  - Overlap der Top 5% und Top 10% Vertices (nach t-Wert)

Input: die in Step 2 erzeugten .func.gii Dateien
       (group_maps/{session}/group_*_{L,R}.func.gii)

Output:
  results/tables/group_map_replication.csv
  ein Scatterplot test vs. retest (t-Werte) als Vorbereitung fuer Step 7
"""

import nibabel as nib
import numpy as np
import os
import csv

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GROUP_MAPS_DIR, TABLES_DIR as OUT_TABLE_DIR, FIGURES_DIR as OUT_FIG_DIR

TOP_PERCENTAGES = [5, 10]


def load_gifti_both_hemis(session, map_basename):
    """Laedt L+R und fuegt sie zu einem Kortex-Vektor zusammen (59412,)."""
    parts = []
    for hemi in ["L", "R"]:
        path = os.path.join(
            GROUP_MAPS_DIR, session, f"{map_basename}_{session}_{hemi}.func.gii"
        )
        img = nib.load(path)
        parts.append(img.darrays[0].data)
    return np.concatenate(parts)


def dice_coefficient(mask_a, mask_b):
    intersection = np.sum(mask_a & mask_b)
    return 2.0 * intersection / (np.sum(mask_a) + np.sum(mask_b))


def top_percent_overlap(values_a, values_b, pct):
    """Jaccard-Overlap der Top-pct% Vertices (nach Wert, hoechste zuerst)."""
    n = len(values_a)
    k = int(np.round(n * pct / 100.0))

    # NaNs ans Ende sortieren, damit sie nie in den Top-k landen
    order_a = np.argsort(-np.nan_to_num(values_a, nan=-np.inf))[:k]
    order_b = np.argsort(-np.nan_to_num(values_b, nan=-np.inf))[:k]

    set_a, set_b = set(order_a.tolist()), set(order_b.tolist())
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    jaccard = intersection / union if union > 0 else np.nan
    return jaccard, intersection, k


def pearson_ignore_nan(a, b):
    valid = ~(np.isnan(a) | np.isnan(b))
    return np.corrcoef(a[valid], b[valid])[0, 1], int(valid.sum())


if __name__ == "__main__":
    os.makedirs(OUT_TABLE_DIR, exist_ok=True)
    os.makedirs(OUT_FIG_DIR, exist_ok=True)

    print("Lade Group-Maps (Test und Retest)...")
    t_test = load_gifti_both_hemis("test", "group_t_criticality")
    t_retest = load_gifti_both_hemis("retest", "group_t_criticality")
    mean_test = load_gifti_both_hemis("test", "group_mean_criticality")
    mean_retest = load_gifti_both_hemis("retest", "group_mean_criticality")
    tthr_test = load_gifti_both_hemis("test", "group_thresholded_t_criticality")
    tthr_retest = load_gifti_both_hemis("retest", "group_thresholded_t_criticality")

    print(f"Vertices pro Map: {len(t_test)}")

    results = {}

    # -----------------------------------------------------------------
    # Primaeranalyse: spatial correlation (unthresholded)
    # -----------------------------------------------------------------
    r_t, n_t = pearson_ignore_nan(t_test, t_retest)
    r_mean, n_mean = pearson_ignore_nan(mean_test, mean_retest)

    print(f"\nSpatial correlation (unthresholded t-maps): r = {r_t:.4f} (n={n_t})")
    print(f"Spatial correlation (mean maps):             r = {r_mean:.4f} (n={n_mean})")

    results["r_unthresholded_t"] = r_t
    results["r_mean_maps"] = r_mean

    # -----------------------------------------------------------------
    # Deskriptive Ergaenzung: Dice der thresholded maps
    # -----------------------------------------------------------------
    mask_test = tthr_test != 0
    mask_retest = tthr_retest != 0
    dice = dice_coefficient(mask_test, mask_retest)
    print(f"\nDice-Koeffizient (FDR-WB thresholded maps): {dice:.4f}")
    print(f"  signifikante Vertices test:   {mask_test.sum()}")
    print(f"  signifikante Vertices retest: {mask_retest.sum()}")
    results["dice_thresholded"] = dice

    # -----------------------------------------------------------------
    # Top-X% Overlap (nach t-Wert, unthresholded)
    # -----------------------------------------------------------------
    print()
    for pct in TOP_PERCENTAGES:
        jaccard, intersection, k = top_percent_overlap(t_test, t_retest, pct)
        print(f"Top {pct}% Overlap: Jaccard = {jaccard:.4f} "
              f"({intersection}/{k} Vertices ueberlappen)")
        results[f"jaccard_top{pct}pct"] = jaccard
        results[f"top{pct}pct_n_vertices"] = k
        results[f"top{pct}pct_overlap_n"] = intersection

    # -----------------------------------------------------------------
    # Tabelle speichern
    # -----------------------------------------------------------------
    table_path = os.path.join(OUT_TABLE_DIR, "group_map_replication.csv")
    with open(table_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["measure", "value"])
        for k, v in results.items():
            writer.writerow([k, v])
    print(f"\nTabelle gespeichert: {table_path}")

    # -----------------------------------------------------------------
    # Scatterplot test vs retest (t-Werte) fuer spaetere Verwendung
    # -----------------------------------------------------------------
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        valid = ~(np.isnan(t_test) | np.isnan(t_retest))
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.scatter(t_test[valid], t_retest[valid], s=1, alpha=0.15, color="steelblue")
        lims = [
            min(t_test[valid].min(), t_retest[valid].min()),
            max(t_test[valid].max(), t_retest[valid].max()),
        ]
        ax.plot(lims, lims, "k--", linewidth=1, label="identity")
        ax.set_xlabel("Group t-value (Test)")
        ax.set_ylabel("Group t-value (Retest)")
        ax.set_title(f"Group-map replication (r = {r_t:.3f})")
        ax.legend()
        fig.tight_layout()
        fig_path = os.path.join(OUT_FIG_DIR, "group_map_replication_scatter.png")
        fig.savefig(fig_path, dpi=150)
        print(f"Scatterplot gespeichert: {fig_path}")
    except ImportError:
        print("matplotlib nicht verfuegbar - Scatterplot uebersprungen "
              "(pip install matplotlib --user falls benoetigt)")

    print("\nFertig.")
