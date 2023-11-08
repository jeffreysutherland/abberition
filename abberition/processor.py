from pathlib import Path
from ccdproc import ImageFileCollection

from . import calibration
from . import io
from . import standard


class Processor:
    lights_src:ImageFileCollection = None
    lights_calib:ImageFileCollection = None
    lights_solved:ImageFileCollection = None
    lights_stacked:ImageFileCollection = None

    flats_src:ImageFileCollection = None
    flats:ImageFileCollection = None
    
    dest_path: Path = None
    light_src_path:Path = None
    light_cal_path:Path = None
    lights_solved_path:Path = None
    lights_stacked_path:Path = None
    flats_src_path:Path = None
    flats_cal_path:Path = None   


    def __init__(self, dest_path:Path):
        self.set_dest_path(dest_path)


    def set_dest_path(self, dest_path:Path, overwrite:bool=False):
        if dest_path is not None and dest_path.exists() and overwrite:
            io.mkdirs_rm_existing(dest_path)
        else:
            io.mkdirs_rm_existing(dest_path)

        self.dest_path = dest_path

        self.light_src_path = self.dest_path / 'lights_src'
        self.light_cal_path = self.dest_path / 'lights_cal'
        self.light_solved_path = self.dest_path / 'lights_solved'
        self.light_stacked_path = self.dest_path / 'lights_stacked'
        self.flats_src_path = self.dest_path / 'flats_src'
        self.flats_cal_path = self.dest_path / 'flats_cal'
        self.processing_path = self.dest_path / 'processing'

        io.mkdirs_rm_existing(self.light_src_path)
        io.mkdirs_rm_existing(self.light_cal_path)
        io.mkdirs_rm_existing(self.light_solved_path)
        io.mkdirs_rm_existing(self.light_stacked_path)
        io.mkdirs_rm_existing(self.flats_src_path)
        io.mkdirs_rm_existing(self.flats_cal_path)
        io.mkdirs_rm_existing(self.processing_path)


    def set_lights(self, path:Path=None, ifc:ImageFileCollection=None, filters:dict=None):
        self.lights_src_ifc = self.__get_ifc(self.light_src_path, ifc, filters)


    def set_flats(self, path:Path=None, ifc:ImageFileCollection=None, filters:dict=None):
        self.flats_src = self.__get_ifc(path, ifc, filters)


    def __get_ifc(self, path:Path=None, ifc:ImageFileCollection=None, filters:dict=None) -> ImageFileCollection:
        if ifc is not None:
            if filters is not None:
                raise ValueError('Cannot specify both ifc and filters')
            self.light_ifc = ifc
        elif path is not None:
            self.light_ifc = io.get_images(path, copy_to_temp_dir=True, filters=filters, sanitize_headers=True)
        else:
            raise ValueError('Must specify one of path or ifc')

        return ifc
    

    def calibrate_flats(self):
        if self.flats is not None:
            self.flats = standard.create_flats(self.flats_src, out_path=self.flats_cal_path, min_exp=1.5, reject_too_dark=False, ignore_temp=True, overwrite=True)


    def calibrate_lights(self, use_flats:bool=True):
        # TODO: ensure light dir exists

        if use_flats and self.flats_src is not None and self.flats is None:
            self.calibrate_flats()

        if self.lights_src is not None:
            # calibrate lights
            calib_fns = []

            for src, src_fn in self.lights_src.ccds(return_fn=True):
                calib_light = calibration.calibrate_light(src, self.flats)
                calib_fns.append(src_fn)
                calib_light.write(self.light_cal_path / src_fn)

            self.lights_calib = ImageFileCollection(self.light_cal_path, filenames=calib_fns)            


    def solve_astrometry(self):
        if self.lights is not None:
            # solve wcs
            wcs_path = self.dest_path / 'wcs'
            self.lights = standard.solve_astrometry(self.lights, wcs_path)


    def create_dirs(self):
        self.light_src_path = self.dest_path / 'lights_src'
        self.light_cal_path = self.dest_path / 'lights_cal'
        self.lights_solved_path = self.dest_path / 'lights_solved'
        self.lights_stacked_path = self.dest_path / 'lights_stacked'

        self.flats_src_path = self.dest_path / 'flats_src'
        self.flats_cal_path = self.dest_path / 'flats_cal'


    def process(self):
        self.create_dirs()

        self.calibrate_flats()

        self.calibrate_lights()
        self.solve_astrometry()
