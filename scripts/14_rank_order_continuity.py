"""
Compute rank-order continuity of whole-cortex mean criticality.

Fixed: restricts the whole-cortex mean to cortical grayordinates
before averaging. The previous version used np.nanmean(test_data,
axis=1) over the full CIFTI grayordinate array, which could include
non-cortical positions for participants with finite values there
(same class of issue fixed in 13_whole_map_similarity.py).
"""

import numpy as np
import pandas as pd
import nibabel as nib
from scipy.stats import pearsonr, spearmanr

from src.config import TABLES_DIR
from src.io import load_dataset, find_subject_files
from src.cifti_utils import get_cortical_mask
from src.icc import compute_icc21


def main():

    # ------------------------------------------------------------
    # Load data
    # ------------------------------------------------------------

    test_data, retest_data, subject_ids = load_dataset()

    subjects = find_subject_files()
    reference_file = subjects[subject_ids[0]]["test"]
    reference_img = nib.load(reference_file)
    cortex_mask = get_cortical_mask(reference_img)

    print(f"Cortical grayordinates: {cortex_mask.sum()}")

    # ------------------------------------------------------------
    # Whole-cortex mean per participant (cortex only)
    # ------------------------------------------------------------

    test_mean = np.nanmean(test_data[:, cortex_mask], axis=1)
    retest_mean = np.nanmean(retest_data[:, cortex_mask], axis=1)

    # ------------------------------------------------------------
    # Correlations
    # ------------------------------------------------------------

    pearson_r, pearson_p = pearsonr(
        test_mean,
        retest_mean,
    )

    spearman_rho, spearman_p = spearmanr(
        test_mean,
        retest_mean,
    )

    icc = compute_icc21(
        test_mean,
        retest_mean,
    )

    # ------------------------------------------------------------
    # Save participant values
    # ------------------------------------------------------------

    participant_table = pd.DataFrame(
        {
            "Subject": subject_ids,
            "Test_mean": test_mean,
            "Retest_mean": retest_mean,
        }
    )

    participant_table.to_csv(
        TABLES_DIR / "whole_cortex_mean_values.csv",
        index=False,
    )

    # ------------------------------------------------------------
    # Save statistics
    # ------------------------------------------------------------

    stats = pd.DataFrame(
        {
            "Metric": [
                "Pearson r",
                "Pearson p",
                "Spearman rho",
                "Spearman p",
                "ICC(2,1)",
            ],
            "Value": [
                pearson_r,
                pearson_p,
                spearman_rho,
                spearman_p,
                icc,
            ],
        }
    )

    stats.to_csv(
        TABLES_DIR / "rank_order_continuity.csv",
        index=False,
    )

    # ------------------------------------------------------------
    # Print
    # ------------------------------------------------------------

    print("\nRank-order continuity completed.\n")

    print(stats)

    print("\nFirst five participants:\n")

    print(participant_table.head())


if __name__ == "__main__":
    main()