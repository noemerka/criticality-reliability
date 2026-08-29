"""
Compute whole-map test-retest similarity for each participant.

Fixed: applies the cortical mask before computing each participant's
test-retest correlation. The previous version only filtered by
np.isfinite() without restricting to cortical grayordinates, which
allowed non-cortical positions to enter the correlation for
participants whose data happened to have finite values there. This
inflated the raw whole-map similarity (observed: ~0.94-0.98 unmasked
vs. ~0.88 masked). See 31_demeaned_whole_map_similarity.py for a
follow-up analysis that additionally removes the shared group-level
spatial pattern from each map before correlating.
"""

import numpy as np
import pandas as pd
import nibabel as nib
from scipy.stats import pearsonr

from src.config import TABLES_DIR
from src.io import load_dataset, find_subject_files
from src.cifti_utils import get_cortical_mask


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

    similarities = []

    # ------------------------------------------------------------
    # Compute participant-wise correlations (cortex only)
    # ------------------------------------------------------------

    for i, subject in enumerate(subject_ids):

        test = test_data[i]
        retest = retest_data[i]

        valid = (
            cortex_mask
            & np.isfinite(test)
            & np.isfinite(retest)
        )

        r, _ = pearsonr(
            test[valid],
            retest[valid],
        )

        similarities.append(
            {
                "Subject": subject,
                "Pearson_r": r,
            }
        )

    similarities = pd.DataFrame(similarities)

    # ------------------------------------------------------------
    # Save participant table
    # ------------------------------------------------------------

    similarities.to_csv(
        TABLES_DIR / "whole_map_similarity.csv",
        index=False,
    )

    # ------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------

    values = similarities["Pearson_r"]

    summary = pd.DataFrame(
        {
            "Metric": [
                "Mean",
                "Standard deviation",
                "Minimum",
                "Maximum",
            ],
            "Value": [
                values.mean(),
                values.std(),
                values.min(),
                values.max(),
            ],
        }
    )

    summary.to_csv(
        TABLES_DIR / "whole_map_similarity_summary.csv",
        index=False,
    )

    # ------------------------------------------------------------
    # Print
    # ------------------------------------------------------------

    print("\nWhole-map similarity completed.\n")

    print(summary)

    print("\nFirst five participants:\n")

    print(similarities.head())


if __name__ == "__main__":
    main()