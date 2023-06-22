# Create standard frames (bias, dark, flat) from a set of images
from shutil import rmtree
import tempfile
from astropy.stats import mad_std
import ccdproc as ccdp
from ccdproc import ImageFileCollection
import logging
import numpy as np 
import os
from pathlib import Path
from abberition import calibration, io, library
from abberition import conversion


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
    Returns true if the bias and dark are compatible based on relevant properties
    '''

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



def create_dark(darks: ImageFileCollection, sigma_low:float=5.0, sigma_high:float=5.0, data_type=np.float32, del_tmp_dir:bool=True):
    '''
    Calibrate and create a dark standard from a collection of darks.
    '''

    logging.debug(f'create_dark: sigma_low={sigma_low}, sigma_high={sigma_high}, data_type={data_type}, del_tmp_dir={del_tmp_dir}')

    temp_dir = tempfile.mkdtemp()
    working_path = Path(temp_dir)

    calibrated_dark_files = []

    # TODO: If darks have different property values, output a collection of darks

    # for each dark, subtract bias
    for dark, dark_fn in darks.ccds(return_fname=True, ccd_kwargs={'unit':'adu'}):
        logging.debug(f'  calibrating dark: {dark_fn}')

        dark = conversion.to_float32(dark)

        # Subtract bias and save
        dark_calibrated = calibration.subtract_bias(dark)

        logging.debug(f'  saving calibrated dark: {dark_fn}')
        dark_temp_fn = str(working_path / dark_fn)
        dark_calibrated.write(dark_temp_fn, overwrite=True)

        # add to list of files
        calibrated_dark_files.append(dark_temp_fn)

    logging.debug(f'Combining {len(calibrated_dark_files)} to use for dark.')
    print(calibrated_dark_files)

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

    rmtree(temp_dir)

    return combined_dark


def create_flat(ifc_flats, out_dir, min_exp=1.5, dtype=np.float32, data_max=None):
    from pathlib import Path
    from os import makedirs
    from ccdproc import CCDData
    import numpy as np
    from astropy import units as u
    import abberition.io
    
    logging.info('Creating flat standard')
    
    # create output dir
    out_path = Path(out_dir)
    makedirs(out_path, exist_ok=True)

    abberition.io.mkdirs_backup_existing(out_path)
    
    # pre-filter flat collection for flats only
    ifc_flats = ifc_flats.filter(imagetyp='Flat Field')
    
    # get list of all unique flat combinations
    # TODO: Add rotator position angle?
    property_sets = set((h['instrume'], h['filter'], h['xbinning'], h['ybinning']) for h in ifc_flats.headers())

    out_flats = []

    for (instrument, filt, xbin, ybin) in property_sets:
        logging.info(f'Processing flats: [instrume="{instrument}", filter="{filt}", bin:{xbin}x{ybin}]')
        filters = {}
        filters['instrume'] = instrument
        filters['filter'] = filt
        filters['xbinning'] = xbin
        filters['ybinning'] = ybin

        ifc = ifc_flats.filter(**filters)
        to_combine = []

        working_dir = tempfile.mkdtemp()
        working_path = Path(working_dir)
        logging.debug(f'Created temp working dir {working_path} for calibrated flats.')

        # calibrate all flats
        for flat, flat_fn in ifc.ccds(return_fname=True, ccd_kwargs={'unit':'adu'}):            
            use_flat = True

            logging.debug('Testing for over/under exposure of flat for rejection')
            if data_max:
                max_data_val = data_max
            elif flat.header['bitpix'] > 0:
                max_data_val = 2 ** flat.header['bitpix'] - 1
            else:
                max_data_val = 65535
                logging.error(f'Max data value not defined for flat normalization. Using default of {max_data_val}')

            # TODO: handle nan's
            pct_1 = np.percentile(flat, 1) / max_data_val
            pct_99 = np.percentile(flat, 99) / max_data_val
            
            if pct_1 < 0.05:
                logging.debug(f'Rejected flat {flat_fn} as it is too dark')
                use_flat = False
            elif pct_99 > 0.9:
                logging.debug(f'Rejected flat {flat_fn} as it is too bright')
                use_flat = False

            if flat.header['exptime'] < min_exp:
                logging.debug(f'Rejected flat as exposure is too short ({flat.header["exptime"]}<{min_exp})')
                use_flat = False

            if use_flat:
                logging.debug(f'Using flat: {flat_fn}')

                # convert to data type
                flat = conversion.to_type(flat, dtype, True)

                # calibrate flat and save to temp dir
                calibrated_flat = calibration.calibrate_flat(flat)

                logging.debug(f'saving calibrated flat: {flat_fn}')
                flat_temp_fn = str(working_path / flat_fn)
                calibrated_flat.write(flat_temp_fn, overwrite=True)
                
                to_combine.append(flat_temp_fn)
                logging.debug(f'Calibrated ', flat_temp_fn)

        logging.debug(f'Combining {len(to_combine)} calibrated flats')
    
        # create scaler as inverse of median for combination
        def inv_median(a):
            return 1.0 / np.median(a)
    
        combined_flat = ccdp.combine(to_combine,
                                     method='median', 
                                     scale=inv_median,
                                     sigma_clip=False,
                                     mem_limit=2e9,
                                     add_keyword=None)
        
        combined_flat.meta['standard'] = True

        # normalize combined flat to max 1
        data = np.array(combined_flat.data)
        combined_flat.data = (1.0 / np.percentile(data, 99.9)) * data

        flat_fn = io.generate_filename(combined_flat)
        flat_path = out_path / flat_fn

        combined_flat.write(str(flat_path))
        out_flats.append(flat_fn)

        # rmtree working_path
        rmtree(working_dir)

        logging.info(f'Saved processed flat to: {flat_fn}')

    return ccdp.ImageFileCollection(str(out_path), filenames=out_flats)

