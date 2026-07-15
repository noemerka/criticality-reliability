
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (RAW_TEST_DIR, RAW_RETEST_DIR, GROUP_MAPS_DIR,
                    SWE_DIR, FDR_ALPHA)

import nibabel as nib
import numpy as np
import glob
import os

# ---------------------------------------------------------------------
# Konfiguration
# ---------------------------------------------------------------------

L_START, L_END = 0, 29696
R_START, R_END = 29696, 59412

SESSIONS = {
    "test": {
        "swe_dir": os.path.join(SWE_DIR, "test"),
        "raw_dir": RAW_TEST_DIR,
        "raw_pattern": "*.dscalar.nii",
    },
    "retest": {
        "swe_dir": os.path.join(SWE_DIR, "retest"),
        "raw_dir": RAW_RETEST_DIR,
        "raw_pattern": "*.dscalar.nii",
    },
}

OUT_DIR = GROUP_MAPS_DIR
FDR_ALPHA = 0.05

REFERENCE_CIFTI = os.path.join(SWE_DIR, "test", "swe_dpx_beta_b01.dscalar.nii")


# ---------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------

def load_cifti_cortex(path):
    img = nib.load(path)
    return img.get_fdata()[0][:59412]


def save_gifti_hemi(data_full, reference_cifti, out_path, hemi):
    """
    Speichert eine GIFTI-Datei mit vollständigen Workbench-Metadaten.
    """

    if hemi == "L":
        data = data_full[L_START:L_END]
        structure = "CortexLeft"
    else:
        data = data_full[R_START:R_END]
        structure = "CortexRight"

    da = nib.gifti.GiftiDataArray(
        data=data.astype(np.float32),
        intent=nib.nifti1.intent_codes["NIFTI_INTENT_SHAPE"],
        datatype="NIFTI_TYPE_FLOAT32",
    )

    ref = nib.load(reference_cifti)

    gii = nib.gifti.GiftiImage()

    # komplette Metadaten übernehmen
    for k, v in ref.meta.items():
        gii.meta[k] = v

    gii.meta["AnatomicalStructurePrimary"] = structure

    gii.add_gifti_data_array(da)

    nib.save(gii, out_path)


# ---------------------------------------------------------------------
# Hauptfunktion
# ---------------------------------------------------------------------

def process_session(session_name, cfg):

    print("\n" + "=" * 60)
    print(session_name.upper())
    print("=" * 60)

    outdir = os.path.join(OUT_DIR, session_name)
    os.makedirs(outdir, exist_ok=True)

    beta = load_cifti_cortex(
        os.path.join(cfg["swe_dir"], "swe_dpx_beta_b01.dscalar.nii")
    )

    tmap = load_cifti_cortex(
        os.path.join(cfg["swe_dir"], "swe_dpx_Tstat_c01.dscalar.nii")
    )

    lp = load_cifti_cortex(
        os.path.join(cfg["swe_dir"], "swe_dpx_Tstat_lpFDR-WB_c01.dscalar.nii")
    )

    raw = sorted(glob.glob(os.path.join(cfg["raw_dir"], cfg["raw_pattern"])))

    mat = np.full((len(raw), 59412), np.nan, dtype=np.float32)

    for i, f in enumerate(raw):
        mat[i] = load_cifti_cortex(f)

    sd = np.nanstd(mat, axis=0, ddof=1)

    p = 10 ** (-lp)

    thresh = np.where(p < FDR_ALPHA, tmap, 0)

    maps = {
        f"group_mean_criticality_{session_name}": beta,
        f"group_sd_criticality_{session_name}": sd,
        f"group_t_criticality_{session_name}": tmap,
        f"group_thresholded_t_criticality_{session_name}": thresh,
    }

    for name, data in maps.items():

        left = os.path.join(outdir, f"{name}_L.func.gii")
        right = os.path.join(outdir, f"{name}_R.func.gii")

        save_gifti_hemi(data, REFERENCE_CIFTI, left, "L")
        save_gifti_hemi(data, REFERENCE_CIFTI, right, "R")

        print("gespeichert:", left)
        print("gespeichert:", right)


# ---------------------------------------------------------------------

if __name__ == "__main__":

    os.makedirs(OUT_DIR, exist_ok=True)

    for session, cfg in SESSIONS.items():
        process_session(session, cfg)

    print("\nFertig.")
