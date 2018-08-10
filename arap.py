import numpy as np
from collections import deque

def compute_mask(mask: np.ndarray, orig: np.ndarray, width: int, height: int, tolerance: int) -> None:
    """
    mask: np.ndarray of bools with shape (height, width)
    orig: np.ndarray of ints with shape (height, width, 3) (RGB channels)
    width: int
    height: int
    tolerance: int

    Returns: None, but should fill mask array
    """
    empty = orig[0, 0, :] & 255
    # bounds
    lo = empty - tolerance
    up = empty + tolerance
    print(lo, up)
    # queue
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
        px = orig[y, x, :] & 255
        print(px)
        if all([px[i] >= lo[i] and px[i] <= up[i] for i in range(len(px))]):
            mask[y][x] = False
            for dx, dy in d:
                queue.append((x + dx, y + dy))

def clear(orig: np.ndarray, data: np.ndarray, width: int, height: int):
    #Numpy smart enough for this
    data = orig[0, 0, :]

def dot(homography, x, y, rx, ry):
    H = homography.dot(np.array([x, y, 1]))
    rx = H[0] / H[2]
    ry = H[1] / H[2]
    return rx, ry

# def store(std::map<int,int> &left, std::map<int,int> &right, int x, int y):
#     """
#     Vrode o4evidno
#     """
#     pass

# def points(std::map<int, int> &left, std::map<int,int> &right, bool swap, int x0, int y0, int x1, int y1):
#     """
#     Nadeus', 4to to}|{e o4evidno
#     """
#     pass
