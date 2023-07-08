'''
Create a library of reference frames (bias, dark, flat), that can be requested based on the properties of an image.

Images are selected through filters, so filenames are 
'''

import logging
from ccdproc import CCDData, ImageFileCollection
from pathlib import Path
from os.path import exists

from abberition import io

__library_path = Path(__file__).parent / 'library/'
__library_ifc = ImageFileCollection(__library_path)

def get_library_path():
    return __library_path

def save_image(image: CCDData):
    filename = io.generate_filename(image)
    filepath = __library_path / filename
    filepath = Path(io.get_first_available_filename(filepath))

    # get image type
    image_type = image.header['imagetyp']

    if image_type == 'Bias Frame':
        filepath = save_bias(image)
    elif image_type == 'Dark Frame':
        filepath = save_dark(image)
    elif image_type == 'Flat Field':
        filepath = save_flat(image)
    else:
        filePath = None
        logging.error(f'Invalid image type for saving to library: {image_type}')
        raise Exception(f'Can\'t save image as it is not a calibration frame: {image_type}')

    logging.info('Saved image to library file ' + str(filepath))
    return filepath

def save_bias(image: CCDData):
    filename = io.generate_filename(image)
    filepath = __library_path / filename
    filepath = Path(io.get_first_available_filename(filepath))
    
    # TODO: hash data and save in keyword
    logging.info('Saving bias to library file ' + str(filepath))

    image.write(filepath, overwrite=False)
    
    return filepath
    

def save_dark(image: CCDData):
    filename = io.generate_filename(image)
    filepath = __library_path / filename
    filepath = Path(io.get_first_available_filename(filepath))
    
    # TODO: hash data and save in keyword
    logging.info('Saving dark to library file ' + str(filepath))

    image.write(filepath, overwrite=False)
    
    return filepath

def save_flat(image:CCDData):
    raise NotImplementedError


def select_bias(image, ignore_temp=True, temp_threshold = 0.25):
    """
    Select a bias frame from the library that matches the parameters of the input ref image. 
    TODO: enable cropped images by splitting out the naxis1, naxis2 and adding xorgsubf and yorgsubf.
    
    Keywords requiring equal values matched are:
        'instrume' - Instrument name
        'naxis' - Number of data axes
        'naxis1' - Width
        'naxis2' - Height
        'bitpix' - Bits per pixel
        'xbinning' - X binning value
        'ybinning' - Y binning value
        'readoutm' - Readout mode
        'gain' - Gain

    Other keywords checked:
        'standard' - Checked to ensure bias is marked as a master frame
        'ccd-temp' - Checked to ensure bias is within temp_threshold of light

    Parameters
    ----------
    light : CCDData
        The light frame to find a matching bias for.
    light_filename : str
        The filename of the light for logging purposes
        TODO: remove once replaced with exceptions on failure

    Returns
    -------
    bias : CCDData
        The matching bias, or None if none found.
    filename : str
        Filename of the returned bias CCDData.

    """        

    filters = {}
    filters['imagetyp'] = 'Bias Frame'
    filters['instrume'] = image.header['instrume']
    filters['naxis']    = image.header['naxis']
    filters['naxis1']   = image.header['naxis1']
    filters['naxis2']   = image.header['naxis2']
    filters['xbinning'] = image.header['xbinning']
    filters['ybinning'] = image.header['ybinning']
    filters['readoutm']  = image.header['readoutm']
    filters['gain']  = image.header['gain']
    filters['standard']   = True


    ifc_biases = __library_ifc.filter(**filters)

    num_biases = 0
    if ifc_biases.summary:
        num_biases = len(ifc_biases.summary)
    
    if num_biases > 0:
        # choose the first within temp range
        ref_temp = float(image.header['ccd-temp'])
        
        for bias, bias_filename in ifc_biases.ccds(return_fname=True):
            bias_temp = float(bias.header['ccd-temp'])
            
            if bias_temp > ref_temp - temp_threshold and bias_temp < ref_temp + temp_threshold:
                return bias, bias_filename
    
        raise Exception('Couldn\'t find matching bias as none of the ' + num_biases + ' otherwise matching biases have temperature within threshold (' + ref_temp + ' +/- ' + temp_threshold + ').')
    
    raise Exception('No biases found matching light')



def select_dark(image, ignore_temp=False, temp_threshold = 0.25):
    """
    Select a dark frame from the library that matches the parameters of the input reference image. 
    
    Keywords requiring equal values matched are:
        'instrume' - Instrument name
        'naxis' - Number of data axes
        'naxis1' - Width
        'naxis2' - Height
        'bitpix' - Bits per pixel
        'xbinning' - X binning value
        'ybinning' - Y binning value

    Other keywords checked:
        'master' - Checked to ensure dark is marked as a master frame
        'ccd-temp' - Checked to ensure dark is within temp_threshold of light

    Parameters
    ----------
    light : CCDData
        The light frame to find a matching dark for.
    light_filename : str
        The filename of the light for logging purposes
        TODO: remove once replaced with exceptions on failure

    Returns
    -------
    dark : CCDData
        The matching dark, or None if none found.
    filename : str
        Filename of the returned dark CCDData.

    """        
    
    filters = {}
    filters['imagetyp'] = 'Dark Frame'
    filters['instrume'] = image.header['instrume']
    filters['naxis']    = image.header['naxis']
    filters['naxis1']   = image.header['naxis1']
    filters['naxis2']   = image.header['naxis2']
    filters['xbinning'] = image.header['xbinning']
    filters['ybinning'] = image.header['ybinning']
    filters['readoutm']  = image.header['readoutm']
    filters['gain']  = image.header['gain']
    
    ifc_darks = __library_ifc.filter(**filters)

    num_darks = 0
    if ifc_darks.summary:
        num_darks = len(ifc_darks.summary)

    if num_darks > 0:
        # choose the first within temp range
        ref_temp = float(image.header['ccd-temp'])
        
        for dark, dark_filename in ifc_darks.ccds(return_fname=True):
            if ignore_temp:
                return dark, dark_filename
            
            dark_temp = float(dark.header['ccd-temp'])
            
            if dark_temp > ref_temp - temp_threshold and dark_temp < ref_temp + temp_threshold:
                return dark, dark_filename
    
        raise Exception('Couldn\'t find matching dark as none of the ' + num_darks + ' otherwise matching darks have temperature within threshold (' + ref_temp + ' +/- ' + temp_threshold + ').')
    
    raise Exception('No darks found matching light')


def select_flat(image, flats:ImageFileCollection=None):
    """
    Select a flat frame from the ifc that matches the parameters of the input light frame. 
    
    Keywords requiring equal values matched are:
        'instrume' - Instrument name
        'naxis' - Number of data axes
        'naxis1' - Width
        'naxis2' - Height
        'bitpix' - Bits per pixel
        'xbinning' - X binning value
        'ybinning' - Y binning value
        'filter' - The filter used

    Other keywords checked:
        'master' - Checked to ensure flat is marked as a master frame

    Parameters
    ----------
    light : CCDData
        The light frame to find a matching flat for.
    light_filename : str
        The filename of the light for logging purposes
        TODO: remove once replaced with exceptions on failure

    Returns
    -------
    flat : CCDData
        The matching flat, or None if none found.
    filename : str
        Filename of the returned flat.

    """

    if flats == None:
        flats = __library_ifc

    filters = {}
    filters['imagetyp'] = 'Flat Field'
    filters['instrume'] = image.header['instrume']
    filters['naxis']    = image.header['naxis']
    filters['naxis1']   = image.header['naxis1']
    filters['naxis2']   = image.header['naxis2']
    filters['xbinning'] = image.header['xbinning']
    filters['ybinning'] = image.header['ybinning']
    filters['filter']   = image.header['filter']
    filters['standard']   = True
    
    filt_flats = flats.filter(**filters)
    
    num_flats = 0
    if type(filt_flats.summary) != type(None):
        num_flats = len(filt_flats.summary)

    if num_flats > 0:
        # choose the first image that satisfies requirements
        # TODO: choose the best one (closest date? etc...)
        flat, flat_filename = next(filt_flats.ccds(return_fname=True, ccd_kwargs={'unit':'adu'}))
        return flat, flat_filename
    
    return None, None
