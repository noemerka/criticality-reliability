"""
Inspect the Yeo-7 network labels.

This script checks:

- number of vertices
- unique labels
- vertices per network
- correspondence to the current CIFTI data

Fixed: reads YEO_LABELS_FILE from src.config instead of a
hard-coded, machine-specific path.
"""

import numpy as np
import nibabel as nib

from src.config import MAPS_DIR, YEO_LABELS_FILE


NETWORK_NAMES = {
    0: "Medial wall / unlabeled",
    1: "Visual",
    2: "Somatomotor",
    3: "Dorsal Attention",
    4: "Ventral Attention",
    5: "Limbic",
    6: "Frontoparietal",
    7: "Default Mode",
}


def main():

    labels = np.load(YEO_LABELS_FILE)

    print("=" * 60)
    print("Yeo atlas")
    print("=" * 60)

    print(f"Number of labels: {len(labels)}")
    print()

    unique = np.unique(labels)

    print("Unique labels:")
    print(unique)
    print()

    print("Vertices per network")
    print("-" * 60)

    for label in unique:

        n = np.sum(labels == label)

        print(
            f"{label}: "
            f"{NETWORK_NAMES.get(label, 'Unknown'):25s}"
            f"{n:8d}"
        )

    print()

    # ------------------------------------------------------------
    # Compare with current CIFTI data
    # ------------------------------------------------------------

    img = nib.load(
        MAPS_DIR / "vertexwise_icc.dscalar.nii"
    )

    data = img.get_fdata()[0]

    print("=" * 60)
    print("Current dataset")
    print("=" * 60)

    print(f"CIFTI vertices: {len(data)}")
    print(f"Finite vertices: {np.isfinite(data).sum()}")
    print(f"NaN vertices: {np.isnan(data).sum()}")

    print()

    print("Comparison")
    print("-" * 60)

    print(f"Atlas labels : {len(labels)}")
    print(f"Finite ICC   : {np.isfinite(data).sum()}")
    print(
        f"Difference   : "
        f"{len(labels) - np.isfinite(data).sum()}"
    )


if __name__ == "__main__":
    main()