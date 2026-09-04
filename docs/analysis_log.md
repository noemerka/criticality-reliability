# Analysis log

This log documents important methodological choices, deviations from the
exposé, bugs found and fixed, and open issues, in roughly chronological
order.

## Data and format

- Criticality maps were kept in CIFTI (`.dscalar.nii`) format rather than
  converted to separate left/right GIFTI (`.func.gii`) files as suggested
  in the exposé. CIFTI preserves the combined cortical grayordinate space
  in a single file and is directly compatible with Connectome Workbench
  and standard HCP tooling; a GIFTI export was not needed for any analysis
  or visualization step and was therefore omitted.
- CIFTI files follow the standard HCP grayordinate layout: 91,282
  grayordinates = 59,412 cortical vertices (fsLR32k) + 31,870 subcortical
  voxels. The subcortical portion is a constant placeholder value of
  exactly 0.0 for all participants and both sessions in this dataset,
  since vIFC is a purely cortical measure. **All analyses explicitly
  restrict to the cortical mask** (`src/cifti_utils.get_cortical_mask`);
  omitting this mask was the source of a significant early bug (see below).
- Final sample: N = 43 participants, differing from the N = 37 stated in
  the original exposé. Not resolved within the scope of this project.
- Data completeness (`scripts/30_check_data_completeness.py`): 58,435 /
  59,412 cortical vertices (98.4%) have complete data from all 43
  participants in both sessions; the remaining 1.6% have reduced
  participant coverage (minimum N = 33 at any single vertex). No
  participant has fully complete data across the whole cortex, which is
  normal for surface-based fMRI data (individual differences in surface
  reconstruction near the medial wall) and not a data-quality concern at
  this magnitude.

## Bugs found and fixed during development

1. **Yeo-7 network mapping (scripts 21, 26, 28).** CIFTI `BrainModelAxis`
   vertex indices (`bm.vertex`) are hemisphere-local (0..32491 for BOTH
   hemispheres), while the Yeo label file is a single array with left
   hemisphere first, right hemisphere second. Concatenating raw `bm.vertex`
   indices across hemispheres and indexing directly into the full label
   array silently swaps in left-hemisphere labels for right-hemisphere
   vertices. Fixed via a single shared helper,
   `src/cifti_utils.map_yeo_labels_to_cifti_cortex`, which slices the label
   array per hemisphere before indexing. Only `scripts/23_network_vertexwise_icc.py`
   had this right from the start (hence the `_corrected` suffix in its
   original output filename, kept for continuity).
2. **NaN propagation in group mean/SD (scripts 02, 03).** The original
   scripts used the plain `.mean(axis=0)` / `.std(axis=0)` methods, which
   propagate NaN to the group statistic at any vertex where even one
   participant has a missing value (affects the 1.6% of vertices with
   incomplete coverage). Fixed by switching to `np.nanmean` / `np.nanstd`,
   consistent with how `scripts/09_group_tmaps.py` already handled missing
   data.
3. **Missing cortical mask in whole-map similarity (scripts 13, 14).**
   These scripts computed correlations/means over the full CIFTI array
   without restricting to the cortical mask. Because the ~31,870
   subcortical grayordinates are a constant 0.0 for every participant in
   both sessions, including them inflated the raw whole-map similarity
   (observed: ~0.94-0.98 unmasked vs. ~0.88 masked), since a large block of
   identical (0, 0) pairs mechanically pulls a Pearson correlation toward
   1. Fixed by restricting both scripts to the cortical mask.
4. **Uncorrected group-level thresholding (script 10).** The original
   script thresholded group t-maps at an uncorrected p < .05 with a fixed
   critical t-value, restricted to vertices with complete N = 43 coverage.
   Because group t-values are very large almost everywhere (14.2-59.4),
   this retained ~99% of the cortex, making the resulting Dice coefficient
   (script 12) trivially close to 1.0. Replaced with a proper
   Benjamini-Hochberg FDR correction (q < .05) using vertex-specific
   degrees of freedom (matching the vertex-specific N already used in
   script 09), removing the dependency on complete-case restriction. FDR
   correction still retains ~99-100% of the cortex in both sessions; this
   is now treated as a **substantive finding** (criticality is reliably
   > 0 across nearly the whole cortex at the group level) rather than a
   thresholding artifact. The top-5%/10% vertex-overlap analysis
   (`scripts/25_criticality_overlap_chance.py`, with a hypergeometric
   significance test) is used as the primary measure of spatial
   specificity for group-map replication instead of the Dice coefficient.

## Superseded / removed scripts

- `04_group_correlation.py` - superseded by `18_group_mean_correlation.py`,
  which adds correct cortical masking. Removed.
- `05_vertexwise_icc.py` - empty (0-byte) duplicate of
  `06_vertexwise_icc.py`. Removed.
- `19_top_percent_overlap.py`, `24_top_overlap_chance.py` - early
  iterations of the top-X% overlap analysis, superseded by
  `25_criticality_overlap_chance.py` (correct cortical masking + a
  hypergeometric significance test against chance overlap). Removed.

## Known artifact: medial-wall boundary peak

The group mean criticality map shows a highly localized, very high-value
peak bilaterally, near the cortical midline. Coordinate-level inspection
(peak vertex location on the midthickness surface, checked in all four
cases: left/right hemisphere x test/retest session) showed the peak sits
within 10 mm of the midline (x ~ 8-9 mm), at a consistent posterior-medial
position (y ~ -43 to -45 mm, z ~ 5-9 mm), with three of the peak vertex's
six mesh neighbors being excluded, non-cortical medial-wall vertices in
both hemispheres. This is far more consistent with a mask-boundary /
partial-volume artifact than a genuine neurobiological effect, and it is
reported as such (not as a "Sylvian fissure" or other anatomical finding)
in the thesis. **Open issue:** a systematic exclusion of vertices within a
fixed distance of the medial wall from any peak-based analysis would be a
useful addition if this pipeline is extended.

## Robustness check: non-parametric confirmation of group-level significance

After the initial analysis, a non-parametric sign-flip permutation test
(`scripts/34_signflip_permutation_robustness.py`) was added to check
whether the near-ubiquitous group-level significance (Section 3.1 /
`10_threshold_group_tmaps.py`) depends on the parametric assumptions of
the classical one-sample t-test. This follows the exposé's explicitly
suggested alternative ("an FSL-based one-sample permutation analysis
with randomise"), implemented directly in Python rather than via FSL.
2,000 sign-flip iterations were used per session, with Benjamini-Hochberg
FDR correction applied to the resulting permutation p-values. Result:
100% of testable cortical vertices remained significant in both
sessions, exactly matching the parametric result. See Thesis Section
4.5 for the interpretation.

## Traceability: thesis tables to source files

The thesis presents a small number of tables that were assembled by
combining values from already-existing, script-generated CSV outputs
(no new computation), to match the exact table format suggested in the
exposé:

- **Thesis Table 4** (whole-map similarity, raw and demeaned) combines
  `results/tables/whole_map_similarity_summary.csv` (script 13) and
  `results/tables/whole_map_similarity_demeaned_summary.csv` (script 31).
- **Thesis Table 5** (rank-order continuity, whole cortex + networks)
  combines the whole-cortex row from
  `results/tables/rank_order_continuity.csv` (script 14) with the
  network rows from `results/tables/network_rank_continuity.csv`
  (script 22).

All other thesis tables correspond 1:1 to a single CSV output file
(e.g. Table 2 = `icc_summary.csv`, Table 3 = `network_icc_qc.csv`).

## Reproducibility: random seeds

With one exception, this pipeline does not use random sampling, bootstrapping, or permutation testing: all core statistics (ICC, Pearson/Spearman correlations, one-sample t-tests, FDR correction, the hypergeometric overlap test) are exact, closed-form computations, so no random seed needs to be fixed for them.

The exception is `scripts/34_signflip_permutation_robustness.py`, a supplementary non-parametric robustness check (added after submission of the initial analysis) that uses a sign-flip permutation test (2,000 iterations) to verify the parametric group-level FDR result without relying on t-distribution assumptions. This script uses a fixed random seed (`RANDOM_SEED = 42`, via `numpy.random.default_rng`) so that its output is exactly reproducible. Result: 100% of testable cortical vertices remained significant after FDR correction in both sessions, matching the parametric result in `10_threshold_group_tmaps.py` exactly (see `docs/analysis_log.md` and Thesis Section 4.5).

## Methodological deviations from the exposé (summary)

See the thesis Methods chapter (Section 2.8) for the full list with
justifications: CIFTI instead of GIFTI output format; manual Python
one-sample t-test instead of SPM12/FSL; FDR correction added (not
specified in the exposé); demeaned whole-map similarity added as a
complement to the exposé's suggested whole-map similarity measure; N = 43
instead of N = 37.