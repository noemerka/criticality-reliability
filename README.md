# Test-retest reliability of functional criticality

## Project summary

This repository contains the analysis code for a Bachelor's thesis evaluating
the test-retest reliability of vertex-wise functional criticality (vIFC) maps
in the Human Connectome Project (HCP) test-retest sample. Reliability is
assessed at four levels: group-level significance and replication, vertex-wise
reliability (ICC), and individual-level stability (whole-map similarity and
rank-order continuity), including a breakdown by Yeo-7 functional network.

## Data

- **Source:** HCP test-retest resting-state fMRI, pre-computed vertex-wise
  Index of Functional Criticality (vIFC) maps (Jiang et al., 2019), provided
  by Alina Podschun (Markett Lab).
- **Participants:** N = 43, two sessions each (test, retest).
- **Format:** CIFTI dscalar files (`.dscalar.nii`), 91,282 grayordinates
  (59,412 cortical vertices in fsLR32k space + 31,870 subcortical voxels,
  the latter zero-filled since vIFC is a cortical-only measure).
- **Surface geometry:** HCP S1200 group-average midthickness surfaces
  (`S1200.{L,R}.midthickness_MSMAll.32k_fs_LR.surf.gii`), used for surface
  rendering only, not part of the vIFC computation itself.
- Raw criticality maps are not redistributed in this repository; see
  `data/README_data.md` for the expected directory layout and how to point
  the pipeline at your own copy of the data.

## Installation

This project uses `pip` with a virtual environment. Exact package
versions are pinned in `requirements.txt`.

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Required environment variables

The pipeline reads all data paths from environment variables instead of
hard-coded paths (see `src/config.py`):

```bash
export CRITICALITY_DATA=/path/to/hcp_test_retest_maps
export CRITICALITY_SURFACES=/path/to/surfaces   # Yeo labels + fsLR32k surfaces
```

## Reproducing the analysis

Run the scripts from the repository root, in the following order:

```bash
python -m scripts.01_check_dataset
python -m scripts.02_group_mean
python -m scripts.03_group_sd
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
```

Scripts `04`, `05`, `19`, and `24` from earlier pipeline iterations were
removed as superseded/empty; see `docs/analysis_log.md` for details.

## Outputs

- **`results/maps/`** — group-level CIFTI maps: mean, SD, and one-sample
  t-maps per session (unthresholded and FDR-thresholded), vertex-wise
  ICC(2,1) map, FDR q-value maps.
- **`results/tables/`** — summary statistics for group-map replication
  (mean-map and t-map correlation, top-5%/10% overlap, Dice), vertex-wise
  and network-wise ICC summaries, whole-map similarity (raw and demeaned),
  rank-order continuity (whole-cortex and per network), data-completeness
  diagnostics.
- **`results/figures/`** — scatterplots (group mean-map and t-map
  replication, rank-order), histograms (ICC distribution, whole-map
  similarity), and cortical surface renderings (group maps, thresholded
  t-maps, ICC map) produced directly from CIFTI + surface geometry via
  `scripts/33_render_surfaces.py`.

## Notes

- **Random seeds:** this pipeline is fully deterministic. No step relies on
  random sampling, bootstrapping, or permutation testing (ICC, Pearson/
  Spearman correlations, the one-sample t-tests, FDR correction, and the
  hypergeometric overlap test are all exact, closed-form computations).
  There is therefore no random seed to fix; this is a deliberate design
  choice rather than an oversight.
- **Sample size:** N = 43 participants were available and used throughout,
  differing from the N = 37 specified in the exposé; the source of this
  discrepancy was not resolved within the scope of this project.
- **Group-level significance is near-ubiquitous:** group t-values are large
  across almost the entire cortex (14.2–59.4), so FDR-thresholded maps
  retain ~99–100% of testable vertices in both sessions. This is reported
  as a substantive finding, not a thresholding error; the top-5%/10%
  vertex-overlap analysis is the primary spatial-specificity measure for
  group-map replication (see `docs/analysis_log.md`).
- **Known artifact:** a highly localized peak in the group mean map, near
  the cortical midline, was traced to the medial-wall mask boundary rather
  than a genuine neurobiological effect (see `docs/analysis_log.md`).
- Vertex-wise ICC and related analyses are restricted to the 58,435 / 59,412
  (98.4%) cortical vertices with complete data from all 43 participants in
  both sessions.
