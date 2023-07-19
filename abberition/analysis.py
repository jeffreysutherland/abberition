import numpy as np
from ccdproc import CCDData


def get_stats(image:CCDData):
    data = image.data

    stats = {}
    stats['mean'] = np.mean(data)
    stats['median'] = np.median(data)
    stats['std'] = np.std(data)
    stats['min'] = np.min(data)
    stats['max'] = np.max(data)
    stats['pct_25'] = np.percentile(data, 25)
    stats['pct_75'] = np.percentile(data, 75)

    return stats


# calculate an optical system distortion model from multiple WCS

# calculate focal plane distortion

# generate a 3d view of the focal plane

# undisort an image with a distortion model

# profile the optical system using focal scan data

# create a flat profile for the sensor independent of the optical system