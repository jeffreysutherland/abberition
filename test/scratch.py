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
