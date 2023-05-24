# -*- coding: utf-8 -*-

def mkdirs_backup_existing(path):
    '''
    Same as makedirs, but if the path already exists, the existing one will be 
    renamed as {path}.#, where # is the first available name.

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
