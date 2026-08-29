"""
Compute mean criticality per Yeo-7 network for every participant.

Fixed version: uses src.cifti_utils.map_yeo_labels_to_cifti_cortex to
align Yeo-7 labels with CIFTI cortical grayordinates via the actual
BrainModelAxis vertex indices, separately per hemisphere.

The previous version filtered out unlabeled (0) vertices from the
Yeo label array and then truncated both the label array and the data
array to the same length. This implicitly assumed that, after
removing zeros, the remaining labels line up 1:1 with the CIFTI
cortical grayordinate order -- which is not guaranteed and produced
an incorrect subject-by-network assignment.
"""

import numpy as np
import pandas as pd
import nibabel as nib

from src.io import load_dataset, find_subject_files
from src.config import TABLES_DIR, YEO_LABELS_FILE
from src.cifti_utils import get_cortical_mask, map_yeo_labels_to_cifti_cortex


NETWORKS = {
    1: "Visual",
    2: "Somatomotor",
    3: "DorsalAttention",
    4: "VentralAttention",
    5: "Limbic",
    6: "Frontoparietal",
    7: "DefaultMode",
}


def main():

    print("Loading data...")
    test_data, retest_data, subject_ids = load_dataset()

    # ------------------------------------------------------------
    # Reference CIFTI image (only used for its BrainModelAxis)
    # ------------------------------------------------------------

    subjects = find_subject_files()
    reference_file = subjects[subject_ids[0]]["test"]
    reference_img = nib.load(reference_file)

    if reference_img.shape[-1] != test_data.shape[1]:
        raise ValueError(
            "Reference image vertex count does not match loaded "
            f"data ({reference_img.shape[-1]} vs {test_data.shape[1]})."
        )

    cortex_mask = get_cortical_mask(reference_img)
    print(f"Cortical grayordinates: {cortex_mask.sum()} / {len(cortex_mask)}")

    # ------------------------------------------------------------
    # Map Yeo-7 labels onto CIFTI cortical grayordinate order
    # ------------------------------------------------------------

    yeo_labels = np.load(YEO_LABELS_FILE)
    print(f"Yeo labels loaded: {len(yeo_labels)}")

    cortex_labels_full = np.zeros(test_data.shape[1], dtype=int)
    cortex_labels_full[cortex_mask] = map_yeo_labels_to_cifti_cortex(
        reference_img, yeo_labels
    )

    print()
    print("Vertices per network (across full cortex):")
    for label, name in NETWORKS.items():
        n = int(np.sum((cortex_labels_full == label) & cortex_mask))
        print(f"  {name:20s} {n:8d}")

    # ------------------------------------------------------------
    # Loop over participants and networks
    # ------------------------------------------------------------

    results = []

    for i, subject in enumerate(subject_ids):

        for label, name in NETWORKS.items():

            mask = cortex_mask & (cortex_labels_full == label)
            n_vertices = int(mask.sum())

            test_mean = (
                np.nanmean(test_data[i, mask]) if n_vertices else np.nan
            )
            retest_mean = (
                np.nanmean(retest_data[i, mask]) if n_vertices else np.nan
            )

            results.append(
                {
                    "Subject": subject,
                    "Network": name,
                    "Vertices": n_vertices,
                    "Test_mean": test_mean,
                    "Retest_mean": retest_mean,
                }
            )

    results = pd.DataFrame(results)

    output_file = TABLES_DIR / "network_summary_scores.csv"

    results.to_csv(
        output_file,
        index=False,
    )

    print()
    print("Network summary scores saved successfully.")
    print(output_file)
    print()
    print(results.head(10))


if __name__ == "__main__":
    main()