"""
Scatterplot of whole-cortex mean criticality:
Test vs Retest.
"""

import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

from src.config import TABLES_DIR, FIGURES_DIR


def main():

    # ------------------------------------------------------------
    # Load participant means
    # ------------------------------------------------------------

    data = pd.read_csv(
        TABLES_DIR / "whole_cortex_mean_values.csv"
    )

    x = data["Test_mean"]
    y = data["Retest_mean"]

    r, p = pearsonr(x, y)

    # ------------------------------------------------------------
    # Plot
    # ------------------------------------------------------------

    plt.figure(figsize=(6, 6))

    plt.scatter(
        x,
        y,
        s=40,
    )

    # Regression line
    m, b = __import__("numpy").polyfit(x, y, 1)

    plt.plot(
        x,
        m * x + b,
    )

    # Identity line
    xmin = min(x.min(), y.min())
    xmax = max(x.max(), y.max())

    plt.plot(
        [xmin, xmax],
        [xmin, xmax],
        linestyle="--",
    )

    plt.xlabel("Test mean criticality")
    plt.ylabel("Retest mean criticality")

    plt.title(
        f"Whole-cortex mean criticality\nPearson r = {r:.3f}"
    )

    plt.tight_layout()

    output = (
        FIGURES_DIR
        / "rank_order_scatter.png"
    )

    plt.savefig(
        output,
        dpi=300,
    )

    plt.close()

    print("Scatterplot saved successfully.")
    print(output)


if __name__ == "__main__":
    main()