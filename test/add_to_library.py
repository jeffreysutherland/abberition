#%%
# add a folder of fits calibration files to the library

import logging
logging.basicConfig(level=logging.INFO)

import test_setup

from abberition import library
from pathlib import Path
from ccdproc import ImageFileCollection

data = [
    ('e:/astrodev/astronomy.data/data/calibration/asi174/bias', 'Bias Frame'), 
    ('e:/astrodev/astronomy.data/data/calibration/asi174/dark', 'Dark Frame'), 
]

for d in data:
    folder = d[0]
    image_type = d[1]

    path = Path(folder)

    ifc = ImageFileCollection(path, keywords='*')

    for ccd in ifc.ccds(ccd_kwargs={'unit':'adu'}):
        ccd.meta['standard'] = True
        ccd.meta['readoutm'] = 'Long Exposure Mode'

        if 'imagetyp' not in ccd.meta:
            ccd.meta['imagetyp'] = image_type

        library.save_image(ccd)


#%%