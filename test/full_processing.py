"""
This script performs full processing of astronomical images, including calibration, WCS solution, additional calibration,
image combination, optical system analysis, astronomy analysis, post processing, visualization, and other tasks.

Author: Jeff Sutherland
Date: 2023/11/09

"""

import logging
import warnings
logging.getLogger().setLevel(level=logging.INFO)

import test_setup

from pathlib import Path
from abberition.processor import Processor

from astropy.utils.exceptions import AstropyWarning
warnings.simplefilter('ignore', category=AstropyWarning)


# Define data dirs
lights_path = Path('E:\\astro\\test_data\\processor_test\\lights')
flats_path = Path('E:\\astro\\test_data\\processor_test\\flats')
dest_path = Path('E:\\astro\\test_data\\processor_test\\out')

# Create processor
proc = Processor(dest_path)

# Set data dirs
proc.set_lights(path=lights_path)
proc.set_flats(path=flats_path)

proc.calibrate_flats()
proc.calibrate_lights()

proc.summary()

# Calibrate lights
# create flats
# calibrate lights

# Solve image WCS
# find stars in image
# initial wcs from astrometry.net
# find gaia stars in image based on wcs
# refine wcs based on gaia stars

# Additional calibration
# - create bad pixel map
# - create cosmic ray map
# - create hot pixel map
# - find stars in image
# - image segmentation
# - extract background
# - generate psf map

# Generate WCS
# + find stars in image
# + initial wcs from astrometry.net
# + find gaia stars in image based on wcs
# + refine wcs based on gaia stars

# Image combination
# - reproject onto common wcs
# - combine images

# Optical system analysis
# - compare photometry with gaia/sloan based on filter
# - generate distortion map from multiple wcs
# - profile optical system via focus sweep

# Astronomy analysis
# - generate H-R diagram

# Post processing
# - generate color image
# - image convolution (deconvolution)

# Visualization
# - generate 3d view of focal plane
# - distortion map
# - relevant visualizations for each process
# - display image
# - overlay coordinates from wcs
# - overlay data points
# - display vignetting
# - display optical system profile


# Other
# - standardized serialization format
# - visual scripting of work-flows
# - image viewer for all data saved in file

