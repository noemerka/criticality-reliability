import nibabel as nib
import numpy as np
import glob

files = sorted(glob.glob("*REST2*.dscalar.nii"))

for f in files:
    data = nib.load(f).get_fdata().squeeze()

    valid = np.sum(~np.isnan(data))
    mean = np.nanmean(data)

    print(f[:6], valid, round(mean, 2))