#%%
# create png's of fits in a folder
import logging
from pathlib import Path
import ccdproc as ccdp

import test_setup
from abberition import io

logging.getLogger().setLevel(level=logging.INFO)

image_dirs = [
    #'../.output/flats/2023.05.12/sloan_r_flat',
    '../.output/flats/2023.05.12/sloan_g_flat',
    '../.output/flats/2023.05.18/sloan_g_flat',
    #'../.output/flats/2023.05.18/sloan_i_flat',
    #'../.output/flats/2023.05.18/ha_flat'
]

#image_scale = io.ImageScale.HistEq
image_scale = io.ImageScale.Remap01

for image_dir in image_dirs:
    images = ccdp.ImageFileCollection(image_dir, keywords='*')
    image_path = Path(image_dir)

    out_path = image_path / '.png_remap01'

    for image, image_fn in images.ccds(return_fname=True):
        png_path = out_path / (image_fn + '.png')
        io.save_mono_png(image, png_path, True, 16, image_scale)
        logging.info(f'Saved {png_path}')
        
logging.info('finished...')
# %%
