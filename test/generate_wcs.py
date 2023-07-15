#%%
# generate wcs for a set of calibrated light 
import logging
import warnings
logging.getLogger().setLevel(level=logging.DEBUG)

import test_setup

from pathlib import Path
from abberition import io, library, standard
from ccdproc import ImageFileCollection

from astropy.utils.exceptions import AstropyWarning
warnings.simplefilter('ignore', category=AstropyWarning)

image_sets = ['']
flat_sets = [ '2023.05.18/guide_flat/best/fixed' ]#, '2023.05.12/sloan_r_flat', '2023.05.12/sloan_g_flat', '2023.05.18/sloan_g_flat', '2023.05.18/sloan_i_flat', '2023.05.18/ha_flat' ]
ignore_temp=True

astronomy_data_dir = '../../astrodev/astronomy.data/'
astronomy_data_path = Path(astronomy_data_dir)

logging.debug(f'data dir: {astronomy_data_dir}')
logging.debug(f'data path: {astronomy_data_path.absolute()}')

output_path = Path('../.output/flats2/')

for flat_set in flat_sets:
    flat_src_path = astronomy_data_path / 'data/raw' / flat_set
