"""
Threshold group-level t-maps using FDR correction.

Updated version. The previous approach restricted inferential
thresholding to vertices with complete data from all N=43
participants, then applied a fixed, uncorrected one-sided p < .05
threshold with a single global critical t-value (df = 42).

Two changes are made here:

1. Vertex-specific degrees of freedom. Each vertex's own valid
   participant count (as already used in 09_group_tmaps.py) is used
   to compute that vertex's p-value, instead of requiring complete
   data from all 43 participants. This uses the full cortex (any
   vertex with at least 2 valid observations) rather than only the
   58,435 / 59,412 (98.4%) vertices with complete N=43 coverage.

2. Benjamini-Hochberg FDR correction (q < .05) across all testable
   cortical vertices, instead of an uncorrected per-vertex p < .05.

Note on expected impact: group-level t-values in this dataset are
very large everywhere on the cortex (observed range in a pilot check:
t = 14.2 to 59.4), so almost every vertex is significant even after
FDR correction. This is expected and is itself a reportable finding
("criticality is reliably greater than zero across nearly the entire
cortex at the group level") -- it does not mean the correction had no
effect; it means the thresholded significance mask is not a
particularly informative measure of spatial specificity for this
particular contrast. The top-X% vertex overlap analysis
(25_criticality_overlap_chance.py) is the more informative measure
for RQ2 spatial-pattern replication and should be treated as the
primary overlap result in the thesis; the Dice coefficient computed
downstream (12_dice_coefficient.py) on these thresholded maps should
be reported alongside an explanation of why it is expected to be
close to its ceiling.

One-sided test:
H0: mean = 0
H1: mean > 0
"""

import numpy as np
import pandas as pd
import nibabel as nib
from scipy.stats import t as t_dist
from statsmodels.stats.multitest import multipletests

from src.config import MAPS_DIR, TABLES_DIR
from src.io import load_dataset
from src.cifti_utils import get_cortical_mask


ALPHA = 0.05


def compute_pvalues(tmap, n_valid):
    """
    One-sided p-values (H1: mean > 0) for a vertex-wise t-map, using
    each vertex's own degrees of freedom (n_valid - 1).
    """

    df = n_valid - 1

    pvals = np.full(tmap.shape, np.nan)

    valid = (
        np.isfinite(tmap)
        & (n_valid >= 2)
    )

    pvals[valid] = t_dist.sf(tmap[valid], df[valid])

    return pvals


def fdr_threshold_map(tmap, pvals, cortex_mask, alpha, label):
    """
    Apply Benjamini-Hochberg FDR correction within the cortical mask.

    Returns the thresholded t-map, a full-length q-value map, and a
    summary dict comparing uncorrected vs. FDR-corrected vertex
    counts.
    """

    testable = (
        cortex_mask
        & np.isfinite(tmap)
        & np.isfinite(pvals)
    )

    n_testable = int(testable.sum())

    rejected, qvals, _, _ = multipletests(
        pvals[testable],
        alpha=alpha,
        method="fdr_bh",
    )

    thresholded = np.full(tmap.shape, np.nan)
    qvalues_full = np.full(tmap.shape, np.nan)

    idx = np.flatnonzero(testable)

    qvalues_full[idx] = qvals
    thresholded[idx[rejected]] = tmap[idx[rejected]]

    n_uncorrected = int(np.sum(pvals[testable] < alpha))
    n_fdr = int(rejected.sum())

    summary = {
        "Map": label,
        "Testable vertices": n_testable,
        "Significant (uncorrected p < .05)": n_uncorrected,
        "Significant (FDR q < .05)": n_fdr,
        "Percent significant (uncorrected)": round(
            n_uncorrected / n_testable * 100, 2
        ),
        "Percent significant (FDR)": round(
            n_fdr / n_testable * 100, 2
        ),
    }

    return thresholded, qvalues_full, summary


def main():

    # ------------------------------------------------------------
    # Load subject-level data (needed for vertex-specific N)
    # ------------------------------------------------------------

    print("Loading subject-level data...")
    test_data, retest_data, subject_ids = load_dataset()

    test_n = np.sum(np.isfinite(test_data), axis=0)
    retest_n = np.sum(np.isfinite(retest_data), axis=0)

    # ------------------------------------------------------------
    # Load group t-maps (from 09_group_tmaps.py)
    # ------------------------------------------------------------

    test_img = nib.load(MAPS_DIR / "group_t_test.dscalar.nii")
    retest_img = nib.load(MAPS_DIR / "group_t_retest.dscalar.nii")

    test_t = test_img.get_fdata().squeeze()
    retest_t = retest_img.get_fdata().squeeze()

    cortex_mask = get_cortical_mask(test_img)

    print(f"Cortical grayordinates: {cortex_mask.sum()}")
    print(f"Alpha: {ALPHA}")

    # ------------------------------------------------------------
    # Vertex-specific p-values
    # ------------------------------------------------------------

    test_p = compute_pvalues(test_t, test_n)
    retest_p = compute_pvalues(retest_t, retest_n)

    # ------------------------------------------------------------
    # FDR-thresholded maps
    # ------------------------------------------------------------

    test_thresh, test_q, test_summary = fdr_threshold_map(
        test_t, test_p, cortex_mask, ALPHA, "Test"
    )

    retest_thresh, retest_q, retest_summary = fdr_threshold_map(
        retest_t, retest_p, cortex_mask, ALPHA, "Retest"
    )

    # ------------------------------------------------------------
    # Save maps
    # ------------------------------------------------------------

    def save(data, filename):
        new_img = nib.Cifti2Image(
            data[np.newaxis, :],
            header=test_img.header,
            nifti_header=test_img.nifti_header,
        )
        nib.save(new_img, MAPS_DIR / filename)

    save(test_thresh, "group_thresholded_t_test.dscalar.nii")
    save(retest_thresh, "group_thresholded_t_retest.dscalar.nii")
    save(test_q, "group_qvalues_test.dscalar.nii")
    save(retest_q, "group_qvalues_retest.dscalar.nii")

    # ------------------------------------------------------------
    # Print / save summary
    # ------------------------------------------------------------

    summary = pd.DataFrame([test_summary, retest_summary])

    print()
    print(summary.to_string(index=False))

    summary_file = TABLES_DIR / "group_tmap_thresholding_summary.csv"
    summary.to_csv(summary_file, index=False)

    print()
    print("Thresholded maps and q-value maps saved successfully.")
    print(summary_file)
    print()
    print(
        "NOTE: this overwrites group_thresholded_t_test.dscalar.nii "
        "and group_thresholded_t_retest.dscalar.nii. Any downstream "
        "script that reads these files (12_dice_coefficient.py, and "
        "any Workbench visualizations built from the thresholded "
        "maps) must be re-run / re-rendered after this change."
    )


if __name__ == "__main__":
    main()