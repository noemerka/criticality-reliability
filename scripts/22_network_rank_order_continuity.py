"""
Compute rank-order continuity for Yeo-7 network summary scores.
"""

import pandas as pd
from scipy.stats import pearsonr, spearmanr

from src.config import TABLES_DIR
from src.icc import compute_icc21


def main():

    # ------------------------------------------------------------
    # Load network summary scores
    # ------------------------------------------------------------

    df = pd.read_csv(
        TABLES_DIR / "network_summary_scores.csv"
    )

    results = []

    # ------------------------------------------------------------
    # Analyse each network separately
    # ------------------------------------------------------------

    for network in df["Network"].unique():

        subset = df[df["Network"] == network]

        test = subset["Test_mean"].values
        retest = subset["Retest_mean"].values

        pearson_r, pearson_p = pearsonr(
            test,
            retest,
        )

        spearman_rho, spearman_p = spearmanr(
            test,
            retest,
        )

        icc = compute_icc21(
            test,
            retest,
        )

        results.append(
            {
                "Network": network,
                "Pearson r": pearson_r,
                "Pearson p": pearson_p,
                "Spearman rho": spearman_rho,
                "Spearman p": spearman_p,
                "ICC(2,1)": icc,
            }
        )

    results = pd.DataFrame(results)

    # ------------------------------------------------------------
    # Save results
    # ------------------------------------------------------------

    results.to_csv(
        TABLES_DIR / "network_rank_continuity.csv",
        index=False,
    )

    print()
    print("Network rank-order continuity completed.")
    print()
    print(results)


if __name__ == "__main__":
    main()
