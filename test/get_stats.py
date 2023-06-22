#%%
# Get image statistics for a folder of images
import logging
logging.basicConfig(level=logging.INFO)

import warnings
from astropy.utils.exceptions import AstropyWarning
warnings.simplefilter('ignore', category=AstropyWarning)

import test_setup

from pathlib import Path
from abberition import io, library, profile
from ccdproc import ImageFileCollection

astronomy_data_dir = '../../astrodev/astronomy.data/'
astronomy_data_path = Path(astronomy_data_dir)

path = Path(library.get_library_path())

logging.info(f'Stats for all images in \'{path}\'')

# load images from directory
images = ImageFileCollection(path)

for image, image_fn in images.ccds(return_fname=True):
    
    stats = profile.get_stats(image)

    s = '\n' + str(image_fn) + ':\n'
    for k, v in stats.items():
        s += f'    {k}: {v}\n'
    s += '\n\n'


    logging.info(s)
# %%
