from pathlib import Path
from ccdproc import ImageFileCollection
import logging

from . import calibration
from . import combine
from . import io
from . import standard


class Processor:
    lights_src:ImageFileCollection = None
    lights_calib:ImageFileCollection = None
    lights_solved:ImageFileCollection = None
    lights_stacked:ImageFileCollection = None

    flats_src:ImageFileCollection = None
    flats_calib:ImageFileCollection = None
    
    dest_path: Path = None
    light_src_path:Path = None
    light_calib_path:Path = None
    light_solved_path:Path = None
    light_stacked_path:Path = None
    flat_src_path:Path = None
    flat_calib_path:Path = None   


    def __init__(self, dest_path:Path):
        self.set_dest_path(dest_path)


    def set_dest_path(self, dest_path:Path, overwrite:bool=False):
        if dest_path is not None and dest_path.exists() and overwrite:
            io.mkdirs_rm_existing(dest_path)
        else:
            io.mkdirs_rm_existing(dest_path)

        self.dest_path = dest_path

        self.light_src_path = self.dest_path / 'lights_source'
        self.light_calib_path = self.dest_path / 'lights_calibrated'
        self.light_solved_path = self.dest_path / 'lights_solved'
        self.light_stacked_path = self.dest_path / 'lights_stacked'

        self.flat_src_path = self.dest_path / 'flats_src'
        self.flat_calib_path = self.dest_path / 'flats_cal'

    def set_source_lights(self, path:Path=None, ifc:ImageFileCollection=None, filters:dict=None):
        dest_path = path
        if dest_path == None and ifc != None:
            dest_path = ifc.location
        
        # if path is the intended source path, don't copy - just get an ifc
        copy_files = dest_path.absolute() != self.light_src_path.absolute()

        if copy_files:
            self.clear_lights()
            io.mkdirs_rm_existing(self.light_src_path)
            self.lights = self.__get_ifc(path, ifc, self.light_src_path, filters)
        else:
            # don't clear the source lights
            self.clear_lights(clear_src=False)
            self.lights_src = self.__get_ifc(path, ifc, self.light_src_path, filters)


    def set_calibrated_lights(self, path:Path=None, ifc:ImageFileCollection=None, filters:dict=None):
        self.clear_lights()
        io.mkdirs_rm_existing(self.light_calib_path)
        self.lights_calib = self.__get_ifc(path, ifc, self.light_calib_path, filters)

    
    def set_solved_lights(self, path:Path=None, ifc:ImageFileCollection=None, filters:dict=None):
        self.clear_lights()
        io.mkdirs_rm_existing(self.light_solved_path)
        self.lights_solved = self.__get_ifc(path, ifc, self.light_solved_path, filters)


    def clear_lights(self, clear_src:bool=True, clear_calib:bool=True, clear_solved:bool=True, clear_stacked:bool=True):
        if clear_src:
            self.lights_src = None
            io.rmdir(self.light_src_path)

        if clear_calib:
            self.lights_calib = None
            io.rmdir(self.light_calib_path)
        
        if clear_solved:
            self.lights_solved = None
            io.rmdir(self.light_solved_path)
    
        if clear_stacked:
            self.lights_stacked = None
            io.rmdir(self.light_stacked_path)


    def set_source_flats(self, path:Path=None, ifc:ImageFileCollection=None, filters:dict=None):
        self.clear_flats()
        io.mkdirs_rm_existing(self.flat_src_path)
        self.flats_src = self.__get_ifc(path, ifc, self.flat_src_path, filters)


    def set_calibrated_flats(self, path:Path=None, ifc:ImageFileCollection=None, filters:dict=None):
        io.mkdirs_rm_existing(self.flats_src_path)

        self.flats_calib = None
        self.flats_src = self.__get_ifc(path, ifc, self.flat_calib_path, filters)
        

    def clear_flats(self):
        self.flats_src = None
        self.flats_calib = None

        io.rmdir(self.flat_src_path)
        io.rmdir(self.flat_calib_path)


    def __get_ifc(self, src_path:Path=None, ifc:ImageFileCollection=None, target_path:Path=None, filters:dict=None) -> ImageFileCollection:
        if ifc is not None and src_path is not None:
            raise ValueError('Cannot specify both ifc and src_path')
        elif ifc is not None:
            ifc = io.copy_ifc(ifc, target_path)
        elif src_path is not None:
            ifc = io.get_images(src_path, target_dir=target_path, copy_to_temp_dir=False, filters=filters, sanitize_headers=True)
        else:
            raise ValueError('Must specify one of path or ifc')

        return ifc
    

    def calibrate_flats(self):
        logging.debug('Deleting existing flat calib dir if it exists')
        io.mkdirs_rm_existing(self.flat_calib_path)

        if self.flats_src is None:
            raise ValueError('Must call set_source_flats before calibrate_flats')
        else:
            self.flats_calib = standard.create_flats(self.flats_src, out_path=self.flat_calib_path, min_exp=1.5, reject_too_dark=False, ignore_temp=True, overwrite=True)


    def calibrate_lights(self):
        '''
        Calibrates the lights by applying bias, dark and flat field correction to each light image.

        If flats are to be used, they must be created first 

        Returns:
            None
        '''
        io.mkdirs_rm_existing(self.light_calib_path)
    
        if self.lights_src is not None:
            calib_fns = []

            for src, src_fn in self.lights_src.ccds(return_fn=True):
                calib_light = calibration.calibrate_light(src, self.flats)
                calib_fns.append(src_fn)
                calib_light.write(self.light_calib_path / src_fn)

            self.lights_calib = ImageFileCollection(self.light_calib_path, filenames=calib_fns)

    def stack_lights(self, resolution:float=1.0):
        io.mkdirs_rm_existing(self.light_stacked_path)
        
        images = None
        reprojection = None

        stacked_images = []

        if self.lights_solved is not None:
            logging.info('Stacking solved lights')
            images = self.lights_solved
            reprojection = combine.get_reprojection(images, resolution)
        elif self.lights_calib is not None:
            logging.info('Stacking calibrated lights')
            images = self.lights_calib
        elif self.lights_src is not None:
            logging.info('Stacking source lights')
            images = self.lights_src
        else:
            raise ValueError('Must have lights to stack')

        if images is not None:
            # get all optical filters from keywords
            filters = set(h['filter'] for h in images.headers())

            # for each filter
            for filter in filters:
                # get all images for that filter
                filter_images = images.filter(filter=filter)

                ccd = None

                if reprojection is not None:
                    ccd = combine.combine_solved_images(filter_images, reprojection)
                else:
                    ccd = combine.combine_solved_images(filter_images) 

                if ccd is not None:
                    fn = self.light_stacked_path / f'{filter}.fits'
                    ccd.write(fn)
                    stacked_images.append(ccd)

        self.lights_stacked = ImageFileCollection(location=self.light_stacked_path, filenames=stacked_images)

        return self.lights_stacked

    def solve_astrometry(self):
        io.mkdirs_rm_existing(self.light_solved_path)

        if self.lights_calib is not None:

            wcs_path = self.dest_path / 'wcs'
            self.lights_solved = standard.solve_astrometry(self.lights, wcs_path)

    def summary(self):
        self.__log_ifc(self.lights_src, 'lights_src')
        self.__log_ifc(self.lights_calib, 'lights_calib')
        self.__log_ifc(self.lights_solved, 'lights_solved')
        self.__log_ifc(self.lights_stacked, 'lights_stacked')
        self.__log_ifc(self.flats_src, 'flats_src')
        self.__log_ifc(self.flats_calib, 'flats_calib')

    def __log_ifc(self, ifc:ImageFileCollection, name:str):
        if ifc is not None:
            logging.info(f'{name} collection {str(ifc.location)} has {len(ifc.files)} images\nSummary:\n{ifc.summary}')
        else:
            logging.info(f'{name} collection is None')

    def process(self):
        self.calibrate_flats()
        self.calibrate_lights()
        self.solve_astrometry()
        self.stack_lights()
