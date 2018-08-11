import numpy as np
from collections import deque
from math import floor, ceil

def round(x):
    c = ceil(x)
    f = floor(x)
    if c - x <= x - f:
        return c
    else:
        return f

def compute_mask(mask: np.ndarray, orig: np.ndarray, width: int, height: int, tolerance: int) -> None:
    """
    mask: np.ndarray of bools with shape (height, width)
    orig: np.ndarray of ints with shape (height, width, 3) (RGB channels)
    width: int
    height: int
    tolerance: int

    Returns: None, but should fill mask array
    """
    empty = np.array([int(i) for i in orig[0, 0, :]])
    # bounds
    lo = empty - tolerance
    up = empty + tolerance
    # queu
    queue = deque()
    queue.append((0, 0))
    d = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    # closed
    closed = np.full((height, width), False)
    while len(queue) != 0:
        x, y = queue.popleft()
        if x < 0 or x >= width or y < 0 or y >= height:
            continue
        if closed[y][x]:
            continue
        closed[y][x] = True
        px = orig[y, x, :]
        if all([px[i] >= lo[i] and px[i] <= up[i] for i in range(len(px))]):
            mask[y][x] = False
            for dx, dy in d:
                queue.append((x + dx, y + dy))
    return mask

def clear(orig: np.ndarray, data: np.ndarray, width: int, height: int) -> np.ndarray:
    data[:, :] = orig[0, 0, :]
    return data

def dot(homography, x, y):
    H = homography.dot(np.array([x, y, 1]))
    rx = H[0] / H[2]
    ry = H[1] / H[2]
    return rx, ry

def store(left: dict, right: dict, x: int, y: int) -> (dict, dict):
    if y in left:
        if x < left[y]:
            left[y] = x
        elif x < right[y]:
            right[y] = x
    else:
        left[y], right[y] = x, x
    return left, right

def points(left: dict, right: dict, swap: bool, x0: int, y0: int, x1: int, y1: int) -> (dict, dict):
    if swap:
        x0, y0 = y0, x0
        x1, y1 = y1, x1
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0
    if y1 < y0:
        y0 = -y0
        y1 = -y1
    D = 2 * dy - dx
    # add
    if swap:
        left, right = store(left, right, abs(y0), abs(x0))
    else:
        left, right = store(left, right, abs(x0), abs(y0))
    y = y0
    for x in range(x0 + 1, x1):
        D += 2 * dy
        if D > 0:
            y += 1
            D -= 2 * dx
        # add
        if swap:
            left, right = store(left, right, abs(y), abs(x))
        else:
            left, right = store(left, right, abs(x), abs(y))
    return left, right

def rasterize(corners: np.ndarray, left: dict, right: dict) -> (np.ndarray, dict, dict):
    for i in range(4):
        x0 = corners[i][0]
        y0 = corners[i][1]
        x1 = corners[(i + 1) % 4][0]
        y1 = corners[(i + 1) % 4][1]
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        points(left, right, dx <= dy, x0, y0, x1, y1)
    return corners, left, right

def project(homography: np.ndarray, mask: np.ndarray, orig: np.ndarray, data: np.ndarray,
            width: int, height: int, corners: np.ndarray) -> None:
    """
    homography: np.ndarray of doubles with shape (3, 3)
    mask: np.ndarray of bools with shape (height, width)
    orig: np.ndarray of ints with shape (height, width, 3) (RGB channels)
    data: np.ndarray of ints with shape (height, width, 3) (RGB channels)
    width: int
    height: int
    corners: np.ndarray of (x_coord, y_coord) with shape (4, )
    """
    left = dict()
    right = dict()
    corners, left, right = rasterize(corners, left, right)
    for y, x_left in left.items():
        x_right = right[y]
        for x in range(x_left, x_right + 1):
            rx, ry = dot(homography, float(x), float(y))
            lft, top = floor(rx), floor(ry)
            rgt, btm = lft + 1, top + 1
            if lft >= 0 and rgt < width and top >= 0 and btm < height:
                if not mask[int(round(ry))][int(round(rx))]:
                    continue
                coefX = rx - float(lft)
                coefY = ry - float(top)
                tl = (1. - coefX) * (1. - coefY)
                tr = coefX * (1. - coefY)
                bl = (1. - coefX) * coefY
                br = coefX * coefY
                data[y][x] = tl * orig[top][lft] +\
                             tr * orig[top][rgt] +\
                             bl * orig[btm][lft] +\
                             br * orig[btm][rgt]