# -*- coding: utf-8 -*-

from pathlib import Path


def get_first_available_filename(path, pad_length: int=3, always_number: bool=True):
    '''
    Returns the first available filename in the form {path}.#, where # is the 
    first available number.

    Parameters
    ----------
    path : str
        Path of the file to check. 
        if file, extension will follow number
        if dir, number will be at end

    pad_length : int
        Zero-padded length of the number

    always_number : bool


    Returns
    -------
    str
        The first available filename.

    '''
    from os.path import exists, is_dir
    raise NotImplementedError
    orig_path = path
    path = Path(path)

    # check if path is a directory or a file
    if exists(path) or always_number:

        i = 0


        while True:
            test_path = Path()
            test_path = path_str + '.'
            if exists(path_str + '.' + str(i)):
                path = 
            i += 1
        

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
