import nibabel as nib

img = nib.load(
    "100307_rfMRI_REST1_priorsmooth2mm_vIFC_secondorderneigh_corrthresh15.dscalar.nii"
)

axis = img.header.get_axis(1)

print("Axis type:")
print(type(axis))

print("\nNumber of grayordinates:")
print(len(axis))

print("\nSurface structures:")

for structure, slc, model in axis.iter_structures():
    if "CORTEX" in str(structure):
        print(structure)

        try:
            print("Vertex count:", model.nvertices)
        except:
            pass

        print()