#%%
# Calibrate a directory of light frames. Flats must be created prior to running this script.

import logging
import warnings
logging.getLogger().setLevel(level=logging.INFO)

import test_setup

from pathlib import Path
from abberition import astrometry, conversion, io, calibration
from ccdproc import ImageFileCollection

from astropy.utils.exceptions import AstropyWarning
warnings.simplefilter('ignore', category=AstropyWarning)

astronomy_data_dir = '../../astrodev/astronomy.data/data/raw'
astronomy_data_path = Path(astronomy_data_dir)

logging.debug(f'data dir: {astronomy_data_dir}')
logging.debug(f'data path: {astronomy_data_path.absolute()}')

src_path = astronomy_data_path

light_src_root = astronomy_data_path
flat_src_root = Path('../.output/calib/')
light_out_root = Path('../.output/lights_g/')

# (light_dir, [flat_dirs])
data_sets = [ 
        #  light_dir          flat_dirs
        ('2023.05.12/m51', ['2023.05.12/sloan_r_flat', '2023.05.12/sloan_g_flat']),
        ('2023.05.18/m51', ['2023.05.12/sloan_g_flat', '2023.05.18/sloan_i_flat', '2023.05.18/ha_flat']),
    ]

# backup and/or create the lights directory
io.mkdirs_backup_existing(light_out_root)

for data_set in data_sets:
    light_dir = data_set[0]
    flat_dirs = data_set[1]

    light_src_path = light_src_root / light_dir
    logging.info(f'light_src_path={light_src_path}')
    
    # make paths of each flat dir
    flat_src_paths = [flat_src_root / flat_dir for flat_dir in flat_dirs]
    logging.info(f'flat_src_paths={[str(p) for p in flat_src_paths]}')

    # create dirs for raw lights and calibration frames
    out_path = light_out_root / data_set[0]
    io.mkdirs_backup_existing(out_path)
    logging.info(f'out_path={out_path}')

    calib_out_path = out_path / 'calib'
    io.mkdirs_backup_existing(calib_out_path)
    logging.info(f'calib_out_path={calib_out_path}')

    # copy flats to calib dir and save pngs
    flat_files = []
    for flat_src_path in flat_src_paths:
        flats = ImageFileCollection(flat_src_path, keywords=['*'])
        logging.info(f"Flat collection {str(flat_src_path)} has {len(flats.files)} image")

        for flat, flat_fn in flats.ccds(return_fname=True):
            logging.info(f'Processing \'{flat_fn}\'')
            flat_src = flat_src_path / flat_fn
            flat_dest = calib_out_path / flat_fn
            logging.info(f'Copying \'{flat_src}\' to \'{flat_dest}\'')

            flat_dest = io.copy(flat_src, flat_dest)
            io.save_mono_png(flat, flat_dest + '.png', True, 16, io.ImageScale.Remap01)
            flat_files.append(flat_dest)

    flats = ImageFileCollection(calib_out_path, keywords='*')

    # calibrate lights
    logging.info(f'Processing lights from \'{light_src_path}\'')
    raw_lights = io.get_images(light_src_path, True, sanitize_headers=True)

    io.mkdirs_backup_existing(out_path / 'lights')

    light_out_path = out_path / 'lights'
    io.mkdirs_backup_existing(light_out_path)

    for light, light_fn in raw_lights.ccds(return_fname=True, ccd_kwargs={'unit':'adu'}):
        logging.info(f'Processing \'{light_fn}\'')

        # calibrate the light
        calibrated_light, (bias, dark, flat) = calibration.calibrate_light(light, flats, return_calibration=True)

        # convert to 32-bit float
        calibrated_light = conversion.to_float32(calibrated_light)

        light_dest = light_out_path / light_fn
        calibrated_light.write(light_dest, overwrite=True)

        wcs_path = out_path / 'wcs'
        out_fn = wcs_path / light_fn
        wcs_ccd = astrometry.solve_wcs(calibrated_light, out_fn, overwrite=True)

        save_work = False
        if save_work:
            light_work_dir = out_path / '.work' / light_fn
            io.mkdirs_backup_existing(light_work_dir)

            # save the calibrated light as png in working
            io.save_mono_png(calibrated_light, str(light_dest) + '.png', True, 16, io.ImageScale.AsIs)

            # save the calibration frames
            bias_dest = light_work_dir / io.generate_filename(bias)
            bias = conversion.to_float32(bias)
            bias.write(bias_dest, overwrite=True)
            io.save_mono_png(bias, str(bias_dest) + '.png', True, 16, io.ImageScale.AsIs)

            dark_dest = light_work_dir / io.generate_filename(dark)
            dark = conversion.to_float32(dark)
            dark.write(dark_dest, overwrite=True)
            io.save_mono_png(dark, str(dark_dest) + '.png', True, 16, io.ImageScale.AsIs)

            if flat is not None:
                flat_dest = light_work_dir / io.generate_filename(flat)
                flat = conversion.to_float32(flat)
                flat.write(flat_dest, overwrite=True)
                io.save_mono_png(flat, str(flat_dest) + '.png', True, 16, io.ImageScale.Remap01)
            else:
                logging.warning('No flat for \'{light_fn}\'')

            # save the original light
            orig_dest = light_work_dir / ('orig.' + light_fn)
            light = conversion.to_float32(light)
            light.write(orig_dest, overwrite=True)
            io.save_mono_png(light, str(orig_dest) + '.png', True, 16, io.ImageScale.AsIs)


logging.info('finished...')

#%%
