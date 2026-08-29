"""
Functions for locating and organizing CIFTI data files.
"""

from pathlib import Path

import nibabel as nib
import numpy as np

from nibabel.cifti2 import Cifti2Image

from src.config import TEST_DIR, RETEST_DIR


def find_subject_files() -> dict[str, dict[str, Path]]:
    """
    Find matching test and retest CIFTI files.

    Returns
    -------
    dict
        Dictionary of the form

        {
            "103818": {
                "test": Path(...),
                "retest": Path(...)
            },
            ...
        }

    Raises
    ------
    ValueError
        If subjects are missing in either the test or retest dataset.
    """

    test_files = sorted(TEST_DIR.glob("*.dscalar.nii"))
    retest_files = sorted(RETEST_DIR.glob("*.dscalar.nii"))

    test_subjects = {
        file.name.split("_")[0]: file
        for file in test_files
    }

    retest_subjects = {
        file.name.split("_")[0]: file
        for file in retest_files
    }

    missing_test = set(retest_subjects) - set(test_subjects)
    missing_retest = set(test_subjects) - set(retest_subjects)

    if missing_test:
        raise ValueError(
            f"Subjects missing from test dataset: {sorted(missing_test)}"
        )

    if missing_retest:
        raise ValueError(
            f"Subjects missing from retest dataset: {sorted(missing_retest)}"
        )

    subjects = {}

    for subject_id in sorted(test_subjects):

        subjects[subject_id] = {
            "test": test_subjects[subject_id],
            "retest": retest_subjects[subject_id],
        }

    return subjects

def load_cifti(file_path: Path) -> np.ndarray:
    """
    Load a CIFTI file and return its data as a one-dimensional NumPy array.
    """

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    img = nib.load(file_path)

    data = img.get_fdata().squeeze()

    if data.ndim != 1:
        raise ValueError(
            f"Expected a 1D array, got shape {data.shape}"
        )

    return data

def load_dataset():
    """
    Load all test and retest data.

    Returns
    -------
    test_data : np.ndarray
        Shape: (n_subjects, n_vertices)

    retest_data : np.ndarray
        Shape: (n_subjects, n_vertices)

    subject_ids : list[str]
        List of subject IDs in matching order.
    """

    subjects = find_subject_files()

    subject_ids = []
    test_data = []
    retest_data = []

    for subject_id, files in subjects.items():

        subject_ids.append(subject_id)

        test_data.append(load_cifti(files["test"]))
        retest_data.append(load_cifti(files["retest"]))

    test_data = np.vstack(test_data)
    retest_data = np.vstack(retest_data)

    return test_data, retest_data, subject_ids

def save_cifti(
    data: np.ndarray,
    reference_file: Path,
    output_file: Path,
) -> None:
    """
    Save a one-dimensional NumPy array as a CIFTI file.

    Parameters
    ----------
    data : np.ndarray
        One-dimensional data array.

    reference_file : Path
        Existing CIFTI file whose header is reused.

    output_file : Path
        Destination of the new CIFTI file.
    """

    reference = nib.load(reference_file)

    new_image = Cifti2Image(
        dataobj=data[np.newaxis, :],
        header=reference.header,
        nifti_header=reference.nifti_header,
    )

    nib.save(new_image, output_file)