import ctypes as c
from numpy.ctypeslib import ndpointer
import numpy as np

class CWrapper:
    """ Wrapper for C functions """

    def __init__(self):
        self._lib = c.cdll.libarap

        #compute_mask API
        self.cmask = self._lib.compute_mask
        self.cmask.restype = None
        self.cmask.argtypes = [ndpointer(c.c_bool, flags="C_CONTIGUOUS"),
                               ndpointer(c.c_uint8, flags="C_CONTIGUOUS"),
                               c.c_int, c.c_int, c.c_int]

        #clear API
        self.cclear = self._lib.clear
        self.cclear.restype = None
        self.cclear.argtypes = [ndpointer(c.c_uint8, flags="C_CONTIGUOUS"),
                                ndpointer(c.c_uint8, flags="C_CONTIGUOUS"),
                                c.c_int, c.c_int]

        #project API
        self.cproject = self._lib.project
        self.cproject.restype = None
        self.cproject.argtypes = [ndpointer(c.c_double, flags="C_CONTIGUOUS"),
                                  ndpointer(c.c_bool, flags="C_CONTIGUOUS"),
                                  ndpointer(c.c_uint8, flags="C_CONTIGUOUS"),
                                  ndpointer(c.c_uint8, flags="C_CONTIGUOUS"),
                                  c.c_int, c.c_int,
                                  ndpointer(c.c_int, flags="C_CONTIGUOUS")]

    def mask(self, mask, orig, width, height, tolerance):
        self.cmask(mask, orig, width, height, tolerance)

    def clear(self, orig, data, width, height):
        self.cclear(orig, data, width, height)

    def project(self, homography, mask, orig, data, width, height, corners):
        self.cproject(homography, mask, orig, data, width, height, corners)
