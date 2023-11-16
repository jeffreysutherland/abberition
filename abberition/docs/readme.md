# Processing Examples
## IO
### Load ImageFileCollection of images in folder
```
biases = io.get_images(bias_src_path, dest_path, filters={'imagetyp':'bias'}, sanitize_headers=True)
```

### Generate filename for image
```
flat_fn = io.generate_filename(combined_flat)
```

### Save scaled png of image
```
io.save_mono_png(calibrated_light, str(light_dest) + '.png', True, 16, io.ImageScale.AsIs)
```

### Create directory and backup existing of same name
```
io.mkdirs_backup_existing(light_work_dir)
```

## Calibration
### Create bias
```
bias_image = standard.create_bias(biases)
```
### Create dark
```
dark_image = standard.create_dark(darks)
```

### Create flats
Create flats for each filter in an ImageFileCollection
```
flat_standards = standard.create_flats(flats, flat_out_path)
```
### Add calibration frame to library
```
    bias_path = library.save_bias(bias_image)
```
### Calibrate lights
Calibrate light frame from library standards with specified flat frames. Can return calibration frames used.
```
calibrated_light, (bias, dark, flat) = calibration.calibrate_light(light, flats, return_calibration=True)
```

## Additional calibration
- create bad pixel map
- create cosmic ray map
- create hot pixel map
- get stars in image
- image segmentation
- extract background
- generate psf map

## Astrometry
### Full wcs solve of image
```
wcs_ccd = astrometry.solve_wcs(calibrated_light, out_fn, overwrite=True)
```
### Find stars in image

### Initial wcs from astrometry.net
### Find gaia stars in image based on wcs
### Define wcs based on gaia stars


## Image combination
- reproject onto common wcs
- combine images

Optical system analysis
- compare photometry with gaia/sloan based on filter
- generate distortion map from multiple wcs
- profile optical system via focus sweep

Astronomy analysis
- generate H-R diagram

Post processing
- generate color image
- image convolution (deconvolution)

Visualization
- generate 3d view of focal plane
- distortion map
- relevant visualizations for each process
- display image
- overlay coordinates from wcs
- overlay data points
- display vignetting
- display optical system profile


Other
- standardized serialization format
- visual scripting of work-flows
- image viewer for all data saved in file 

