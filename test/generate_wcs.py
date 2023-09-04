#%%
# generate wcs for a set of calibrated light 
import logging
import warnings
logging.getLogger().setLevel(level=logging.INFO)

from test_setup import *

from pathlib import Path
from abberition import astrometry, io, visualize

from astropy.utils.exceptions import AstropyWarning
warnings.simplefilter('ignore', category=AstropyWarning)

data_path = Path('../.output/lights_g/2023.05.12/m51/lights')
wcs_path = Path('../.output/lights_g/2023.05.12/m51/wcs')

ifc = io.get_images(data_path, True, sanitize_headers=True)

io.mkdirs_backup_existing(wcs_path)

import matplotlib.pyplot as plt
import numpy as np
from numpy.linalg import norm
from astropy.visualization import make_lupton_rgb, ImageNormalize
from astropy.visualization.stretch import HistEqStretch


for ccd, fn in ifc.ccds(return_fname=True):
    out_fn = wcs_path / fn
    wcs_ccd = astrometry.solve_wcs(ccd, out_fn, overwrite=True)

    visualize.draw_ccd(wcs_ccd)
#%%
