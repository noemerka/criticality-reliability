"""
Quality control of vertex-wise ICC across Yeo-7 networks.

Fixed version: the previous version built the CIFTI-to-fsLR vertex
mapping by concatenating raw bm.vertex indices across hemispheres and
indexing directly into the full (left+right) Yeo label array -- the
same hemisphere-mixing bug as the original scripts 21 and 26. This
version uses src.cifti_utils.map_yeo_labels_to_cifti_cortex, which
handles each hemisphere separately, and reads the label path from
src.config.
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

    print("Loading ICC map...")

    img = nib.load(MAPS_DIR / "vertexwise_icc.dscalar.nii")
    icc = img.get_fdata().squeeze()

    print("Loading Yeo-7 labels...")
    yeo_labels = np.load(YEO_LABELS_FILE)

    cortex_mask = get_cortical_mask(img)

    print()
    print("CIFTI cortical vertices:", int(cortex_mask.sum()))
    print("Expected fsLR vertices:", len(yeo_labels))

    # ------------------------------------------------------------
    # Correct, hemisphere-aware label mapping
    # ------------------------------------------------------------

    cortical_labels = map_yeo_labels_to_cifti_cortex(img, yeo_labels)
    cortical_icc = icc[cortex_mask]

    valid = (
        np.isfinite(cortical_icc)
        & (cortical_labels > 0)
    )

    cortical_icc = cortical_icc[valid]
    cortical_labels = cortical_labels[valid]

    print()
    print("Valid ICC + Yeo vertices:", len(cortical_icc))

    # ------------------------------------------------------------
    # Network statistics
    # ------------------------------------------------------------

    results = []

    for label, name in NETWORKS.items():

        values = cortical_icc[cortical_labels == label]

        if len(values) == 0:
            continue

        q1 = np.percentile(values, 25)
        median = np.percentile(values, 50)
        q3 = np.percentile(values, 75)

        results.append(
            {
                "Network": name,
                "Label": label,
                "Vertices": len(values),
                "Mean ICC": values.mean(),
                "SD ICC": values.std(ddof=1),
                "Minimum ICC": values.min(),
                "Q1 ICC": q1,
                "Median ICC": median,
                "Q3 ICC": q3,
                "IQR ICC": q3 - q1,
                "Maximum ICC": values.max(),
                "ICC < 0.40 (%)": (values < 0.40).mean() * 100,
                "ICC >= 0.60 (%)": (values >= 0.60).mean() * 100,
                "ICC >= 0.75 (%)": (values >= 0.75).mean() * 100,
            }
        )

    results = pd.DataFrame(results)

    results = results.sort_values("Median ICC", ascending=False)

    # ------------------------------------------------------------
    # Save
    # ------------------------------------------------------------

    output = TABLES_DIR / "network_icc_qc.csv"

    results.to_csv(output, index=False)

    # ------------------------------------------------------------
    # Print
    # ------------------------------------------------------------

    print()
    print("=" * 80)
    print("NETWORK ICC QUALITY CONTROL")
    print("=" * 80)

    print()
    print(
        results.to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}",
        )
    )

    print()
    print("Results saved:")
    print(output)


if __name__ == "__main__":
    main()