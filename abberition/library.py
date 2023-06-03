'''
Create a library of reference frames (bias, dark, flat), that can be requested based on the properties of an image.

Images are selected through filters, so filenames are 
'''

from ccdproc import CCDData, ImageFileCollection
from pathlib import Path
from os.path import exists

from abberition import io

__library_path = Path(__file__).parent / 'library/'
__library_ifc = ImageFileCollection(__library_path)

def __generate_filename(image:CCDData):
    '''
    Generate filename for image based on header values. Using binning instead resolution 
    for filename as it's assumed it's using the entire sensor. This relies on the library
    directory for unique filenames.
    '''

    instrument = image.header['instrume']
    binning = str(image.header['xbinning']) + 'x' + str(image.header['ybinning'])
    imagetype = image.header['imagetyp']
    exp_time = image.header['exptime']
    
    if imagetype == 'Bias Frame' or imagetype == 'Bias':
        filename = 'bias.' + instrument + '.' + binning + '.fits'
    elif imagetype == 'Dark Frame' or imagetype == 'Dark':
        temp = str(image.header['ccd-temp'])
        filename = 'dark.' + instrument + '.' + binning + '.' + temp + 'C.' + exp_time + 's' + '.###.fits'
    elif imagetype == 'Flat Field' or imagetype == 'Flat':
        filename = 'flat.' + instrument + '.' + binning + '.' + image.header['filter'] + '.fits'

    filepath = __library_path / io.get_first_available_filename(filename)
    filename = io.get_first_available_filename(filepath)

    return filename


def save_bias(image: CCDData):
    filepath = __generate_filename(image)
    
    # TODO: hash data and save in keyword
    

def save_dark():
    raise NotImplementedError

def save_flat():
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
    filters['instrume'] = image.header['instrume']
    filters['naxis']    = image.header['naxis']
    filters['naxis1']   = image.header['naxis1']
    filters['naxis2']   = image.header['naxis2']
    filters['xbinning'] = image.header['xbinning']
    filters['ybinning'] = image.header['ybinning']
    filters['master']   = True


    ifc_biases = __library_ifc.filter(**filters)

    num_biases = 0
    if ifc_biases.summary != None:
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
    filters['master']   = True
    
    ifc_darks = __library_ifc.filter(**filters)

    num_darks = 0
    if ifc_darks.summary != None:
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


def select_flat(image, ifc_flats=None):
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

    if ifc_flats == None:
        ifc_flats = __library_ifc

    filters = {}
    filters['imagetyp'] = 'Flat Field'
    filters['instrume'] = image.header['instrume']
    filters['naxis']    = image.header['naxis']
    filters['naxis1']   = image.header['naxis1']
    filters['naxis2']   = image.header['naxis2']
    filters['xbinning'] = image.header['xbinning']
    filters['ybinning'] = image.header['ybinning']
    filters['filter']   = image.header['filter']
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
