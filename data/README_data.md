# Data

## Source

The criticality maps analyzed in this project are vertex-wise Index of
Functional Criticality (vIFC; Jiang et al., 2019) maps computed from the
Human Connectome Project (HCP) test-retest resting-state fMRI sample. The
maps were already computed prior to the start of this thesis and were
provided by Alina Podschun (research group of Prof. Dr. Sebastian Markett,
Humboldt-Universität zu Berlin). Computing vIFC from raw fMRI timeseries is
**not** part of this repository.

- **Participants:** N = 43, two resting-state sessions each (test, retest).
- **Format:** CIFTI dscalar files (`.dscalar.nii`), one file per participant
  per session.
- **Space:** fsLR32k standard grayordinate space (91,282 grayordinates:
  59,412 cortical vertices + 31,870 subcortical voxels, the latter
  zero-filled since vIFC is a cortical-only measure).

## ⚠️ Data is not included in this repository

The raw criticality maps are **not** redistributed here, since they derive
from identifiable participant scan data (HCP restricted/open data usage
terms) and are not the author's to publish. Anyone wanting to rerun this
pipeline needs their own copy of the vIFC maps, obtained through the
appropriate channel (e.g. the Markett Lab, or by computing vIFC from HCP
resting-state data following Jiang et al., 2019).

`data/raw/` and `data/derivatives/` are present as placeholders for the
expected directory structure (see below) and are excluded from version
control via `.gitignore`.

## Expected directory layout

The pipeline does not hard-code a data location. Instead, it reads the
`CRITICALITY_DATA` and `CRITICALITY_SURFACES` environment variables (see
`src/config.py`). Point these at your own copies of the data:
````
$CRITICALITY_DATA/
├── hcp_test/
│ ├── <subject-id><...>.dscalar.nii
│ └── ...
└── hcp_retest/
├── <subject-id><...>.dscalar.nii
└── ...

$CRITICALITY_SURFACES/
├── yeo7_fslr32k_labels.npy
├── S1200.L.midthickness_MSMAll.32k_fs_LR.surf.gii
└── S1200.R.midthickness_MSMAll.32k_fs_LR.surf.gii
````
Subject IDs are inferred from the file name (the part before the first
underscore; see `src/io.py: find_subject_files()`). Every subject present
in `hcp_test/` must have a matching file in `hcp_retest/`, and vice versa,
or the pipeline will raise an error listing the mismatch.

## `data/derivatives/`

Not currently used by this pipeline; all derived outputs are written to
`results/` (see main README). This folder is kept as a placeholder in case
future extensions of this project introduce an intermediate derived-data
stage.