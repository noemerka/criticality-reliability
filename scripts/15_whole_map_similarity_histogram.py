"""
Plot histogram of participant-wise whole-map test-retest similarity.
"""

import pandas as pd
import matplotlib.pyplot as plt

from src.config import TABLES_DIR, FIGURES_DIR


def main():

    # ------------------------------------------------------------
    # Load participant correlations
    # ------------------------------------------------------------

    data = pd.read_csv(
        TABLES_DIR / "whole_map_similarity.csv"
    )

    values = data["Pearson_r"]

    # ------------------------------------------------------------
    # Plot
    # ------------------------------------------------------------

    plt.figure(figsize=(8, 5))

    plt.hist(
        values,
        bins=10,
    )

    plt.xlabel("Whole-map Pearson correlation")
    plt.ylabel("Number of participants")
    plt.title("Whole-map test-retest similarity")

    plt.tight_layout()

    output = FIGURES_DIR / "whole_map_similarity_histogram.png"

    plt.savefig(
        output,
        dpi=300,
    )

    plt.close()

    print("Histogram saved successfully.")
    print(output)

    print("\nSummary")
    print(f"Mean:   {values.mean():.4f}")
    print(f"SD:     {values.std():.4f}")
    print(f"Min:    {values.min():.4f}")
    print(f"Max:    {values.max():.4f}")


if __name__ == "__main__":
    main()