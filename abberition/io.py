# -*- coding: utf-8 -*-

import logging
from os import makedirs, rename
from os.path import exists
from pathlib import Path
from ccdproc import CCDData

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

    if (exists(path)):
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
