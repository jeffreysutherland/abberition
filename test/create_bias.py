#%%
# create bias standard and save to library
import logging
from abberition import io
logging.basicConfig(level=logging.INFO)

import test_setup

import abberition
from importlib import reload
reload(abberition)

from pathlib import Path
from abberition import library
from abberition import standard
from ccdproc import CCDData, ImageFileCollection

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

    library.save_bias(bias_image)

    io.save_mono_jpg(bias_image, f'../.output/standard/{bias_set}.jpg')

logging.info('Finished creating bias frames.')

# %%
