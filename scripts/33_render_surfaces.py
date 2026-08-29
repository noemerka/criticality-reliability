"""
Render cortical CIFTI maps as brain surface figures using nilearn and
the S1200 fsLR32k group-average inflated surfaces.

This replaces manual Connectome Workbench screenshots with a fully
reproducible, scripted rendering step -- consistent with the
exposé's requirement that all main figures be reproducible from
code (Section 8: "reproducible scripts for all main figures and
tables").

Produces:
- vertexwise_icc_surface.png       : single map, 4 panels
                                      (L/R x lateral/medial)
- group_t_surface.png              : test vs retest, lateral views
- group_thresholded_t_surface.png  : test vs retest, lateral views
- group_mean_surface.png           : test vs retest, lateral views

Requires: pip install nilearn (if not already installed)
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
from nilearn import plotting

from src.config import (
    MAPS_DIR,
    FIGURES_DIR,
    SURFACE_LEFT_INFLATED,
    SURFACE_RIGHT_INFLATED,
)
from src.cifti_utils import cifti_hemi_to_surface


def load_mesh(path):
    surf = nib.load(path)
    return (surf.darrays[0].data, surf.darrays[1].data)


def render_single_map(
    cifti_path,
    title,
    output_path,
    left_mesh,
    right_mesh,
    cmap="viridis",
    vmin=None,
    vmax=None,
    views=("lateral", "medial"),
):
    """
    Render one CIFTI map as a grid figure: rows = hemispheres,
    columns = the requested views (e.g. lateral, medial, ventral).
    """

    img = nib.load(cifti_path)
    data = img.get_fdata().squeeze()

    left = cifti_hemi_to_surface(data, img, "LEFT")
    right = cifti_hemi_to_surface(data, img, "RIGHT")

    if vmin is None:
        vmin = np.nanpercentile(
            np.concatenate([left[np.isfinite(left)], right[np.isfinite(right)]]),
            2,
        )
    if vmax is None:
        vmax = np.nanpercentile(
            np.concatenate([left[np.isfinite(left)], right[np.isfinite(right)]]),
            98,
        )

    n_views = len(views)

    fig, axes = plt.subplots(
        2, n_views, figsize=(5 * n_views, 8), subplot_kw={"projection": "3d"}
    )
    if n_views == 1:
        axes = axes.reshape(2, 1)

    for col, view in enumerate(views):
        plotting.plot_surf_stat_map(
            left_mesh, stat_map=left, hemi="left", view=view,
            colorbar=False, cmap=cmap, vmin=vmin, vmax=vmax,
            axes=axes[0, col], figure=fig, bg_on_data=False,
        )
        axes[0, col].set_title(f"Left {view}", fontsize=10)

        plotting.plot_surf_stat_map(
            right_mesh, stat_map=right, hemi="right", view=view,
            colorbar=False, cmap=cmap, vmin=vmin, vmax=vmax,
            axes=axes[1, col], figure=fig, bg_on_data=False,
        )
        axes[1, col].set_title(f"Right {view}", fontsize=10)

    fig.suptitle(title, fontsize=14)

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm.set_array([])
    cbar_ax = fig.add_axes([0.92, 0.15, 0.015, 0.7])
    fig.colorbar(sm, cax=cbar_ax)

    plt.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close()

    print(f"Saved: {output_path}")


def render_test_retest_lateral(
    test_path,
    retest_path,
    title,
    output_path,
    left_mesh,
    right_mesh,
    cmap="magma",
    vmin=None,
    vmax=None,
):
    """
    Render a test/retest pair as a 2x2 figure: rows = test/retest,
    columns = left/right hemisphere, lateral view only. Both maps
    share one color scale for direct visual comparison.
    """

    test_img = nib.load(test_path)
    retest_img = nib.load(retest_path)

    test_data = test_img.get_fdata().squeeze()
    retest_data = retest_img.get_fdata().squeeze()

    test_left = cifti_hemi_to_surface(test_data, test_img, "LEFT")
    test_right = cifti_hemi_to_surface(test_data, test_img, "RIGHT")
    retest_left = cifti_hemi_to_surface(retest_data, retest_img, "LEFT")
    retest_right = cifti_hemi_to_surface(retest_data, retest_img, "RIGHT")

    allvals = np.concatenate([
        test_left[np.isfinite(test_left)],
        test_right[np.isfinite(test_right)],
        retest_left[np.isfinite(retest_left)],
        retest_right[np.isfinite(retest_right)],
    ])

    if vmin is None:
        vmin = np.nanpercentile(allvals, 2)
    if vmax is None:
        vmax = np.nanpercentile(allvals, 98)

    fig, axes = plt.subplots(2, 2, figsize=(9, 8), subplot_kw={"projection": "3d"})

    panels = [
        (left_mesh, test_left, "left", axes[0, 0], "Test - Left"),
        (right_mesh, test_right, "right", axes[0, 1], "Test - Right"),
        (left_mesh, retest_left, "left", axes[1, 0], "Retest - Left"),
        (right_mesh, retest_right, "right", axes[1, 1], "Retest - Right"),
    ]

    for mesh, data_hemi, hemi, ax, subtitle in panels:
        plotting.plot_surf_stat_map(
            mesh,
            stat_map=data_hemi,
            hemi=hemi,
            view="lateral",
            colorbar=False,
            cmap=cmap,
            vmin=vmin,
            vmax=vmax,
            axes=ax,
            figure=fig,
            bg_on_data=False,
        )
        ax.set_title(subtitle, fontsize=10)

    fig.suptitle(title, fontsize=14)

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm.set_array([])
    cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])
    fig.colorbar(sm, cax=cbar_ax)

    plt.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close()

    print(f"Saved: {output_path}")


def main():

    print("Loading surface geometry...")
    left_mesh = load_mesh(SURFACE_LEFT_INFLATED)
    right_mesh = load_mesh(SURFACE_RIGHT_INFLATED)

    # ------------------------------------------------------------
    # RQ3: vertex-wise ICC map (single map, full 4-panel detail)
    # ------------------------------------------------------------

    render_single_map(
        MAPS_DIR / "vertexwise_icc.dscalar.nii",
        "Vertex-wise ICC(2,1)",
        FIGURES_DIR / "vertexwise_icc_surface.png",
        left_mesh,
        right_mesh,
        cmap="viridis",
        vmin=0.0,
        vmax=1.0,
        views=("lateral", "medial", "ventral"),
    )

    # ------------------------------------------------------------
    # RQ1/RQ2: group t-maps, test vs retest
    # ------------------------------------------------------------

    render_test_retest_lateral(
        MAPS_DIR / "group_t_test.dscalar.nii",
        MAPS_DIR / "group_t_retest.dscalar.nii",
        "Group-level t-map (unthresholded)",
        FIGURES_DIR / "group_t_surface.png",
        left_mesh,
        right_mesh,
        cmap="magma",
    )

    render_test_retest_lateral(
        MAPS_DIR / "group_thresholded_t_test.dscalar.nii",
        MAPS_DIR / "group_thresholded_t_retest.dscalar.nii",
        "Group-level t-map (FDR-thresholded, q < .05)",
        FIGURES_DIR / "group_thresholded_t_surface.png",
        left_mesh,
        right_mesh,
        cmap="magma",
    )

    # ------------------------------------------------------------
    # Supplementary: group mean maps, test vs retest
    # ------------------------------------------------------------

    render_test_retest_lateral(
        MAPS_DIR / "group_mean_test.dscalar.nii",
        MAPS_DIR / "group_mean_retest.dscalar.nii",
        "Group mean criticality",
        FIGURES_DIR / "group_mean_surface.png",
        left_mesh,
        right_mesh,
        cmap="viridis",
    )

    print("\nAll surface figures saved to:", FIGURES_DIR)


if __name__ == "__main__":
    main()