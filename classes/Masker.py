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
            self._mask_im = cv2.imread(self._mask_path)  # TODO: check if success
            self.whole_mask = self.mask2bool(self._mask_im[:, :, 0])
            if not self.is_binary(self._mask_im):
                self.body_mask = self.mask2bool(self._mask_im[:, :, 1])
                for part in self.PARTS:
                    part_mask = self._mask_im[:, :, 2] == self.COLORS[part]
                    if part_mask.sum() > 0:
                        self.parts_masks[part] = part_mask
        elif mask is not None:
            self.whole_mask = mask
            self._mask_im = mask.copy()
        else:
            print("Mask.py: Provide either mask as np.array, or path to mask")
            sys.exit(1)

    def is_segmented(self):
        return self.is_binary(self._mask_im)

    def is_binary(self, mask):
        # Check whether the layers are the same
        # TODO: more sophisticated method
        if len(mask.shape) == 2:
            return True
        diff1 = mask[:, :, 1] - mask[:, :, 0]
        diff2 = mask[:, :, 2] - mask[:, :, 0]
        return diff1.sum() + diff2.sum() == 0

    def segmented_body_parts(self):
        return self.parts_masks.keys()

    def save(self, path):
        return cv2.imwrite(path, self._mask_im*(255/np.max(self._mask_im)))

    def get_mask(self, part_name):
        if part_name in self.parts_masks:
            return self.parts_masks[part_name]
        elif part_name == "whole" or part_name == "all":
            return self.whole_mask
        elif part_name == "body":
            return self.body_mask
        else:
            return None

    def get_contour(self, continious=True):
        # TODO: support getting mask & contour for deformed image
        chain_approx_method = cv2.CHAIN_APPROX_NONE if continious else cv2.CHAIN_APPROX_SIMPLE
        im2, contours, hierarchy = cv2.findContours(self.get_mask('whole').astype(np.uint8)*255, cv2.RETR_TREE, chain_approx_method)
        contour = contours[0].reshape(-1, 2)
        return contour

    def mask2bool(self, mask):
        # TODO: more sophisticated method
        return mask.astype(np.bool)
