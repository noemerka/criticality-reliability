"""
Consistency-based ICC(3,1), computed as a secondary comparison to the
primary absolute-agreement ICC(2,1) used elsewhere in this thesis
(script 06). This follows the exposé's suggestion that "consistency-based
ICC can also be informative if feasible" (RQ3).

ICC(2,1) and ICC(3,1) differ only in whether systematic between-session
differences are treated as part of the disagreement (absolute agreement,
ICC(2,1)) or removed before computing reliability (consistency,
ICC(3,1)). If the two forms are similar, this indicates that any
unreliability mainly reflects unsystematic, vertex-level noise rather
than a systematic session-wide shift in criticality.

Both forms are computed here using the standard two-way ANOVA
decomposition (Shrout & Fleiss, 1979; McGraw & Wong, 1996), restricted
to the same 58,435 cortical vertices with complete N = 43 coverage used
for ICC(2,1) in script 06, for a directly comparable, apples-to-apples
result.
"""

import numpy as np
import pandas as pd

from src.config import TABLES_DIR
from src.io import load_dataset
from src.cifti_utils import get_cortical_mask
from src.io import find_subject_files
import nibabel as nib


def compute_icc_2_1_and_3_1(test, retest):
    """
    Vectorized two-way ANOVA-based ICC(2,1) and ICC(3,1) for paired
    test/retest data.

    Parameters
    ----------
    test, retest : ndarray, shape (n_subjects, n_vertices)
        Must already be restricted to vertices with complete data
        (no NaNs) for all subjects in both sessions.

    Returns
    -------
    icc21, icc31 : ndarray, shape (n_vertices,)
    """
    n = test.shape[0]  # number of subjects
    k = 2               # number of sessions (test, retest)

    data = np.stack([test, retest], axis=2)  # (n_subjects, n_vertices, k)

    grand_mean = data.mean(axis=(0, 2))       # (v,)
    subj_mean = data.mean(axis=2)             # (n, v) -- mean over sessions, per subject
    sess_mean = data.mean(axis=0)             # (v, k) -- mean over subjects, per session

    # Sum of squares
    SST = ((data - grand_mean[None, :, None]) ** 2).sum(axis=(0, 2))   # (v,)
    SSR = k * ((subj_mean - grand_mean[None, :]) ** 2).sum(axis=0)     # (v,) rows = subjects
    SSC = n * ((sess_mean - grand_mean[:, None]) ** 2).sum(axis=1)     # (v,) columns = sessions
    SSE = SST - SSR - SSC                                             # (v,) residual/error

    dfR = n - 1
    dfC = k - 1
    dfE = (n - 1) * (k - 1)

    MSR = SSR / dfR
    MSC = SSC / dfC
    MSE = SSE / dfE

    # ICC(2,1): two-way random effects, absolute agreement, single measurement
    icc21 = (MSR - MSE) / (MSR + (k - 1) * MSE + (k / n) * (MSC - MSE))

    # ICC(3,1): two-way mixed effects, consistency, single measurement
    icc31 = (MSR - MSE) / (MSR + (k - 1) * MSE)

    return icc21, icc31


def main():
    print("Loading data...")
    test_data, retest_data, subject_ids = load_dataset()

    subjects = find_subject_files()
    reference_img = nib.load(subjects[subject_ids[0]]["test"])
    cortex_mask = get_cortical_mask(reference_img)

    test_cortex = test_data[:, cortex_mask]
    retest_cortex = retest_data[:, cortex_mask]

    # Restrict to vertices with complete data across all subjects, both
    # sessions (same restriction as script 06's ICC(2,1) analysis)
    valid = np.all(np.isfinite(test_cortex), axis=0) & np.all(np.isfinite(retest_cortex), axis=0)
    print(f"Valid vertices (complete N=43, both sessions): {valid.sum()}")

    test_valid = test_cortex[:, valid]
    retest_valid = retest_cortex[:, valid]

    print("Computing ICC(2,1) and ICC(3,1) at every valid vertex...")
    icc21, icc31 = compute_icc_2_1_and_3_1(test_valid, retest_valid)

    summary = pd.DataFrame({
        "Metric": ["Valid vertices", "Mean ICC(2,1)", "Mean ICC(3,1)",
                   "Median ICC(2,1)", "Median ICC(3,1)",
                   "Pearson r between ICC(2,1) and ICC(3,1) across vertices",
                   "Mean absolute difference |ICC(2,1) - ICC(3,1)|"],
        "Value": [
            int(valid.sum()),
            round(float(np.nanmean(icc21)), 4),
            round(float(np.nanmean(icc31)), 4),
            round(float(np.nanmedian(icc21)), 4),
            round(float(np.nanmedian(icc31)), 4),
            round(float(np.corrcoef(icc21, icc31)[0, 1]), 4),
            round(float(np.nanmean(np.abs(icc21 - icc31))), 4),
        ],
    })

    output_file = TABLES_DIR / "icc21_vs_icc31_comparison.csv"
    summary.to_csv(output_file, index=False)

    print("\n" + "=" * 60)
    print("ICC(2,1) vs ICC(3,1) COMPARISON")
    print("=" * 60)
    print(summary.to_string(index=False))
    print(f"\nSaved: {output_file}")


if __name__ == "__main__":
    main()