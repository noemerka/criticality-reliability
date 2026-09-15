# Data

The criticality maps used in this project are vertex-wise Index of
Functional Criticality (vIFC) maps from the HCP test-retest
resting-state sample (Jiang et al., 2019). The maps were computed
prior to the start of this thesis and were provided by Alina Podschun
(research group of Prof. Dr. Sebastian Markett, Humboldt-Universität
zu Berlin); computing vIFC from raw fMRI timeseries is not part of
this repository.

Sample: 43 participants, two sessions each (test, retest), stored as
CIFTI dscalar files (one file per participant per session). Standard
fsLR32k grayordinate space: 91,282 grayordinates total, of which
59,412 are cortical; the remainder are subcortical and zero-filled,
since vIFC is defined only for cortex.

## Raw data is not included in this repository

The maps are not redistributed here, since they derive from
identifiable HCP scan data and are not the author's to publish.
Reproducing this pipeline requires an independently obtained copy of
the vIFC maps (e.g. via the Markett lab, or by computing vIFC from HCP
resting-state data following Jiang et al., 2019).

`data/raw/` and `data/derivatives/` exist as empty placeholders for
the directory layout described below and are excluded via
`.gitignore`.

## Expected directory layout

Paths are not hard-coded; the pipeline reads two environment variables
(see `src/config.py`):

```
$CRITICALITY_DATA/
├── hcp_test/
│   ├── <subject-id>_<...>.dscalar.nii
│   └── ...
└── hcp_retest/
    ├── <subject-id>_<...>.dscalar.nii
    └── ...

$CRITICALITY_SURFACES/
├── yeo7_fslr32k_labels.npy
├── S1200.L.midthickness_MSMAll.32k_fs_LR.surf.gii
└── S1200.R.midthickness_MSMAll.32k_fs_LR.surf.gii
```

Subject IDs are inferred from the filename, taken as everything before
the first underscore (`src/io.py`, `find_subject_files()`). A subject
present in `hcp_test/` but missing from `hcp_retest/`, or vice versa,
causes the pipeline to raise an error listing the mismatch.

`data/derivatives/` is not currently used; all derived output is
written to `results/` instead. The folder is kept as a placeholder in
case this changes in a future extension.