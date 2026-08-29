"""
Compute the spatial correlation between the group-level
unthresholded test and retest t-maps.
"""

import numpy as np
import pandas as pd
import nibabel as nib
from scipy.stats import pearsonr

from src.config import MAPS_DIR, TABLES_DIR


def main():

    # ------------------------------------------------------------
    # Load t-maps
    # ------------------------------------------------------------

    test_img = nib.load(
        MAPS_DIR / "group_t_test.dscalar.nii"
    )

    retest_img = nib.load(
        MAPS_DIR / "group_t_retest.dscalar.nii"
    )

    test = test_img.get_fdata().squeeze()
    retest = retest_img.get_fdata().squeeze()

    # ------------------------------------------------------------
    # Remove invalid vertices
    # ------------------------------------------------------------

    valid = (
        np.isfinite(test)
        & np.isfinite(retest)
    )

    print(f"Valid vertices: {valid.sum()}")

    # ------------------------------------------------------------
    # Spatial correlation
    # ------------------------------------------------------------

    r, p = pearsonr(
        test[valid],
        retest[valid],
    )

    print(f"\nPearson r = {r:.6f}")
    print(f"P-value   = {p:.3e}")

    # ------------------------------------------------------------
    # Save results
    # ------------------------------------------------------------

    results = pd.DataFrame(
        {
            "Metric": [
                "Spatial Pearson correlation",
                "P-value",
                "Valid vertices",
            ],
            "Value": [
                r,
                p,
                valid.sum(),
            ],
        }
    )

    results.to_csv(
        TABLES_DIR / "group_tmap_correlation.csv",
        index=False,
    )

    print("\nResults saved successfully.")


if __name__ == "__main__":
    main()