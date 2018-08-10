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

def dot(homography, x, y, rx, ry):
    H = homography.dot(np.array([x, y, 1]))
    rx = H[0] / H[2]
    ry = H[1] / H[2]
    return rx, ry

def store(std::map<int,int> &left, std::map<int,int> &right, int x, int y):
    """
    Vrode o4evidno
    """
    pass

def points(std::map<int, int> &left, std::map<int,int> &right, bool swap, int x0, int y0, int x1, int y1):
    