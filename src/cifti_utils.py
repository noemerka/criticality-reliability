import numpy as np
import nibabel as nib


def get_cortical_mask(img):
    """
    Return a boolean mask selecting left and right cortical
    grayordinates from a CIFTI BrainModelAxis.
    """

    axis = img.header.get_axis(1)

    cortex_mask = np.zeros(len(axis), dtype=bool)

    for structure, slc, bm in axis.iter_structures():
        if structure in (
            "CIFTI_STRUCTURE_CORTEX_LEFT",
            "CIFTI_STRUCTURE_CORTEX_RIGHT",
        ):
            cortex_mask[slc] = True

    return cortex_mask


def cifti_hemi_to_surface(cifti_data, img, hemi, n_vertices=32492):
    """
    Map a 1D CIFTI cortical data array onto a single hemisphere's
    fsLR surface vertex order, for use with surface rendering
    libraries (e.g. nilearn.plotting.plot_surf_stat_map).

    Parameters
    ----------
    cifti_data : np.ndarray
        1D data array in CIFTI grayordinate order (e.g. the data of
        a .dscalar.nii file, same length as img's data).

    img : nib.Cifti2Image
        The CIFTI image `cifti_data` was taken from (used only for
        its BrainModelAxis geometry).

    hemi : str
        "LEFT" or "RIGHT".

    n_vertices : int
        Number of fsLR surface vertices for this hemisphere (32492
        for the standard 32k_fs_LR surfaces).

    Returns
    -------
    surf_data : np.ndarray
        Length-`n_vertices` array in fsLR surface vertex order.
        Vertices with no corresponding CIFTI grayordinate (i.e. the
        medial wall) are NaN.
    """

    axis = img.header.get_axis(1)

    surf_data = np.full(n_vertices, np.nan)

    for structure, slc, bm in axis.iter_structures():
        if structure == f"CIFTI_STRUCTURE_CORTEX_{hemi}":
            surf_data[bm.vertex] = cifti_data[slc]

    return surf_data


def map_yeo_labels_to_cifti_cortex(img, yeo_labels, n_per_hemisphere=None):
    """
    Map concatenated (left + right) Yeo-7 fsLR labels onto the
    cortical grayordinates of a CIFTI image, respecting the fact
    that CIFTI BrainModelAxis vertex indices (bm.vertex) are
    hemisphere-local (0..n_per_hemisphere-1 for BOTH hemispheres),
    while `yeo_labels` is a single array with left hemisphere first
    and right hemisphere second.

    A naive concatenation of raw bm.vertex indices across both
    hemispheres and indexing directly into the full `yeo_labels`
    array silently mixes up the two hemispheres for any grayordinate
    belonging to the right hemisphere. This function avoids that by
    slicing `yeo_labels` per hemisphere before indexing.

    Parameters
    ----------
    img : nib.Cifti2Image
        Any CIFTI image whose BrainModelAxis (axis 1) contains
        CIFTI_STRUCTURE_CORTEX_LEFT and CIFTI_STRUCTURE_CORTEX_RIGHT.
        Only the axis/geometry is used, not the image's data values.

    yeo_labels : np.ndarray
        1D array of Yeo-7 (or similar) labels in fsLR vertex order,
        left hemisphere first, right hemisphere second.

    n_per_hemisphere : int, optional
        Number of fsLR vertices per hemisphere. If not given, it is
        inferred as len(yeo_labels) // 2 (requires an even length).

    Returns
    -------
    cortex_labels : np.ndarray
        Integer label for every cortical grayordinate in `img`, in
        the same order as `img`'s data when indexed with
        `get_cortical_mask(img)`. Length equals the number of
        cortical grayordinates (True entries in the cortex mask).
    """

    axis = img.header.get_axis(1)

    cortex_mask = get_cortical_mask(img)
    n_cortex = int(cortex_mask.sum())

    if n_per_hemisphere is None:
        if len(yeo_labels) % 2 != 0:
            raise ValueError(
                "yeo_labels has an odd length and cannot be split "
                "evenly into two hemispheres. Pass n_per_hemisphere "
                "explicitly."
            )
        n_per_hemisphere = len(yeo_labels) // 2

    cortex_labels = np.zeros(n_cortex, dtype=int)
    offset = 0

    for structure, slc, bm in axis.iter_structures():

        if structure == "CIFTI_STRUCTURE_CORTEX_LEFT":
            hemi_labels = yeo_labels[:n_per_hemisphere]
        elif structure == "CIFTI_STRUCTURE_CORTEX_RIGHT":
            hemi_labels = yeo_labels[n_per_hemisphere:]
        else:
            continue

        vertex_indices = bm.vertex

        if vertex_indices.max() >= n_per_hemisphere:
            raise ValueError(
                f"Vertex index {vertex_indices.max()} in structure "
                f"{structure} exceeds n_per_hemisphere="
                f"{n_per_hemisphere}. Check the label file resolution."
            )

        cortex_labels[offset: offset + len(bm)] = hemi_labels[vertex_indices]
        offset += len(bm)

    if offset != n_cortex:
        raise ValueError(
            f"Mapped {offset} cortical grayordinates but expected "
            f"{n_cortex}. Check that the image's BrainModelAxis "
            "contains both CIFTI_STRUCTURE_CORTEX_LEFT and "
            "CIFTI_STRUCTURE_CORTEX_RIGHT."
        )

    return cortex_labels