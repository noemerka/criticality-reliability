#!/bin/bash
set -e

cd /home/noemerka/criticality_project

echo "=== Step 1: Removing obsolete top-level content (still safe in git history) ==="
rm -rf group_maps matlab scripts surfaces criticality-reliability config.py
rm -f run_swe_cifti_onesample.m
rm -f data/check_rest2_validity.py data/inspect_brainmodel.py data/inspect_cifti.py data/surface_space_and_resolution.py

echo "=== Step 2: Replacing results/ with the verified, current results ==="
rm -rf results
cp -r bachelor_pipeline/results results

echo "=== Step 3: Bringing in the current, verified scripts and src package ==="
mkdir -p scripts src
cp bachelor_pipeline/scripts/*.py scripts/
cp bachelor_pipeline/src/*.py src/

echo "=== Step 4: Ensuring data/ + docs/ placeholder structure exists ==="
mkdir -p data/raw data/derivatives docs notebooks
touch data/raw/.gitkeep data/derivatives/.gitkeep

echo "=== Step 5: Removing everything from git's index (files on disk are untouched) ==="
git rm -r --cached . > /dev/null

echo "=== Done. Now review with: git status ==="
