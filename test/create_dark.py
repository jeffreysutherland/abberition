#%%
# create dark standard and save to library
import logging
logging.basicConfig(level=logging.INFO)

import test_setup

import abberition
from importlib import reload
reload(abberition)

from pathlib import Path
from abberition import library
from abberition import standard
from ccdproc import ImageFileCollection

astronomy_data_dir = '../../astrodev/astronomy.data/'
astronomy_data_path = Path(astronomy_data_dir)

logging.debug(f'data dir: {astronomy_data_dir}')
logging.debug(f'data path: {astronomy_data_path.absolute()}')

dark_sets = [ 'dark.2x2.300s.-50C.hq' ]

for dark_set in dark_sets:
    dark_src_path = astronomy_data_path / 'data/calibration/pixis_2048b' / dark_set
    logging.info(f'Creating dark from \'{dark_src_path}\'')

    # load dark images from directory
    darks = ImageFileCollection(dark_src_path)

    dark_image = standard.create_dark(darks)

    library.save_dark(dark_image)

logging.info('Finished creating dark frames.')

# %%
