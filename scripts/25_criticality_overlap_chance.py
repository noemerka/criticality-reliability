"""
Test whether the observed overlap of the highest-criticality
vertices between test and retest is greater than expected
by chance using the hypergeometric distribution.
"""

import numpy as np
import pandas as pd
import nibabel as nib
from scipy.stats import hypergeom

from src.config import MAPS_DIR, TABLES_DIR
from src.cifti_utils import get_cortical_mask


def main():

    # ------------------------------------------------------------
    # Load group mean criticality maps
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
    # Valid cortical vertices
    # ------------------------------------------------------------

    cortex = get_cortical_mask(test_img)

    valid = (
        cortex
        & np.isfinite(test)
        & np.isfinite(retest)
    )

    test = test[valid]
    retest = retest[valid]

    n = len(test)

    print(f"Valid cortical vertices: {n}")

    results = []

    # ------------------------------------------------------------
    # Top-percent overlap
    # ------------------------------------------------------------

    for percent in [5, 10]:

        k = int(np.ceil(percent / 100 * n))

        test_idx = np.argsort(test)[-k:]
        retest_idx = np.argsort(retest)[-k:]

        test_set = set(test_idx)
        retest_set = set(retest_idx)

        overlap = len(test_set & retest_set)

        observed_percent = overlap / k * 100

        # Expected overlap under random selection
        expected_count = k * k / n
        expected_percent = k / n * 100

        # Hypergeometric probability:
        # probability of observing >= the actual overlap
        p_value = hypergeom.sf(
            overlap - 1,
            n,
            k,
            k,
        )

        # Fold enrichment over chance
        enrichment = overlap / expected_count

        # Dice coefficient
        dice = (
            2 * overlap
            / (k + k)
        )

        results.append(
            {
                "Top (%)": percent,
                "N vertices": n,
                "Vertices per set": k,
                "Observed overlap": overlap,
                "Observed overlap (%)": observed_percent,
                "Expected overlap": expected_count,
                "Expected overlap (%)": expected_percent,
                "Dice coefficient": dice,
                "Enrichment": enrichment,
                "Hypergeometric p": p_value,
            }
        )

        print("\n" + "=" * 60)
        print(f"Top {percent}%")
        print("=" * 60)

        print(f"Vertices per set:       {k}")
        print(f"Observed overlap:       {overlap}")
        print(f"Observed overlap (%):   {observed_percent:.2f}")
        print(f"Expected overlap:       {expected_count:.2f}")
        print(f"Expected overlap (%):   {expected_percent:.2f}")
        print(f"Dice coefficient:       {dice:.4f}")
        print(f"Enrichment:             {enrichment:.2f}x")
        print(f"Hypergeometric p:       {p_value:.3e}")

    # ------------------------------------------------------------
    # Save results
    # ------------------------------------------------------------

    results = pd.DataFrame(results)

    results.to_csv(
        TABLES_DIR / "criticality_overlap_chance.csv",
        index=False,
    )

    print("\nResults saved successfully.")


if __name__ == "__main__":
    main()