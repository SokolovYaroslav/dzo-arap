import cv2
import os
import numpy as np
import sys


class Masker:
    PARTS = ["head", "left_leg", "right_leg", "left_arm", "right_arm"]
    COLORS = dict()
    for i in range(len(PARTS)):
        COLORS[PARTS[i]] = 50 * (i + 1)

    def __init__(self, mask_path=None, mask=None):
        self._mask_path = mask_path
        self._mask_im = None
        self.whole_mask = None
        self.body_mask = None
        self.parts_masks = dict()

        if mask_path is not None:
            self._mask_im = cv2.imread(self._mask_im)  # TODO: check if success
            self.whole_mask = self._mask_im[:, :, 0]
            if not self.is_binary(mask):
                self.body_mask = self.mask2bool(self._mask_im[:, :, 1])
                for part in self.PARTS:
                    self.parts_masks[part] = self._mask_im[:, :, 2] == self.COLORS[part]
        elif mask is not None:
            self.whole_mask = mask
            self._mask_im = mask.copy()
        else:
            print("Mask.py: Provide either mask as np.array, or path to mask")
            sys.exit(1)

    def is_binary(self, mask):
        # Check whether the layers are the same
        # TODO: more sophisticated method
        if len(mask.shape) == 2:
            return True
        return np.sum(mask) == np.sum(mask[:, :, 0]) * 3

    def save(self, path):
        return cv2.imwrite(path, self._mask_im * 255)

    def get_mask(self, part_name):
        if part_name in self.PARTS:
            return self.parts_mask[part_name]
        elif part_name == "whole" or part_name == "all":
            return self.whole_mask
        elif part_name == "body":
            return self.body_mask

    def mask2bool(self, mask):
        # TODO: more sophisticated method
        return mask.astype(np.bool)
