from ccdproc import CCDData, ImageFileCollection
import numpy as np
from pathlib import Path
from . import io

def to_float32(image:CCDData):
    return to_type(image, np.float32, True)

def to_type(images:CCDData|ImageFileCollection, dtype:np.dtype, copy:bool=True):
    if images is CCDData:
        if copy:
            image = image.copy()

        image.data = image.data.astype(dtype)
    return image

def convert_all_to_type(images:ImageFileCollection, dtype:np.dtype, dest_path:Path, overwrite:bool=False):
    if dest_path.exists():
        if overwrite:
            io.mkdirs_rm_existing(dest_path)
        else:
            io.mkdirs_backup_existing(dest_path)
    else:
        io.mkdirs(dest_path)

    files = []
    for ccd, fn in images.ccds(return_fname=True):
        ccd.data = ccd.data.astype(dtype)
        ccd.write(dest_path / fn)

        files.append(fn)

    ifc = ImageFileCollection(location=dest_path, filenames=files)

    return ifc
