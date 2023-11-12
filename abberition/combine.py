from . import io
from astropy import units as u
from astropy.wcs import WCS
from ccdproc import ImageFileCollection
from ccdproc import wcs_project
from pathlib import Path
from reproject import reproject_interp
from reproject.mosaicking import reproject_and_coadd, find_optimal_celestial_wcs

class Reprojection:
    def width(self):
        return self.shape[0]
    
    def height(self):
        return self.shape[1]

    def __init__(self, wcs:WCS, shape):
        self.wcs = wcs
        self.shape = shape
        

def get_reprojection(ifc:ImageFileCollection, res_arcsec:float=1.0):
    hdus = ifc.hdus()
    wcs_out, shape_out = find_optimal_celestial_wcs(hdus, resolution=res_arcsec * u.arcsec, auto_rotate=True)
    reprojection = Reprojection(wcs_out, shape_out)
    return reprojection


def reproject_images(ifc:ImageFileCollection, reprojection:Reprojection, dest_path:Path=None):
    files = []
    
    for ccd, fn in ifc.ccds(return_fname=True):
        projected = wcs_project(ccd, reprojection.wcs, shape_out=reprojection.shape)
        files.append(fn)
        projected.write(dest_path / fn, overwrite=True)
    
    projected_ifc = ImageFileCollection(dest_path, filenames=files, keywords='*')
    return projected_ifc

def combine_images(ifc:ImageFileCollection):

    #from astropy.nddata import CCDData
    from astropy.io import fits

    hdus = list(ifc.hdus())

    # get encompassing footprint
    wcs_out, shape_out = find_optimal_celestial_wcs(hdus, resolution=1.0 * u.arcsec, auto_rotate=True)

    # combine and align in one go
    array, footprint = reproject_and_coadd(hdus, wcs_out, shape_out=shape_out, reproject_function=reproject_interp, match_background=True)
