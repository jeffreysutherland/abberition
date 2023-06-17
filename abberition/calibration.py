# collection of calibration functions for calibration of images

import logging
import ccdproc as ccdp

from abberition import library

def bias_subtract(image: ccdp.CCDData, bias: ccdp.CCDData=None):
    '''
    Calibrate image with bias subtraction. If bias is not provided, it will be loaded from the library.
    '''
    logging.info('Calibrating image with bias.')

    if bias is None:
        bias, _ = library.select_bias(image)

    image = ccdp.subtract_bias(image, bias)

    return image

