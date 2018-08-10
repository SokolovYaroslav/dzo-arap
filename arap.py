import numpy as np

def compute_mask(mask, orig, int width, int height, int tolerance):
    """
    mask: np.ndarray of bools with shape (height, width)
    orig: np.ndarray of ints with shape (height, width, 3) (RGB channels)
    width: int
    height: int
    tolerance: int

    Returns: None, but should fill mask array
    """
    pass

def clear(orig, data, width, height):
    data = orig[0, 0, :]

def dot(double * homography, float x, float y, float &rx, float &ry):
    