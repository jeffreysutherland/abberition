#%%
# generate wcs for a set of calibrated light 
import logging
import warnings
logging.getLogger().setLevel(level=logging.DEBUG)

from test_setup import *

from pathlib import Path
from abberition import astrometry, io

from astropy.utils.exceptions import AstropyWarning
warnings.simplefilter('ignore', category=AstropyWarning)

data_path = Path('../.output/lights_g/2023.05.12/m51/lights')
wcs_path = Path('../.output/lights_g/2023.05.12/m51/wcs')

io.mkdirs_backup_existing(wcs_path)

ifc = io.get_images(data_path, True, sanitize_headers=True)

for ccd, fn in ifc.ccds(return_fname=True):
    out_fn = wcs_path / fn
    wcs_ccd = astrometry.full_wcs(ccd, out_fn, overwrite=True)



# %%
