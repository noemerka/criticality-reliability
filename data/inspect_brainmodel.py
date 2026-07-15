import nibabel as nib

img = nib.load(
    "100307_rfMRI_REST1_priorsmooth2mm_vIFC_secondorderneigh_corrthresh15.dscalar.nii"
)

axis = img.header.get_axis(1)

for structure in axis.iter_structures():
    print(structure)