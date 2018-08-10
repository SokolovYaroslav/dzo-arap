import arap as lib

class PyWrapper:
    """ Wrapper for C functions """

    def __init__(self):
        self._lib = lib

    def mask(self, mask, orig, width, height, tolerance):
        mask = self._lib.compute_mask(mask, orig, width, height, tolerance)
        print(mask)
        print(mask.shape)
        print(mask.sum())

    def clear(self, orig, data, width, height):
        self._lib.clear(orig.data, data.data_as(c.POINTER(c.c_char)), width, height)

    def project(self, homography, mask, orig, data, width, height, corners):

        self._lib.project(
            homography.data,
            mask.data,
            orig.data,
            data.data,
            width,
            height,
            corners.data
        )
