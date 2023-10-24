# processes to perform on images

import logging
from ccdproc import CCDData
from astropy.io.fits import HDUList


def sanitize(header):
    '''
    Standardize header values for use in processing.
    
    Mandatory keywords:
        instrume: Instrument
        xbinning: X Binning
        ybinning: Y Binning
        naxis:    Number of axes
        naxis1:   Number of pixels in axis 1
        naxis2:   Number of pixels in axis 2
        xpixsz:   Pixel size in X axis
        ypixsz:   Pixel size in Y axis
        bunit:    Units of data

    Ensure keywords:
        imagetyp: Image Type
        quality:  ADC Quality
        gain:     Gain value
        gainadu:  Gain (e-/ADU)
        speed:    Speed (MHz)
        ccd-temp: CCD Temperature (C)
        exptime:  Exposure time (s)
        filter:   Filter name
        bitpix:   Bits per pixel
        localtim: Time of observation (local)
    '''

    # ensure mandatory keywords are present and valid
    __ensure_str_field(header, 'instrume')
    __ensure_int_field(header, 'xbinning')
    __ensure_int_field(header, 'ybinning')
    __ensure_int_field(header, 'naxis')
    __ensure_int_field(header, 'naxis1')
    __ensure_int_field(header, 'naxis2')
    __ensure_float_field(header, 'xpixsz')
    __ensure_float_field(header, 'ypixsz')
    __ensure_str_field(header, 'bunit', 'adu')

    # ensure optional keywords are present and valid
    __validate_imagetyp(header)
    __validate_quality(header)
    __validate_gain(header)
    __ensure_float_field(header, 'gainadu', 0.0)
    __ensure_float_field(header, 'speed', 0.0)
    __ensure_float_field(header, 'ccd-temp', 100.0)
    __ensure_float_field(header, 'exptime', 0.0)
    __ensure_str_field(header, 'filter', 'none')
    __ensure_int_field(header, 'bitpix', 0)
    __ensure_str_field(header, 'localtim', '')


def __ensure_str_field(header, key:str, default:str=None):
    '''
    Ensure the specified key is a string.
    '''
    if key not in header:
        if default is not None:
            logging.warning(f'Keyword \'{key}\' not found in header. Using default value of \'{default}\'.')
            header[key] = default
        else:
            logging.error(f'Mandatory keyword \'{key}\' not found in header.')
            raise ValueError(f'Mandatory keyword \'{key}\' not found in header.')
    
    if not isinstance(header[key], str):
        logging.warning(f'Mandatory keyword \'{key}\' expected a string, found {header[key]}:{type(header[key])}. Casting to string.')
        header[key] = str(header[key])


def __ensure_int_field(header, key:str, default:int=None):
    '''
    Ensure the specified key is an integer.
    '''
    if key not in header:
        if default is not None:
            logging.warning(f'Keyword \'{key}\' is not found. Using default value of {default}.')
            header[key] = default
        else:
            logging.error(f'Mandatory keyword \'{key}\' not found in header.')
            raise ValueError(f'Mandatory keyword \'{key}\' not found in header.')
    
    if not isinstance(header[key], int):
        logging.error(f'Mandatory keyword \'{key}\' expected an integer, found {header[key]}.')
        raise ValueError(f'Mandatory keyword \'{key}\' expected an integer, found {header[key]}')
    

def __ensure_float_field(header, key:str, default:float=None):
    '''
    Ensure the specified key is a float.
    '''
    if key not in header:
        if default is not None:
            logging.warning(f'Keyword \'{key}\' is not found. Using default value of {default}.')
            header[key] = default
        else:
            logging.warning(f'Mandatory keyword \'{key}\' not found in header.')
            raise ValueError(f'Mandatory keyword \'{key}\' not found in header.')
    
    if not isinstance(header[key], float):
        logging.error(f'Mandatory keyword \'{key}\' expected a float, found {header[key]}.')
        raise ValueError(f'Mandatory keyword \'{key}\' expected a float, found {header[key]}')

__imagetyp_key = 'imagetyp'
__imagetyp_default = 'unknown'
__imagetyp_lookup = {
    'unknown': 'unknown',
    'bias': 'bias',
    'Bias Frame': 'bias',
    'dark': 'dark',
    'Dark Frame': 'dark',
    'flat': 'flat',
    'Flat Field': 'flat',
    'light': 'light',
    'Light Frame': 'light',
    'Object': 'light',
}
__imagetyp_valid = {
    'unknown': 'Unknown image type',
    'bias': 'Bias frame',
    'dark': 'Dark frame',
    'flat': 'Flat frame',
    'light': 'Light frame',
}

def __validate_imagetyp(header):
    imagetyp = __imagetyp_default

    if __imagetyp_key in header:
        imagetyp = header[__imagetyp_key]

    if imagetyp in __imagetyp_lookup.keys():
        imagetyp = __imagetyp_lookup[imagetyp]
    else:
        imagetyp = __imagetyp_default

    header[__imagetyp_key] = imagetyp


__adc_quality_key = 'quality'
__adc_quality_default = 'st'
__adc_quality_lookup = {
    'st': 'st',
    'hc': 'hc',
    'hs': 'hs',
    'ln': 'ln',
    'em': 'em',
}
__adc_quality_valid = {
    'st': 'Standard/unknown ADC quality',
    'hc': 'High capacity mode',
    'hs': 'High speed',
    'ln': 'Low noise',
    'em': 'Electron multiplied',
}

def __validate_quality(header):
    quality = __adc_quality_default
    
    if __adc_quality_key in header:
        quality = header[__adc_quality_key]

    if quality in __adc_quality_lookup.keys():
        quality = __adc_quality_lookup[quality]
    else:
        quality = __adc_quality_default

    header[__adc_quality_key] = quality

def __validate_gain(header):
    '''
    Ensure the specified key is an integer.
    '''
    key = 'gain'

    if key not in header:
        default = -1
        logging.warning(f'Keyword \'{key}\' is not found. Using default value of {default}.')
        header[key] = default

    val = header[key]

    if isinstance(val, str):
        if val.lower() == 'high':
            header[key] = 2
        elif val.lower() == 'low':
            header[key] = 0

    if not isinstance(header[key], int):
        logging.error(f'Mandatory keyword \'{key}\' expected an integer, found {header[key]}.')
        raise ValueError(f'Mandatory keyword \'{key}\' expected an integer, found {header[key]}')
 
 