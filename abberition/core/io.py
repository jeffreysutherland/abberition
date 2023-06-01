# -*- coding: utf-8 -*-

from pathlib import Path

def get_first_available_dirname(path,  pad_length: int=3, always_number: bool=True):
    raise NotImplementedError

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
    from os.path import exists

    path = Path(path)
    ext = path.suffix()
    path_base = path.root

    new_path = path
    
    # rename dir if it exists
    if exists(str(path)) or always_number:
        path_str = str(path)
        i = 0

        while exists(path_str + '.' + str(i)):
            i += 1
            
        new_path = path_str + '.' + str(i)

    else:
        path_str = str(path)
        
    return path_str + '.' + str(i)


def mkdirs_backup_existing(path):
    '''
    Same as makedirs, but if the path already exists, the existing one will be 
    renamed as {path}.#, where # is the first available number.

    Parameters
    ----------
    path : str
        Path of the directory to create.

    Returns
    -------
    None.

    '''

    from os.path import exists
    from os import rename, makedirs

    # rename dir if it exists
    if exists(str(path)):
        path_str = str(path)
        i = 0
        while exists(path_str + '.' + str(i)):
            i += 1
            
        new_path = path_str + '.' + str(i)
        rename(path_str, new_path)
    
    # create primary output dir
    makedirs(name=str(path), exist_ok=False)

def mkdirs_rm_existing(path):
    '''
    Same as makedirs, but if the path already exists, the existing one will be
    deleted and recreated.
    '''
    from os.path import exists
    from os import makedirs
    from shutil import rmtree

    # rename dir if it exists
    if exists(str(path)):
        rmtree(str(path))
    
    # create primary output dir
    makedirs(name=str(path), exist_ok=False)
