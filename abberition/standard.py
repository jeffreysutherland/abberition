# Create standard frames (bias, dark, flat) from a set of images
import tempfile
from astropy.stats import mad_std
import ccdproc as ccdp
from ccdproc import ImageFileCollection
import logging
import numpy as np 
import os
from pathlib import Path
import abberition
from abberition import library


def create_bias(biases: ImageFileCollection, sigma_low=5.0, sigma_high=5.0, data_type=np.float32):
    # get list of files
    bias_files = biases.files_filtered(include_path=True)
    logging.info(f'Combining {len(bias_files)} files to use for bias.')

    combined_bias = ccdp.combine(bias_files,
        unit='adu',
        method='average',
        sigma_clip=True,      
        sigma_clip_low_thresh=sigma_low,
        sigma_clip_high_thresh=sigma_high,         
        sigma_clip_func=np.ma.median,   
        sigma_clip_dev_func=mad_std, 
        mem_limit=2e9,
        dtype=data_type)
        
    combined_bias.meta['standard'] = True

    logging.info(f'Finished combining biases')


    return combined_bias

def is_bias_dark_match(bias, dark):
    '''
    Checks if a bias and dark are a match based on relevant properties.
    '''
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


    return  bias.header['imagetyp'] == 'Bias Frame' and \
            dark.header['imagetyp'] == 'Dark Frame' and \
            bias.header['instrume'] == dark.header['instrume'] and \
            bias.header['naxis'] == dark.header['naxis'] and \
            bias.header['naxis1'] == dark.header['naxis1'] and \
            bias.header['naxis2'] == dark.header['naxis2'] and \
            bias.header['xbinning'] == dark.header['xbinning'] and \
            bias.header['ybinning'] == dark.header['ybinning'] and \
            bias.header['ccd-temp'] == dark.header['ccd-temp'] and \
            bias.header['gain'] == dark.header['gain'] and \
            bias.header['readoutm'] == dark.header['readoutm']



def create_dark(darks: ImageFileCollection, sigma_low=5.0, sigma_high=5.0, data_type=np.float32, overwrite=True):

    # create working dir as output file name + '_working'
    working_path = Path(tempfile.TemporaryDirectory())
    working_path.mkdir(parents=True, exist_ok=True)

    calibrated_dark_files = []

    # TODO: ensure all darks have the same property values
    # TODO: If darks have different property values, output a 

    # for each dark, subtract bias
    for dark, dark_fn in darks.ccds(return_fname=True, ccd_kwargs={'unit':'adu'}):
        # Subtract bias and save
        dark_temp_fn = str(working_path / dark_fn)
        bias = library.select_bias(dark)
        dark_calibrated = ccdp.subtract_bias(dark, bias)
        dark_calibrated.write(dark_temp_fn, overwrite=True)

        # add to list of files
        calibrated_dark_files.append(dark_temp_fn)

    logging.debug(f'Combining {len(calibrated_dark_files)} to use for dark.')
    # combine calibrated darks for dark standard
    combined_dark = ccdp.combine(calibrated_dark_files,
        unit='adu',
        method='average',
        sigma_clip=True,      
        sigma_clip_low_thresh=sigma_low,
        sigma_clip_high_thresh=sigma_high,         
        sigma_clip_func=np.ma.median,   
        sigma_clip_dev_func=mad_std, 
        mem_limit=2e9,
        dtype=data_type)

    combined_dark.meta['combined'] = True

    combined_dark.write(out_file, overwrite=overwrite)

    # delete temp files
    print('Deleting temp files')
    for f in calibrated_dark_files:
        os.remove(f)

    # if working dir empty, delete it.
    if len(os.listdir(working_path)) == 0:
        os.removedirs(working_path)

    return combined_dark


def create_flats(ifc_biases, ifc_darks, ifc_flats, output_dir, min_exp=2.0, del_tmp=True, working_dir=None, del_intermediate_files=True, data_type=np.float32, overwrite=True):
    from pathlib import Path
    from os import makedirs
    import ccdproc as ccdp
    import numpy as np
    from astropy import units as u
    #from astropy.io import fits
    import abberition.io
    
    print('Creating master flats')
    
    # create output and calibrated dirs
    out_path = Path(output_dir)
    
    abberition.io.mkdirs_backup_existing(str(out_path))
    
    # pre-filter flat collection for flats only
    ifc_flats = ifc_flats.filter(imagetyp='Flat Field')
    
    # get list of all unique flat combinations
    # TODO: Rotator (position angle?)
    property_sets = set((h['instrume'], h['filter'], h['xbinning'], h['ybinning']) for h in ifc_flats.headers())

    out_flats = []    

    for (instrument, filt, xbin, ybin) in property_sets:
        print('Processing flat: [instrume=',instrument,'filter=', filt, 'bin:', xbin, 'x', ybin, ']')
        filters = {}
        filters['instrume'] = instrument
        filters['filter'] = filt
        filters['xbinning'] = xbin
        filters['ybinning'] = ybin

        ifc = ifc_flats.filter(**filters)
        to_combine = []

        # calibrate all flats
        print('  Calibrating flats...')
        for flat, filename in ifc.ccds(return_fname=True, ccd_kwargs={'unit':'adu'}):            

            max_val = 2 ** flat.header['bitpix']

            pct_1 = np.percentile(flat, 1) / max_val
            pct_99 = np.percentile(flat, 99) / max_val
            
            
            if pct_1 < 0.05:
                print('    Rejected', filename, 'as it is too dark')
            elif pct_99 > 0.9:
                print('    Rejected', filename, 'as it is too bright')
            elif flat.header['exptime'] < min_exp:
                print('    Rejected', filename, 'as exposure is too short (', flat.header['exptime'],'< 2.0s)')
            else:
                master_bias, master_bias_filename = abberition.library.select_bias(ifc_biases, flat)
                master_dark, master_bias_filename = abberition.library.select_dark(ifc_darks, flat)
                calibrated_flat = ccdp.subtract_bias(flat, master_bias, add_keyword=None)
                calibrated_flat = ccdp.subtract_dark(calibrated_flat, master_dark, exposure_time='exptime', exposure_unit=u.second, scale=True, add_keyword=None)
                calibrated_flat.meta['reduced'] = True
                calibrated_filename = str(out_path / filename)
                
                # save file
                calibrated_flat.write(calibrated_filename)
                
                to_combine.append(calibrated_filename)
                print('    Calibrated:', calibrated_filename)
               

        print('Finished calibrating flats')
    
        # stack flats
        print('Combining calibrated flats')
    
        # create scaler as inverse of the median
        def inv_median(a):
            return 1 / np.median(a)
    
        combined_flat = ccdp.combine(to_combine,
                                     method='median', 
                                     scale=inv_median,
                                     sigma_clip=False,
                                     mem_limit=2e9,
                                     add_keyword=None)
        
        combined_flat.meta['standard'] = True

        flat_path = out_path / flat_filename
        
        if del_tmp:
            for fn in to_combine:
                print(f'removing {fn}')
                os.remove(fn)

        combined_flat.write(str(flat_path))
        print('Finished processing flat:', flat_filename)
        out_flats.append(flat_filename)
        
    return ccdp.ImageFileCollection(str(out_path), filenames=out_flats)
