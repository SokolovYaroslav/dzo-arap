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

    def get_contour(self, parts=["whole"], continious=True):
        # TODO: support getting mask & contour for deformed image
        #if part not in ["whole", "body", "all"] and \
        #   part not in self.segmented_body_parts():
        #    print("Can't get contour for {}. No such body part found.".format(part))
        #    return None
        mask = sum([self.get_mask(part).astype(np.uint8) for part in parts])
        mask = np.clip(mask, 0, 1)

        chain_approx_method = cv2.CHAIN_APPROX_NONE if continious else cv2.CHAIN_APPROX_SIMPLE
        im2, contours, hierarchy = cv2.findContours(mask*255, cv2.RETR_TREE, chain_approx_method)
        cont_ind = np.argmax(np.array([cont.shape[0] for cont in contours]))
        contour = contours[cont_ind].reshape(-1, 2)[:,[1,0]]
        return contour

    def bounding_box(self):
        # [x0, y0, x1, y1] Note: y is counted from the top
        contour = np.array(self.get_contour())
        return [np.min(contour[:,1]), np.min(contour[:,0]), np.max(contour[:,1]), np.max(contour[:,0])]

    def mask2bool(self, mask):
        # TODO: more sophisticated method
        return mask.astype(np.bool)
