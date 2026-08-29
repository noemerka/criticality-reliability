"""
Quality control for CIFTI-to-fsLR Yeo-7 mapping.

Fixed version: the previous version built `cifti_to_fslr` by
concatenating raw bm.vertex indices across both hemispheres and then
indexing directly into the full (left+right) Yeo label array. Because
bm.vertex is hemisphere-local (0..32491 for BOTH hemispheres), this
silently pulled left-hemisphere labels for right-hemisphere
grayordinates -- the same class of bug as the original script 21.

This version uses src.cifti_utils.map_yeo_labels_to_cifti_cortex,
which slices the Yeo label array per hemisphere before indexing, and
reads paths from src.config instead of a hard-coded, machine-specific
path.
"""

import numpy as np
import nibabel as nib

from src.config import MAPS_DIR, YEO_LABELS_FILE
from src.cifti_utils import get_cortical_mask, map_yeo_labels_to_cifti_cortex


def main():

    # ------------------------------------------------------------
    # Load ICC map
    # ------------------------------------------------------------

    img = nib.load(MAPS_DIR / "vertexwise_icc.dscalar.nii")

    icc = img.get_fdata().squeeze()

    # ------------------------------------------------------------
    # Load Yeo-7 labels
    # ------------------------------------------------------------

    labels = np.load(YEO_LABELS_FILE)

    print("Yeo labels:", len(labels))

    # ------------------------------------------------------------
    # Cortical mask and correct hemisphere-aware label mapping
    # ------------------------------------------------------------

    cortex_mask = get_cortical_mask(img)

    print()
    print("CIFTI cortical grayordinates:", int(cortex_mask.sum()))
    print("Expected fsLR vertices:", len(labels))

    cifti_yeo_cortex = map_yeo_labels_to_cifti_cortex(img, labels)

    cortical_icc = icc[cortex_mask]

    valid_icc = np.isfinite(cortical_icc)
    valid_yeo = cifti_yeo_cortex > 0
    valid_both = valid_icc & valid_yeo

    # ------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------

    print()
    print("=" * 60)
    print("YEO-7 / CIFTI QUALITY CONTROL")
    print("=" * 60)

    print()
    print("Cortical CIFTI grayordinates:", len(cortical_icc))
    print("Valid ICC:", valid_icc.sum())
    print("Yeo-labelled cortical vertices:", valid_yeo.sum())
    print("Valid ICC + Yeo:", valid_both.sum())
    print("Unlabelled cortical vertices:", np.sum(cifti_yeo_cortex == 0))
    print(
        "Unlabelled vertices with valid ICC:",
        np.sum((cifti_yeo_cortex == 0) & valid_icc),
    )

    # ------------------------------------------------------------
    # Yeo label counts
    # ------------------------------------------------------------

    print()
    print("Yeo label counts in CIFTI cortex:")

    for label in range(8):
        print(f"Label {label}:", np.sum(cifti_yeo_cortex == label))

    # ------------------------------------------------------------
    # Valid ICC count per network
    # ------------------------------------------------------------

    print()
    print("Valid ICC vertices per network:")

    for label in range(1, 8):
        valid_network = (cifti_yeo_cortex == label) & valid_icc
        print(f"Network {label}:", valid_network.sum())

    # ------------------------------------------------------------
    # Consistency checks
    # ------------------------------------------------------------

    print()
    print("=" * 60)
    print("CONSISTENCY CHECKS")
    print("=" * 60)

    expected_cortex = int(cortex_mask.sum())

    print(
        "Mapped length == cortex mask length:",
        len(cifti_yeo_cortex) == expected_cortex,
    )

    network_sum = sum(
        np.sum((cifti_yeo_cortex == label) & valid_icc)
        for label in range(1, 8)
    )

    print(
        "Network sum = valid ICC + Yeo:",
        network_sum == valid_both.sum(),
    )

    print()
    print("QC completed successfully.")


if __name__ == "__main__":
    main()