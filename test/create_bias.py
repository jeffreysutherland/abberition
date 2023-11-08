#%%
# create bias standard and save to library
import logging
logging.basicConfig(level=logging.INFO)

import test_setup

from pathlib import Path
from abberition import io, library, standard

astronomy_data_dir = '../../astrodev/astronomy.data/'
astronomy_data_path = Path(astronomy_data_dir)
calibration_path = astronomy_data_path / 'data/calibration'

bias_sets = [ 
    'pixis_2048b/bias.1x1.-50C.fast',
    'pixis_2048b/bias.1x1.-50C.hq',
    'pixis_2048b/bias.2x2.-50C.fast',
    'pixis_2048b/bias.2x2.-50C.hq',
]

for bias_set in bias_sets:
    bias_src_path = calibration_path / bias_set
    logging.info(f'Creating bias from \'{bias_src_path}\'')

    # load bias images from directory
    biases = io.get_images(bias_src_path, True, filters={'imagetyp':'bias'}, sanitize_headers=True)

    bias_image = standard.create_bias(biases)

    bias_path = library.save_bias(bias_image)

    # save png next to library file
    png_path = str(bias_path) + '.png'
    io.save_mono_png(bias_image, png_path)

logging.info('Finished creating bias frames.')

# %%
