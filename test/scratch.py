#%%
from astropy.visualization.stretch import HistEqStretch
from astropy.visualization import ImageNormalize
import numpy as np
from ccdproc import CCDData

# apply histogram equalization stretch
#max = np.max(data)
#min = np.min(data)
#foo = CCDData.read('E:/abberition/.output/flats/2023.05.12/sloan_r_flat/flat.PIXIS_2048B.b1x1.-50.0C.3.0s.qln.gh.s0.0.fits')
foo = CCDData.read('E:/abberition/abberition/library/dark.PIXIS_2048B.b1x1.-50.0C.60.0s.qhs.gh.s0.0.000.fits')
data = foo.data

stretch = HistEqStretch(data)
norm = ImageNormalize(data, stretch=stretch, clip=True)
out_data = norm(data)

import matplotlib.pyplot as plt
plt.imshow(out_data)


# %%
# Set some metadata
from ccdproc import ImageFileCollection
from pathlib import Path

in_path = Path('E:\\abberition\\abberition\\library\\tmp')
out_path = Path('E:\\abberition\\abberition\\library\\tmp2')

ifc = ImageFileCollection(in_path, keywords='*')

for ccd, ccd_fn in ifc.ccds(return_fname=True, unit='adu'):
    ccd.meta['instrume'] = 'ZWO ASI174MM Mini'
    ccd.write(out_path / ccd_fn, overwrite=True)

# %%
from ccdproc import ImageFileCollection
from pathlib import Path
import test_setup

path = Path('E:/astrodev/astronomy.data/data/raw/2023.05.18/guide_flat/best')
out_path = Path('E:/astrodev/astronomy.data/data/raw/2023.05.18/guide_flat/best/fixed')

from abberition import io

io.mkdirs_backup_existing(out_path)

kvps = { 'instrume':'ZWO ASI174MM Mini' }


ifc = ImageFileCollection(path)
filters = { 'instrume':'ASICamera' }
ifc = ifc.filter(**filters)
foo = next(ifc)

#%%
print('Original headers:')
print([x['instrume'] for x in ImageFileCollection(path).headers()])

io.add_keys_to_dir(ifc, kvps, out_path)

print('After headers:')
print([x['instrume'] for x in ImageFileCollection(out_path).headers()])

# %%
