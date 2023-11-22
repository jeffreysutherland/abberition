from ccdproc import CCDData

# find stars in the image


def solve_wcs(ccd:CCDData, out_fn=None):
    '''
    WCS refinement flow:
    - load image
    - find stars
    - get Astrometry.net (astnet) WCS with point pairs
    - get gaias for astnet wcs
    - project gaias to px with astnet wcs
    - match found stars with astnet projected gaia pixels, keeping track of the gaia indices
    - get gwcs with matched star px to gaia sky coords with low spline order to handle edges
    - project all gaias via gwcs into pixels
    - match found stars with gaia gwcs pixels
    - local search for stars at gaia projected positions
    - 


    Future Improvements:
    - merge multiple wcs's to refine
    - fix refinement
    - deal with duplicates better

    Create or add the following to $HOME/.astropy/config/astroquery.cfg, or uncomment api_key line:

    [astrometry_net]

    ## The Astrometry.net API key.
    api_key = '#############'

    ## Name of server
    server = http://nova.astrometry.net

    ## Default timeout for connecting to server
    timeout = 120
    '''


    from astropy import units as u
    from astropy.coordinates import SkyCoord
    from astropy.io import fits
    from astropy.wcs.utils import fit_wcs_from_points
    from astropy.wcs import WCS
    from gwcs.wcstools import wcs_from_points
    import matplotlib.pyplot as plt
    import numpy as np
    from numpy.linalg import norm
    import os
    import pathlib
    import sys
    import logging

    p = os.path.abspath("../processing")
    if not p in sys.path:
        sys.path.append(p)
        
    from . import wcs_helpers

    log_status = True
    log_plots = True

    ###############################################################################
    # Configuration Parameters

    #filename = 'm27.ha.0'
    filename = 'pelican.10'

    # find stars
    fwhm_est = 1.7
    fwhm_min = 1.5
    find_threshold = 3.0
    min_star_count = 20

    # wcs
    gaia_request_count = 1000
    gaia_mag_limit=17
    max_sep_px = 25

    # gwcs refine
    gwcs_refin_max_stdev = 2.0
    hdus = ccd.to_hdu()
    im_hdu = hdus[0]
    header = im_hdu.header
    data = im_hdu.data.astype(np.float32)
    width, height = np.shape(data)

    logging.info('removing existing wcs header')
    wcs_helpers.remove_wcs_header(header)

    # find star pixel locations, ordered by brightness
    logging.info('Finding stars in image.')
    stars_tbl = find_stars(data, fwhm_est, fwhm_min, find_threshold)

    #return

    if len(stars_tbl) < min_star_count:
        logging.error(f'Not enough stars found - try tuning threshold and fwhm estimate')
        raise Exception('Not enough stars found - try tuning threshold and fwhm estimate')

    stars_x_px = np.array(stars_tbl['xcentroid'], dtype=np.float32)
    stars_y_px = np.array(stars_tbl['ycentroid'], dtype=np.float32)
    stars_px = np.array([stars_x_px, stars_y_px])

    matched_star_indices = np.array(range(len(stars_x_px)))
    all_star_indices = matched_star_indices
    logging.info(f'Found {len(stars_tbl)} stars.')

    # Use astrometry.net for initial wcs
    logging.info('Solving astrometry.net WCS')
    astnet_wcs = wcs_helpers.solve_astrometry_net(stars_x_px, stars_y_px, width, height)


    # Get contained GAIA stars
    logging.info('Searching for gaia stars within wcs footprint')
    gaias_tbl = wcs_helpers.gaia_get_wcs(astnet_wcs, (2048, 2048), max_count=gaia_request_count, mag_limit=gaia_mag_limit)

    # set up some data structures for the found gaiass
    gaias_ra = wcs_helpers.gaia_get_data(gaias_tbl, 'ra')
    gaias_dec = wcs_helpers.gaia_get_data(gaias_tbl, 'dec')
    gaias_sky = SkyCoord(gaias_ra, gaias_dec, unit='deg')
    gaias_sky_np = np.array([gaias_ra, gaias_dec])

    matched_gaia_indices = np.array(range(len(gaias_ra)))
    logging.info(f'... found {len(gaias_tbl)} Gaia stars.')

    def get_dists(src, dests):
        # src is [a, b]
        # dests is [[a0, a1, a2], [b0, b1, b2]]
        diffs = np.array([src[0]-dests[0], src[1]-dests[1]])
        dists = norm(diffs, axis=0)
        return dists

    def match_coords_px(stars_px, catalog_px):
        #  idx: indices into catalog_sky of the closest star in the catalog
        #  sep: separation of the closest star, NaN if bad result

        num_stars = len(stars_px[0])
        separations = [] #1.0e42 * np.ones(num_stars, dtype=np.float32)
        indices = [] #np.zeros(num_stars, dtype=np.int32)

        for i in range(num_stars):
            # get distances to other stars
            seps = get_dists(stars_px[:,i], catalog_px)
            
            # choose the closest
            min_idx = seps.argmin()

            # store the separation
            #separations[i] = seps[min_idx]
            #indices[i] = min_idx
            separations.append(seps[min_idx])
            indices.append(min_idx)

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

    logging.info('matching gaia projections with found star positions')
    astnet_gaias_px = np.array(astnet_wcs.world_to_pixel(gaias_sky))
    idx, sep = match_coords_px(stars_px, astnet_gaias_px)
    logging.info(f'Found {sum(np.isnan(sep))} stars with duplicate gaias')

    is_dup = np.isnan(sep)
    dup_gaia_ind = idx[is_dup]

    sep_constraint = (sep < max_sep_px) & ~np.isnan(sep)

    matched_stars_px = stars_px[:,sep_constraint]

    matched_gaias_sky = gaias_sky[idx[sep_constraint]]
    matched_gaias_sky_np = np.array([matched_gaias_sky.ra.deg, matched_gaias_sky.dec.deg])

    # track indices
    star_gaia_dup_indices = matched_star_indices[sep == np.NaN]

    matched_star_indices = matched_star_indices[sep_constraint]
    matched_gaia_indices = matched_gaia_indices[idx[sep_constraint]]

    logging.info('calculating gwcs')
    gwcs_wcs = wcs_from_points(matched_stars_px, matched_gaias_sky)

    # Refine gwcs by removing all more than x stdev's from wcs says they should be
    matched_gaias_gwcs_px = np.array(gwcs_wcs.world_to_pixel(matched_gaias_sky_np[0], matched_gaias_sky_np[1]))
    diff_gwcs = matched_gaias_gwcs_px - matched_stars_px
    dist_gwcs = get_dists([0, 0], diff_gwcs)
    std_gwcs = np.std(dist_gwcs)

    dist_in_range = dist_gwcs < gwcs_refin_max_stdev * std_gwcs

    matched_star_indices = matched_star_indices[dist_in_range]
    matched_gaia_indices = matched_gaia_indices[dist_in_range]

    logging.info('refining wcs')
    
    # recalc gwcs WCS from best matches
    refined_gwcs = wcs_from_points(matched_stars_px, matched_gaias_sky, poly_degree=3)
    refined_gwcs_fits = refined_gwcs.to_fits_sip(((0, width), (0, height)))

    refined_wcs = WCS(refined_gwcs_fits)

    logging.info('creating data table for fits')
    fits_tbl = wcs_helpers.create_starinfo_table(stars_tbl, matched_star_indices, gaias_tbl, matched_gaia_indices)
    hdus.append(fits_tbl)

    logging.info('writing fits output file')
    
    # save to output file
    hdus[0].header.update(refined_gwcs_fits)

    if out_fn is not None:
        hdus.writeto(out_fn, overwrite=True)
        hdus.close()
        wcs_ccd = CCDData.read(out_fn, unit="adu")  
    else:
        wcs_ccd = ccd.copy()
        wcs_ccd.wcs = refined_wcs
    
    return wcs_ccd

def find_stars(data, fwhm_est=2.0, fwhm_min=1.5, threshold_stddevs=4.0, mask=None):
    '''
    Finds stars via iraf method and returns table with:
        id: unique object identification number.
        xcentroid, ycentroid: object centroid.
        fwhm: object FWHM.
        sharpness: object sharpness.
        roundness: object roundness.
        pa: object position angle (degrees counter clockwise from the positive x axis).
        npix: the total number of (positive) unmasked pixels.
        sky: the local sky value.
        peak: the peak, sky-subtracted, pixel value of the object.
        flux: the object instrumental flux.
        mag: the object instrumental magnitude calculated as -2.5 * log10(flux).

    '''
    from astropy.stats import sigma_clipped_stats
    from photutils.detection import IRAFStarFinder

    mean, median, std = sigma_clipped_stats(data, sigma=3.0)

    iraffind = IRAFStarFinder(fwhm=fwhm_est, exclude_border=True, threshold=threshold_stddevs * std)
    sources = iraffind.find_stars(data, mask=mask)
    sources.sort('peak', reverse=True) 

    return sources

