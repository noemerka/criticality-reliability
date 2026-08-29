"""
Functions for computing intraclass correlation coefficients (ICC).
"""

import numpy as np


def compute_icc21(
    test_values: np.ndarray,
    retest_values: np.ndarray,
) -> float:
    """
    Compute ICC(2,1) (two-way random effects, absolute agreement,
    single measurement) for one cortical vertex.

    Parameters
    ----------
    test_values : np.ndarray
        Test values for one vertex.

    retest_values : np.ndarray
        Retest values for one vertex.

    Returns
    -------
    float
        ICC(2,1) value.
    """

    # ------------------------------------------------------------------
    # Arrange data (subjects × sessions)
    # ------------------------------------------------------------------

    data = np.column_stack((test_values, retest_values))

    n, k = data.shape

    # ------------------------------------------------------------------
    # Skip invalid vertices
    # ------------------------------------------------------------------

    if np.isnan(data).any():
        return np.nan

    # ------------------------------------------------------------------
    # Means
    # ------------------------------------------------------------------

    subject_means = data.mean(axis=1)
    session_means = data.mean(axis=0)
    grand_mean = data.mean()

    # ------------------------------------------------------------------
    # Sum of Squares
    # ------------------------------------------------------------------

    ss_subjects = k * np.sum((subject_means - grand_mean) ** 2)

    ss_sessions = n * np.sum((session_means - grand_mean) ** 2)

    residuals = (
        data
        - subject_means[:, None]
        - session_means[None, :]
        + grand_mean
    )

    ss_error = np.sum(residuals ** 2)

    # ------------------------------------------------------------------
    # Degrees of freedom
    # ------------------------------------------------------------------

    df_subjects = n - 1
    df_sessions = k - 1
    df_error = (n - 1) * (k - 1)

    # ------------------------------------------------------------------
    # Mean Squares
    # ------------------------------------------------------------------

    ms_subjects = ss_subjects / df_subjects
    ms_sessions = ss_sessions / df_sessions
    ms_error = ss_error / df_error

    # ------------------------------------------------------------------
    # ICC(2,1)
    # ------------------------------------------------------------------

    denominator = (
        ms_subjects
        + (k - 1) * ms_error
        + (k / n) * (ms_sessions - ms_error)
    )

    # Avoid division by zero
    if denominator == 0:
        return np.nan

    with np.errstate(divide="ignore", invalid="ignore"):
        icc = (ms_subjects - ms_error) / denominator

    return float(icc)