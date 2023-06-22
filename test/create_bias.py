#%%
# create bias standard and save to library
import logging
logging.basicConfig(level=logging.INFO)

import test_setup

import abberition

from pathlib import Path
from abberition import io, library, standard
from ccdproc import ImageFileCollection

astronomy_data_dir = '../../astrodev/astronomy.data/'
astronomy_data_path = Path(astronomy_data_dir)

logging.debug(f'data dir: {astronomy_data_dir}')
logging.debug(f'data path: {astronomy_data_path.absolute()}')

bias_sets = [ 'bias.1x1.-50C.fast', 'bias.1x1.-50C.hq', 'bias.2x2.-50C.fast', 'bias.2x2.-50C.hq' ]

for bias_set in bias_sets:
    bias_src_path = astronomy_data_path / 'data/calibration/pixis_2048b' / bias_set
    logging.info(f'Creating bias from \'{bias_src_path}\'')

    # load bias images from directory
    biases = ImageFileCollection(bias_src_path)

    bias_image = standard.create_bias(biases)

    bias_path = library.save_bias(bias_image)

    # save png next to library file
    png_path = str(bias_path) + '.png'
    io.save_mono_png(bias_image, png_path)

logging.info('Finished creating bias frames.')

# %%
