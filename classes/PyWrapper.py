import arap as lib

class PyWrapper:
    """ Wrapper for C functions """

    def __init__(self):
        self._lib = lib

    def mask(self, mask, orig, width, height, tolerance):
        self._lib.compute_mask(mask, orig, width, height, tolerance)

    def clear(self, orig, data, width, height):
        self._lib.clear(orig, data, width, height)

    def project(self, homography, mask, orig, data, width, height, corners):

        self._lib.project(
            homography,
            mask,
            orig,
            data,
            width,
            height,
            corners
        )
