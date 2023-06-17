#%%
# create dark standard and save to library
import logging
logging.basicConfig(level=logging.INFO)

import test_setup

from pathlib import Path
from abberition import io, library, standard
from ccdproc import ImageFileCollection

astronomy_data_dir = '../../astrodev/astronomy.data/'
astronomy_data_path = Path(astronomy_data_dir)

logging.debug(f'data dir: {astronomy_data_dir}')
logging.debug(f'data path: {astronomy_data_path.absolute()}')

dark_src_path = astronomy_data_path / 'data/calibration/pixis_2048b/dark.2x2.300s.-50C.hq'
logging.info(f'Creating dark from \'{dark_src_path}\'')

# load dark images from directory
darks = ImageFileCollection(dark_src_path)

# create dark
dark_image = standard.create_dark(darks)

# %%
output_path = Path('../.output/')
output_path.mkdir(parents=True, exist_ok=True)

# save dark to library
library.save_dark(dark_image)

io.save_mono_jpg(dark_image, output_path / 'dark.jpg')

logging.info('finished...')

# %%
