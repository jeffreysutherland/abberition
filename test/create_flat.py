#%%
# Create a flat field image from a set of images
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

output_path = Path('../.output/')
output_path.mkdir(parents=True, exist_ok=True)

flat_sets = [ '2023.05.12/sloan_r_flat', '2023.05.12/sloan_i_flat', '2023.05.18/sloan_g_flat', '2023.05.18/sloan_i_flat' ]
for flat_set in flat_sets:
    flat_src_path = astronomy_data_path / 'data/raw' / flat_set

    logging.info(f'Creating flat from \'{flat_src_path}\'')

    # load flat images from directory
    flats = ImageFileCollection(flat_src_path)

    # create flat
    flat_image = standard.create_flat(flats)

    flat_path = Path(flat_path)

    jpg_path = Path(f'../.output/standard/{flat_path.name}.jpg')
    jpg_path.parent.mkdir(parents=True, exist_ok=True)

    io.save_mono_jpg(flat_image, output_path / jpg_path)

logging.info('finished...')

# %%




