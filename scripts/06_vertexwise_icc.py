"""
Compute vertex-wise ICC(2,1) across the cortex.
"""

import numpy as np
import pandas as pd

from src.config import MAPS_DIR, TABLES_DIR
from src.icc import compute_icc21
from src.io import (
    find_subject_files,
    load_dataset,
    save_cifti,
)


def main():

    # ------------------------------------------------------------------
    # Load data
    # ------------------------------------------------------------------

    test_data, retest_data, subject_ids = load_dataset()

    n_vertices = test_data.shape[1]

    print(f"Computing ICC for {n_vertices} vertices...")

    # ------------------------------------------------------------------
    # Compute ICC
    # ------------------------------------------------------------------

    icc_map = np.full(n_vertices, np.nan)

    for vertex in range(n_vertices):

        test_values = test_data[:, vertex]
        retest_values = retest_data[:, vertex]

        # Skip vertices containing NaNs
        if (
            np.isnan(test_values).any()
            or np.isnan(retest_values).any()
        ):
            continue

        icc_map[vertex] = compute_icc21(
            test_values,
            retest_values,
        )

        if (vertex + 1) % 10000 == 0:
            print(f"Processed {vertex + 1}/{n_vertices} vertices")

    # ------------------------------------------------------------------
    # Save ICC map
    # ------------------------------------------------------------------

    subjects = find_subject_files()
    reference_file = subjects[subject_ids[0]]["test"]

    save_cifti(
        icc_map,
        reference_file,
        MAPS_DIR / "vertexwise_icc.dscalar.nii",
    )

    # ------------------------------------------------------------------
    # Summary statistics
    # ------------------------------------------------------------------

    valid_icc = icc_map[np.isfinite(icc_map)]
    n_valid = len(valid_icc)

    summary = pd.DataFrame(
        {
            "Metric": [
                "Valid vertices",
                "Mean ICC",
                "Median ICC",
                "Minimum ICC",
                "Maximum ICC",
                "ICC > 0.40 (%)",
                "ICC > 0.60 (%)",
                "ICC > 0.75 (%)",
            ],
            "Value": [
                n_valid,
                valid_icc.mean(),
                np.median(valid_icc),
                valid_icc.min(),
                valid_icc.max(),
                (valid_icc > 0.40).mean() * 100,
                (valid_icc > 0.60).mean() * 100,
                (valid_icc > 0.75).mean() * 100,
            ],
        }
    )

    summary.to_csv(
        TABLES_DIR / "icc_summary.csv",
        index=False,
    )

    # ------------------------------------------------------------------
    # Print summary
    # ------------------------------------------------------------------

    print()
    print("Vertex-wise ICC completed successfully.")
    print(f"Valid vertices: {n_valid}")

    print()
    print(summary)


if __name__ == "__main__":
    main()