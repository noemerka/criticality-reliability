"""
Compute demeaned (residualized) whole-map test-retest similarity per
participant, alongside the original raw whole-map similarity.

Rationale
---------
13_whole_map_similarity.py correlates each participant's raw test map
with their raw retest map across the whole cortex. All participants
share a common, strong group-level spatial pattern (large systematic
differences between networks -- e.g. Limbic vs. Somatomotor baseline
levels, see 21_network_summary_scores.py). That shared pattern can
dominate a whole-cortex Pearson correlation and inflate the apparent
whole-map similarity even if the participant-specific deviation from
that pattern is not itself reliable across sessions.

This script subtracts the group mean map (test-session group mean
from every test map, retest-session group mean from every retest
map) before computing each participant's test-retest correlation.
This isolates the individual-specific component of the map. Comparing
"demeaned" to "raw" whole-map similarity indicates how much of the
raw correlation is attributable to the shared group pattern versus
genuine individual-level reliability:

- If demeaned r is only slightly lower than raw r, the raw whole-map
  similarity mainly reflects real individual signal.
- If demeaned r is substantially lower than raw r (especially if it
  drops toward the vertex-wise ICC range, ~0.68 on average), the raw
  whole-map similarity was mostly driven by the shared group pattern
  and should be interpreted cautiously as an individual-reliability
  measure.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import nibabel as nib
from scipy.stats import pearsonr

from src.config import TABLES_DIR, FIGURES_DIR
from src.io import load_dataset, find_subject_files
from src.cifti_utils import get_cortical_mask


def main():

    print("Loading data...")
    test_data, retest_data, subject_ids = load_dataset()

    subjects = find_subject_files()
    reference_file = subjects[subject_ids[0]]["test"]
    reference_img = nib.load(reference_file)
    cortex_mask = get_cortical_mask(reference_img)

    print(f"Cortical grayordinates: {cortex_mask.sum()}")

    # ------------------------------------------------------------
    # Group mean maps per session (NaN-aware, unlike the plain
    # .mean(axis=0) in 02_group_mean.py -- see note below)
    # ------------------------------------------------------------

    group_mean_test = np.nanmean(test_data, axis=0)
    group_mean_retest = np.nanmean(retest_data, axis=0)

    # ------------------------------------------------------------
    # Raw vs. demeaned whole-map similarity per participant
    # ------------------------------------------------------------

    results = []

    for i, subject in enumerate(subject_ids):

        test = test_data[i]
        retest = retest_data[i]

        valid = (
            cortex_mask
            & np.isfinite(test)
            & np.isfinite(retest)
            & np.isfinite(group_mean_test)
            & np.isfinite(group_mean_retest)
        )

        # Raw similarity, cortically masked (13_whole_map_similarity.py
        # did not apply a cortex mask; restricting to cortex here for
        # a clean, consistent comparison against the demeaned version)
        raw_r, _ = pearsonr(test[valid], retest[valid])

        # Demeaned: subtract each session's group mean map first
        test_demeaned = test[valid] - group_mean_test[valid]
        retest_demeaned = retest[valid] - group_mean_retest[valid]

        demeaned_r, _ = pearsonr(test_demeaned, retest_demeaned)

        results.append(
            {
                "Subject": subject,
                "Raw_Pearson_r": raw_r,
                "Demeaned_Pearson_r": demeaned_r,
            }
        )

    results = pd.DataFrame(results)

    output_file = TABLES_DIR / "whole_map_similarity_demeaned.csv"
    results.to_csv(output_file, index=False)

    # ------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------

    summary = pd.DataFrame(
        {
            "Metric": [
                "Mean (raw)",
                "SD (raw)",
                "Minimum (raw)",
                "Maximum (raw)",
                "Mean (demeaned)",
                "SD (demeaned)",
                "Minimum (demeaned)",
                "Maximum (demeaned)",
            ],
            "Value": [
                results["Raw_Pearson_r"].mean(),
                results["Raw_Pearson_r"].std(),
                results["Raw_Pearson_r"].min(),
                results["Raw_Pearson_r"].max(),
                results["Demeaned_Pearson_r"].mean(),
                results["Demeaned_Pearson_r"].std(),
                results["Demeaned_Pearson_r"].min(),
                results["Demeaned_Pearson_r"].max(),
            ],
        }
    )

    summary_file = TABLES_DIR / "whole_map_similarity_demeaned_summary.csv"
    summary.to_csv(summary_file, index=False)

    print()
    print(summary.to_string(index=False))

    # ------------------------------------------------------------
    # Figure: raw vs demeaned distributions side by side
    # ------------------------------------------------------------

    fig, axes = plt.subplots(1, 2, figsize=(11, 5), sharey=True)

    axes[0].hist(results["Raw_Pearson_r"], bins=10)
    axes[0].set_title("Raw whole-map similarity")
    axes[0].set_xlabel("Pearson r")
    axes[0].set_ylabel("Number of participants")

    axes[1].hist(results["Demeaned_Pearson_r"], bins=10)
    axes[1].set_title("Demeaned whole-map similarity")
    axes[1].set_xlabel("Pearson r")

    plt.tight_layout()

    fig_file = FIGURES_DIR / "whole_map_similarity_raw_vs_demeaned.png"
    plt.savefig(fig_file, dpi=300)
    plt.close()

    print()
    print("Saved:")
    print(output_file)
    print(summary_file)
    print(fig_file)


if __name__ == "__main__":
    main()