"""
Sign-flip permutation robustness check for the group-level one-sample
t-test (scripts 09/10).

Rationale
---------
The exposé suggests SPM12's Sandwich Estimator (SwE; Guillaume et al.,
2014) as the preferred group-level analysis, or, as an explicit
alternative, "an FSL-based one-sample permutation analysis with
randomise". This script implements the latter directly in Python: a
sign-flip (Rademacher) permutation test for a one-sample design, which
is the same non-parametric logic FSL's randomise uses for one-sample
t-tests, and does not require installing FSL, SPM12, or MATLAB.

Unlike the classical one-sample t-test (scripts 09/10), which assumes
the sampling distribution of the mean is well approximated by a
t-distribution, this test makes no distributional assumption: under
the null hypothesis (true mean = 0), each participant's sign is
exchangeable, so randomly flipping signs and recomputing the group
mean directly simulates the null distribution.

Procedure
---------
For each session (test, retest) separately, and restricted to the
cortical mask:

1. For each of N_PERM sign-flip iterations, multiply each participant's
   data by a random +1/-1, and record the resulting group mean at
   every cortical vertex.
2. For each vertex, compute a one-sided permutation p-value: the
   proportion of sign-flipped group means at least as large as the
   observed (non-flipped) group mean.
3. Apply Benjamini-Hochberg FDR correction (q < .05) to these
   permutation p-values, exactly as done for the parametric p-values
   in script 10, for a direct, apples-to-apples comparison.

This does not test the same thing as SwE's repeated-measures
covariance correction (not relevant here; see Discussion Section 4.5
for why), but it does directly test the second, independent advantage
of bootstrap/permutation-based inference mentioned there: robustness
to the parametric assumptions underlying the classical t-test.
"""

import numpy as np
import pandas as pd
from statsmodels.stats.multitest import multipletests

from src.config import TABLES_DIR
from src.io import load_dataset, find_subject_files
from src.cifti_utils import get_cortical_mask
import nibabel as nib


N_PERM = 2000
ALPHA = 0.05
RANDOM_SEED = 42  # fixed for reproducibility of this robustness check


def sign_flip_test(data, cortex_mask, n_perm, rng):
    """
    Sign-flip permutation test for a one-sample design.

    Parameters
    ----------
    data : ndarray, shape (n_subjects, n_grayordinates)
    cortex_mask : boolean ndarray, shape (n_grayordinates,)
    n_perm : int
    rng : np.random.Generator

    Returns
    -------
    p_values : ndarray, shape (n_grayordinates,)
        One-sided permutation p-values (H1: mean > 0) at cortical
        vertices; NaN elsewhere.
    observed_mean : ndarray, shape (n_grayordinates,)
    """

    n_subjects = data.shape[0]

    cortex_data = data[:, cortex_mask]  # (n_subjects, n_cortex)
    n_cortex = cortex_data.shape[1]

    # Only use vertices with complete data across all subjects for this
    # check (matches the vertex-wise ICC / complete-case subset already
    # used elsewhere in the thesis, keeps the comparison clean).
    valid_cols = np.all(np.isfinite(cortex_data), axis=0)

    observed_mean_valid = np.nanmean(cortex_data[:, valid_cols], axis=0)

    ge_count = np.zeros(valid_cols.sum(), dtype=np.int64)

    for i in range(n_perm):
        signs = rng.choice([-1.0, 1.0], size=(n_subjects, 1))
        boot_mean = (cortex_data[:, valid_cols] * signs).mean(axis=0)
        ge_count += (boot_mean >= observed_mean_valid)

        if (i + 1) % 500 == 0:
            print(f"  {i + 1}/{n_perm} permutations done")

    p_valid = (1.0 + ge_count) / (n_perm + 1.0)

    p_values = np.full(n_cortex, np.nan)
    p_values[valid_cols] = p_valid

    observed_mean = np.full(n_cortex, np.nan)
    observed_mean[valid_cols] = observed_mean_valid

    return p_values, observed_mean, valid_cols.sum()


def main():

    rng = np.random.default_rng(RANDOM_SEED)

    print("Loading data...")
    test_data, retest_data, subject_ids = load_dataset()

    subjects = find_subject_files()
    reference_img = nib.load(subjects[subject_ids[0]]["test"])
    cortex_mask = get_cortical_mask(reference_img)

    print(f"Cortical grayordinates: {cortex_mask.sum()}")
    print(f"N permutations: {N_PERM}")

    results = []

    for label, data in [("Test", test_data), ("Retest", retest_data)]:

        print(f"\n=== {label} session ===")

        p_values, observed_mean, n_testable = sign_flip_test(
            data, cortex_mask, N_PERM, rng
        )

        testable = np.isfinite(p_values)

        rejected, q_values, _, _ = multipletests(
            p_values[testable], alpha=ALPHA, method="fdr_bh"
        )

        n_uncorrected = int(np.sum(p_values[testable] < ALPHA))
        n_fdr = int(rejected.sum())

        results.append({
            "Session": label,
            "Method": "Sign-flip permutation (non-parametric)",
            "Testable vertices": n_testable,
            "Significant (uncorrected p < .05)": n_uncorrected,
            "Significant (FDR q < .05)": n_fdr,
            "Percent significant (uncorrected)": round(
                n_uncorrected / n_testable * 100, 2
            ),
            "Percent significant (FDR)": round(
                n_fdr / n_testable * 100, 2
            ),
        })

        print(f"{label}: {n_fdr}/{n_testable} vertices significant after "
              f"FDR correction ({n_fdr / n_testable * 100:.2f}%)")

    results_df = pd.DataFrame(results)

    output_file = TABLES_DIR / "signflip_permutation_robustness.csv"
    results_df.to_csv(output_file, index=False)

    print("\n" + "=" * 70)
    print("SIGN-FLIP PERMUTATION ROBUSTNESS CHECK — SUMMARY")
    print("=" * 70)
    print(results_df.to_string(index=False))
    print(f"\nSaved: {output_file}")

    print(
        "\nFor comparison, the parametric FDR result from script 10 was "
        "~100% of testable vertices significant in both sessions. If "
        "the numbers above are similarly close to 100%, this confirms "
        "that the group-level finding (criticality > 0 across nearly "
        "the whole cortex) does not depend on the parametric "
        "t-distribution assumption."
    )


if __name__ == "__main__":
    main()