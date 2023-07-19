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

data_path = Path('../.output/lights_g/2023.05.12/m51/lights/tmp')
wcs_path = Path('../.output/lights_g/2023.05.12/m51/wcs')

ifc = io.get_images(data_path, True, sanitize_headers=True)

io.mkdirs_backup_existing(wcs_path)

import matplotlib.pyplot as plt
import numpy as np
from numpy.linalg import norm
from astropy.visualization import make_lupton_rgb, ImageNormalize
from astropy.visualization.stretch import HistEqStretch


for ccd, fn in ifc.ccds(return_fname=True):
    data = ccd.data
    max_val = 1.0

    stretch = HistEqStretch(data)
    norm = ImageNormalize(data, stretch=stretch, clip=True)
    data = norm(data)

    mn = np.min(data)
    mx = np.max(data)

    data = max_val * ((mx - mn) * data - mn)

    im = data

    plt.figure(figsize=(25,25))
    plt.imshow(im, cmap='gray')

    x_stars = sources['xcentroid']
    y_stars = sources['ycentroid']
    
    plt.plot(x_stars, y_stars, 'bo', fillstyle="none", ms=16.0)
    
    plt.show()

    #out_fn = wcs_path / fn
    #wcs_ccd = astrometry.solve_wcs(ccd, out_fn, overwrite=True)

    if True:
        sources = astrometry.find_stars(ccd.data)
        plt.figure(figsize=(10, 10))
        
        
        im = visualize.data_to_image(ccd.data)
        
        data = ccd.data
        max_val = 1.0

        stretch = HistEqStretch(data)
        norm = ImageNormalize(data, stretch=stretch, clip=True)
        data = norm(data)

        mn = np.min(data)
        mx = np.max(data)

        #im = max_val * ((mx - mn) * data - mn)
        plt.imshow(im)
        plt.title('im1')
        
        visualize.draw_stars(im, sources['xcentroid'], sources['ycentroid'])
        plt.title('find_stars2')
        plt.show()


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

    break

# %%
