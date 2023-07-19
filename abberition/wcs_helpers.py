#%%
'''
Create WCS header with SIP based off astrometric solve

    Initial solve from $/examples/wcs.py


References:
Plate Solving:
- https://arxiv.org/abs/0910.2233   <- how astrometry.net works
- https://olegignat.com/how-plate-solving-works/
- https://www.hnsky.org/astap_astrometric_solving.htm
- https://github.com/lgrcia/twirl
- https://github.com/lgrcia/twirl/blob/master/docs/notebooks/under%20the%20hood.ipynb
- https://github.com/user29A/fastrometry
- https://github.com/keflavich/W51-GTC-2020/blob/master/parker/h2Band/wcsFunction.py
- https://scamp.readthedocs.io/en/latest/index.html


WCS:
- Mosaic keywords for Multi-HDU fits files: https://www.ucolick.org/%7Esla/fits/mosaic/
- https://fits.gsfc.nasa.gov/fits_wcs.html

# TODO: pass distortion model into solve wcs?

'''
from astropy import units as u
from astropy.coordinates import SkyCoord
from astroquery.astrometry_net import AstrometryNet
from astroquery.gaia import Gaia
from astropy.io import fits
from astropy.wcs.utils import fit_wcs_from_points
from enum import Enum
from gwcs.wcstools import wcs_from_points
from matplotlib import pyplot as plt
import numpy as np
from numpy.linalg import norm
import time
from  astropy.wcs import WCS
from . import visualize

def solve_astrometry_net(stars_x_px, stars_y_px, width, height):
    # Use astrometry.net for initial wcs
    print('Using astrometry.net for initial wcs')
    ast = AstrometryNet()
    #ast.api_key = '#############'

    hdr = ast.solve_from_source_list(stars_x_px, stars_y_px, image_width=width, image_height=height)
    return WCS(hdr)

def get_distortion(wcs:WCS, grid_res:None):
    # Draw exaggerated distortion map from WCS
    w = wcs.array_shape[1]
    h = wcs.array_shape[0]

    if grid_res is None:
        grid_res = [w, h]
    elif np.isscalar(grid_res):
        grid_res = [grid_res, grid_res]

    x = np.linspace(0, w-1, grid_res[0])
    y = np.linspace(0, h-1, grid_res[1])
    X, Y = np.meshgrid(x, y)
    
    scale_x = norm(wcs.wcs.cd[0])*3600
    scale_y = norm(wcs.wcs.cd[1])*3600

    # build a simple wcs with similar scale/rotation/translation parameters 
    # and project points
    lin_wcs = WCS(naxis=2)
    lin_wcs.wcs.crpix = wcs.wcs.crpix
    lin_wcs.wcs.cd = wcs.wcs.cd
    lin_wcs.wcs.crval = wcs.wcs.crval
    lin_wcs.wcs.ctype = ['RA---TAN', 'DEC--TAN']

    # get grid points of 
    px = np.reshape(X, (X.size))
    py = np.reshape(Y, (Y.size))

    # find sky position of pixels on undistorted wcs
    rect_sky = lin_wcs.pixel_to_world(px, py)

    # find pixel positions of undistorted sky positions on the actual wcs
    wcs_px = wcs.world_to_pixel(rect_sky)
    wcs_x = np.reshape(wcs_px[0], np.shape(X))
    wcs_y = np.reshape(wcs_px[1], np.shape(X))

    dx1 = wcs_x - px
    dy1 = wcs_y - py
    dl1 = norm(np.array([dx1, dy1]), axis=0)

    dx = np.reshape(dx1, np.shape(X))
    dy = np.reshape(dy1, np.shape(X))
    dl = np.reshape(dl1, np.shape(X))

    return X, Y, dx, dy, dl

def get_fov_deg(wcs, width_px, height_px):
    pts = wcs.pixel_to_world([0, width_px], [0, height_px])
    return pts[0].separation(pts[1]).deg

def get_center_sky(wcs, width_px, height_px):
    return wcs.pixel_to_world(width_px/2, height_px/2)

def extract_background(data):
    from photutils.background import Background2D, SExtractorBackground, MedianBackground, MMMBackground
    from astropy.stats import SigmaClip
    
    sigma_clip = SigmaClip(sigma=3.0)
    bkg_estimator = SExtractorBackground()
    bkg_proc = Background2D(data, (32, 32), filter_size=(3, 3), sigma_clip=sigma_clip, bkg_estimator=bkg_estimator)

    return bkg_proc.background

def gaia_get_wcs(wcs, im_size, pixel_border=50, max_count=1000, mag_limit=16):

    vert_x = [-pixel_border, -pixel_border, im_size[0]+pixel_border, im_size[0]+pixel_border]
    vert_y = [-pixel_border, im_size[0]+pixel_border, im_size[0]+pixel_border, -pixel_border]

    vert_sky = wcs.pixel_to_world(vert_x, vert_y)


    # need to call job.get_results() to get data table
    query = (f"select top {max_count} source_id, ra, dec, phot_g_mean_mag, phot_rp_mean_mag from gaiaedr3.gaia_source where "
                        f"phot_g_mean_mag < {mag_limit} "
                        "AND "
                        "1=CONTAINS("
                        "POINT('ICRS', ra, dec), "
                        "POLYGON('ICRS', "
                        f"{vert_sky[0].ra.deg}, {vert_sky[0].dec.deg}, "
                        f"{vert_sky[1].ra.deg}, {vert_sky[1].dec.deg}, "
                        f"{vert_sky[2].ra.deg}, {vert_sky[2].dec.deg}, "
                        f"{vert_sky[3].ra.deg}, {vert_sky[3].dec.deg})) "
                        "order by phot_g_mean_mag")
    #print(f'Gaia TAP query: \n{query}')

    job = Gaia.launch_job_async(query)

    while not job.is_finished():
        time.sleep(0.1)

    return job.get_results()

def gaia_get(num_stars, center:SkyCoord, fov_deg):
    # async await for a gaia job to complete
    job = gaia_request_async(num_stars, center, fov_deg)

    while not job.is_finished():
        time.sleep(0.1)

    return job.get_results()

def gaia_request_async(num_stars, center:SkyCoord, fov_deg):
    # need to call job.get_results() to get data table
    query = (f"select top {num_stars} source_id, ra, dec, phot_g_mean_mag, phot_rp_mean_mag from gaiaedr3.gaia_source where "
                        "1=CONTAINS("
                        f"POINT('ICRS', {center.ra.deg}, {center.dec.deg}), "
                        f"CIRCLE('ICRS',ra, dec, {fov_deg/2})) "
                        "order by phot_g_mean_mag")

    job = Gaia.launch_job_async(query)
    return job

def gaia_get_data(gaia_tbl, header):
    return np.array(gaia_tbl[header].data.data)

def remove_wcs_header(header:fits.Header):
    # TODO: make more robust
    wcs_keywords_to_remove = [
            'WCSAXES', 'WCSVER',
            'CRPIX1', 'CRPIX2', 
            'PC1_1', 'PC1_2', 'PC2_1', 'PC2_2',
            'CDELT1', 'CDELT2', 
            'CUNIT1', 'CUNIT2', 
            'CTYPE1', 'CTYPE2', 
            'CRVAL1', 'CRVAL2',
            'A_ORDER', 'AP_ORDER', 
            'A_0_0', 'A_0_1', 'A_0_2', 'A_0_3', 
            'A_1_0', 'A_1_1', 'A_1_2', 'A_1_3',
            'A_2_0', 'A_2_1', 'A_2_2', 'A_2_3',
            'A_3_0', 'A_3_1', 'A_3_2', 'A_3_3', 
            'B_ORDER', 'BP_ORDER',
            'B_0_0', 'B_0_1', 'B_0_2', 'B_0_3', 
            'B_1_0', 'B_1_1', 'B_1_2', 'B_1_3',
            'B_2_0', 'B_2_1', 'B_2_2', 'B_2_3',
            'B_3_0', 'B_3_1', 'B_3_2', 'B_3_3', 
            'CD1_1', 'CD1_2', 'CD2_1', 'CD2_2'
        ]

    for key in wcs_keywords_to_remove:
        header.remove(key, ignore_missing=True, remove_all=True)


def get_fits_sky_coord(header: fits.Header, ra_key='OBJCTRA', dec_key='OBJCTDEC'):
    return SkyCoord(header[ra_key], header[dec_key], frame='icrs', unit=(u.hourangle, u.deg))

def create_starinfo_table(stars_tbl, matched_star_indices, gaias_tbl, matched_gaia_indices):
    stars_id = np.array(stars_tbl['id'], dtype=np.int32)
    stars_x = np.array(stars_tbl['xcentroid'], dtype=np.int32)
    stars_y = np.array(stars_tbl['ycentroid'], dtype=np.int32)
    stars_fwhm = np.array(stars_tbl['fwhm'], dtype=np.float32)
    stars_sharpness = np.array(stars_tbl['sharpness'], dtype=np.float32)
    stars_roundness = np.array(stars_tbl['roundness'], dtype=np.float32)
    stars_pa = np.array(stars_tbl['pa'], dtype=np.float32)
    stars_sky = np.array(stars_tbl['sky'], dtype=np.float32)
    stars_peak = np.array(stars_tbl['peak'], dtype=np.float32)
    stars_flux = np.array(stars_tbl['flux'], dtype=np.float32)
    stars_mag = np.array(stars_tbl['mag'], dtype=np.float32)

    gaias_id = gaia_get_data(gaias_tbl, 'source_id')
    gaias_ra = gaia_get_data(gaias_tbl, 'ra')
    gaias_dec = gaia_get_data(gaias_tbl, 'dec')
    gaias_g_mag = gaia_get_data(gaias_tbl, 'phot_g_mean_mag')
    gaias_rp_mag = gaia_get_data(gaias_tbl, 'phot_rp_mean_mag')

    columns = []
    columns.append(fits.Column(name='id', format='J', array=stars_id[matched_star_indices]))
    columns.append(fits.Column(name='x', format='E', array=stars_x[matched_star_indices]))
    columns.append(fits.Column(name='y', format='E', array=stars_y[matched_star_indices]))
    columns.append(fits.Column(name='fwhm', format='E', array=stars_fwhm[matched_star_indices]))
    columns.append(fits.Column(name='sharpness', format='E', array=stars_sharpness[matched_star_indices]))
    columns.append(fits.Column(name='roundness', format='E', array=stars_roundness[matched_star_indices]))
    columns.append(fits.Column(name='pa', format='E', array=stars_pa[matched_star_indices]))
    columns.append(fits.Column(name='sky', format='E', array=stars_sky[matched_star_indices]))
    columns.append(fits.Column(name='peak', format='E', array=stars_peak[matched_star_indices]))
    columns.append(fits.Column(name='flux', format='E', array=stars_flux[matched_star_indices]))
    columns.append(fits.Column(name='mag', format='E', array=stars_mag[matched_star_indices]))

    columns.append(fits.Column(name='gaia_id', format='K', array=gaias_id[matched_gaia_indices]))
    columns.append(fits.Column(name='gaia_ra', format='D', array=gaias_ra[matched_gaia_indices]))
    columns.append(fits.Column(name='gaia_dec', format='D', array=gaias_dec[matched_gaia_indices]))
    columns.append(fits.Column(name='gaia_g_mag', format='E', array=gaias_g_mag[matched_gaia_indices]))
    columns.append(fits.Column(name='gaia_rp_mag', format='E', array=gaias_rp_mag[matched_gaia_indices]))

    fits_tbl = fits.BinTableHDU.from_columns(columns=columns)
    return fits_tbl

def get_dists(src, dests):
    # src is [a, b]
    # dests is [[a0, a1, a2], [b0, b1, b2]]
    diffs = dests - src
    dists = norm(diffs, axis=0)

    return dists

def match_coords_px(stars_px, catalog_px, window_extent_px=20):
    #  idx: indices into catalog_sky of the closest star in the catalog
    #  sep: separation of the closest star, NaN if bad result
    indices = []
    separations = []
    big_int=100000000000
    num_stars = len(stars_px[0])

    for i in range(num_stars):
        star_xy = stars_px[:,i]

        # get bool array of stars within window_extent_px
        l = star_xy - window_extent_px
        u = star_xy + window_extent_px

        ge = np.greater_equal(catalog_px.T, l)
        le = np.less_equal(catalog_px.T, u)
        c = np.array([ge.T[0], ge.T[1], le.T[0], le.T[1]]).T
        near = np.all(c, axis=1)
        nearby_star_indices = np.where(near)[0]

        if len(nearby_star_indices) > 0:
            nearby_stars = catalog_px.T[nearby_star_indices]

            seps = get_dists(star_xy, nearby_stars)
            min_idx = seps.argmin()

            indices.append(min_idx)
            separations.append(seps[min_idx])
        else:
            indices.append(big_int)
            separations.append(np.NaN)

    indices = np.array(indices)
    separations = np.array(separations)

    # remove stars with duplicate gaia indices 
    for i in range(num_stars):
        dups = [i]
        i_idx = indices[i]

        # get list of duplicates
        for j in range(i+1,num_stars):
            if i_idx == indices[j]:
                dups.append(j)

        # if there are dups, find the nearest stars and their offsets from the 
        # paired stars and find which of the dups is closest to that point
        if len(dups) > 1:
            # just setting separations to NaN so we don't use the points
            separations[dups] = np.NaN

    return np.array(indices), np.array(separations)    

def replace_wcs_fits(header, wcs):
    hdr = remove_wcs_header(header)
    hdr.wcs = wcs
    return hdr

def compute_wcs_fits(filename, out_filename, fwhm_est=2.0, find_threshold=3.0, fwhm_min=1.5, min_star_count=15, gaia_request_count=1000, gaia_mag_limit=17, max_match_sep_px=20, gwcs_refine_max_stdev=1.5):
    # fits file in, fits file out, full metadata saved
    hdus = fits.open(filename)
    hdu = hdus[0]
    data = hdu.data
    header = hdu.header
    
    wcs, tbl = generate_wcs(data, fwhm_est, find_threshold, fwhm_min, min_star_count, gaia_request_count, gaia_mag_limit, max_match_sep_px, gwcs_refine_max_stdev)

    out_fits = fits.HDUList()

    # create primary hdu with updated header info
    out_header = remove_wcs_header(header)
    replace_wcs_fits(header, wcs)
    primary = fits.PrimaryHDU(data, out_header)

    out_fits.append(primary)
    out_fits.append(tbl)  

    return out_fits  

def generate_wcs(data, fwhm_est=2.0, find_threshold=3.0, fwhm_min=1.5, min_star_count=15, gaia_request_count=1000, gaia_mag_limit=17, max_match_sep_px=20, gwcs_refine_max_stdev=1.5):
    width, height = np.shape(data)

    # find star pixel locations, ordered by brightness
    stars_tbl = find_stars(data, fwhm_est, fwhm_min, find_threshold)

    if len(stars_tbl) < min_star_count:
        raise Exception('Not enough stars found - try tuning threshold and fwhm estimate')

    stars_x_px = np.array(stars_tbl['xcentroid'], dtype=np.float32)
    stars_y_px = np.array(stars_tbl['ycentroid'], dtype=np.float32)
    stars_px = np.array([stars_x_px, stars_y_px])

    matched_star_indices = np.array(range(len(stars_x_px)))
    print(f'Found {len(stars_tbl)} stars.')

    # Use astrometry.net for initial wcs
    astnet_wcs = solve_astrometry_net(stars_x_px, stars_y_px, width, height)

    print(f'Astrometry.net WCS:\n{astnet_wcs}')

    # Get contained GAIA stars
    print('Searching for gaia stars within wcs footprint')
    gaias_tbl = gaia_get_wcs(astnet_wcs, (2048, 2048), max_count=gaia_request_count, mag_limit=gaia_mag_limit)

    # set up some data structures for the found gaiass
    gaias_ra = gaia_get_data(gaias_tbl, 'ra')
    gaias_dec = gaia_get_data(gaias_tbl, 'dec')
    gaias_sky = SkyCoord(gaias_ra, gaias_dec, unit='deg')
    gaias_sky_np = np.array([gaias_ra, gaias_dec])

    matched_gaia_indices = np.array(range(len(gaias_ra)))
    print(f'... found {len(gaias_tbl)} Gaia stars.')

    print('matching gaia projections with found star positions')
    astnet_gaias_px = np.array(astnet_wcs.world_to_pixel(gaias_sky))
    
    idx, sep = match_coords_px(stars_px, astnet_gaias_px)
    print(f'Found {sum(np.isnan(sep))} stars with duplicate gaias')

    sep_constraint = (sep < max_match_sep_px) & ~np.isnan(sep)
    
    matched_stars_px = stars_px[:,sep_constraint]

    matched_gaias_sky = gaias_sky[idx[sep_constraint]]
    matched_gaias_sky_np = np.array([matched_gaias_sky.ra.deg, matched_gaias_sky.dec.deg])

    # track indices
    matched_star_indices = matched_star_indices[sep_constraint]
    matched_gaia_indices = matched_gaia_indices[idx[sep_constraint]]

    return gaias_sky, astnet_gaias_px, astnet_wcs, matched_stars_px, matched_star_indices, matched_gaia_indices

    print('calculating gwcs')
    gwcs_wcs = wcs_from_points(matched_stars_px, matched_gaias_sky)

    # Refine gwcs by removing all more than x stdev's from wcs says they should be
    matched_gaias_gwcs_px = np.array(gwcs_wcs.world_to_pixel(matched_gaias_sky_np[0], matched_gaias_sky_np[1]))
    diff_gwcs = matched_gaias_gwcs_px - matched_stars_px
    dist_gwcs = get_dists([0, 0], diff_gwcs)
    std_gwcs = np.std(dist_gwcs)

    dist_in_range = dist_gwcs < gwcs_refine_max_stdev * std_gwcs

    matched_star_indices = matched_star_indices[dist_in_range]
    matched_gaia_indices = matched_gaia_indices[dist_in_range]

    print('refining wcs')
    # recalc gwcs WCS from best matches
    refined_gwcs = wcs_from_points(matched_stars_px, matched_gaias_sky, poly_degree=3)
    refined_gwcs_fits = refined_gwcs.to_fits_sip(((0, width), (0, height)))

    refined_wcs = WCS(refined_gwcs_fits)

    print('creating data table for fits')
    fits_tbl_hdu = create_starinfo_table(stars_tbl, matched_star_indices, gaias_tbl, matched_gaia_indices)

    return refined_wcs, fits_tbl_hdu

# TESTING
def test_solve_wcs():
    from astropy import units as u
    from astropy.io import fits
    import matplotlib.pyplot as plt
    import numpy as np
    import pathlib

    from . import visualize

    filename = 'pelican.00'

    # inputs
    src_path = pathlib.Path('../examples/data/wcs_test')

    in_filename = str(src_path / f'{filename}.fits')

    # Load file
    print(f'Loading fits file ({in_filename})')
    hdus = fits.open(in_filename)
    im_hdu = hdus[0]
    data = im_hdu.data.astype(np.float32)

    wcs, tbl = generate_wcs(data, fwhm_est=1.7)

    print(tbl)

    plt.figure(figsize=(20,20))
    visualize.draw_wcs_distortion(wcs)

#test_solve_wcs()

# %%
