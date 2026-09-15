# Analysis log

Notes on the main methodological choices, bugs, and fixes in this
pipeline.

## Data

CIFTI (`.dscalar.nii`) was kept throughout rather than converting to
GIFTI: it preserves both hemispheres in a single file and is directly
compatible with Connectome Workbench, and no analysis step required a
GIFTI export. Standard HCP grayordinate layout: 91,282 grayordinates
total, 59,412 cortical, the remainder subcortical (constant zero for
this dataset, since vIFC is a purely cortical measure).

Final N = 43, differing from the N = 37 stated in the exposé. The
source of this discrepancy was not resolved within the scope of this
project; it does not appear to affect the qualitative pattern of
results.

Not every vertex has data from all 43 participants in both sessions:
58,435 of 59,412 (98.4%) do; the remainder have reduced coverage
(minimum N = 33). See `scripts/30_check_data_completeness.py`.

## Bugs found and fixed

**Yeo-7 label mapping (scripts 21, 26, 28).** CIFTI vertex indices are
hemisphere-local, while the Yeo label file is a single concatenated
array (left hemisphere first). Combining the two directly mixes up
which labels belong to which hemisphere. Fixed via a shared helper,
`map_yeo_labels_to_cifti_cortex` in `src/cifti_utils.py`, which slices
the label array per hemisphere before indexing. Script 23 already
handled this correctly.

**NaN propagation in group mean/SD (scripts 02, 03).** The plain
`.mean()`/`.std()` methods propagate NaN to the group statistic at any
vertex with even one missing participant. Fixed by switching to
`np.nanmean`/`np.nanstd`.

**Missing cortical mask (scripts 13, 14).** Correlations were computed
over the full grayordinate array rather than restricted to cortex.
Because the subcortical portion is a constant zero for every
participant, this inflated the raw whole-map similarity (~0.95
unmasked vs. ~0.88 masked). Fixed by applying the cortical mask before
computing each correlation.

**Uncorrected thresholding (script 10).** The original version used an
uncorrected one-sided p < .05 with a single fixed critical t-value,
restricted to vertices with complete N = 43 coverage. Group t-values
are very large almost everywhere (14.2–59.4 in a pilot check), so this
retained close to the entire cortex regardless of threshold choice.
Replaced with vertex-specific degrees of freedom and Benjamini-Hochberg
FDR correction; the result is materially unchanged (~99–100%
significant in both sessions), which is reported as a substantive
finding rather than a thresholding artifact. The top-5%/10% vertex
overlap analysis (script 25) is used as the primary measure of spatial
specificity for this reason, rather than the Dice coefficient computed
on the thresholded maps.

## Removed / renumbered scripts

An earlier `04_group_correlation.py` was superseded by
`18_group_mean_correlation.py` and removed; the number `04` was later
reused for an unrelated ICC validation script. An earlier, empty
`05_vertexwise_icc.py` duplicate was likewise removed, with `05` later
reused for a different validation script. `19_top_percent_overlap.py`
and `24_top_overlap_chance.py` were early iterations of the top-X%
overlap analysis, superseded by `25_criticality_overlap_chance.py` and
removed without reuse of their numbers.

## Medial-wall boundary artifact

The group mean criticality map shows a highly localized peak near the
cortical midline in both hemispheres and sessions. Coordinate-level
inspection showed the peak sits directly on the boundary of the
medial-wall mask, with half of its immediate mesh neighbors excluded
as non-cortical. This is consistent with a partial-volume artifact at
the mask boundary rather than a genuine effect, and is reported as
such rather than as an anatomical finding.

## Sign-flip permutation check (script 34)

Added as a non-parametric robustness check on the group-level t-test,
following the exposé's suggested FSL-randomise-style alternative,
implemented directly in Python to avoid an FSL/MATLAB dependency.
2,000 sign-flip iterations per session, with the same FDR correction
procedure as script 10. Result matches the parametric outcome almost
exactly (100% significant in both sessions). Uses a fixed random seed
(42); this is the only step in the pipeline that relies on randomness.

## ICC(2,1) vs. ICC(3,1) comparison (script 35)

Added the consistency-based ICC(3,1) alongside the primary
absolute-agreement ICC(2,1), per the exposé's suggestion that this
"can also be informative if feasible." The two forms are nearly
identical (r = .999 across vertices), indicating that the observed
unreliability mainly reflects unsystematic noise rather than a
systematic shift between sessions.

## Table sources

Most thesis tables correspond directly to a single script's CSV
output. Two exceptions: the whole-map-similarity table combines the
summaries from scripts 13 and 31 (raw and demeaned); the rank-order
table combines the whole-cortex row from script 14 with the
network-level rows from script 22.

## Random seeds

With the exception of script 34, this pipeline uses no random
sampling, bootstrapping, or permutation testing; all other statistics
are exact, closed-form computations.