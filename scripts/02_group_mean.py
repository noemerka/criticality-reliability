"""
Compute group mean maps for the test and retest datasets.

Fixed: uses np.nanmean instead of the plain .mean(axis=0) method.
The plain mean propagates NaN to the group mean at any vertex where
even a single participant has a missing value, which affected the
977 cortical vertices without full N=43 coverage (see
30_check_data_completeness.py). np.nanmean instead computes the mean
over whatever valid data is available at each vertex, consistent
with how 09_group_tmaps.py already handles missing data.
"""

import numpy as np

from src.io import load_dataset, save_cifti, find_subject_files
from src.config import MAPS_DIR


def main():

    test_data, retest_data, subject_ids = load_dataset()

    group_mean_test = np.nanmean(test_data, axis=0)
    group_mean_retest = np.nanmean(retest_data, axis=0)

    subjects = find_subject_files()

    reference_file = subjects[subject_ids[0]]["test"]

    save_cifti(
        group_mean_test,
        reference_file,
        MAPS_DIR / "group_mean_test.dscalar.nii",
    )

    save_cifti(
        group_mean_retest,
        reference_file,
        MAPS_DIR / "group_mean_retest.dscalar.nii",
    )

    print("\nGroup mean maps saved successfully.")

    print("Test mean shape:", group_mean_test.shape)
    print("Retest mean shape:", group_mean_retest.shape)

    print()

    print("First five vertices (Test):")
    print(group_mean_test[:5])

    print()

    print("First five vertices (Retest):")
    print(group_mean_retest[:5])


if __name__ == "__main__":
    main()