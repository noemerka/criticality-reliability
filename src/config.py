"""
Global project configuration.

All project paths are defined here to avoid hard-coded paths in scripts.
"""

from pathlib import Path
import os

# =============================================================================
# Project directories
# =============================================================================

# Root directory of the project
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# =============================================================================
# Data directories
# =============================================================================

# Data directory is read from an environment variable.
# If the variable is not set, use ./data as a fallback.
DATA_DIR = Path(
    os.environ.get(
        "CRITICALITY_DATA",
        PROJECT_ROOT / "data",
    )
)

TEST_DIR = DATA_DIR / "hcp_test"
RETEST_DIR = DATA_DIR / "hcp_retest"

if not TEST_DIR.exists():
    raise FileNotFoundError(
        f"Test directory does not exist: {TEST_DIR}"
    )

if not RETEST_DIR.exists():
    raise FileNotFoundError(
        f"Retest directory does not exist: {RETEST_DIR}"
    )

# =============================================================================
# Surface / atlas directory (e.g. Yeo-7 network labels)
# =============================================================================

# Previously hard-coded as /home/noemerka/criticality_project/surfaces
# in several scripts. Now configurable like DATA_DIR, with the same
# environment-variable fallback pattern.
SURFACES_DIR = Path(
    os.environ.get(
        "CRITICALITY_SURFACES",
        PROJECT_ROOT / "data" / "surfaces",
    )
)

YEO_LABELS_FILE = SURFACES_DIR / "yeo7_fslr32k_labels.npy"

# fsLR32k surface geometry (S1200 group-average), used for rendering
# CIFTI cortical maps as brain surface figures.
SURFACE_LEFT_INFLATED = (
    SURFACES_DIR / "S1200.L.midthickness_MSMAll.32k_fs_LR.surf.gii"
)
SURFACE_RIGHT_INFLATED = (
    SURFACES_DIR / "S1200.R.midthickness_MSMAll.32k_fs_LR.surf.gii"
)

# =============================================================================
# Output directories
# =============================================================================

RESULTS_DIR = PROJECT_ROOT / "results"

MAPS_DIR = RESULTS_DIR / "maps"
TABLES_DIR = RESULTS_DIR / "tables"
FIGURES_DIR = RESULTS_DIR / "figures"

# =============================================================================
# Create output directories automatically
# =============================================================================

for directory in (
    RESULTS_DIR,
    MAPS_DIR,
    TABLES_DIR,
    FIGURES_DIR,
):
    directory.mkdir(parents=True, exist_ok=True)