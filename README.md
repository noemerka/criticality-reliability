# Test-retest reliability of functional criticality

Code for a Bachelor's thesis evaluating the test-retest reliability of
vertex-wise functional criticality (vIFC) in the HCP test-retest
sample. Reliability is assessed at four levels: group-level
significance and replication, vertex-wise reliability (ICC), and
individual-level stability (whole-map similarity and rank-order
continuity), including a breakdown by Yeo-7 functional network.

## Data

HCP test-retest resting-state fMRI, pre-computed vIFC maps (Jiang et
al., 2019). 43 participants, two sessions each. CIFTI dscalar files,
91,282 grayordinates (59,412 cortical in fsLR32k space, the remainder
subcortical and zero-filled). Surface rendering (script 33) uses the
HCP S1200 group-average midthickness surfaces, independent of the
vIFC computation itself.

Raw maps are not included in this repository; see
`data/README_data.md` for the expected directory layout and for
pointing the pipeline at an independently obtained copy of the data.

## Installation

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Data paths are read from environment variables rather than
hard-coded (see `src/config.py`):

```bash
export CRITICALITY_DATA=/path/to/hcp_test_retest_maps
export CRITICALITY_SURFACES=/path/to/surfaces
```

`CRITICALITY_DATA` requires `hcp_test/` and `hcp_retest/` subfolders
(exact file naming in `data/README_data.md`); `CRITICALITY_SURFACES`
requires the Yeo label file and the two S1200 surface files.

## Reproducing the analysis

Run the scripts from the repository root, in the following order.
Scripts `04`, `05`, and `29` are standalone ICC-validation checks
rather than part of the main pipeline (see `docs/analysis_log.md`),
but are listed here for completeness.

```bash
python -m scripts.01_check_dataset
python -m scripts.02_group_mean
python -m scripts.03_group_sd
python -m scripts.04_test_icc
python -m scripts.05_validate_icc
python -m scripts.06_vertexwise_icc
python -m scripts.07_icc_histogram
python -m scripts.08_export_statistics
python -m scripts.09_group_tmaps
python -m scripts.10_threshold_group_tmaps
python -m scripts.11_group_tmap_correlation
python -m scripts.12_dice_coefficient
python -m scripts.13_whole_map_similarity
python -m scripts.14_rank_order_continuity
python -m scripts.15_whole_map_similarity_histogram
python -m scripts.16_rank_order_scatter
python -m scripts.17_group_tmap_scatter
python -m scripts.18_group_mean_correlation
python -m scripts.20_check_yeo_labels
python -m scripts.21_network_summary_scores
python -m scripts.22_network_rank_order_continuity
python -m scripts.23_network_vertexwise_icc
python -m scripts.25_criticality_overlap_chance
python -m scripts.26_qc_yeo_mapping
python -m scripts.27_qc_reliability
python -m scripts.28_network_icc_qc
python -m scripts.29_test_icc_ci
python -m scripts.30_check_data_completeness
python -m scripts.31_demeaned_whole_map_similarity
python -m scripts.32_group_mean_scatter
python -m scripts.33_render_surfaces
python -m scripts.34_signflip_permutation_robustness
python -m scripts.35_icc21_vs_icc31_comparison
```

Scripts `19` and `24` from earlier pipeline iterations were removed as
superseded; see `docs/analysis_log.md` for details. `rerun_all.sh`
runs the full sequence above (excluding the standalone `04`/`05`
checks) and logs the output.

## Outputs

- `results/maps/` — group mean, SD, and one-sample t-maps per session
  (unthresholded and FDR-thresholded, with q-value maps), and the
  vertex-wise ICC(2,1) map.
- `results/tables/` — group-map replication statistics (correlations,
  top-5%/10% overlap with a hypergeometric enrichment test, Dice
  coefficient), vertex-wise and network-level ICC summaries (including
  the ICC(2,1) vs. ICC(3,1) comparison), whole-map similarity (raw and
  demeaned), rank-order continuity, data-completeness diagnostics, and
  supporting QC tables.
- `results/figures/` — scatterplots, histograms, and cortical surface
  renderings, produced directly from CIFTI and surface geometry via
  `scripts/33_render_surfaces.py` rather than manual screenshots.

## Notes

This pipeline is deterministic except for
`scripts/34_signflip_permutation_robustness.py`, which uses a fixed
random seed (42) for its sign-flip permutation test.

N = 43 participants were available throughout, differing from the
N = 37 specified in the exposé; the source of this discrepancy was
not resolved within the scope of this project.

Group-level significance after FDR correction is close to 100% of
testable vertices in both sessions, reflecting the very large effect
sizes in this dataset rather than a thresholding issue; the
top-5%/10% vertex-overlap analysis (script 25) is used as the primary
measure of spatial specificity for group-map replication (see
`docs/analysis_log.md`).

A highly localized peak in the group mean map, near the cortical
midline, was traced to the medial-wall mask boundary rather than a
neurobiological effect (see `docs/analysis_log.md`).

Vertex-wise ICC and related complete-case analyses are restricted to
the 58,435 of 59,412 (98.4%) cortical vertices with complete data from
all 43 participants in both sessions.