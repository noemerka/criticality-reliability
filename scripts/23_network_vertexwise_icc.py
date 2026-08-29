"""
Summarize vertex-wise ICC within each Yeo-7 network.

This was already the one script in the original set that mapped
hemispheres correctly. This version keeps that logic but:

- reads YEO_LABELS_FILE from src.config instead of a hard-coded,
  machine-specific path
- uses the shared src.cifti_utils.map_yeo_labels_to_cifti_cortex
  helper instead of a bespoke loop, so any future fix only has to be
  made in one place
- uses the actual cortical mask instead of a hard-coded 59412 slice
  length, in case the CIFTI grayordinate ordering ever changes
"""

import numpy as np
import pandas as pd
import nibabel as nib

from src.config import MAPS_DIR, TABLES_DIR, YEO_LABELS_FILE
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

    # --------------------------------------------------------------
    # Load ICC CIFTI
    # --------------------------------------------------------------

    print("Loading ICC map...")

    img = nib.load(
        MAPS_DIR / "vertexwise_icc.dscalar.nii"
    )

    icc = img.get_fdata().squeeze()

    cortex_mask = get_cortical_mask(img)
    n_cortex = int(cortex_mask.sum())

    print(f"CIFTI grayordinates: {len(icc)}")
    print(f"Cortical grayordinates: {n_cortex}")

    # --------------------------------------------------------------
    # Load and map Yeo labels
    # --------------------------------------------------------------

    print("Loading Yeo-7 labels...")

    yeo_labels = np.load(YEO_LABELS_FILE)

    print(f"Yeo labels: {len(yeo_labels)}")

    cortex_labels = map_yeo_labels_to_cifti_cortex(img, yeo_labels)

    print()
    print("Yeo label counts in CIFTI cortex:")
    for label in range(8):
        print(f"Label {label}:", np.sum(cortex_labels == label))

    # --------------------------------------------------------------
    # Extract cortical ICC values
    # --------------------------------------------------------------

    cortical_icc = icc[cortex_mask]

    valid = (
        (cortex_labels > 0)
        & np.isfinite(cortical_icc)
    )

    labels = cortex_labels[valid]
    values = cortical_icc[valid]

    print()
    print("Valid labeled cortical vertices:", len(values))

    # --------------------------------------------------------------
    # Network summaries
    # --------------------------------------------------------------

    results = []

    for label, name in NETWORKS.items():

        network_values = values[labels == label]

        if len(network_values) == 0:
            continue

        results.append(
            {
                "Network": name,
                "Label": label,
                "Vertices": len(network_values),
                "Mean ICC": network_values.mean(),
                "Median ICC": np.median(network_values),
                "Minimum ICC": network_values.min(),
                "Maximum ICC": network_values.max(),
                "ICC > 0.40 (%)":
                    (network_values > 0.40).mean() * 100,
                "ICC > 0.60 (%)":
                    (network_values > 0.60).mean() * 100,
                "ICC > 0.75 (%)":
                    (network_values > 0.75).mean() * 100,
            }
        )

    results = pd.DataFrame(results)

    # --------------------------------------------------------------
    # Save
    # --------------------------------------------------------------

    output_file = (
        TABLES_DIR / "network_vertexwise_icc_corrected.csv"
    )

    results.to_csv(
        output_file,
        index=False,
    )

    # --------------------------------------------------------------
    # Print
    # --------------------------------------------------------------

    print()
    print("Corrected network vertex-wise ICC summary")
    print()
    print(results.to_string(index=False))

    print()
    print("Results saved successfully.")
    print(output_file)


if __name__ == "__main__":
    main()