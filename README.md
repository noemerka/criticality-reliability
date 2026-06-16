# Criticality Reliability Project

## Project Overview

This project investigates the test-retest reliability of precomputed criticality maps derived from resting-state fMRI data.

The goal is not to compute criticality measures from raw fMRI data, but to evaluate the reliability and stability of the resulting maps across repeated measurements.

---

## Dataset

### Participants

* 100 unique participant IDs currently available
* Each participant has:

  * REST1 session
  * REST2 session

### File Format

* CIFTI-2 Scalar (`.dscalar.nii`)

### Spatial Resolution

* 91,282 grayordinates per map
* Left cortex: 29,696 grayordinates
* Right cortex: 29,716 grayordinates
* Additional subcortical structures included

### Surface Space

* HCP fsLR 32k surface space
* 32,492 vertices per hemisphere in the original mesh

### Missing Values

* Missing or excluded grayordinates are represented as NaN values

### Value Scaling

* Values do not appear to be z-scored or standardized
* Maps likely contain raw criticality metric values

---

## Current Status

* Data structure documented
* Initial test-retest similarity analysis completed
* Mean whole-brain REST1-REST2 correlation across participants: r ≈ 0.97

---

## Open Questions

* Project description mentions 37 HCP test-retest participants
* Current dataset contains 100 participant IDs
* Clarification from supervisor required
