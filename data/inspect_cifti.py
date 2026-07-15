import nibabel as nib

img = nib.load(
    "100307_rfMRI_REST1_priorsmooth2mm_vIFC_secondorderneigh_corrthresh15.dscalar.nii"
)

print(img)

print("\nShape:")
print(img.shape)

print("\nHeader:")
print(img.header)


import nibabel as nib
import numpy as np

img = nib.load(
    "100307_rfMRI_REST1_priorsmooth2mm_vIFC_secondorderneigh_corrthresh15.dscalar.nii"
)

x = img.get_fdata().squeeze()

print("Mean:", np.nanmean(x))
print("Std:", np.nanstd(x))
print("Min:", np.nanmin(x))
print("Max:", np.nanmax(x))


#2.Analyse
import nibabel as nib
import numpy as np

filepath = "/home/groups/markett/hcpcrit/100307_rfMRI_REST1_priorsmooth2mm_vIFC_secondorderneigh_corrthresh15.dscalar.nii"
img = nib.load(filepath)
data = img.get_fdata()
print("Shape (Maps x Grayordinates):", data.shape)

ax1 = img.header.get_axis(1)
n_total = data.shape[1]
print("\nStrukturen in den Grayordinates:")
for name, slc, bm in ax1.iter_structures():
    stop = slc.stop if slc.stop is not None else n_total
    print(f"  {name}: {stop - slc.start} Vertices (Index {slc.start}:{stop})")

print("\nWerte-Statistik:")
print("  min:", np.nanmin(data))
print("  max:", np.nanmax(data))
print("  mean:", np.nanmean(data))
print("  std:", np.nanstd(data))
print("  Anzahl NaN:", np.isnan(data).sum())
print("  Anzahl exakter Nullen:", (data == 0).sum())

# nochmal nur Cortex:
cortex_data = data[0, :59412]
print("Cortex-only Statistik:")
print("  min:", np.nanmin(cortex_data))
print("  max:", np.nanmax(cortex_data))
print("  mean:", np.nanmean(cortex_data))
print("  std:", np.nanstd(cortex_data))
print("  Anzahl NaN:", np.isnan(cortex_data).sum())
print("  Anzahl exakter Nullen:", (cortex_data == 0).sum())

# wo liegen die 27 NaNs?
cortex_data = data[0, :59412]
print("Cortex-only Statistik:")
print("  min:", np.nanmin(cortex_data))
print("  max:", np.nanmax(cortex_data))
print("  mean:", np.nanmean(cortex_data))
print("  std:", np.nanstd(cortex_data))
print("  Anzahl NaN:", np.isnan(cortex_data).sum())
print("  Anzahl exakter Nullen:", (cortex_data == 0).sum())

# bei jedem Probanden dieselben 27?
import nibabel as nib
import numpy as np
import glob

files = sorted(glob.glob("/home/groups/markett/hcpcrit/*REST1*.dscalar.nii"))[:10]
nan_sets = []
for f in files:
    img = nib.load(f)
    data = img.get_fdata()[0]
    nan_idx = set(np.where(np.isnan(data))[0].tolist())
    nan_sets.append((f.split('/')[-1], nan_idx))
    print(f"{f.split('/')[-1]}: {len(nan_idx)} NaNs")

all_same = all(s == nan_sets[0][1] for _, s in nan_sets)
print("\nAlle Dateien haben identische NaN-Positionen:", all_same)
if not all_same:
    print("Union aller NaN-Positionen ueber alle Dateien:", len(set.union(*[s for _, s in nan_sets])))