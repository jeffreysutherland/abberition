'''
Create a library of reference frames (bias, dark, flat), that can be requested based on the properties of an image.
'''

from pathlib import Path

library_path = Path('library')

temp_threshold = 0.25

def select_bias(ifc_biases, ref_image):
    """
    Select a bias frame from ifc_biases that matches the parameters of the input ref image. 
    TODO: enable cropped images by splitting out hte naxis1, naxis2 and adding xorgsubf and yorgsubf.
    
    Keywords requiring equal values matched are:
        'instrume' - Instrument name
        'naxis' - Number of data axes
        'naxis1' - Width
        'naxis2' - Height
        'bitpix' - Bits per pixel
        'xbinning' - X binning value
        'ybinning' - Y binning value


    Other keywords checked:
        'master' - Checked to ensure bias is marked as a master frame
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
    filters['instrume'] = ref_image.header['instrume']
    filters['naxis']    = ref_image.header['naxis']
    filters['naxis1']   = ref_image.header['naxis1']
    filters['naxis2']   = ref_image.header['naxis2']
    filters['xbinning'] = ref_image.header['xbinning']
    filters['ybinning'] = ref_image.header['ybinning']
    filters['master']   = True

    ifc_biases = ifc_biases.filter(**filters)

    num_biases = 0
    if ifc_biases.summary != None:
        num_biases = len(ifc_biases.summary)
    
    if num_biases > 0:
        # choose the first within temp range
        ref_temp = float(ref_image.header['ccd-temp'])
        
        for bias, bias_filename in ifc_biases.ccds(return_fname=True):
            bias_temp = float(bias.header['ccd-temp'])
            
            if bias_temp > ref_temp - temp_threshold and bias_temp < ref_temp + temp_threshold:
                return bias, bias_filename
    
        raise Exception('Couldn\'t find matching bias as none of the ' + num_biases + ' otherwise matching biases have temperature within threshold (' + ref_temp + ' +/- ' + temp_threshold + ').')
    
    raise Exception('No biases found matching light')



def select_dark(ifc_darks, ref_image):
    """
    Select a dark frame from ifc_darks that matches the parameters of the input reference image. 
    
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
    filters['instrume'] = ref_image.header['instrume']
    filters['naxis']    = ref_image.header['naxis']
    filters['naxis1']   = ref_image.header['naxis1']
    filters['naxis2']   = ref_image.header['naxis2']
    filters['xbinning'] = ref_image.header['xbinning']
    filters['ybinning'] = ref_image.header['ybinning']
    filters['master']   = True
    
    ifc_darks = ifc_darks.filter(**filters)

    num_darks = 0
    if ifc_darks.summary != None:
        num_darks = len(ifc_darks.summary)

    if num_darks > 0:
        # choose the first within temp range
        ref_temp = float(ref_image.header['ccd-temp'])
        
        for dark, dark_filename in ifc_darks.ccds(return_fname=True):
            dark_temp = float(dark.header['ccd-temp'])
            
            if dark_temp > ref_temp - temp_threshold and dark_temp < ref_temp + temp_threshold:
                return dark, dark_filename
    
        raise Exception('Couldn\'t find matching dark as none of the ' + num_darks + ' otherwise matching darks have temperature within threshold (' + ref_temp + ' +/- ' + temp_threshold + ').')
    
    raise Exception('No darks found matching light')


def select_flat(ifc_flats, ref_image):
    """
    Select a flat frame from flats_dir() that matches the parameters of the input light frame. 
    
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

    filters = {}
    filters['imagetyp'] = 'Flat Field'
    filters['instrume'] = ref_image.header['instrume']
    filters['naxis']    = ref_image.header['naxis']
    filters['naxis1']   = ref_image.header['naxis1']
    filters['naxis2']   = ref_image.header['naxis2']
    filters['xbinning'] = ref_image.header['xbinning']
    filters['ybinning'] = ref_image.header['ybinning']
    filters['filter']   = ref_image.header['filter']
    filters['master']   = True
    
    ifc_flats = ifc_flats.filter(**filters)
    
    num_flats = 0
    if type(ifc_flats.summary) != type(None):
        num_flats = len(ifc_flats.summary)

    if num_flats > 0:
        # choose the first image that satisfies requirements
        flat, flat_filename = next(ifc_flats.ccds(return_fname=True, ccd_kwargs={'unit':'adu'}))
        return flat, flat_filename
    
    return None, None
