#%%
# calibrate a directory of light frames

import logging
import warnings
logging.getLogger().setLevel(level=logging.DEBUG)

import test_setup

from pathlib import Path
from abberition import io, standard
from ccdproc import ImageFileCollection

from astropy.utils.exceptions import AstropyWarning
warnings.simplefilter('ignore', category=AstropyWarning)

astronomy_data_dir = '../../astrodev/astronomy.data/'
sub_dir = ''
astronomy_data_path = Path(astronomy_data_dir)

logging.debug(f'data dir: {astronomy_data_dir}')
logging.debug(f'data path: {astronomy_data_path.absolute()}')

output_path = Path('../.output/flats/')

flat_sets = [ '2023.05.12/sloan_r_flat', '2023.05.12/sloan_g_flat', '2023.05.18/sloan_g_flat', '2023.05.18/sloan_i_flat' ]
for flat_set in flat_sets:
    flat_src_path = astronomy_data_path / 'data/raw' / flat_set

    logging.info(f'Creating flat from \'{flat_src_path}\'')

    # load flat images from directory
    flats = ImageFileCollection(flat_src_path)

    # create dir for output files
    flat_out_path = output_path / flat_set
    io.mkdirs_backup_existing(flat_out_path)

    # create flat
    flats = standard.create_flat(flats, flat_out_path)

    for flat, flat_fn in flats.ccds(return_fname=True):
        png_path = str(flat_out_path / flat_fn) + '.png'
        io.save_mono_png(flat, png_path, True, io.ImageScale.HistEq)

logging.info('finished...')

# %%
