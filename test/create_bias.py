#%%
# create bias standard and save to library
import logging
import test_setup

# %reload_ext autoreload
#%autoreload 2

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

    # load bias images from dir

    biases = ImageFileCollection(bias_src_path)

    bias_image = standard.create_bias(biases)

    library.save_bias(bias_image)


# %%
