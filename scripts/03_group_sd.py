"""
Compute group standard deviation maps for the test and retest datasets.

Fixed: uses np.nanstd instead of the plain .std(axis=0) method, for
the same reason as 02_group_mean.py -- plain .std propagates NaN to
any vertex with even one missing participant.
"""

import numpy as np

from src.config import MAPS_DIR
from src.io import (
    find_subject_files,
    load_dataset,
    save_cifti,
)


def main():
    # Load all data
    test_data, retest_data, subject_ids = load_dataset()

    # Compute group standard deviation (NaN-aware)
    group_sd_test = np.nanstd(test_data, axis=0)
    group_sd_retest = np.nanstd(retest_data, axis=0)

    # Get a reference CIFTI file for saving
    subjects = find_subject_files()
    reference_file = subjects[subject_ids[0]]["test"]

    # Save maps
    save_cifti(
        group_sd_test,
        reference_file,
        MAPS_DIR / "group_sd_test.dscalar.nii",
    )

    save_cifti(
        group_sd_retest,
        reference_file,
        MAPS_DIR / "group_sd_retest.dscalar.nii",
    )

    # Print summary
    print("Group standard deviation maps saved successfully.\n")

    print("Test SD shape:", group_sd_test.shape)
    print("Retest SD shape:", group_sd_retest.shape)

    print("\nFirst five vertices (Test):")
    print(group_sd_test[:5])

    print("\nFirst five vertices (Retest):")
    print(group_sd_retest[:5])


if __name__ == "__main__":
    main()