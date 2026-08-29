"""
Validate the 95% confidence interval for ICC(2,1)
against Pingouin ICC(A,1).

Only one cortical vertex is tested here.
"""

import numpy as np
import pandas as pd
import pingouin as pg

from src.io import load_dataset
from src.icc import compute_icc21


def compute_icc21_ci(
    test_values: np.ndarray,
    retest_values: np.ndarray,
    alpha: float = 0.05,
):
    """
    Compute ICC(2,1) and its approximate 95% CI.

    The ICC corresponds to the two-way random-effects,
    absolute-agreement, single-measurement model.
    """

    data = np.column_stack(
        (test_values, retest_values)
    )

    n, k = data.shape

    if np.isnan(data).any():
        return np.nan, np.nan, np.nan

    # ------------------------------------------------------------
    # Means
    # ------------------------------------------------------------

    subject_means = data.mean(axis=1)
    session_means = data.mean(axis=0)
    grand_mean = data.mean()

    # ------------------------------------------------------------
    # Sum of squares
    # ------------------------------------------------------------

    ss_subjects = (
        k * np.sum(
            (subject_means - grand_mean) ** 2
        )
    )

    ss_sessions = (
        n * np.sum(
            (session_means - grand_mean) ** 2
        )
    )

    residuals = (
        data
        - subject_means[:, None]
        - session_means[None, :]
        + grand_mean
    )

    ss_error = np.sum(
        residuals ** 2
    )

    # ------------------------------------------------------------
    # Degrees of freedom
    # ------------------------------------------------------------

    df_subjects = n - 1
    df_sessions = k - 1
    df_error = (n - 1) * (k - 1)

    # ------------------------------------------------------------
    # Mean squares
    # ------------------------------------------------------------

    ms_subjects = (
        ss_subjects / df_subjects
    )

    ms_sessions = (
        ss_sessions / df_sessions
    )

    ms_error = (
        ss_error / df_error
    )

    # ------------------------------------------------------------
    # ICC(2,1)
    # ------------------------------------------------------------

    denominator = (
        ms_subjects
        + (k - 1) * ms_error
        + (k / n)
        * (ms_sessions - ms_error)
    )

    if denominator == 0:
        return np.nan, np.nan, np.nan

    icc = (
        ms_subjects - ms_error
    ) / denominator

    # ------------------------------------------------------------
    # F statistic
    # ------------------------------------------------------------

    F = ms_subjects / ms_error

    # ------------------------------------------------------------
    # Confidence interval
    #
    # Two-way absolute-agreement ICC
    # ------------------------------------------------------------

    from scipy.stats import f

    df1 = n - 1
    df2 = (n - 1) * (k - 1)

    alpha_lower = alpha / 2
    alpha_upper = 1 - alpha / 2

    F_lower = f.ppf(
        alpha_lower,
        df1,
        df2,
    )

    F_upper = f.ppf(
        alpha_upper,
        df1,
        df2,
    )

    # Lower CI
    lower = (
        (F / F_upper - 1)
        /
        (
            F / F_upper
            + k - 1
            + (k / n)
            * (
                ms_sessions / ms_error
                - 1
            )
        )
    )

    # Upper CI
    upper = (
        (F / F_lower - 1)
        /
        (
            F / F_lower
            + k - 1
            + (k / n)
            * (
                ms_sessions / ms_error
                - 1
            )
        )
    )

    return (
        float(icc),
        float(lower),
        float(upper),
    )


def main():

    # ------------------------------------------------------------
    # Load data
    # ------------------------------------------------------------

    test_data, retest_data, _ = (
        load_dataset()
    )

    vertex = 0

    test = test_data[:, vertex]
    retest = retest_data[:, vertex]

    # ------------------------------------------------------------
    # Our ICC + CI
    # ------------------------------------------------------------

    my_icc, my_lower, my_upper = (
        compute_icc21_ci(
            test,
            retest,
        )
    )

    # ------------------------------------------------------------
    # Pingouin
    # ------------------------------------------------------------

    df = pd.DataFrame(
        {
            "subject": (
                list(range(len(test))) * 2
            ),
            "session": (
                ["test"] * len(test)
                + ["retest"] * len(test)
            ),
            "value": (
                list(test) + list(retest)
            ),
        }
    )

    icc_table = pg.intraclass_corr(
        data=df,
        targets="subject",
        raters="session",
        ratings="value",
    )

    pingouin_icc = icc_table[
        icc_table["Type"] == "ICC2"
    ]

    # Pingouin names the absolute-agreement
    # model ICC(A,1) as ICC2.
    if len(pingouin_icc) == 0:
        pingouin_icc = icc_table[
            icc_table["Type"] == "ICC(A,1)"
        ]

    print()
    print("=" * 60)
    print("ICC(2,1) CONFIDENCE INTERVAL VALIDATION")
    print("=" * 60)

    print()
    print("Our implementation:")
    print(f"ICC:       {my_icc:.6f}")
    print(f"95% CI:    [{my_lower:.6f}, {my_upper:.6f}]")

    print()
    print("Pingouin:")
    print(
        pingouin_icc[
            ["Type", "ICC", "CI95"]         
        ].to_string(index=False)
    )

    print()
    print("Full Pingouin table:")
    print(icc_table)


if __name__ == "__main__":
    main()