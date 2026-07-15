"""
config.py
=========
Zentrale Pfad-Konfiguration. Hier EINMAL anpassen, alle Skripte
importieren von hier - keine hard-coded Pfade in den Skripten.
"""
import os

# ============================================================
# HIER ANPASSEN: Pfade zu den Rohdaten
# ============================================================
RAW_TEST_DIR   = "/home/groups/markett/hcpcrit/hcp_test"
RAW_RETEST_DIR = "/home/groups/markett/hcpcrit/hcp_retest"

# ============================================================
# AUTOMATISCH: Rest wird relativ zum Projekt-Root berechnet
# ============================================================
REPO_ROOT       = os.path.dirname(os.path.abspath(__file__))
DATA_DIR        = os.path.join(REPO_ROOT, "data")
SURFACES_DIR    = os.path.join(REPO_ROOT, "surfaces")
DERIVATIVES_DIR = os.path.join(REPO_ROOT, "derivatives")
GROUP_MAPS_DIR  = os.path.join(REPO_ROOT, "group_maps")
SWE_DIR         = os.path.join(REPO_ROOT, "swe_results")
RESULTS_DIR     = os.path.join(REPO_ROOT, "results")
TABLES_DIR      = os.path.join(RESULTS_DIR, "tables")
FIGURES_DIR     = os.path.join(RESULTS_DIR, "figures")
SCRIPTS_DIR     = os.path.join(REPO_ROOT, "scripts")

# Surfaces
SURF_L = os.path.join(REPO_ROOT, "surfaces",
    "S1200.L.midthickness_MSMAll.32k_fs_LR.surf.gii")
SURF_R = os.path.join(REPO_ROOT, "surfaces",
    "S1200.R.midthickness_MSMAll.32k_fs_LR.surf.gii")
AREA_L = os.path.join(REPO_ROOT, "surfaces",
    "S1200.L.midthickness_MSMAll.32k_fs_LR_area.func.gii")
AREA_R = os.path.join(REPO_ROOT, "surfaces",
    "S1200.R.midthickness_MSMAll.32k_fs_LR_area.func.gii")
YEO_LABELS = os.path.join(REPO_ROOT, "surfaces",
    "yeo7_fslr32k_labels.npy")

# Konstanten
N_VERT_L, N_VERT_R, N_VERT = 29696, 29716, 59412
N_MESH   = 32492
FDR_ALPHA   = 0.05
N_BOOTSTRAPS = 999
ICC_THRESHOLDS = [0.40, 0.60, 0.75]
YEO_NETWORKS = {
    1: "Visual", 2: "Somatomotor", 3: "Dorsal_Attention",
    4: "Ventral_Attention", 5: "Limbic",
    6: "Frontoparietal", 7: "Default_Mode",
}

for _d in [DERIVATIVES_DIR, GROUP_MAPS_DIR, SWE_DIR,
           RESULTS_DIR, TABLES_DIR, FIGURES_DIR]:
    os.makedirs(_d, exist_ok=True)
