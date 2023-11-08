# Full processing of images

# Calibrate lights
## create flats
## calibrate lights

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

