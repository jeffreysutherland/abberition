# -*- coding: utf-8 -*-

from enum import Enum
import logging
from os import makedirs, rename
from os.path import exists
from pathlib import Path
from ccdproc import CCDData

from astropy.visualization import make_lupton_rgb, ImageNormalize
from astropy.visualization.stretch import HistEqStretch
import numpy as np
from skimage.io import imread, imsave

from abberition import calibration


def get_first_available_dirname(path,  pad_length: int=3, always_number: bool=True):
    '''
    Returns the first available directory name given a set of parameters.

    Examples:
    get_first_available_dirname('dir', 3, always_number)

    always_number          Dir exists      Dir doesn't exist
    True                   'dir.000'       'dir.000'
    False                  'dir.000'       'dir'
    
    
    Parameters
    ----------
    path : str
        Path of the directory to check. 

    pad_length : int
        Zero-padded length of the number

    always_number : bool
        If true, will return a numbered directory name even if path doesn't exist.
        If false, will return path if it doesn't exist, otherwise first available numbered directory name


    Returns
    -------
    str
        The first available directory name.

    '''

    path = Path(path)
    path_base = str(path)
    new_path = str(path)

    if exists(new_path) or always_number:
        i = 0

        while i < (10**pad_length):
            new_path = f'{path_base}.{str(i).zfill(pad_length)}'
            if not exists(new_path):
                break

            i += 1

            if i > 10 ** pad_length:
                raise FileExistsError(f'All directories of numbered length {pad_length} have been taken for dir {str(path)}')
        
    return new_path


def get_first_available_filename(path, pad_length: int=3, always_number: bool=True):
    '''
    Returns the first available filename given a set of parameters.

    Examples:
    get_first_available_filename('file.ext', 3, always_number)

    always_number          File exists          File doesn't exist
    True                   'file.000.ext'       'file.000.ext'
    False                  'file.000.ext'       'file.ext'
    
    
    Parameters
    ----------
    path : str
        Path of the file to check. 

    pad_length : int
        Zero-padded length of the number

    always_number : bool
        If true, will return a numbered filename even if path doesn't exist.
        If false, will return path if it doesn't exist, otherwise first available numbered filename


    Returns
    -------
    str
        The first available filename.

    '''
    path = Path(path)
    ext = path.suffix
    path_base = str(path.parent / path.stem)

    new_path = str(path)

    if exists(new_path) or always_number:
        i = 0

        while i < (10**pad_length):
            new_path = f'{path_base}.{str(i).zfill(pad_length)}{ext}'
            if not exists(new_path):
                break

            i += 1

            if i > 10 ** pad_length:
                raise FileExistsError(f'All files of numbered length {pad_length} have been taken for file {str(path)}')
        
    return new_path

def mkdirs_backup_existing(path, pad_length:int=3):
    '''
    Same as makedirs, but if the path already exists, the existing one will be 
    renamed as {path}.#, where # is the first available number.

    Parameters
    ----------
    path : str
        Path of the directory to create.

    pad_length : int
        Zero-padded length
    
    pad_length

    Returns
    -------
    If directory was backed up, returns path to backup directory, else None.

    '''
    bk_path = None

    if exists(path):
        bk_path = get_first_available_dirname(path, pad_length, True)
        rename(path, bk_path)    

    # create primary output dir
    makedirs(name=str(path), exist_ok=False)

    return bk_path

def mkdirs_rm_existing(path):
    '''
    Same as makedirs, but if the path already exists, the existing one will be
    deleted and recreated.
    '''
    from shutil import rmtree

    # rename dir if it exists
    if exists(str(path)):
        rmtree(str(path))
    
    # create primary output dir
    makedirs(name=str(path), exist_ok=False)

def copy(src, dst, pad_length:int=3, always_number=True):
    '''
    Copy the file, but if the destination already exists, the src file will be renamed to
    the first available number.

    Parameters
    ----------
    src : str
        Path of the file to copy.

    dst : str
        Path of the file to copy to.

    pad_length : int
        Zero-padded length
    
    pad_length

    Returns
    -------
    If file was backed up, returns path to backup file, else None.

    '''
    path = get_first_available_filename(dst, pad_length, always_number)

    # create primary output dir
    makedirs(name=str(dst.parent), exist_ok=True)

    # copy file
    from shutil import copyfile
    logging.info(f'src={src}\ndst={dst}\n')
    copyfile(src, dst)

    return path

def save_image(image:CCDData, path:Path, overwrite:bool=True):
    '''
    Save image to file. If file exists, it will be backed up and overwritten.

    Parameters
    ----------
    image : CCDData
        Image to save.

    path : Path
        Path to save image to.

    '''
    path = Path(path)

    logging.info('Saving Bias to {out_file}')

    # ensure output directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    image.write(path, overwrite=overwrite)


class ImageScale(Enum):
    AsIs = 0
    HistEq = 1
    Linear = 2
    Remap01 = 3

def save_mono_png(image:CCDData, path, overwrite:bool=True, bits=16, image_scale:ImageScale=ImageScale.HistEq):
    path = Path(path)

    dtype = np.uint8
    max_val = 255.0
    if bits == 16:
        dtype = np.uint16
        max_val = 65535.0

    if image_scale == ImageScale.Remap01:
        data = np.clip(image.data, 0, max_val)
        data = data * max_val
    if image_scale == ImageScale.AsIs:
        data = np.clip(image.data, 0, max_val)

    elif image_scale == ImageScale.HistEq:
        data = image.data
        # apply histogram equalization stretch
        data = image.data
        stretch = HistEqStretch(data)
        norm = ImageNormalize(data, stretch=stretch, clip=True)
        data = norm(data)

        mn = np.min(data)
        mx = np.max(data)

        data = max_val * ((mx - mn) * data - mn)

    # convert to proper data type if not already
    if data.dtype != dtype:
        data = np.array(data, dtype=dtype)

    if overwrite and path.exists():
        path.unlink()

    # save image
    imsave(path, data)


def save_mono_jpg(image:CCDData, path:Path, overwrite:bool=True, softening_param:float=5.0, stretch:float=700.0):
    save_rgb_jpg(image, image, image, path, overwrite, softening_param, stretch)


def save_rgb_jpg(r:CCDData, g:CCDData, b:CCDData, path:Path, overwrite:bool=True, softening_param:float=5.0, stretch:float=700.0):
    '''
    Save image to file. If file exists, it will be backed up and overwritten.

    Parameters
    ----------
    r : CCDData
        Red channel of output image
        
    g : CCDData
        Green channel of output image
        
    b : CCDData
        Blue channel of output image
        
    path : Path
        Path to save image to.

    '''
    

    minimum = np.array([np.percentile(r, 1), np.percentile(g, 1), np.percentile(b, 1)])
    maximum = np.array([np.percentile(r, 99.5), np.percentile(g, 99.5), np.percentile(b, 99.5)])
    #TODO: implement histogram equalization
    
    if (not overwrite) and (path.exists()):
        path = get_first_available_filename(path, 3, True)

    rgb = make_lupton_rgb(r, g, b, minimum=minimum, Q=softening_param, stretch = stretch, filename=path)

    return path


def generate_filename(image:CCDData):
    '''
    Generate filename for image based on header values. Using binning instead resolution 
    for filename as it's assumed it's using the entire sensor. 

    '''

    instrument = str(image.header['instrume'].replace(' ', '_').replace(':', '').replace('/', ''))
    temp = str(image.header['ccd-temp'])
    binning = str(image.header['xbinning']) + 'x' + str(image.header['ybinning'])
    imagetype = str(image.header['imagetyp'])
    exp_time = str(image.header['exptime'])
    quality = calibration.get_quality(image.header)
    gain = calibration.get_gain(image.header)
    speed = calibration.get_speed(image.header)

    if imagetype == 'Bias Frame' or imagetype == 'Bias':
        filename = f'bias.{instrument}.b{binning}.{temp}C.q{quality}.g{gain}.s{speed}.fits'

    elif imagetype == 'Dark Frame' or imagetype == 'Dark':
        filename = f'dark.{instrument}.b{binning}.{temp}C.{exp_time}s.q{quality}.g{gain}.s{speed}.fits'

    elif imagetype == 'Flat Field' or imagetype == 'Flat':
        filename = f'flat.{instrument}.b{binning}.{temp}C.{exp_time}s.q{quality}.g{gain}.s{speed}.fits'

    return filename

