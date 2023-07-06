# collection of calibration functions for calibration of images

import astropy.units as u
import logging
import ccdproc as ccdp
import numpy as np

from abberition import library

def calibrate_dark(image:ccdp.CCDData):
    '''
    Calibrate a dark image.

    Steps:
    1. bias calibration

    '''

    return subtract_bias(image)


def calibrate_flat(raw_flat:ccdp.CCDData):
    '''
    Calibrate a dark image.

    Steps:
    1. bias calibration
    2. dark calibration

    '''

    bias_calib_flat = subtract_bias(raw_flat)
    calib_flat = subtract_dark(bias_calib_flat)

    return calib_flat


def apply_mask():
    '''
    Add mask information to the image. This information is loaded from the library based on the frame.
    '''

    raise NotImplementedError()


def subtract_bias(image: ccdp.CCDData, bias: ccdp.CCDData=None):
    '''
    Calibrate image with bias subtraction. If bias is not provided, it will be loaded from the library.
    '''
    logging.info('Calibrating image with bias.')

    if bias is None:
        bias, _ = library.select_bias(image)

    image = ccdp.subtract_bias(image, bias)

    # TODO: add keyword for bias subtracted to header

    return image

def subtract_dark(image:ccdp.CCDData, dark: ccdp.CCDData=None):
    '''
    Subtract dark from image. Scaled by time using 'exptime' keyword
    '''
    logging.info('Calibrating image with dark.')

    if dark is None:
        dark, _ = library.select_dark(image)
    
    # subtract the dark
    image_calib = ccdp.subtract_dark(image, dark, exposure_time='exptime', exposure_unit=u.second, scale=True)

    # TODO: add keyword for dark subtracted to header

    return image_calib

def get_quality(header):
    '''
    Get the ADC quality based on the header values.
    Possible values are:
        'em' - Electron multiplication
        'hc' - High capacity
        'hs' - High speed
        'ln' - Low noise
    '''
    quality = header['quality'].lower()

    if quality == 'unknown':
        cds = header['cds'].lower()
        if cds == 'fastest & most sensitive':
            quality = 'hs'
        elif cds == 'best quality':
            quality = 'ln'
    elif quality == 'high capacity':
        quality = 'hc'
    elif quality == 'high speed':
        quality = 'hs'
    elif quality == 'low noise':
        quality = 'ln'

    return quality


def get_gain(header):
    '''
    Get the gain of the image based on the header values.

    Possible values are:
        'h' - High gain
        'm' - Medium gain
        'l' - Low gain
    '''
    gain = header['gain'].lower()

    if gain == 'high':
        gain = 'h'
    elif gain == 'medium':
        gain = 'm'
    elif gain == 'low':
        gain = 'l'
    
    return gain

def get_speed(header):
    '''
    Get the speed of the image based on the header values. Speed in MHz
    '''
    speed = 0.0
    
    if 'speed' in header:
        speed = header['speed']

    return speed

def calibrate_light(image: ccdp.CCDData, flat=None, bias: ccdp.CCDData=None, dark: ccdp.CCDData=None, return_calibration=False):
    '''
    Calibrate a light image.

    Steps:
    1. bias calibration
    2. dark calibration
    3. flat calibration
    '''

    if bias is None:
        bias, _ = library.select_bias(image)

    if dark is None:
        dark, _ = library.select_dark(image)
        

    if flat is None:
        flat, _ = library.select_flat(image)
    elif isinstance(flat, ccdp.ImageFileCollection):
        flat, _ = library.select_flat(image, flats=flat)
    elif isinstance(flat, ccdp.CCDData):
        pass
    else:
        logging.error(f'Invalid flat type for calibrate_light: {type(flat)}')


    calib_light = ccdp.ccd_process(image, master_bias=bias, dark_frame=dark, master_flat=flat, exposure_key='exptime', exposure_unit=u.second, dark_scale=True)

    if return_calibration:
        return calib_light, (bias, dark, flat)
    
    return calib_light