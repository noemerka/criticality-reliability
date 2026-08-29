"""
Diagnose participant- and vertex-level data completeness.

This script directly answers the "N=43 vs N=39" question:

- How many of the 43 participants have FULLY complete cortical data
  (no missing/NaN vertices) in test and in retest?
- For vertices that are NOT complete across all 43 participants, how
  many participants actually contribute valid data at those
  locations?

This matters because 09_group_tmaps.py computes a vertex-specific N
(participants can vary per vertex), while 10_threshold_group_tmaps.py
currently only inferentially thresholds vertices with data from ALL
43 participants (test_n == N_SUBJECTS). If a relevant number of
vertices have less-than-complete coverage, that choice needs to be
explicitly justified and reported in the Methods section.
"""

import numpy as np
import pandas as pd
import nibabel as nib

from src.io import load_dataset, find_subject_files
from src.config import TABLES_DIR
from src.cifti_utils import get_cortical_mask


def main():

    print("Loading data...")
    test_data, retest_data, subject_ids = load_dataset()

    n_subjects = len(subject_ids)
    print(f"Subjects loaded: {n_subjects}")

    # ------------------------------------------------------------
    # Cortical mask (reference geometry from the first subject)
    # ------------------------------------------------------------

    subjects = find_subject_files()
    reference_file = subjects[subject_ids[0]]["test"]
    reference_img = nib.load(reference_file)

    cortex_mask = get_cortical_mask(reference_img)
    n_cortex = int(cortex_mask.sum())
    print(f"Cortical grayordinates: {n_cortex}")

    test_cortex = test_data[:, cortex_mask]
    retest_cortex = retest_data[:, cortex_mask]

    # ------------------------------------------------------------
    # Per-participant completeness
    # ------------------------------------------------------------

    test_missing = np.sum(~np.isfinite(test_cortex), axis=1)
    retest_missing = np.sum(~np.isfinite(retest_cortex), axis=1)

    participant_table = pd.DataFrame(
        {
            "Subject": subject_ids,
            "Test_missing_vertices": test_missing,
            "Retest_missing_vertices": retest_missing,
        }
    )

    participant_table["Complete_test"] = (
        participant_table["Test_missing_vertices"] == 0
    )
    participant_table["Complete_retest"] = (
        participant_table["Retest_missing_vertices"] == 0
    )
    participant_table["Complete_both"] = (
        participant_table["Complete_test"]
        & participant_table["Complete_retest"]
    )

    n_complete = int(participant_table["Complete_both"].sum())

    print()
    print("=" * 60)
    print("PARTICIPANT-LEVEL COMPLETENESS")
    print("=" * 60)
    print(
        f"Participants with fully complete cortical data "
        f"(test AND retest): {n_complete} / {n_subjects}"
    )
    print(
        f"Participants with at least one missing cortical vertex: "
        f"{n_subjects - n_complete}"
    )

    incomplete = participant_table[~participant_table["Complete_both"]]

    if len(incomplete) > 0:
        print()
        print("Participants with incomplete data:")
        print(incomplete.to_string(index=False))
    else:
        print("\nAll participants have fully complete cortical data.")

    # ------------------------------------------------------------
    # Per-vertex participant coverage
    # ------------------------------------------------------------

    both_valid = np.isfinite(test_cortex) & np.isfinite(retest_cortex)
    n_valid_per_vertex = np.sum(both_valid, axis=0)

    coverage_counts = (
        pd.Series(n_valid_per_vertex)
        .value_counts()
        .sort_index(ascending=False)
        .reset_index()
    )
    coverage_counts.columns = [
        "N_participants_with_valid_data",
        "N_vertices",
    ]
    coverage_counts["Percent_of_cortex"] = (
        coverage_counts["N_vertices"] / n_cortex * 100
    )

    print()
    print("=" * 60)
    print("VERTEX-LEVEL COVERAGE (test AND retest valid)")
    print("=" * 60)
    print(coverage_counts.to_string(index=False))

    n_full = int(np.sum(n_valid_per_vertex == n_subjects))
    n_partial = int(np.sum(n_valid_per_vertex < n_subjects))

    print()
    print(f"Vertices with all {n_subjects} participants valid: {n_full}")
    print(f"Vertices with fewer than {n_subjects} participants valid: {n_partial}")
    print(f"Minimum participant coverage across cortex: {int(n_valid_per_vertex.min())}")
    print(f"Maximum participant coverage across cortex: {int(n_valid_per_vertex.max())}")

    # ------------------------------------------------------------
    # Save
    # ------------------------------------------------------------

    participant_out = TABLES_DIR / "data_completeness_participants.csv"
    coverage_out = TABLES_DIR / "data_completeness_vertex_coverage.csv"

    participant_table.to_csv(participant_out, index=False)
    coverage_counts.to_csv(coverage_out, index=False)

    print()
    print("Tables saved:")
    print(participant_out)
    print(coverage_out)


if __name__ == "__main__":
    main()