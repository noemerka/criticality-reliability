"""
Final quality control for test-retest reliability.

Checks:

1. ICC value range and missing values
2. Distribution of vertex-wise ICC values
3. Spatial Pearson and Spearman correlation between
   test and retest group t-maps
4. Test-retest difference and absolute agreement
"""

import numpy as np
import pandas as pd
import nibabel as nib
from scipy.stats import spearmanr, pearsonr

from src.config import MAPS_DIR, TABLES_DIR
from src.cifti_utils import get_cortical_mask


def main():

    # ------------------------------------------------------------
    # Load maps
    # ------------------------------------------------------------

    print("Loading maps...")

    test_img = nib.load(
        MAPS_DIR / "group_t_test.dscalar.nii"
    )

    retest_img = nib.load(
        MAPS_DIR / "group_t_retest.dscalar.nii"
    )

    icc_img = nib.load(
        MAPS_DIR / "vertexwise_icc.dscalar.nii"
    )

    test = test_img.get_fdata()[0]
    retest = retest_img.get_fdata()[0]
    icc = icc_img.get_fdata()[0]

    # ------------------------------------------------------------
    # Cortical mask
    # ------------------------------------------------------------

    cortex = get_cortical_mask(test_img)

    # ------------------------------------------------------------
    # Valid test-retest vertices
    # ------------------------------------------------------------

    valid_maps = (
        cortex
        & np.isfinite(test)
        & np.isfinite(retest)
    )

    test_valid = test[valid_maps]
    retest_valid = retest[valid_maps]

    n_valid_maps = len(test_valid)

    # ------------------------------------------------------------
    # Test-retest differences
    # ------------------------------------------------------------

    difference = test_valid - retest_valid

    absolute_difference = np.abs(difference)

    mean_test = np.mean(test_valid)
    mean_retest = np.mean(retest_valid)

    mean_difference = np.mean(difference)
    sd_difference = np.std(difference, ddof=1)

    mean_absolute_difference = np.mean(
        absolute_difference
    )

    median_absolute_difference = np.median(
        absolute_difference
    )

    max_absolute_difference = np.max(
        absolute_difference
    )

    # ------------------------------------------------------------
    # ICC quality control
    # ------------------------------------------------------------

    valid_icc = cortex & np.isfinite(icc)
    icc_valid = icc[valid_icc]

    n_cortical = int(cortex.sum())
    n_valid_icc = len(icc_valid)

    n_nan_icc = int(
        np.sum(cortex & ~np.isfinite(icc))
    )

    n_negative = int(
        np.sum(icc_valid < 0)
    )

    n_zero_one = int(
        np.sum(
            (icc_valid >= 0)
            & (icc_valid <= 1)
        )
    )

    n_above_one = int(
        np.sum(icc_valid > 1)
    )

    # ------------------------------------------------------------
    # ICC distribution
    # ------------------------------------------------------------

    categories = [
        (
            "ICC < 0",
            np.sum(icc_valid < 0)
        ),
        (
            "0 <= ICC < 0.40",
            np.sum(
                (icc_valid >= 0)
                & (icc_valid < 0.40)
            )
        ),
        (
            "0.40 <= ICC < 0.60",
            np.sum(
                (icc_valid >= 0.40)
                & (icc_valid < 0.60)
            )
        ),
        (
            "0.60 <= ICC < 0.75",
            np.sum(
                (icc_valid >= 0.60)
                & (icc_valid < 0.75)
            )
        ),
        (
            "0.75 <= ICC < 0.90",
            np.sum(
                (icc_valid >= 0.75)
                & (icc_valid < 0.90)
            )
        ),
        (
            "ICC >= 0.90",
            np.sum(
                icc_valid >= 0.90
            )
        ),
    ]

    distribution_rows = []

    for category, count in categories:

        percentage = (
            count / n_valid_icc * 100
        )

        distribution_rows.append(
            {
                "Category": category,
                "Vertices": int(count),
                "Percentage": percentage,
            }
        )

    distribution = pd.DataFrame(
        distribution_rows
    )

    # ------------------------------------------------------------
    # Spatial correlation
    # ------------------------------------------------------------

    print()
    print("Computing spatial correlations...")

    pearson_r, pearson_p = pearsonr(
        test_valid,
        retest_valid,
    )

    spearman_rho, spearman_p = spearmanr(
        test_valid,
        retest_valid,
    )

    # ------------------------------------------------------------
    # Summary table
    # ------------------------------------------------------------

    summary = pd.DataFrame(
        {
            "Metric": [
                "Cortical vertices",
                "Valid ICC vertices",
                "ICC NaN vertices",
                "ICC < 0 vertices",
                "ICC between 0 and 1",
                "ICC > 1 vertices",
                "Valid test-retest map vertices",
                "Mean test t",
                "Mean retest t",
                "Mean test-retest difference",
                "SD test-retest difference",
                "Mean absolute test-retest difference",
                "Median absolute test-retest difference",
                "Maximum absolute test-retest difference",
                "Pearson r",
                "Pearson p",
                "Spearman rho",
                "Spearman p",
            ],
            "Value": [
                n_cortical,
                n_valid_icc,
                n_nan_icc,
                n_negative,
                n_zero_one,
                n_above_one,
                n_valid_maps,
                mean_test,
                mean_retest,
                mean_difference,
                sd_difference,
                mean_absolute_difference,
                median_absolute_difference,
                max_absolute_difference,
                pearson_r,
                pearson_p,
                spearman_rho,
                spearman_p,
            ],
        }
    )

    # ------------------------------------------------------------
    # Save results
    # ------------------------------------------------------------

    summary_file = (
        TABLES_DIR / "reliability_qc_summary.csv"
    )

    distribution_file = (
        TABLES_DIR / "icc_distribution.csv"
    )

    summary.to_csv(
        summary_file,
        index=False,
    )

    distribution.to_csv(
        distribution_file,
        index=False,
    )

    # ------------------------------------------------------------
    # Print results
    # ------------------------------------------------------------

    print()
    print("=" * 60)
    print("FINAL RELIABILITY QUALITY CONTROL")
    print("=" * 60)

    print()
    print("ICC QUALITY CONTROL")
    print("-" * 60)

    print(
        f"Cortical vertices:       {n_cortical}"
    )
    print(
        f"Valid ICC vertices:      {n_valid_icc}"
    )
    print(
        f"ICC NaN vertices:        {n_nan_icc}"
    )
    print(
        f"ICC < 0:                 {n_negative}"
    )
    print(
        f"ICC 0-1:                 {n_zero_one}"
    )
    print(
        f"ICC > 1:                 {n_above_one}"
    )

    print()
    print("ICC DISTRIBUTION")
    print("-" * 60)

    print(
        distribution.to_string(index=False)
    )

    print()
    print("TEST-RETEST AGREEMENT")
    print("-" * 60)

    print(
        f"Valid map vertices:      {n_valid_maps}"
    )
    print(
        f"Mean test t:             {mean_test:.6f}"
    )
    print(
        f"Mean retest t:           {mean_retest:.6f}"
    )
    print(
        f"Mean difference:         {mean_difference:.6f}"
    )
    print(
        f"SD difference:           {sd_difference:.6f}"
    )
    print(
        f"Mean absolute difference:{mean_absolute_difference:.6f}"
    )
    print(
        f"Median absolute diff.:   {median_absolute_difference:.6f}"
    )
    print(
        f"Maximum absolute diff.:  {max_absolute_difference:.6f}"
    )

    print()
    print("SPATIAL TEST-RETEST CORRELATION")
    print("-" * 60)

    print(
        f"Pearson r:               {pearson_r:.6f}"
    )
    print(
        f"Pearson p:               {pearson_p:.3e}"
    )
    print(
        f"Spearman rho:            {spearman_rho:.6f}"
    )
    print(
        f"Spearman p:              {spearman_p:.3e}"
    )

    print()
    print("Files saved:")
    print(summary_file)
    print(distribution_file)

    print()
    print("QC completed successfully.")


if __name__ == "__main__":
    main()