"""
Create a histogram of vertex-wise ICC values.
"""

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np

from src.config import MAPS_DIR, FIGURES_DIR


def main():

    print("Loading ICC map...")

    img = nib.load(MAPS_DIR / "vertexwise_icc.dscalar.nii")

    icc = img.get_fdata().squeeze()

    # Remove invalid values
    icc = icc[np.isfinite(icc)]

    print(f"Valid vertices: {len(icc)}")

    # ------------------------------------------------------------------
    # Plot
    # ------------------------------------------------------------------

    plt.figure(figsize=(8, 5))

    plt.hist(
        icc,
        bins=50,
    )

    plt.xlabel("ICC(2,1)")
    plt.ylabel("Number of vertices")
    plt.title("Distribution of vertex-wise ICC values")

    plt.tight_layout()

    output_file = FIGURES_DIR / "icc_histogram.png"

    plt.savefig(
        output_file,
        dpi=300,
    )

    plt.close()

    print()
    print(f"Histogram saved to:")
    print(output_file)


if __name__ == "__main__":
    main()