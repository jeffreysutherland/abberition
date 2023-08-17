# An assortment of visualizations to display data


import astropy.visualization as vis
from astropy.wcs import WCS
import matplotlib.pyplot as plt
import numpy as np
from numpy.linalg import norm
from astropy.visualization import make_lupton_rgb, ImageNormalize
from astropy.visualization.stretch import HistEqStretch

def hist_eq(data, max_val):
    # apply histogram equalization stretch
    stretch = HistEqStretch(data)
    norm = ImageNormalize(data, stretch=stretch, clip=True)
    data = norm(data)

    mn = np.min(data)
    mx = np.max(data)

    data = max_val * ((mx - mn) * data - mn)

    return data

def data_to_image(data, max_val=1.0):
    #low = np.nanpercentile(data, 0.001)
    #return vis.make_lupton_rgb(data, data, data, minimum=low, stretch=100, Q=6)
    return hist_eq(data, 1.0)

def new_plot(figsize=(20,20)):
    plt.figure(figsize=figsize)

def show_plot():
    plt.show()

def draw_wcs_grid(wcs:WCS, grid_res=20):
    # configure plot to draw wcs grid overlay
    pass

def draw_stars(x_stars, y_stars, style='bo', marker_size=16):
    plt.plot(x_stars, y_stars, style, fillstyle="none", ms=marker_size)

def draw_rejected_stars(im, x_stars, y_stars, x_rejected, y_rejected):
    # draw stars and rejected stars on image
    draw_stars(im, x_stars, y_stars, 'go')
    plt.plot(x_rejected, y_rejected, 'rx')

def points_to_image(x, y, val, min_x=0, min_y=0, max_x=2048, max_y=2048, grid_res=16j):
    # gridify points and return as 2d image array
    from  scipy.interpolate import griddata
    grid_x, grid_y = np.mgrid[min_x:max_x:grid_res, min_y:max_y:grid_res]
    return griddata((x, y), val, (grid_x, grid_y), method='nearest').T

def draw_im_overlay(im, alpha=1.0, interp='bicubic', cmap='gray', show_scale=False):
    ix = plt.imshow(im, origin='lower', alpha=alpha, cmap=cmap, interpolation=interp)
    if show_scale:
        plt.colorbar(ix)

def draw_im_wcs_points(im, x_stars, y_stars, wcs:WCS, star_sky):
    draw_stars(im, x_stars, y_stars, 'bx', 10)
    wcs_px = star_sky.to_pixel(wcs)
    plt.plot(wcs_px[0], wcs_px[1], 'ro', fillstyle='none', ms=12)

def draw_im(data, stretch=True):
    im = data
    if stretch:
        im = data_to_image(data)

    plt.figure(figsize=(20,20))
    plt.imshow(im)

def draw_wcs_distortion(wcs:WCS, grid_res=20, exaggeration=10):
    # Draw exaggerated distortion map from WCS
    w = wcs.array_shape[1]
    h = wcs.array_shape[0]

    if np.isscalar(grid_res):
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

    # find and scale (exaggerate) offsets
    ex = exaggeration * (wcs_px[0] - px) + px
    ey = exaggeration * (wcs_px[1] - py) + py

    # plot grid with exaggerated offsets (and linear)
    pX = np.reshape(ex, (np.shape(X)))
    pY = np.reshape(ey, (np.shape(Y)))

    # draw undistorted pixel bounds
    bx = [0, 0, w, w, 0]
    by = [0, h, h, 0, 0]
    plt.plot(bx, by, c='blue')
    
    #draw vertical lines
    plt.plot(pX, pY, color='gray', linewidth=1)
    # draw horizontal
    plt.plot(pX.T, pY.T, color='gray', linewidth=1)

