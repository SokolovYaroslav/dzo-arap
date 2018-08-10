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
    empty = orig[0:0:] & 255
    # bounds
    lo = empty - tolerance
    up = empty + tolerance
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
        px = orig[y:x:] & 255
        if all([px[i] >= lo[i] and px[i] <= up[i] for i in len(px)]):
            mask[y][x] = False
            for dx, dy in d:
                queue.append((x + dx, y + dy))

def clear(orig: np.ndarray, data: np.ndarray, width: int, height: int):
    data = [[orig[0, 0, :] for _ in range(width)] for _ in range(height)]

def project():
    pass

def dot(homography: np.ndarray, x: float, y: float, rx: float, ry: float):
    pass
    