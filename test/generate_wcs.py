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
#%%
io.mkdirs_backup_existing(wcs_path)

ifc = io.get_images(data_path, True, sanitize_headers=True)

for ccd, fn in ifc.ccds(return_fname=True):
    out_fn = wcs_path / fn
    wcs_ccd = astrometry.full_wcs(ccd, out_fn, overwrite=True)

    

# %%
# draw wcs solution

from abberition import debug_draw
import matplotlib.pyplot as plt
from ccdproc import ImageFileCollection

logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)

wcs_ifc = ImageFileCollection(wcs_path)
for ccd, fn in wcs_ifc.ccds( return_fname=True):
    #debug_draw.draw_im(ccd.data)
    #debug_draw.draw_wcs_distortion(ccd.wcs, 20, 1)
       

    fig = plt.figure(figsize=(10, 10))
    ax = plt.subplot(projection=ccd.wcs)
    plt.imshow(ccd.data, origin='lower', cmap='cividis', aspect='equal')
    plt.xlabel(r'RA')
    plt.ylabel(r'Dec')

    overlay = ax.get_coords_overlay('icrs')
    overlay.grid(color='white', ls='dotted')


# %%
