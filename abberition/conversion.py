from ccdproc import CCDData
import numpy as np


def to_float32(image:CCDData):
    return to_type(image, np.float32, True)

def to_type(image:CCDData, dtype:np.dtype, copy:bool=True):
    ''''''
    if copy:
        image = image.copy()

    image.data = image.data.astype(dtype)

    return image

