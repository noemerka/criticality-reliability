"""
Scatterplot of cortical group-level mean criticality values:
Test vs Retest.

Companion figure to 18_group_mean_correlation.py (which computes the
correlation but does not plot it), analogous to how
17_group_tmap_scatter.py complements 11_group_tmap_correlation.py.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
import nibabel as nib

from src.config import MAPS_DIR, FIGURES_DIR
from src.cifti_utils import get_cortical_mask


def main():

    # ------------------------------------------------------------
    # Load group mean maps
    # ------------------------------------------------------------

    test_img = nib.load(MAPS_DIR / "group_mean_test.dscalar.nii")
    retest_img = nib.load(MAPS_DIR / "group_mean_retest.dscalar.nii")

    test = test_img.get_fdata().squeeze()
    retest = retest_img.get_fdata().squeeze()

    # ------------------------------------------------------------
    # Cortical mask
    # ------------------------------------------------------------

    cortex_mask = get_cortical_mask(test_img)

    valid = (
        cortex_mask
        & np.isfinite(test)
        & np.isfinite(retest)
    )

    x = test[valid]
    y = retest[valid]

    # ------------------------------------------------------------
    # Correlation
    # ------------------------------------------------------------

    r, p = pearsonr(x, y)

    print(f"Cortical valid vertices: {len(x)}")
    print(f"Pearson r: {r:.6f}")
    print(f"P-value: {p:.3e}")

    # ------------------------------------------------------------
    # Plot
    # ------------------------------------------------------------

    plt.figure(figsize=(6, 6))

    plt.scatter(x, y, s=2, alpha=0.15)

    m, b = np.polyfit(x, y, 1)
    xx = np.linspace(x.min(), x.max(), 100)

    plt.plot(xx, m * xx + b, linewidth=2, label="Regression")

    plt.plot(
        [x.min(), x.max()],
        [x.min(), x.max()],
        linestyle="--",
        linewidth=1,
        label="Identity",
    )

    plt.xlabel("Test mean criticality")
    plt.ylabel("Retest mean criticality")
    plt.title(f"Cortical group-mean map replication\nPearson r = {r:.3f}")
    plt.legend()
    plt.tight_layout()

    output = FIGURES_DIR / "group_mean_scatter.png"
    plt.savefig(output, dpi=300)
    plt.close()

    print("\nScatterplot saved successfully.")
    print(output)


if __name__ == "__main__":
    main()