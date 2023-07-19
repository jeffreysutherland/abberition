# Full processing of images

# Calibrate lights
# + create bias
# + create dark
# + create flat
# + calibrate lights

# Additional calibration
# - create bad pixel map
# - create cosmic ray map
# - create hot pixel map
# - find stars in image
# - image segmentation
# - generate background map
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
# - 

# Visualization
# - generate 3d view of focal plane
# - distortion map
# - relevant visualizations for each process


# Additional tools
# - standardized serialization format
# - visual scripting of work-flows
# - image viewer for all data saved in file 