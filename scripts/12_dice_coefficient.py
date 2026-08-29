"""
Compute Dice coefficient between thresholded
cortical group-level test and retest t-maps.
"""

import numpy as np
import nibabel as nib
import pandas as pd

from src.config import MAPS_DIR, TABLES_DIR
from src.cifti_utils import get_cortical_mask


def main():

    # ------------------------------------------------------------
    # Load thresholded maps
    # ------------------------------------------------------------

    test_img = nib.load(
        MAPS_DIR / "group_thresholded_t_test.dscalar.nii"
    )

    retest_img = nib.load(
        MAPS_DIR / "group_thresholded_t_retest.dscalar.nii"
    )

    test = test_img.get_fdata().squeeze()
    retest = retest_img.get_fdata().squeeze()

    # ------------------------------------------------------------
    # Cortical mask
    # ------------------------------------------------------------

    cortex_mask = get_cortical_mask(test_img)

    # ------------------------------------------------------------
    # Binary masks
    # ------------------------------------------------------------

    test_mask = (
        cortex_mask
        & np.isfinite(test)
    )

    retest_mask = (
        cortex_mask
        & np.isfinite(retest)
    )

    # ------------------------------------------------------------
    # Dice coefficient
    # ------------------------------------------------------------

    intersection = np.sum(
        test_mask & retest_mask
    )

    n_test = np.sum(test_mask)
    n_retest = np.sum(retest_mask)

    dice = (
        2 * intersection
        / (n_test + n_retest)
    )

    print(f"Cortical vertices:  {cortex_mask.sum()}")
    print(f"Test vertices:      {n_test}")
    print(f"Retest vertices:    {n_retest}")
    print(f"Overlap vertices:   {intersection}")

    print(f"\nDice coefficient = {dice:.6f}")

    # ------------------------------------------------------------
    # Save
    # ------------------------------------------------------------

    results = pd.DataFrame(
        {
            "Metric": [
                "Cortical vertices",
                "Test significant vertices",
                "Retest significant vertices",
                "Overlap vertices",
                "Dice coefficient",
            ],
            "Value": [
                cortex_mask.sum(),
                n_test,
                n_retest,
                intersection,
                dice,
            ],
        }
    )

    results.to_csv(
        TABLES_DIR / "dice_coefficient.csv",
        index=False,
    )

    print("\nResults saved successfully.")


if __name__ == "__main__":
    main()
