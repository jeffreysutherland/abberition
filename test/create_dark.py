#%%
# create dark standard and save to library
import logging
logging.basicConfig(level=logging.INFO)

import test_setup

from pathlib import Path
from abberition import io, library, standard

astronomy_data_dir = '../../astrodev/astronomy.data/'
astronomy_data_path = Path(astronomy_data_dir)
calibration_path = astronomy_data_path / 'data/calibration'

dark_sets = [ 
    'pixis_2048b/dark.1x1.60s.-50C.fast',
    'pixis_2048b/dark.1x1.600s.-50C.hq',
    'pixis_2048b/dark.2x2.300s.-50C.hq' 
]


for dark_set in dark_sets:
    dark_src_path = calibration_path / dark_set
    logging.info(f'Creating dark from \'{dark_src_path}\'')

    # load dark images from directory
    darks = io.get_images(dark_src_path, True, sanitize_headers=True)

    dark_image = standard.create_dark(darks)

    dark_path = library.save_dark(dark_image)

    # save png next to library file
    png_path = str(dark_path) + '.png'
    io.save_mono_png(dark_image, png_path)

logging.info('finished...')

# %%
