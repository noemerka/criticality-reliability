
"""
Spatial correlation between the cortical group mean maps
(test vs. retest).
"""

import numpy as np
import pandas as pd
import nibabel as nib
from scipy.stats import pearsonr

from src.config import MAPS_DIR, TABLES_DIR
from src.cifti_utils import get_cortical_mask


def main():

    # ------------------------------------------------------------
    # Load group mean maps
    # ------------------------------------------------------------

    test_img = nib.load(
        MAPS_DIR / "group_mean_test.dscalar.nii"
    )

    retest_img = nib.load(
        MAPS_DIR / "group_mean_retest.dscalar.nii"
    )

    test = test_img.get_fdata()[0]
    retest = retest_img.get_fdata()[0]

    # ------------------------------------------------------------
    # Cortical mask
    # ------------------------------------------------------------

    cortex_mask = get_cortical_mask(test_img)

    # ------------------------------------------------------------
    # Keep valid cortical vertices
    # ------------------------------------------------------------

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
    # Save results
    # ------------------------------------------------------------

    results = pd.DataFrame(
        {
            "Metric": [
                "Cortical valid vertices",
                "Pearson r",
                "P-value",
            ],
            "Value": [
                len(x),
                r,
                p,
            ],
        }
    )

    results.to_csv(
        TABLES_DIR / "group_mean_correlation.csv",
        index=False,
    )

    print("\nResults saved successfully.")


if __name__ == "__main__":
    main()
