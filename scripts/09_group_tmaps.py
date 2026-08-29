"""
Compute group-level one-sample t-maps for test and retest sessions.
"""

import numpy as np
from scipy.stats import t

from src.config import MAPS_DIR
from src.io import (
    load_dataset,
    find_subject_files,
    save_cifti,
)


def compute_tmap(data):
    """
    Compute a one-sample t-statistic at each vertex.

    The number of valid observations is determined separately
    for each vertex to account for missing values.

    Parameters
    ----------
    data : ndarray
        Shape (subjects, vertices)

    Returns
    -------
    tmap : ndarray
        Vertex-wise t-values.
    """

    # Number of valid observations per vertex
    n_valid = np.sum(np.isfinite(data), axis=0)

    # Mean and standard deviation per vertex
    mean = np.nanmean(data, axis=0)
    sd = np.nanstd(data, axis=0, ddof=1)

    # Initialize output
    tmap = np.full(mean.shape, np.nan)

    # Valid vertices require at least 2 observations
    valid = (
        (n_valid >= 2)
        & np.isfinite(mean)
        & np.isfinite(sd)
        & (sd > 0)
    )

    # Vertex-specific one-sample t-statistic
    tmap[valid] = (
        mean[valid]
        / (sd[valid] / np.sqrt(n_valid[valid]))
    )

    return tmap

def main():

    # ------------------------------------------------------------
    # Load data
    # ------------------------------------------------------------

    test_data, retest_data, subject_ids = load_dataset()

    print(f"Subjects: {test_data.shape[0]}")
    print(f"Vertices: {test_data.shape[1]}")

    # ------------------------------------------------------------
    # Compute t-maps
    # ------------------------------------------------------------

    print("\nComputing test t-map...")
    test_t = compute_tmap(test_data)

    print("Computing retest t-map...")
    retest_t = compute_tmap(retest_data)

    # ------------------------------------------------------------
    # Save maps
    # ------------------------------------------------------------

    subjects = find_subject_files()
    reference = subjects[subject_ids[0]]["test"]

    save_cifti(
        test_t,
        reference,
        MAPS_DIR / "group_t_test.dscalar.nii",
    )

    save_cifti(
        retest_t,
        reference,
        MAPS_DIR / "group_t_retest.dscalar.nii",
    )

    # ------------------------------------------------------------
    # Print summary
    # ------------------------------------------------------------

    print("\nFinished!")

    print("\nTest")
    print("Mean t:", np.nanmean(test_t))
    print("Max t :", np.nanmax(test_t))

    print("\nRetest")
    print("Mean t:", np.nanmean(retest_t))
    print("Max t :", np.nanmax(retest_t))


if __name__ == "__main__":
    main()
