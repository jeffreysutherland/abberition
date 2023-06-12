# abberition

### Aberration
1. A departure from what is normal, usual, or expected, typically one that is unwelcome
2. The failure of rays to converge at one focus because of limitations or defects in an optical system


### Apparition

1. An unusual or unexpected sight or phenomenon strange apparitions in the sky
2. The act of becoming visible

The goal of abberition is to get the most out of deeply flawed astronomical images.


## TODO
1. Add fully functional set of functions to enable each step of image processing.
2. Create UI with qt/some web framework (django?)
3. Integrate [Ryven](https://ryven.org/guide#/?id=programming-nodes) node editor for qt


## Functionality

### Standard frames
	* Create bias standard
	* Create dark standard
	* Create flat standard

## Library
	* Add bias to library
	* Add dark to library
	* Add flat to library
	* Get bias for image
	* Get dark for image
	* Get flat for image
	
## Calibration
	* Bias calibration
	* Dark calibration
	* Flat calibration
	* Defect mask calibration
	* Distortion calibration

## WCS
	* Solve image wcs
	* Generate distortion model
	* Undistort to projection
	* Align images

## Optics Profiling
	* Profile system
    * Generate defect list
    * Generate distortion data

## Stacking
	* Merge calibrated/aligned images
    * Create color image