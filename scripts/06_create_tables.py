"""
06_create_tables.py
===================
Erstellt alle vier finalen Thesis-Tabellen aus den bereits
berechneten Analyseergebnissen.

Inputs (aus vorherigen Skripten):
  results/tables/group_map_replication.csv     (Step 3)
  results/tables/icc_summary_table.csv         (Step 4)
  results/tables/whole_map_similarity_full.csv (Step 5)
  results/tables/step6_trt_associations.csv    (Step 6)

Outputs:
  results/tables/Table1_GroupMapReplication.csv
  results/tables/Table2_ICCSummary.csv
  results/tables/Table3_MapSimilarity.csv
  results/tables/Table4_RankOrderContinuity.csv
"""

import os
import numpy as np
import pandas as pd

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TABLES_DIR as IN_DIR
OUT_DIR = IN_DIR
os.makedirs(OUT_DIR, exist_ok=True)


# ============================================================
# Table 1: Group-map replication (RQ2)
# ============================================================

rep_raw = pd.read_csv(os.path.join(IN_DIR, "group_map_replication.csv"))
rep = rep_raw.set_index("measure")["value"].to_dict()

table1 = pd.DataFrame([
    {"Measure": "Spatial correlation, unthresholded t-maps",
     "Value": f"r = {rep['r_unthresholded_t']:.3f}"},
    {"Measure": "Spatial correlation, group mean maps",
     "Value": f"r = {rep['r_mean_maps']:.3f}"},
    {"Measure": "Dice coefficient, thresholded maps (FDR-WB p < .05)",
     "Value": f"D = {rep['dice_thresholded']:.3f}"},
    {"Measure": "Jaccard index, Top-5% vertices (by t-value)",
     "Value": f"J = {rep['jaccard_top5pct']:.3f} "
              f"({int(rep['top5pct_overlap_n'])}/{int(rep['top5pct_n_vertices'])})"},
    {"Measure": "Jaccard index, Top-10% vertices (by t-value)",
     "Value": f"J = {rep['jaccard_top10pct']:.3f} "
              f"({int(rep['top10pct_overlap_n'])}/{int(rep['top10pct_n_vertices'])})"},
])

out1 = os.path.join(OUT_DIR, "Table1_GroupMapReplication.csv")
table1.to_csv(out1, index=False)
print("Table 1: Group-map replication")
print(table1.to_string(index=False))
print()


# ============================================================
# Table 2: ICC summary (RQ3)
# ============================================================

icc_raw = pd.read_csv(os.path.join(IN_DIR, "icc_summary_table.csv"))
icc = icc_raw[icc_raw["icc_type"] == "ICC(2,1)_absolute_agreement"].set_index("measure")["value"]

table2 = pd.DataFrame([
    {"Statistic": "Mean ICC",      "ICC(2,1)": f"{icc['mean']:.3f}"},
    {"Statistic": "Median ICC",    "ICC(2,1)": f"{icc['median']:.3f}"},
    {"Statistic": "Minimum",       "ICC(2,1)": f"{icc['min']:.3f}"},
    {"Statistic": "Maximum",       "ICC(2,1)": f"{icc['max']:.3f}"},
    {"Statistic": "% Vertices ≥ .40", "ICC(2,1)": f"{icc['pct_above_0.4']:.1f}%"},
    {"Statistic": "% Vertices ≥ .60", "ICC(2,1)": f"{icc['pct_above_0.6']:.1f}%"},
    {"Statistic": "% Vertices ≥ .75", "ICC(2,1)": f"{icc['pct_above_0.75']:.1f}%"},
])

out2 = os.path.join(OUT_DIR, "Table2_ICCSummary.csv")
table2.to_csv(out2, index=False)
print("Table 2: ICC summary")
print(table2.to_string(index=False))
print()


# ============================================================
# Table 3: Whole-map similarity (RQ4)
# ============================================================

sim = pd.read_csv(os.path.join(IN_DIR, "whole_map_similarity_full.csv"))

table3 = pd.DataFrame([
    {"Statistic": "Mean",   "Pearson r": f"{sim['pearson_r'].mean():.3f}",
                            "Spearman ρ": f"{sim['spearman_rho'].mean():.3f}"},
    {"Statistic": "SD",     "Pearson r": f"{sim['pearson_r'].std(ddof=1):.3f}",
                            "Spearman ρ": f"{sim['spearman_rho'].std(ddof=1):.3f}"},
    {"Statistic": "Minimum","Pearson r": f"{sim['pearson_r'].min():.3f}",
                            "Spearman ρ": f"{sim['spearman_rho'].min():.3f}"},
    {"Statistic": "Maximum","Pearson r": f"{sim['pearson_r'].max():.3f}",
                            "Spearman ρ": f"{sim['spearman_rho'].max():.3f}"},
    {"Statistic": "Median", "Pearson r": f"{sim['pearson_r'].median():.3f}",
                            "Spearman ρ": f"{sim['spearman_rho'].median():.3f}"},
])

out3 = os.path.join(OUT_DIR, "Table3_MapSimilarity.csv")
table3.to_csv(out3, index=False)
print("Table 3: Whole-map similarity")
print(table3.to_string(index=False))
print()


# ============================================================
# Table 4: Rank-order continuity (RQ4)
# ============================================================

assoc = pd.read_csv(os.path.join(IN_DIR, "step6_trt_associations.csv"))

LABELS = {
    "Whole_Cortex":      "Whole Cortex",
    "Visual":            "Visual (VIS)",
    "Somatomotor":       "Somatomotor (SM)",
    "Dorsal_Attention":  "Dorsal Attention (DAN)",
    "Ventral_Attention": "Ventral Attention (VAN)",
    "Limbic":            "Limbic (LIM)",
    "Frontoparietal":    "Frontoparietal (FPN)",
    "Default_Mode":      "Default Mode (DMN)",
}

rows = []
for _, row in assoc.iterrows():
    label = LABELS.get(row["measure"], row["measure"])
    rows.append({
        "Region":       label,
        "Pearson r":    f"{row['pearson_r']:.3f}",
        "Spearman ρ":   f"{row['spearman_rho']:.3f}",
        "ICC(2,1)":     f"{row['icc21']:.3f}",
        "N":            int(row["n"]),
    })

table4 = pd.DataFrame(rows)

out4 = os.path.join(OUT_DIR, "Table4_RankOrderContinuity.csv")
table4.to_csv(out4, index=False)
print("Table 4: Rank-order continuity")
print(table4.to_string(index=False))
print()

print("=" * 60)
print("Alle Tabellen gespeichert in:")
for f in [out1, out2, out3, out4]:
    print(f"  {f}")
