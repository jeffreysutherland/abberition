from ccdproc import CCDData
from os import makedirs
import pathlib

import numpy as np

def to_32b_fits(file, out_file=None, overwrite=True):
    '''
    Saves the input file as 32bit fits to out_file. defaults to same directory with .f32.fit instead of .fit/.fits.
    Returns new IFC with output files
    '''

    from astropy.io import fits
    import numpy as np
    from os.path import exists
    
    print('Processing:', file)
    f = fits.open(file)
    if out_file:
        new_file = out_file
    else:
        new_file = file[0:file.rfind('.')] + '.f32.fit'

    print('Processing', file, ' - dtype:', f[0].data.dtype.name, ' - out_file:', new_file)
    
    if f[0].data.dtype.name != 'float32':
            f[0].data = f[0].data.astype(np.float32)

    if exists(new_file) and ~overwrite:
        print(new_file, 'already exists, not overwriting.')
        return None

    # make output dir if doesn't exist
    out_dir = pathlib.Path(new_file).parent
    makedirs(out_dir, exist_ok=True)
    f.writeto(new_file, overwrite=True)
    return new_file

def to_float32(image:CCDData):
    image = image.copy()
    image.data = image.data.astype(np.float32)
    return image

