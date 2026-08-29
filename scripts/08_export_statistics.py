"""
Export summary statistics for the Bachelor thesis.
"""

import pandas as pd

from src.config import TABLES_DIR
from src.io import load_dataset


def main():

    # ------------------------------------------------------------------
    # Load participant information
    # ------------------------------------------------------------------

    test_data, retest_data, subject_ids = load_dataset()

    n_subjects = len(subject_ids)

    # ------------------------------------------------------------------
    # Load ICC summary
    # ------------------------------------------------------------------

    summary = pd.read_csv(TABLES_DIR / "icc_summary.csv")

    summary = summary.set_index("Metric")

    # ------------------------------------------------------------------
    # Create report
    # ------------------------------------------------------------------

    report = pd.DataFrame({

        "Metric": [

            "Participants",
            "Valid vertices",
            "Mean ICC",
            "Median ICC",
            "Minimum ICC",
            "Maximum ICC",
            "ICC > 0.40 (%)",
            "ICC > 0.60 (%)",
            "ICC > 0.75 (%)",

        ],

        "Value": [

            n_subjects,
            int(summary.loc["Valid vertices", "Value"]),
            summary.loc["Mean ICC", "Value"],
            summary.loc["Median ICC", "Value"],
            summary.loc["Minimum ICC", "Value"],
            summary.loc["Maximum ICC", "Value"],
            summary.loc["ICC > 0.40 (%)", "Value"],
            summary.loc["ICC > 0.60 (%)", "Value"],
            summary.loc["ICC > 0.75 (%)", "Value"],

        ]

    })

    output_file = TABLES_DIR / "results_summary.csv"

    report.to_csv(
        output_file,
        index=False,
    )

    print()
    print("Results summary exported successfully.")
    print()
    print(report)


if __name__ == "__main__":
    main()