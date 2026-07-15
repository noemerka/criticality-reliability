"""
07_create_figures.py
====================
Erstellt alle Thesis-Abbildungen.

Figure 1: Group-level criticality maps (Test + Retest)
         → manuell in wb_view (Anleitung wird ausgegeben)

Figure 2: Scatterplot Test vs. Retest Vertex t-Werte (RQ2)
         → matplotlib, automatisch

Figure 3: Vertex-wise ICC map
         → manuell in wb_view (Anleitung wird ausgegeben)

Figure 4: Histogramm Whole-map similarity (RQ4)
         → matplotlib, automatisch

Figure 5: Scatterplot Whole-cortex mean Test vs. Retest (RQ4)
         → matplotlib, automatisch

Outputs:
  results/figures/Figure2_GroupReplicationScatter.png
  results/figures/Figure4_MapSimilarityHistogram.png
  results/figures/Figure5_WholeCortexScatter.png
"""

import os
import glob
import numpy as np
import pandas as pd
import nibabel as nib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from scipy.stats import pearsonr, spearmanr, linregress

# ------------------------------------------------------------
# Konfiguration
# ------------------------------------------------------------

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (RAW_TEST_DIR as TEST_DIR, RAW_RETEST_DIR as RETEST_DIR,
                    TABLES_DIR as TABLE_DIR, FIGURES_DIR as FIG_DIR,
                    GROUP_MAPS_DIR)
os.makedirs(FIG_DIR, exist_ok=True)

STYLE = {
    "color_main":   "#2166AC",   # blau
    "color_line":   "#D73027",   # rot für Regressionslinie
    "color_diag":   "#888888",   # grau für Diagonale
    "fontsize":     11,
    "dpi":          200,
}

plt.rcParams.update({
    "font.family":  "sans-serif",
    "font.size":    STYLE["fontsize"],
    "axes.spines.top":   False,
    "axes.spines.right": False,
})


# ------------------------------------------------------------
# Hilfsfunktionen
# ------------------------------------------------------------

def load_cortex(path):
    return nib.load(path).get_fdata()[0, :59412].astype(np.float64)


def load_group_map(directory, kind="t"):
    """Laedt die group_{kind}_map aus dem group_maps-Ordner."""
    session = os.path.basename(directory.rstrip("/"))
    base = f"/home/noemerka/criticality_project/group_maps/{session}"
    l_path = os.path.join(base, f"group_{kind}_criticality_{session}_L.func.gii")
    r_path = os.path.join(base, f"group_{kind}_criticality_{session}_R.func.gii")
    l = nib.load(l_path).darrays[0].data.astype(np.float64)
    r = nib.load(r_path).darrays[0].data.astype(np.float64)
    return np.concatenate([l, r])


def add_stats_text(ax, r, rho=None, x=0.05, y=0.95):
    lines = [f"Pearson r = {r:.3f}"]
    if rho is not None:
        lines.append(f"Spearman ρ = {rho:.3f}")
    ax.text(x, y, "\n".join(lines),
            transform=ax.transAxes,
            va="top", ha="left",
            fontsize=STYLE["fontsize"] - 1,
            bbox=dict(boxstyle="round,pad=0.3",
                      facecolor="white", edgecolor="#cccccc", alpha=0.9))


# ============================================================
# Figure 2: Group-map replication scatterplot (RQ2)
# ============================================================

print("Erstelle Figure 2: Group-map replication scatter...")

t_test   = load_group_map("test",   kind="t")
t_retest = load_group_map("retest", kind="t")

valid = np.isfinite(t_test) & np.isfinite(t_retest)
x, y = t_test[valid], t_retest[valid]

r2, _   = pearsonr(x, y)
slope, intercept, *_ = linregress(x, y)
xfit = np.linspace(x.min(), x.max(), 200)

fig, ax = plt.subplots(figsize=(5.5, 5.5))
ax.scatter(x, y, s=1, alpha=0.08, color=STYLE["color_main"], rasterized=True)
lims = [min(x.min(), y.min()) - 1, max(x.max(), y.max()) + 1]
ax.plot(lims, lims, "--", color=STYLE["color_diag"],
        linewidth=1, label="identity")
ax.plot(xfit, slope * xfit + intercept,
        color=STYLE["color_line"], linewidth=1.5, label="regression")
ax.set_xlim(lims); ax.set_ylim(lims)
ax.set_xlabel("Group t-value – Test", fontsize=STYLE["fontsize"])
ax.set_ylabel("Group t-value – Retest", fontsize=STYLE["fontsize"])
ax.set_title("Figure 2: Spatial replication of group t-maps",
             fontsize=STYLE["fontsize"], pad=10)
ax.legend(fontsize=STYLE["fontsize"] - 1, frameon=False)
add_stats_text(ax, r2)
fig.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "Figure2_GroupReplicationScatter.png"),
            dpi=STYLE["dpi"])
plt.close()
print(f"  r = {r2:.3f}  (N = {valid.sum()} Vertices)")


# ============================================================
# Figure 4: Histogramm Whole-map similarity (RQ4)
# ============================================================

print("Erstelle Figure 4: Map similarity histogram...")

sim = pd.read_csv(os.path.join(TABLE_DIR, "whole_map_similarity_full.csv"))
r_vals   = sim["pearson_r"].values
rho_vals = sim["spearman_rho"].values

fig, ax = plt.subplots(figsize=(6, 4))
bins = np.linspace(0.7, 1.0, 16)
ax.hist(r_vals,   bins=bins, alpha=0.7,
        color=STYLE["color_main"],  label="Pearson r",    edgecolor="white")
ax.hist(rho_vals, bins=bins, alpha=0.5,
        color=STYLE["color_line"],  label="Spearman ρ",   edgecolor="white")
ax.axvline(r_vals.mean(),   color=STYLE["color_main"],
           linestyle="--", linewidth=1.5,
           label=f"Mean r = {r_vals.mean():.3f}")
ax.axvline(rho_vals.mean(), color=STYLE["color_line"],
           linestyle="--", linewidth=1.5,
           label=f"Mean ρ = {rho_vals.mean():.3f}")
ax.set_xlabel("Whole-map test-retest correlation", fontsize=STYLE["fontsize"])
ax.set_ylabel("Number of participants",            fontsize=STYLE["fontsize"])
ax.set_title("Figure 4: Distribution of individual map similarity (N = 43)",
             fontsize=STYLE["fontsize"], pad=10)
ax.legend(fontsize=STYLE["fontsize"] - 1, frameon=False)
fig.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "Figure4_MapSimilarityHistogram.png"),
            dpi=STYLE["dpi"])
plt.close()
print(f"  Pearson:  M={r_vals.mean():.3f}  SD={r_vals.std(ddof=1):.3f}")
print(f"  Spearman: M={rho_vals.mean():.3f}  SD={rho_vals.std(ddof=1):.3f}")


# ============================================================
# Figure 5: Whole-cortex mean scatterplot (RQ4)
# ============================================================

print("Erstelle Figure 5: Whole-cortex mean scatter...")

def load_whole_mean(directory):
    files = sorted(glob.glob(os.path.join(directory, "*.dscalar.nii")))
    return np.array([float(np.nanmean(nib.load(f).get_fdata()[0, :59412]))
                     for f in files])

wt = load_whole_mean(TEST_DIR)
wr = load_whole_mean(RETEST_DIR)

r5,   _ = pearsonr(wt, wr)
rho5, _ = spearmanr(wt, wr)
slope5, intercept5, *_ = linregress(wt, wr)
xfit5 = np.linspace(wt.min(), wt.max(), 200)

fig, ax = plt.subplots(figsize=(5.5, 5.5))
ax.scatter(wt, wr, s=50,
           color=STYLE["color_main"],
           edgecolors="white", linewidths=0.6, zorder=3)
lims5 = [min(wt.min(), wr.min()) - 2, max(wt.max(), wr.max()) + 2]
ax.plot(lims5, lims5, "--", color=STYLE["color_diag"],
        linewidth=1, label="identity", zorder=1)
ax.plot(xfit5, slope5 * xfit5 + intercept5,
        color=STYLE["color_line"], linewidth=1.8,
        label="regression", zorder=2)
ax.set_xlim(lims5); ax.set_ylim(lims5)
ax.set_xlabel("Whole-cortex mean criticality – Test",   fontsize=STYLE["fontsize"])
ax.set_ylabel("Whole-cortex mean criticality – Retest", fontsize=STYLE["fontsize"])
ax.set_title("Figure 5: Rank-order continuity, whole-cortex mean",
             fontsize=STYLE["fontsize"], pad=10)
ax.legend(fontsize=STYLE["fontsize"] - 1, frameon=False)
add_stats_text(ax, r5, rho5)
fig.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "Figure5_WholeCortexScatter.png"),
            dpi=STYLE["dpi"])
plt.close()
print(f"  Pearson r = {r5:.3f},  Spearman rho = {rho5:.3f}")


# ============================================================
# Anleitung fuer Figure 1 und 3 (wb_view)
# ============================================================

print()
print("=" * 60)
print("Figure 1 und 3: manuell in wb_view erstellen")
print("=" * 60)
print("""
Figure 1: Group-level criticality maps (Test + Retest)
-------------------------------------------------------
Dateien: group_maps/test/group_t_criticality_test_{L,R}.func.gii
         group_maps/retest/group_t_criticality_retest_{L,R}.func.gii
Surface: surfaces/S1200.{L,R}.midthickness_MSMAll.32k_fs_LR.surf.gii

wb_view Einstellungen:
  Palette: ROY-BIG-BL oder videen_style
  Pos Min: 2.0 (zeigt t >= 2)
  Pos Max: 100 (Abs Pct)
  Negative: aus
  Show Data Inside Thresholds: an
  Ansicht: Montage, Left+Lateral+Medial+Right
  Speichern: File > Capture Image > Figure1a_TestMap.png
             dann Retest laden > Figure1b_RetestMap.png

Figure 3: Vertex-wise ICC map
------------------------------
Dateien: group_maps/icc/vertexwise_icc_{left,right}.func.gii

wb_view Einstellungen:
  Palette: videen_style
  Modus: Fixed, Min=0.0, Max=1.0
  Negative: aus
  Show Data Inside Thresholds: an
  Ansicht: Montage, Left+Lateral+Medial+Right
  Speichern: File > Capture Image > Figure3_ICC_Map.png
""")

print("=" * 60)
print("Fertig. Automatisch erstellte Abbildungen:")
for fn in ["Figure2_GroupReplicationScatter.png",
           "Figure4_MapSimilarityHistogram.png",
           "Figure5_WholeCortexScatter.png"]:
    print(f"  {os.path.join(FIG_DIR, fn)}")
